import time
import pandas as pd
from playwright.async_api import async_playwright, expect, TimeoutError
import config
import asyncio

data = []

# ------------------------
# Helpers
# ------------------------
def add_item(id, first_name, last_name, job_title, employment_type, department):
    data.append({
        "ID": id,
        "First Name": first_name,
        "Last Name": last_name,
        "Job Title": job_title,
        "Employment Type": employment_type,
        "Department": department
    })


def safe_text(locator):
    try:
        return locator.inner_text().strip()
    except:
        return "N/A"


# ------------------------
# Scraping Logic
# ------------------------
def scrape_current_page(page):
    cards = page.locator(config.EMPLOYEE_CARD)
    expect(cards.first).to_be_visible()

    cards = page.locator(config.EMPLOYEE_CARD)
    count = cards.count()
    print(f"Found {count} employee cards")

    for i in range(count):
        card = cards.nth(i)

        add_item(
            safe_text(card.locator('div:nth-child(2) div')),
            safe_text(card.locator('div:nth-child(3) div')),
            safe_text(card.locator('div:nth-child(4) div')),
            safe_text(card.locator('div:nth-child(5) div')),
            safe_text(card.locator('div:nth-child(6) div')),
            safe_text(card.locator('div:nth-child(7) div')),
        )


def click_next_page(page):
    next_icon = page.locator(config.NEXT_BUTTON_ICON)

    if next_icon.count() == 0:
        return False

    button = next_icon.locator("..")

    disabled = (
        button.get_attribute("disabled") is not None or
        "disabled" in (button.get_attribute("class") or "")
    )

    if disabled:
        return False

    button.click()
    page.wait_for_load_state("networkidle")
    time.sleep(1)
    return True


# ------------------------
# Main Runner
# ------------------------
def run():
    retries = 0

    while retries < config.MAX_RETRIES:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=config.HEADLESS,
                    slow_mo=config.SLOW_MO
                )

                page = browser.new_page()
                page.set_default_timeout(config.PAGE_TIMEOUT)

                # Go to site
                page.goto(config.BASE_URL)

                # Login
                expect(page.locator(config.USERNAME_INPUT)).to_be_visible()
                page.fill(config.USERNAME_INPUT, config.USERNAME)
                page.fill(config.PASSWORD_INPUT, config.PASSWORD)
                page.click(config.LOGIN_BUTTON)

                # Navigate to PIM
                expect(page.locator(config.PIM_MENU)).to_be_visible()
                page.click(config.PIM_MENU)

                # Pagination loop
                page_num = 1
                while True:
                    print(f"\nScraping page {page_num}")
                    scrape_current_page(page)

                    if not click_next_page(page):
                        break

                    page_num += 1

                # Save data
                df = pd.DataFrame(data)
                df.to_csv(config.CSV_OUTPUT, index=False)
                df.to_excel(config.EXCEL_OUTPUT, index=False)

                print(f"\nScraped {len(data)} records successfully")
                browser.close()
                return

        except TimeoutError as e:
            retries += 1
            print(f"[Retry {retries}] Timeout error: {e}")
            time.sleep(config.RETRY_DELAY)

        except Exception as e:
            print("Fatal error:", e)
            try:
                page.screenshot(path=config.SCREENSHOT_ON_ERROR, full_page=True)
            except:
                pass
            raise


if __name__ == "__main__":
    run()