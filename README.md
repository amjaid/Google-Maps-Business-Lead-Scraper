# 📍 Google Maps Business Scraper  
### Python • Playwright • Async Automation

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-Async-green.svg)
![Status](https://img.shields.io/badge/Status-Stable-success.svg)
![Scraping](https://img.shields.io/badge/Use%20Case-Lead%20Generation-orange.svg)
![License](https://img.shields.io/badge/License-Educational-lightgrey.svg)

A **production-ready Google Maps scraper** built with **Python + Playwright (async)** to extract **clean, unique, and structured business data** from Google Maps.

Designed specifically for **JavaScript-heavy pages**, infinite scrolling, and real-world scraping challenges.

---

## ✨ Key Highlights

✅ Handles infinite scroll & lazy loading  
✅ Extracts **unique** business listings  
✅ Human-like behavior to reduce detection  
✅ Retry-safe & fault-tolerant  
✅ CSV & Excel export  
✅ Persistent browser sessions  
✅ Suitable for **lead generation & market research**

## 🧱 Architecture Diagram

```text
┌──────────────┐
│  config.py   │  ← Search query, limits, paths
└──────┬───────┘
       │
       ▼
┌──────────────────────────┐
│   Playwright Browser     │
│  (Persistent Context)   │
└─────────┬────────────────┘
          │
          ▼
┌──────────────────────────┐
│ Google Maps Search Page  │
│ - Infinite Scroll Panel │
│ - Business Cards        │
└─────────┬────────────────┘
          │
          ▼
┌──────────────────────────┐
│ Data Extraction Engine   │
│ - Retry Logic            │
│ - Safe Selectors         │
│ - Duplicate Filtering   │
└─────────┬────────────────┘
          │
          ▼
┌──────────────────────────┐
│ pandas DataFrame         │
│ CSV / Excel Export       │
└──────────────────────────┘
```

🚀 How It Works

1. Launches Chromium with a persistent profile

2. Opens Google Maps

3. Types the search query naturally

4. Scrolls results gradually

5. Extracts data from each business card:

    -> Uses text-based heuristics (not brittle selectors)

    -> Separates category and address reliably

6. Stops when:

    -> Target count is reached

    -> No new businesses load

7. Saves results to CSV and Excel

▶️ How to Run
1️⃣ Install dependencies

```bash
pip install playwright pandas
playwright install chromium
```

2️⃣ Run the scraper

```bash
python scraper.py
```

🧠 Extraction Logic (Important)

Category and address are extracted using semantic rules, not fixed DOM positions:

-> Category

-> Short text

-> No digits

-> No RM / Open / Closed keywords

-> Address

-> Long text

-> Contains digits (street numbers, building info)

This makes the scraper resilient to Google Maps UI changes.


⚠️ Important Notes

This scraper is not headless by default (intentional)

Excessive speed may trigger:

-> CAPTCHA

-> Temporary IP throttling


⚠️ Recommended limits:

-> 300–1000 records/day per IP

-> Avoid running multiple instances simultaneously

🔒 Session Persistence

The script uses:

```python
launch_persistent_context(user_data_dir=PROFILE_DIR)
```

This means:

-> Cookies are saved

-> Login/session state is reused

-> Lower chance of repeated bot detection


❗ Legal & Ethical Disclaimer

This project is for educational and research purposes only.

Scraping Google Maps may violate:

Google Terms of Service

Local data protection laws

Use responsibly and at your own risk.


📈 Possible Improvements

Click into business detail pages to extract phone numbers

Deduplicate by business name + address

Add proxy / IP rotation support

Resume scraping from last saved record

Multi-location scraping


🧑‍💻 Author Notes

This scraper is optimized for:

-> Freelance data collection tasks

-> Proof-of-concept scraping

-> Controlled data extraction jobs



👤 Author Abdullah Mohammad Jaid

🌐 Website
```bash
amjaid.com
```

🐙 GitHub
```bash
github.com/amjaid
```