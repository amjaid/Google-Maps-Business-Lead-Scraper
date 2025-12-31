# config.py
BASE_URL = "https://www.google.com/maps"
SEARCH = "restaurants in kuala lumpur"
DEFAULT_LOCATION = "Kuala Lumpur"

# Timeouts & Retries
PAGE_TIMEOUT = 30000
MAX_RETRIES = 3

# Profile
PROFILE_DIR = "chrome_profile_google_maps"

# Output
CSV_OUTPUT = "businesses.csv"
EXCEL_OUTPUT = "business_data.xlsx"
SCREENSHOT_ON_ERROR = "error_screenshot.png"

# Targets
TARGET = 100