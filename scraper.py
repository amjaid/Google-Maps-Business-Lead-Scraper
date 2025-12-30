import asyncio
import re
import pandas as pd
from playwright.async_api import async_playwright, Playwright
import undetected_playwright

# Assuming config.py is in the same directory
from config import BASE_URL, SEARCH_QUERIES, SELECTORS, OUTPUT_DIR, MAX_SCROLL_ATTEMPTS, MAX_LEADS_PER_QUERY, SCROLL_PAUSE

async def extract_business_details(page, card_locator):
    """
    Clicks a business card and extracts detailed data from the main panel.
    Returns a dictionary of business data.
    """
    data = {
        "name": None,
        "category": None,
        "address": None,
        "phone": None,
        "website": None,
        "rating": None,
        "reviews": None,
        "url": None
    }
    
    try:
        # Click the card to load details
        await card_locator.click()
        
        # Wait for the detail panel to stabilize. 
        # Watching for the address button is a good proxy for "loaded"
        try:
            await page.wait_for_selector(SELECTORS["address_button"], timeout=3000)
        except:
            pass # Some valid businesses might not have addresses
            
        # 1. Name
        if await page.locator(SELECTORS["business_name"]).count() > 0:
            data["name"] = await page.locator(SELECTORS["business_name"]).first.inner_text()
            
        # 2. Address (Using data-item-id)
        if await page.locator(SELECTORS["address_button"]).count() > 0:
            data["address"] = await page.locator(SELECTORS["address_button"]).first.get_attribute("aria-label")
            if data["address"]:
                data["address"] = data["address"].replace("Address: ", "").strip()

        # 3. Phone (Using data-item-id)
        if await page.locator(SELECTORS["phone_button"]).count() > 0:
            data["phone"] = await page.locator(SELECTORS["phone_button"]).first.get_attribute("aria-label")
            if data["phone"]:
                data["phone"] = data["phone"].replace("Phone: ", "").strip()
        
        # 4. Website (Using data-item-id)
        if await page.locator(SELECTORS["website_link"]).count() > 0:
            data["website"] = await page.locator(SELECTORS["website_link"]).first.get_attribute("href")

        # 5. Rating & Reviews
        if await page.locator(SELECTORS["rating_span"]).count() > 0:
            raw_rating = await page.locator(SELECTORS["rating_span"]).first.get_attribute("aria-label")
            match = re.search(r"(\d+\.\d+)", raw_rating or "")
            if match:
                data["rating"] = float(match.group(1))

        if await page.locator(SELECTORS["review_count_span"]).count() > 0:
            raw_reviews = await page.locator(SELECTORS["review_count_span"]).first.get_attribute("aria-label")
            match = re.search(r"([\d,]+)", raw_reviews or "")
            if match:
                data["reviews"] = int(match.group(1).replace(",", ""))
                
        # 6. Category
        if await page.locator(SELECTORS["category_button"]).count() > 0:
             data["category"] = await page.locator(SELECTORS["category_button"]).first.inner_text()

    except Exception as e:
        print(f"Error extracting details: {e}")
        
    return data

async def run_scraper():
    # Use undetected_playwright's async_playwright
    async with async_playwright() as p:
        # Launch Browser (Stealth Mode)
        # Undetected Playwright is most effective with headless=False
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"]
        )
        
        # Create a new context. 
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        all_leads = []

        for query in SEARCH_QUERIES:
            print(f"--- Processing Query: {query} ---")
            
            # Navigate
            await page.goto(BASE_URL)
            
            # Handle Consent Modal (EU Support)
            try:
                consent = page.locator(SELECTORS["consent_accept_button"])
                if await consent.is_visible(timeout=3000):
                    await consent.click()
                    print("Consent accepted.")
            except:
                pass

            # Search
            await page.locator(SELECTORS["search_box_input"]).fill(query)
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(3000) # Initial Load

            # Infinite Scroll
            try:
                await page.wait_for_selector(SELECTORS["feed_panel"], timeout=10000)
            except:
                print("Feed not found. Skipping.")
                continue

            feed = page.locator(SELECTORS["feed_panel"])
            
            print("Scrolling feed...")
            for i in range(MAX_SCROLL_ATTEMPTS):
                await feed.evaluate("el => el.scrollTop = el.scrollHeight")
                await page.wait_for_timeout(SCROLL_PAUSE * 1000)
                
                # Check lead count
                count = await page.locator(SELECTORS["result_card_link"]).count()
                if count >= MAX_LEADS_PER_QUERY:
                    print(f"Reached target lead count: {count}")
                    break
            
            # Extract
            card_locators = await page.locator(SELECTORS["result_card_link"]).all()
            print(f"Found {len(card_locators)} cards. Beginning extraction...")
            
            # Process strictly up to limit
            limit = min(len(card_locators), MAX_LEADS_PER_QUERY)
            for i in range(limit):
                print(f"Processing lead {i+1}/{limit}")
                lead_data = await extract_business_details(page, card_locators[i])
                lead_data["search_query"] = query 
                all_leads.append(lead_data)
                
            # Clear search for next iteration
            try:
                await page.locator(SELECTORS["clear_search_button"]).click()
            except:
                pass

        await browser.close()

        # Data Cleaning & Export
        if all_leads:
            df = pd.DataFrame(all_leads)
            
            # Deduplication
            initial_count = len(df)
            df.drop_duplicates(subset=["name", "address"], inplace=True)
            print(f"Removed {initial_count - len(df)} duplicates.")
            
            # Export
            import os
            if not os.path.exists(OUTPUT_DIR):
                os.makedirs(OUTPUT_DIR)
                
            filename = f"{OUTPUT_DIR}/leads_export.csv"
            df.to_csv(filename, index=False)
            print(f"Successfully saved {len(df)} leads to {filename}")
        else:
            print("No leads extracted.")

if __name__ == "__main__":
    asyncio.run(run_scraper())