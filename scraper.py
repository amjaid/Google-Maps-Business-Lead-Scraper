import asyncio
import undetected_playwright as up
import time
import pandas as pd
import config

data = []

# ------------------------
# Helpers
# ------------------------
def add_item(name, category, full_address, phone_number, website_url, rating, reviews, location):
    data.append({
        "Business name" : name
        "Business category" : category
        "Full address" : full_address
        "Phone number" : phone_number
        "Website URL" : website_url
        "Star rating"
        "Total number of reviews"
        "Business location"
    })
