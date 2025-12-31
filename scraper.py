import time
import pandas as pd
import config
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import random
from datetime import datetime

data = []
seen_urls = set()  # Track seen URLs to avoid duplicates

# ------------------------
# Helpers
# ------------------------
def add_item(name, category, address, phone, url, rating, reviews, location):
    """Add item to data list if URL is not already seen"""
    # Skip if URL is already in our set (or if it's "N/A" and we've seen this name)
    if url != "N/A" and url in seen_urls:
        print(f"⚠️  Duplicate URL skipped: {name} ({url})")
        return False
    
    # Also check for duplicate names for businesses without URLs
    if url == "N/A":
        # Create a unique identifier from name + address for duplicate checking
        unique_id = f"{name}|{address}"
        if unique_id in seen_urls:  # Reusing the set for all unique identifiers
            print(f"⚠️  Duplicate business skipped: {name} ({address})")
            return False
        seen_urls.add(unique_id)
    else:
        seen_urls.add(url)
    
    data.append({
        "Business name": name,
        "Business category": category,
        "Full address": address,
        "Phone number (if available)": phone,
        "Website URL": url,
        "Star rating": rating,
        "Total number of reviews": reviews,
        "Business location": location,
        "Scraped at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return True


async def safe_text(locator, timeout=5000):
    """Safely extract text from locator with timeout and retry"""
    try:
        await locator.wait_for(state="visible", timeout=timeout)
        text = await locator.inner_text()
        return text.strip() if text else "N/A"
    except:
        return "N/A"


async def safe_attribute(locator, attribute, timeout=5000):
    """Safely get attribute from locator with timeout"""
    try:
        await locator.wait_for(state="attached", timeout=timeout)
        return await locator.get_attribute(attribute) or "N/A"
    except:
        return "N/A"


async def extract_and_add_business_data(card, attempt=1):
    """Extract data from a business card with retry logic"""
    max_attempts = 3
    
    try:
        # Wait for card to be stable
        await card.wait_for(state="visible", timeout=5000)
        
        # Get the container where most data is stored
        container = card.locator(".UaQhfb.fontBodyMedium")
        await container.wait_for(state="attached", timeout=3000)
        
        # 1. Business Name
        name_element = container.locator(".qBF1Pd.fontHeadlineSmall")
        name = await safe_text(name_element)
        
        if name == "N/A" and attempt < max_attempts:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            return await extract_and_add_business_data(card, attempt + 1)
        elif name == "N/A":
            print("Skipping card - no name found after retries")
            return False
        
        # ---- CATEGORY & ADDRESS ----
        category = "N/A"
        address = "N/A"
        
        try:
            info_blocks = container.locator(".W4Efsd span")
            block_count = await info_blocks.count()
            
            for i in range(block_count):
                text = await safe_text(info_blocks.nth(i), 2000)
                
                if not text or text in ("·",):
                    continue
                
                # CATEGORY: short, no digits, no RM, no Open/Closed
                if (category == "N/A" and len(text) < 30 and 
                    not any(x in text for x in ["RM", "Open", "Closed", "Opens", "closes"]) and
                    not any(char.isdigit() for char in text)):
                    category = text
                    continue
                
                # ADDRESS: long text with numbers or commas
                if (address == "N/A" and len(text) > 20 and 
                    (any(char.isdigit() for char in text) or ',' in text)):
                    address = text
        except:
            pass
        
        # 4. URL
        link_element = card.locator("a.hfpxzc")
        url = await safe_attribute(link_element, "href")
        
        # 5. Rating
        rating_element = container.locator(".MW4etd")
        rating = await safe_text(rating_element, 2000)
        
        # 6. Reviews
        reviews_element = container.locator(".UY7F9")
        reviews_raw = await safe_text(reviews_element, 2000)
        reviews = reviews_raw.replace("(", "").replace(")", "").strip()
        
        # 7. Phone (try to find in card)
        phone = "N/A"
        phone_elements = card.locator('button[data-item-id*="phone"]')
        if await phone_elements.count() > 0:
            phone_text = await safe_text(phone_elements.first(), 2000)
            if phone_text != "N/A":
                phone = phone_text
        
        # 8. Location
        location = config.DEFAULT_LOCATION
        if "Kuala Lumpur" in address or "KL" in address:
            location = "Kuala Lumpur"
        elif "Petaling Jaya" in address or "PJ" in address:
            location = "Petaling Jaya"
        elif "Subang" in address:
            location = "Subang"
        elif "Cheras" in address:
            location = "Cheras"
        
        # Add to data list with duplicate check
        added = add_item(
            name=name,
            category=category,
            address=address,
            phone=phone,
            url=url,
            rating=rating,
            reviews=reviews,
            location=location
        )
        
        if added:
            print(f"✓ Added: {name}")
        return added
        
    except Exception as e:
        if attempt < max_attempts:
            await asyncio.sleep(random.uniform(1, 2))
            return await extract_and_add_business_data(card, attempt + 1)
        print(f"✗ Error extracting data (attempt {attempt}): {e}")
        return False


async def scrape_current_businesses(page):
    """Scrape all currently loaded business cards"""
    try:
        # Wait for at least one business card
        await page.wait_for_selector("div[role='article']", timeout=10000)
        
        business_cards = page.locator("div[role='article']")
        current_count = await business_cards.count()
        
        if current_count == 0:
            print("No business cards found")
            return 0
        
        print(f"Found {current_count} business cards, checking for new ones...")
        
        # Get indices of already scraped cards
        already_scraped = len(data)
        
        # Only scrape new cards
        new_cards_scraped = 0
        for i in range(already_scraped, current_count):
            try:
                card = business_cards.nth(i)
                if await extract_and_add_business_data(card):
                    new_cards_scraped += 1
                
                # Random delays to appear human-like
                if i % 3 == 0:
                    delay = random.uniform(0.5, 2)
                    await page.wait_for_timeout(int(delay * 1000))
                
                # Occasionally move mouse
                if random.random() > 0.8:
                    await page.mouse.move(
                        random.randint(100, 400),
                        random.randint(100, 400)
                    )
                    
            except Exception as e:
                print(f"Error processing card {i}: {e}")
                continue
        
        # Show summary including duplicates
        total_processed = current_count - already_scraped
        duplicates = total_processed - new_cards_scraped
        if duplicates > 0:
            print(f"Processed {total_processed} cards: {new_cards_scraped} new, {duplicates} duplicates")
        else:
            print(f"Scraped {new_cards_scraped} new businesses")
        
        print(f"Unique records so far: {len(data)}")
        
        return new_cards_scraped
        
    except Exception as e:
        print(f"Error in scrape_current_businesses: {e}")
        return 0


async def save_data():
    """Save data to CSV and Excel"""
    if not data:
        print("No data to save")
        return
    
    df = pd.DataFrame(data)
    
    # Save to CSV
    try:
        df.to_csv(config.CSV_OUTPUT, index=False, encoding='utf-8-sig')
        print(f"✅ Data saved to {config.CSV_OUTPUT}")
    except Exception as e:
        print(f"Error saving CSV: {e}")
    
    # Save to Excel
    try:
        df.to_excel(config.EXCEL_OUTPUT, index=False)
        print(f"✅ Data saved to {config.EXCEL_OUTPUT}")
    except Exception as e:
        print(f"Error saving Excel: {e}")


async def wait_for_element(page, selector, timeout=30000, retries=3):
    """Wait for element with retry logic"""
    for attempt in range(retries):
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            if attempt < retries - 1:
                print(f"Element {selector} not found, retrying ({attempt + 1}/{retries})...")
                await page.wait_for_timeout(2000)
                continue
            else:
                print(f"Element {selector} not found after {retries} attempts")
                return False
    return False


async def perform_search(page):
    """Perform search with retry logic"""
    for attempt in range(3):
        try:
            print(f"Attempting search (attempt {attempt + 1}/3)...")
            
            # Clear and type search
            search_box = page.locator('#searchboxinput')
            await search_box.wait_for(state="visible", timeout=10000)
            await search_box.click()
            await search_box.fill("")
            await search_box.type(config.SEARCH, delay=random.uniform(50, 150))
            
            # Press Enter
            await page.keyboard.press("Enter")
            
            # Wait for results
            await page.wait_for_timeout(random.randint(3000, 6000))
            
            # Check if results appeared
            results = page.locator("div[role='article']")
            await results.first.wait_for(state="visible", timeout=15000)
            
            result_count = await results.count()
            if result_count > 0:
                print(f"✅ Search successful, found {result_count} results")
                return True
                
        except Exception as e:
            print(f"Search attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await page.wait_for_timeout(3000)
                continue
    
    print("❌ Search failed after 3 attempts")
    return False


async def get_scrollable_panel(page):
    """Find and return the scrollable panel containing business results"""
    # Try multiple selectors for the scrollable panel
    scrollable_selectors = [
        'div[role="feed"]',  # Primary selector for Google Maps results
        '.m6QErb[aria-label*="Results for"]',  # Another common selector
        '.m6QErb.DxyBCb',  # Alternative class
        'div[aria-label*="Results"]',  # Generic results container
    ]
    
    for selector in scrollable_selectors:
        try:
            panel = page.locator(selector).first
            if await panel.count() > 0:
                await panel.wait_for(state="visible", timeout=5000)
                print(f"✅ Found scrollable panel with selector: {selector}")
                
                # Try to get bounding box to confirm it's visible
                bbox = await panel.bounding_box()
                if bbox:
                    print(f"Panel position: x={bbox['x']}, y={bbox['y']}, width={bbox['width']}, height={bbox['height']}")
                    return panel
        except:
            continue
    
    print("⚠️ Could not find specific scrollable panel, using page scroll")
    return None


async def scroll_to_load_more(page, panel=None):
    """Scroll to load more business cards"""
    try:
        if panel:
            # Get panel position and move mouse to it
            bbox = await panel.bounding_box()
            if bbox:
                # Move mouse to the center of the panel
                center_x = bbox['x'] + bbox['width'] / 2
                center_y = bbox['y'] + bbox['height'] / 2
                await page.mouse.move(center_x, center_y)
                await page.wait_for_timeout(1000)
                
                # Scroll within the panel
                scroll_amount = random.randint(300, 800)
                await page.mouse.wheel(0, scroll_amount)
                print(f"Scrolled panel by {scroll_amount}px")
            else:
                # Fallback to page scroll
                await page.mouse.wheel(0, random.randint(300, 800))
        else:
            # Scroll the entire page
            await page.mouse.wheel(0, random.randint(300, 800))
        
        # Wait for new content to load
        await page.wait_for_timeout(random.randint(2000, 4000))
        
        # Check if we're at the bottom (end of results)
        if panel:
            try:
                scroll_height = await panel.evaluate('element => element.scrollHeight')
                scroll_top = await panel.evaluate('element => element.scrollTop')
                client_height = await panel.evaluate('element => element.clientHeight')
                
                # If we're near the bottom (within 100px)
                if scroll_height - (scroll_top + client_height) < 100:
                    print("⚠️  Near bottom of results")
                    return False
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"Error during scroll: {e}")
        return False


# ------------------------
# Main Runner
# ------------------------
async def run():
    retries = 0
    
    while retries < config.MAX_RETRIES:
        try:
            print(f"\n{'='*50}")
            print(f"Starting scraping session (Attempt {retries + 1}/{config.MAX_RETRIES})")
            print(f"Target: {config.TARGET} unique businesses")
            print(f"{'='*50}")
            
            # Clear seen URLs at start of each retry to avoid stale data
            seen_urls.clear()
            
            async with async_playwright() as p:
                # Launch browser with persistent context
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=config.PROFILE_DIR,
                    headless=False,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--start-maximized",
                        "--disable-infobars",
                        "--disable-notifications",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                    viewport=None,
                    locale="en-MY",
                    timezone_id="Asia/Kuala_Lumpur",
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                
                # Use existing tab or create one
                if context.pages:
                    page = context.pages[0]
                else:
                    page = await context.new_page()
                
                # Set default timeout
                page.set_default_timeout(config.PAGE_TIMEOUT)
                
                # --------------------------------
                # SESSION WARM-UP 
                # --------------------------------
                print("Navigating to Google Maps...")
                await page.goto(config.BASE_URL, wait_until="domcontentloaded")
                
                # Human-like interactions
                await page.wait_for_timeout(random.randint(3000, 6000))
                await page.mouse.move(400, 300)
                await page.wait_for_timeout(1000)
                await page.mouse.wheel(0, 200)
                await page.wait_for_timeout(random.randint(2000, 4000))
                
                # Perform search with retry
                if not await perform_search(page):
                    raise Exception("Search failed")
                
                # Find the scrollable panel
                scroll_panel = await get_scrollable_panel(page)
                
                # Initial scroll to load more results
                print("Performing initial scrolls to load more results...")
                for i in range(3):
                    print(f"Initial scroll {i+1}/3...")
                    await scroll_to_load_more(page, scroll_panel)
                    await page.wait_for_timeout(random.randint(1500, 3000))
                
                # Main scraping loop
                stuck_counter = 0
                max_stuck_attempts = 8
                no_new_data_counter = 0
                last_card_count = 0
                
                while len(data) < config.TARGET:
                    # Get current card count before scraping
                    business_cards = page.locator("div[role='article']")
                    current_card_count = await business_cards.count()
                    
                    # Scrape current businesses
                    new_scraped = await scrape_current_businesses(page)
                    
                    # Check if we reached target
                    if len(data) >= config.TARGET:
                        print(f"\n✅ Reached target of {config.TARGET} unique businesses!")
                        break
                    
                    # Check if we're stuck (no new cards loaded)
                    if current_card_count == last_card_count:
                        no_new_data_counter += 1
                        print(f"No new cards loaded (counter: {no_new_data_counter}/3)")
                    else:
                        no_new_data_counter = 0
                    
                    last_card_count = current_card_count
                    
                    # Check if we're stuck (no new unique businesses scraped)
                    if new_scraped == 0:
                        stuck_counter += 1
                        print(f"No new unique businesses scraped (stuck: {stuck_counter}/{max_stuck_attempts})")
                        
                        if stuck_counter >= max_stuck_attempts:
                            print("Too many attempts without new unique businesses. Stopping.")
                            break
                        
                        # Try different strategies when stuck
                        print("Trying alternative scrolling strategies...")
                        
                        # Strategy 1: Scroll more aggressively
                        if scroll_panel:
                            try:
                                # Scroll to a specific business card
                                cards = page.locator("div[role='article']")
                                if await cards.count() > 5:
                                    last_card = cards.nth(await cards.count() - 3)
                                    await last_card.scroll_into_view_if_needed()
                                    print("Scrolled to last business card")
                            except:
                                pass
                        
                        # Strategy 2: Scroll in larger increments
                        for _ in range(2):
                            await scroll_to_load_more(page, scroll_panel)
                            await page.wait_for_timeout(random.randint(2000, 4000))
                        
                        # Strategy 3: Try clicking on a business card to trigger loading
                        if random.random() > 0.5:
                            try:
                                cards = page.locator("div[role='article']")
                                if await cards.count() > 3:
                                    random_card = cards.nth(random.randint(0, await cards.count() - 1))
                                    await random_card.click()
                                    await page.wait_for_timeout(2000)
                                    
                                    # Click back on the list
                                    if scroll_panel:
                                        bbox = await scroll_panel.bounding_box()
                                        if bbox:
                                            await page.mouse.click(bbox['x'] + 50, bbox['y'] + 50)
                                            await page.wait_for_timeout(1000)
                                    print("Clicked on random business card to trigger loading")
                            except:
                                pass
                    else:
                        stuck_counter = 0  # Reset counter if we got new data
                    
                    # Regular scroll to load more content
                    print("Scrolling to load more businesses...")
                    scroll_success = await scroll_to_load_more(page, scroll_panel)
                    
                    if not scroll_success:
                        print("⚠️  May have reached end of results")
                        stuck_counter += 1
                        if stuck_counter >= 3:
                            print("End of results reached. Stopping.")
                            break
                    
                    # Random delay between actions
                    delay = random.uniform(1.5, 4)
                    await page.wait_for_timeout(int(delay * 1000))
                    
                    # Human-like mouse movement (within the panel if available)
                    if random.random() > 0.7:
                        if scroll_panel:
                            try:
                                bbox = await scroll_panel.bounding_box()
                                if bbox:
                                    await page.mouse.move(
                                        random.randint(int(bbox['x']), int(bbox['x'] + bbox['width'])),
                                        random.randint(int(bbox['y']), int(bbox['y'] + bbox['height']))
                                    )
                            except:
                                # Fallback to general area
                                await page.mouse.move(
                                    random.randint(100, 700),
                                    random.randint(100, 500)
                                )
                        else:
                            await page.mouse.move(
                                random.randint(100, 700),
                                random.randint(100, 500)
                            )
                
                # Save data
                await save_data()
                
                # Take final screenshot
                try:
                    await page.screenshot(path="final_results.png", full_page=True)
                    print("✅ Final screenshot saved")
                except:
                    pass
                
                # Close context
                await context.close()
                
                print(f"\n{'='*50}")
                print(f"Scraping completed successfully!")
                print(f"Total unique records: {len(data)}")
                print(f"Total duplicates skipped: {len(seen_urls) - len(data)}")
                print(f"Output files: {config.CSV_OUTPUT}, {config.EXCEL_OUTPUT}")
                print(f"{'='*50}")
                
                break  # Exit retry loop on success
                
        except Exception as e:
            retries += 1
            print(f"\n❌ Error occurred (Attempt {retries}/{config.MAX_RETRIES}): {str(e)}")
            
            # Save error screenshot
            try:
                await page.screenshot(path=config.SCREENSHOT_ON_ERROR, full_page=True)
                print(f"Error screenshot saved: {config.SCREENSHOT_ON_ERROR}")
            except:
                pass
            
            # Save any scraped data so far
            if data:
                await save_data()
            
            if retries < config.MAX_RETRIES:
                print(f"Retrying in 10 seconds...")
                await asyncio.sleep(10)
            else:
                print(f"Max retries reached. Exiting.")
                raise


if __name__ == "__main__":
    start_time = time.time()
    
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        if data:
            df = pd.DataFrame(data)
            df.to_csv(config.CSV_OUTPUT, index=False)
            df.to_excel(config.EXCEL_OUTPUT, index=False)
            print(f"✅ Saved {len(data)} unique records before exit")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    
    end_time = time.time()
    print(f"\n⏱️  Total execution time: {end_time - start_time:.2f} seconds")