import time
import pandas as pd
import config
import asyncio
from playwright.async_api import async_playwright
import random

data = []

# ------------------------
# Helpers
# ------------------------
def add_item(name, category, address, phone, url, rating, reviews, location):
    data.append({
        "Business name" : name,
        "Business category" : category,
        "Full address" : address,
        "Phone number (if available)" : phone,
        "Website URL" : url,
        "Star rating" : rating,
        "Total number of reviews" : reviews,
        "Business location" : location
    })


async def safe_text(locator):
    try:
        text = await locator.inner_text()
        return text.strip() if text else "N/A"
    except:
        return "N/A"


async def extract_and_add_business_data(card):
    """Extract data from a business card and add to data list"""
    try:
        # Get the UaQhfb container where most data is stored
        container = card.locator(".UaQhfb.fontBodyMedium")
        
        # 1. Business Name
        name_element = container.locator(".qBF1Pd.fontHeadlineSmall")
        name = await safe_text(name_element)
        
        if name == "N/A":
            print("Skipping card - no name found")
            return False
        
        # ---- CATEGORY & ADDRESS (ROBUST) ----
        category = "N/A"
        address = "N/A"

        info_blocks = container.locator(".W4Efsd span")

        for i in range(await info_blocks.count()):
            text = await safe_text(info_blocks.nth(i))

            if not text or text in ("·",):
                continue

            # CATEGORY: short, no digits, no RM, no Open/Closed
            if (
                category == "N/A"
                and len(text) < 30
                and not any(x in text for x in ["RM", "Open", "Closed", "Opens"])
                and not any(char.isdigit() for char in text)
            ):
                category = text
                continue

            # ADDRESS: long text with numbers or commas
            if (
                address == "N/A"
                and len(text) > 30
                and any(char.isdigit() for char in text)
            ):
                address = text
        
        # 4. URL
        url = "N/A"
        link_element = card.locator("a.hfpxzc")
        if await link_element.count() > 0:
            url = await link_element.get_attribute("href")
        
        # 5. Rating
        rating_element = container.locator(".MW4etd")
        rating = await safe_text(rating_element)
        
        # 6. Reviews
        reviews_element = container.locator(".UY7F9")
        reviews_raw = await safe_text(reviews_element)
        reviews = reviews_raw.replace("(", "").replace(")", "")
        
        # 7. Phone (usually not available in main card)
        phone = "N/A"
        
        # 8. Location (extract from address or use default)
        location = config.DEFAULT_LOCATION if hasattr(config, 'DEFAULT_LOCATION') else "Kuala Lumpur"
        if "Kuala Lumpur" in address or "KL" in address:
            location = "Kuala Lumpur"
        
        # Add to data list
        add_item(
            name=name,
            category=category,
            address=address,
            phone=phone,
            url=url,
            rating=rating,
            reviews=reviews,
            location=location
        )
        
        print(f"✓ Added: {name}")
        return True
        
    except Exception as e:
        print(f"✗ Error extracting data: {e}")
        return False


async def scrape_current_businesses(page):
    """Scrape all currently loaded business cards"""
    try:
        business_cards = page.locator("div[role='article']")
        current_count = await business_cards.count()
        
        print(f"Found {current_count} business cards, scraping...")
        
        # Get indices of already scraped cards
        already_scraped = len(data)
        
        # Only scrape new cards (from already_scraped to end)
        new_cards_scraped = 0
        for i in range(already_scraped, current_count):
            card = business_cards.nth(i)
            if await extract_and_add_business_data(card):
                new_cards_scraped += 1
            
            # Small delay to avoid detection
            if i % 5 == 0:
                await page.wait_for_timeout(random.randint(200, 500))
        
        print(f"Scraped {new_cards_scraped} new businesses")
        print(f"Total scraped: {len(data)}")
        
        return new_cards_scraped
        
    except Exception as e:
        print(f"Error scraping businesses: {e}")
        return 0  


# ------------------------
# Main Runner
# ------------------------
async def run():
    retries = 0

    while retries < config.MAX_RETRIES:
        try:
            async with async_playwright() as p:
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=config.PROFILE_DIR,
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--start-maximized",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                    viewport=None, 
                    locale="en-MY",
                    timezone_id="Asia/Kuala_Lumpur",
                )

                # Use existing tab or create one
                if context.pages:
                    page = context.pages[0]
                else:
                    page = await context.new_page()

                # --------------------------------
                # SESSION WARM-UP 
                # --------------------------------
                await page.goto(config.BASE_URL, timeout=60000)

                await page.wait_for_timeout(random.randint(8000, 12000))
                await page.mouse.move(400, 400)
                await page.wait_for_timeout(2000)
                await page.mouse.wheel(0, 200)
                await page.wait_for_timeout(random.randint(3000, 6000))

                await page.type('#searchboxinput', config.SEARCH, delay=random.uniform(50, 150))
                await page.locator("[aria-label=\"Search\"]").press("Enter")

                await page.mouse.move(
                    random.randint(100, 300),
                    random.randint(100, 300)
                )
                
                await page.wait_for_selector("div[role='article']", timeout=config.PAGE_TIMEOUT)
                await page.wait_for_timeout(random.randint(5000, 10000))

                

                # # Save the UaQhfb fontBodyMedium element HTML
                # element = page.locator(".UaQhfb.fontBodyMedium").first
                # element_html = await element.inner_html()

                # with open("UaQhfb_element.html", "w", encoding="utf-8") as f:
                #     f.write(element_html)

                # print(f"✅ Saved UaQhfb element HTML ({len(element_html)} chars)")


                while len(data) < config.TARGET:
                    # Scrape current businesses first
                    await scrape_current_businesses(page)
                    
                    # If we've reached target, break
                    if len(data) >= config.TARGET:
                        print(f"✅ Reached target of {config.TARGET} businesses")
                        break
                    
                    # Scroll to load more
                    await page.mouse.wheel(0, random.randint(300, 800))
                    
                    # Random human-like delays
                    await page.wait_for_timeout(random.randint(1000, 3000))
                    
                    # Sometimes move mouse
                    if random.random() > 0.7:  # 30% chance
                        await page.mouse.move(
                            random.randint(100, 500),
                            random.randint(100, 500)
                        )
                    
                    # Check if we're stuck (no new cards loading)
                    business_cards = page.locator("div[role='article']")
                    current_count = await business_cards.count()
                    
                    # If no new cards after 3 scrolls, break
                    if hasattr(page, '_last_card_count'):
                        if current_count == page._last_card_count:
                            page._stuck_count = getattr(page, '_stuck_count', 0) + 1
                            if page._stuck_count > 3:
                                print("No new businesses loading. Stopping.")
                                break
                        else:
                            page._stuck_count = 0
                    
                    page._last_card_count = current_count  
                
                # Save data
                df = pd.DataFrame(data)
                df.to_csv(config.CSV_OUTPUT, index=False)
                df.to_excel(config.EXCEL_OUTPUT, index=False)

                print(f"\nScraped {len(data)} records successfully")


                await page.screenshot(path=config.SCREENSHOT_ON_ERROR, full_page=True)
                break

        except Exception as e:
            retries += 1
            await asyncio.sleep(10)

            print("Fatal error:", e)
            try:
                await page.screenshot(path=config.SCREENSHOT_ON_ERROR, full_page=True)
            except:
                pass
            raise 


if __name__ == "__main__":
    asyncio.run(run())
