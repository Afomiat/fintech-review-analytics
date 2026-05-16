# Fintech Review Analytics

> A data engineering pipeline that transforms raw Google Play Store reviews from Ethiopian bank mobile apps into actionable business insights for product teams.

Built as part of a consulting engagement at **Omega Consultancy**, advising Ethiopian banks on how to improve their mobile products and retain customers in an increasingly competitive fintech landscape.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Banks Analyzed](#banks-analyzed)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Task 1: Data Collection & Preprocessing](#task-1-data-collection--preprocessing)
- [Data Quality Report](#data-quality-report)
- [Limitations](#limitations)
- [CI/CD Pipeline](#cicd-pipeline)
- [Contributing](#contributing)

---

## Project Overview

Mobile banking adoption in Ethiopia is accelerating. Customer reviews on the Google Play Store are one of the richest, most unfiltered signals of product quality available to product teams. This pipeline:

1. **Scrapes** raw reviews from the Google Play Store
2. **Cleans and validates** the data into an analysis-ready dataset
3. **Analyzes** sentiment and extracts recurring themes using NLP
4. **Stores** processed data in a PostgreSQL database
5. **Visualizes** findings into bank-specific product recommendations

---

## Banks Analyzed

| Bank | App Name | Google Play ID | Play Store Rating |
|------|----------|---------------|-------------------|
| Commercial Bank of Ethiopia | CBE Mobile Banking | `com.combanketh.mobilebanking` | 4.2 |
| Bank of Abyssinia | BOA Mobile Banking | `com.boa.boaMobileBanking` | 3.4 |
| Dashen Bank | Amole | `com.cr2.amolelight` | 4.1 |

---

## Project Structure

```
fintech-review-analytics/
│
├── .github/
│   └── workflows/
│       └── unittests.yml        # CI/CD pipeline — runs on every push to main
│
├── data/
│   └── raw/                     # Local data files — never committed to GitHub
│       ├── reviews_raw.csv      # Output of scrape_reviews.py
│       └── reviews_clean.csv    # Output of preprocess_reviews.py
│
├── notebooks/
│   ├── __init__.py
│   └── explore_scraper.py       # Exploration script to inspect raw scraper output
│
├── scripts/
│   ├── __init__.py
│   ├── scrape_reviews.py        # Scrapes reviews from Google Play Store
│   ├── preprocess_reviews.py    # Cleans, deduplicates, and normalizes raw data
│   └── validate_data.py         # Validates cleaned data against project KPIs
│
├── src/
│   └── __init__.py              # Reusable modules (populated in later tasks)
│
├── tests/
│   └── __init__.py              # Unit tests (populated in later tasks)
│
├── .gitignore                   # Excludes data files, venv, and cache
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Setup & Installation

### Prerequisites

- Python 3.11.2
- Git
- A terminal (Git Bash on Windows, Terminal on Mac/Linux)

### 1. Clone the Repository

```bash
git clone https://github.com/Afomiat/fintech-review-analytics.git
cd fintech-review-analytics
```

### 2. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate — Windows (Git Bash)
source venv/Scripts/activate

# Activate — Mac/Linux
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Task 1: Data Collection & Preprocessing

### Pipeline Overview

```
Google Play Store
      ↓
scrape_reviews.py       → data/raw/reviews_raw.csv    (raw, unprocessed)
      ↓
preprocess_reviews.py   → data/raw/reviews_clean.csv  (clean, normalized)
      ↓
validate_data.py        → ALL CHECKS PASSED ✓
```

### Running the Pipeline

Run each script in order from the project root:

```bash
# Step 1: Scrape reviews from Google Play Store
python scripts/scrape_reviews.py

# Step 2: Clean and normalize the raw data
python scripts/preprocess_reviews.py

# Step 3: Validate the cleaned data meets all KPIs
python scripts/validate_data.py
```

### What Each Script Does

**`scrape_reviews.py`**
- Connects to the Google Play Store using `google-play-scraper`
- Requests 600 reviews per bank (to account for duplicates removed in preprocessing)
- Collects: review text, star rating, date, bank name, source
- Saves raw output to `data/raw/reviews_raw.csv`

**`preprocess_reviews.py`**
- Loads the raw CSV
- Reports missing values before and after cleaning
- Removes duplicate reviews (same text from the same bank)
- Drops rows missing review text or rating (unusable for analysis)
- Normalizes dates to `YYYY-MM-DD` string format
- Keeps only the five required columns: `review, rating, date, bank, source`
- Saves cleaned output to `data/raw/reviews_clean.csv`

**`validate_data.py`**
- Checks total reviews >= 1,200
- Checks each bank has >= 400 reviews
- Checks all required columns are present
- Checks missing data is < 5%
- Checks date format is `YYYY-MM-DD`
- Checks all ratings are between 1 and 5
- Checks source column is always `'Google Play'`

### Scraping Methodology

| Parameter | Value |
|-----------|-------|
| Library | `google-play-scraper` |
| Country | Ethiopia (`et`) |
| Language | English (`en`) |
| Sort order | Newest first |
| Requested per bank | 600 |
| Date range collected | November 2024 – May 2026 |

---

## Data Quality Report

Results after running the full pipeline:

| Metric | Value |
|--------|-------|
| Total reviews collected | 1,450 |
| Reviews — Commercial Bank of Ethiopia | 456 |
| Reviews — Bank of Abyssinia | 498 |
| Reviews — Dashen Bank | 496 |
| Duplicates removed | 350 |
| Rows dropped (missing values) | 0 |
| Missing values in final dataset | 0 (0.00%) |
| Date range | Nov 2024 – May 2026 |

### Rating Distribution

| Stars | Count | Percentage |
|-------|-------|------------|
| ⭐ 1 star | 373 | 26% |
| ⭐⭐ 2 stars | 59 | 4% |
| ⭐⭐⭐ 3 stars | 88 | 6% |
| ⭐⭐⭐⭐ 4 stars | 104 | 7% |
| ⭐⭐⭐⭐⭐ 5 stars | 826 | 57% |

> **Note:** The strong skew toward 1-star and 5-star ratings reflects a known bias in user-generated review data. Users are most likely to leave a review after an extremely positive or extremely negative experience. Middle ratings (2–4 stars) are underrepresented. This will be accounted for in the sentiment analysis in Task 2.

---

## Limitations

### 1. Duplicate Reviews from Scraper
The `google-play-scraper` library returns duplicate reviews when requesting large counts — it loops back to previously seen reviews to fill the requested number. To compensate, we request 600 reviews per bank and rely on deduplication in preprocessing to produce a clean dataset above the 400-per-bank minimum.

### 2. English Reviews Only
The scraper is configured with `lang='en'`. Reviews written in Amharic or other languages are excluded from this dataset. Given that Ethiopia is a multilingual country, this represents a meaningful gap in coverage that could bias findings toward English-speaking users.

### 3. Rate Limiting
Sending too many requests to Google Play in a short time can trigger rate limiting, which silently reduces the number of reviews returned. A 2-second delay between bank requests is included in the scraper to mitigate this. On repeated runs, counts may vary slightly.

### 4. Review Availability
The number of available English-language reviews on Google Play is finite. Some banks may have fewer reviews than others simply due to their user base size or app age — not necessarily due to product quality differences.

---

## CI/CD Pipeline

Every push to `main` and every Pull Request targeting `main` triggers an automated pipeline via GitHub Actions that:

1. Spins up a fresh Ubuntu virtual machine
2. Installs Python 3.10
3. Runs `pip install -r requirements.txt`
4. Verifies key packages import correctly

This ensures the project is reproducible on any machine, not just the developer's local environment.

Pipeline configuration: `.github/workflows/unittests.yml`

---

## Contributing

This project follows [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | Adding new functionality |
| `fix:` | Fixing a bug |
| `docs:` | Updating documentation |
| `refactor:` | Restructuring code without changing behavior |
| `chore:` | Setup tasks, config changes |
| `test:` | Adding or updating tests |

Branch strategy:
- `main` — always clean, working code
- `task-1`, `task-2`, etc. — one branch per task, merged via Pull Request

---

*Built by [Afomiat](https://github.com/Afomiat) · Omega Consultancy Data Engineering Challenge · May 2026*
