# config.py

# ========================
# BASIC CONFIG
# ========================
BASE_URL = "https://www.google.com/maps"
# USERNAME = "Admin"
# PASSWORD = "admin123"

HEADLESS = False
SLOW_MO = 50  # ms delay between actions (human-like)
TARGET = 1000
# ========================
# TIMEOUTS & RETRIES
# ========================
PAGE_TIMEOUT = 30000
MAX_RETRIES = 1
RETRY_DELAY = 2  # seconds

# ========================
# OUTPUT FILES
# ========================
CSV_OUTPUT = "employees.csv"
EXCEL_OUTPUT = "employee_data.xlsx"
SCREENSHOT_ON_ERROR = "error_screenshot.png"

# ========================
# SELECTORS
# ========================
USERNAME_INPUT = 'input[placeholder="Username"]'
PASSWORD_INPUT = 'input[placeholder="Password"]'
LOGIN_BUTTON = 'button[type="submit"]'
PIM_MENU = 'text="PIM"'
EMPLOYEE_CARD = 'div.oxd-table-card'
NEXT_BUTTON_ICON = 'button i.bi-chevron-right'
SEARCH = "restaurants in kuala lumpur"