import time
import pandas as pd
import config
import asyncio
from playwright.async_api import async_playwright, expect
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


def safe_text(locator):
    try:
        return locator.inner_text().strip()
    except:
        return "N/A"
    

# # ------------------------
# # Scraping Logic
# # ------------------------
# def scrape_current_page(page):
#     cards = page.locator(config.EMPLOYEE_CARD)
#     expect(cards.first).to_be_visible()

#     cards = page.locator(config.EMPLOYEE_CARD)
#     count = cards.count()
#     print(f"Found {count} employee cards")

#     for i in range(count):
#         card = cards.nth(i)

#         add_item(
#             safe_text(card.locator('div:nth-child(2) div')),
#             safe_text(card.locator('div:nth-child(3) div')),
#             safe_text(card.locator('div:nth-child(4) div')),
#             safe_text(card.locator('div:nth-child(5) div')),
#             safe_text(card.locator('div:nth-child(6) div')),
#             safe_text(card.locator('div:nth-child(7) div')),
#         )


# def click_next_page(page):
#     next_icon = page.locator(config.NEXT_BUTTON_ICON)

#     if next_icon.count() == 0:
#         return False

#     button = next_icon.locator("..")

#     disabled = (
#         button.get_attribute("disabled") is not None or
#         "disabled" in (button.get_attribute("class") or "")
#     )

#     if disabled:
#         return False

#     button.click()
#     page.wait_for_load_state("networkidle")
#     time.sleep(1)
#     return True


# ------------------------
# Main Runner
# ------------------------
async def run():
    retries = 0

    while retries < config.MAX_RETRIES:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=False, # Headful is less detectable
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-infobars',
                        '--window-size=1920,1080', # Set a common resolution
                        '--enable-webgl', # Enable graphics for fingerprinting
                    ]
                )

                # 2. Realistic Browser Context Configuration
                context = await browser.new_context(
                    # Use a modern, realistic user agent
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='America/New_York',
                )

                page = await context.new_page()
                if page is None:
                    raise Exception("Failed to create new page - context.new_page() returned None")
                # page.set_default_timeout(3000)

                # Go to site
                await page.goto(config.BASE_URL)
                
                # Add random delays to mimic reading/thinking
                await page.wait_for_timeout(random.randint(2000, 5000))
                
                # Simulate human-like mouse movement
                await page.mouse.move(
                    random.randint(100, 300),
                    random.randint(100, 300)
                )

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


                while(len(data) < config.TARGET):
                    await page.mouse.move(
                        random.randint(100, 300),
                        random.randint(100, 300)
                    )
                    locator = page.get_by_role('article')
                    await page.mouse.wheel(0, 500)
                    await page.wait_for_timeout(random.randint(5000, 10000))


                await page.screenshot(path=config.SCREENSHOT_ON_ERROR, full_page=True)
                break

        except Exception as e:
            print("Fatal error:", e)
            try:
                await page.screenshot(path=config.SCREENSHOT_ON_ERROR, full_page=True)
            except:
                pass
            raise 
                


#                 # Pagination loop
#                 page_num = 1
#                 while True:
#                     print(f"\nScraping page {page_num}")
#                     scrape_current_page(page)

#                     if not click_next_page(page):
#                         break

#                     page_num += 1

#                 # Save data
#                 df = pd.DataFrame(data)
#                 df.to_csv(config.CSV_OUTPUT, index=False)
#                 df.to_excel(config.EXCEL_OUTPUT, index=False)

#                 print(f"\nScraped {len(data)} records successfully")
#                 browser.close()
#                 return

#         except TimeoutError as e:
#             retries += 1
#             print(f"[Retry {retries}] Timeout error: {e}")
#             time.sleep(config.RETRY_DELAY)

#         except Exception as e:
#             print("Fatal error:", e)
#             try:
#                 page.screenshot(path=config.SCREENSHOT_ON_ERROR, full_page=True)
#             except:
#                 pass
#             raise

# 
if __name__ == "__main__":
    asyncio.run(run())
