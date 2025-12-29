"""
config.py
Configuration settings for the Google Maps Business Lead Scraper.
Centralizes selectors and runtime parameters to ensure maintainability.
"""

import os

# ==============================================================================
# SEARCH CONFIGURATION
# ==============================================================================
BASE_URL = "https://www.google.com/maps"

# The queries to be executed.
SEARCH_QUERIES =

# ==============================================================================
# SCRAPING LIMITS & TIMING
# ==============================================================================
# Maximum number of leads to extract per search query to prevent memory overflow
MAX_LEADS_PER_QUERY = 100 

# Number of times to scroll the results feed
MAX_SCROLL_ATTEMPTS = 50 

# Delays (in seconds) to mimic human behavior
SCROLL_PAUSE = 1.5
MIN_WAIT = 1.0

# ==============================================================================
# DOM SELECTORS (CSS / XPATH)
# ==============================================================================
SELECTORS = {
    # ------------------- Search & Navigation -------------------
    "search_box_input": "input#searchboxinput",
    "search_button": "button#searchbox-searchbutton",
    "consent_accept_button": "button[aria-label='Accept all']",  # For EU regions
    "clear_search_button": "button[aria-label='Clear search']",

    # ------------------- Results Feed -------------------
    # The scrollable container sidebar. Role='feed' is a stable accessibility attribute.
    "feed_panel": "div[role='feed']", 
    
    # The individual card item in the list.
    "result_card_link": "a[href*='/maps/place/']",

    # ------------------- Detail View (Business Data) -------------------
    # These are visible AFTER clicking a result card.
    
    # Business Name: Often an H1 with a specific class or aria-label
    "business_name": "h1.DUwDvf", 
    
    # Rating: Looks for the span containing the star count
    "rating_span": "div.F7nice span[aria-hidden='true']",
    
    # Review Count: Usually formatted as "(500)" inside a span
    "review_count_span": "div.F7nice span[aria-label*='reviews']",
    
    # Address: identified by the data-item-id 'address'
    "address_button": "button[data-item-id='address']",
    
    # Phone: identified by the data-item-id starting with 'phone:tel:'
    "phone_button": "button[data-item-id^='phone:tel:']",
    
    # Website: identified by the data-item-id 'authority'
    "website_link": "a[data-item-id='authority']",
    
    # Category: Often a button with jsaction containing 'category'
    "category_button": "button[jsaction*='category']"
}

# ==============================================================================
# OUTPUT SETTINGS
# ==============================================================================
OUTPUT_DIR = "data"
OUTPUT_FORMAT = "csv"