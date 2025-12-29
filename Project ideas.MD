====================================================
PORTFOLIO PROJECT 1
====================================================
Project Name:
Google Maps Business Lead Scraper

----------------------------------------------------
Client Problem:
----------------------------------------------------
The client needs a scalable way to collect local business leads from Google Maps
for marketing, sales outreach, and market research. Manual searching is slow,
error-prone, and not scalable across multiple locations or business categories.

----------------------------------------------------
Target Website:
----------------------------------------------------
https://www.google.com/maps

----------------------------------------------------
What Data Is Scraped From Google Maps:
----------------------------------------------------
- Business name
- Business category
- Full address
- Phone number (if available)
- Website URL
- Star rating
- Total number of reviews
- Business location (city / area)

----------------------------------------------------
Core Requirements:
----------------------------------------------------
- Python-based browser automation
- Handle JavaScript-rendered content
- Infinite scrolling and lazy loading
- Location and category-based searches
- Structured output (CSV / JSON)
- Stable and maintainable scraping logic

----------------------------------------------------
Project Steps and Libraries Used:
----------------------------------------------------

Step 1: Launch Stealth Browser Session
Library:
- playwright
- playwright-stealth / undetected-playwright

Explanation:
Google Maps relies heavily on JavaScript and detects basic automation.
A stealth Playwright browser helps load pages consistently.

----------------------------------------------------

Step 2: Navigate to Maps and Perform Search
Library:
- playwright (page.goto, page.fill, page.keyboard)

Explanation:
Simulates real user behavior by entering location and business keywords.

----------------------------------------------------

Step 3: Handle Infinite Scroll Results Panel
Library:
- playwright (mouse.wheel, page.evaluate)

Explanation:
Scrolls the results panel until all businesses are loaded.

----------------------------------------------------

Step 4: Extract Business Details
Library:
- playwright (locator, inner_text)

Explanation:
Reads structured business information from the DOM.

----------------------------------------------------

Step 5: Data Cleaning and Deduplication
Library:
- pandas

Explanation:
Removes duplicates and normalizes data fields.

----------------------------------------------------

Step 6: Export Data
Library:
- pandas

Explanation:
Exports final data to CSV or JSON format.

====================================================
END PROJECT 1
====================================================



====================================================
PORTFOLIO PROJECT 2
====================================================
Project Name:
Amazon Product & Review Data Scraper

----------------------------------------------------
Client Problem:
----------------------------------------------------
The client needs up-to-date product and customer review data from Amazon
for pricing analysis, competitor research, and product intelligence.

----------------------------------------------------
Target Website:
----------------------------------------------------
https://www.amazon.com
(amazon.in / amazon.sg can also be used)

----------------------------------------------------
What Data Is Scraped From Amazon:
----------------------------------------------------
From Product Pages:
- Product title
- Brand name
- Price
- Availability / stock status
- Star rating
- Total number of reviews
- Product description

From Review Pages:
- Reviewer name
- Review title
- Review text
- Review rating
- Review date

----------------------------------------------------
Core Requirements:
----------------------------------------------------
- JavaScript-rendered page handling
- Product and review page support
- Session and cookie reuse
- Error handling and retries
- Structured output (CSV / Excel)

----------------------------------------------------
Project Steps and Libraries Used:
----------------------------------------------------

Step 1: Start Browser with Persistent Context
Library:
- playwright

Explanation:
Stores cookies and session data to improve navigation stability.

----------------------------------------------------

Step 2: Load Search or Product Pages
Library:
- playwright (page.goto)

Explanation:
Loads Amazon pages that rely on dynamic rendering.

----------------------------------------------------

Step 3: Wait for Key Elements
Library:
- playwright (page.wait_for_selector)

Explanation:
Ensures content is fully loaded before extraction.

----------------------------------------------------

Step 4: Extract Product Data
Library:
- playwright (locator, inner_text)

Explanation:
Extracts product-level information such as price and rating.

----------------------------------------------------

Step 5: Navigate and Extract Reviews
Library:
- playwright

Explanation:
Handles review pagination and extracts customer feedback.

----------------------------------------------------

Step 6: Error Handling and Retries
Library:
- Python standard library (try/except, logging)

Explanation:
Prevents script crashes due to temporary failures.

----------------------------------------------------

Step 7: Data Structuring and Export
Library:
- pandas

Explanation:
Outputs data to CSV or Excel format.

====================================================
END PROJECT 2
====================================================



====================================================
PORTFOLIO PROJECT 3
====================================================
Project Name:
Cloudflare-Protected SaaS Review Site Scraper

----------------------------------------------------
Client Problem:
----------------------------------------------------
The client wants to collect public company and product review data from
SaaS comparison platforms for market research and competitive analysis.
These sites use JavaScript rendering and traffic protection.

----------------------------------------------------
Target Website (Choose One):
----------------------------------------------------
https://www.g2.com
https://www.capterra.com
https://www.trustpilot.com

----------------------------------------------------
What Data Is Scraped From These Sites:
----------------------------------------------------
From Listing Pages:
- Product or company name
- Category
- Overall rating
- Total number of reviews

From Review Pages:
- Individual review rating
- Review title or summary
- Review text
- Review date

----------------------------------------------------
Core Requirements:
----------------------------------------------------
- Handle bot-protected websites
- JavaScript-heavy rendering
- Pagination or infinite loading
- Asynchronous scraping
- Clean structured output

----------------------------------------------------
Project Steps and Libraries Used:
----------------------------------------------------

Step 1: Launch Stealth Browser
Library:
- playwright
- undetected-playwright / playwright-stealth

Explanation:
Loads protected pages using a real browser environment.

----------------------------------------------------

Step 2: Ensure Full Page Render
Library:
- playwright (page.wait_for_load_state)

Explanation:
Waits for JavaScript execution to complete.

----------------------------------------------------

Step 3: Navigate Listings
Library:
- playwright

Explanation:
Accesses category or company listing pages.

----------------------------------------------------

Step 4: Handle Pagination or Infinite Load
Library:
- playwright

Explanation:
Iterates through multiple pages or dynamically loaded content.

----------------------------------------------------

Step 5: Extract Review and Company Data
Library:
- playwright

Explanation:
Extracts ratings, reviews, and company details.

----------------------------------------------------

Step 6: Asynchronous Task Management
Library:
- asyncio

Explanation:
Runs multiple page tasks concurrently with controlled load.

----------------------------------------------------

Step 7: Normalize and Export Data
Library:
- pandas

Explanation:
Cleans and exports data into CSV or JSON.

====================================================
END PROJECT 3
====================================================
