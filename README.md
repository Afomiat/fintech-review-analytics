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
- [Task 2: Sentiment & Thematic Analysis](#task-2-sentiment--thematic-analysis)
- [Task 3: Database Engineering](#task-3-database-engineering)
- [Task 4: Insights & Recommendations](#task-4-insights--recommendations)
- [Data Quality Report](#data-quality-report)
- [Key Findings](#key-findings)
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
fintech-review-analytics/
│
├── .github/
│   └── workflows/
│       └── unittests.yml              # CI/CD pipeline — runs on every push to main
│
├── data/
│   ├── raw/                           # Local only — never committed to GitHub
│   │   ├── reviews_raw.csv            # Output of scrape_reviews.py
│   │   └── reviews_clean.csv          # Output of preprocess_reviews.py
│   ├── processed/                     # Local only — never committed to GitHub
│   │   ├── reviews_with_sentiment.csv # Output of sentiment_analysis.py
│   │   └── reviews_analyzed.csv       # Output of thematic_analysis.py
│   └── plots/                         # Committed — visualization outputs
│       ├── rating_distribution.png
│       ├── sentiment_by_bank.png
│       ├── themes_by_bank.png
│       ├── sentiment_over_time.png
│       └── top_keywords.png
│
├── notebooks/
│   ├── init.py
│   ├── explore_scraper.py             # Inspects raw scraper output
│   ├── explore_sentiment.py           # Tests VADER on sample reviews
│   ├── explore_tfidf.py               # Explores TF-IDF keywords per bank
│   ├── theme_grouping_logic.ipynb     # Documents theme keyword grouping logic
│   ├── sentiment_analysis_report.ipynb # Interim report notebook
│   └── final_report.ipynb             # Final report with all visualizations
│
├── scripts/
│   ├── init.py
│   ├── scrape_reviews.py              # Scrapes reviews from Google Play Store
│   ├── preprocess_reviews.py          # Cleans, deduplicates, normalizes raw data
│   ├── validate_data.py               # Validates cleaned data against KPIs
│   ├── sentiment_analysis.py          # DistilBERT + VADER sentiment pipeline
│   ├── thematic_analysis.py           # TF-IDF keyword extraction + theme assignment
│   ├── schema.sql                     # PostgreSQL database schema
│   └── insert_data.py                 # Inserts review data into PostgreSQL
│
├── src/
│   └── init.py
│
├── tests/
│   └── init.py
│
├── .gitignore
├── requirements.txt
└── README.md

---

## Setup & Installation

### Prerequisites

- Python 3.11.2
- Git
- PostgreSQL 17+
- A terminal (Git Bash on Windows, Terminal on Mac/Linux)

### 1. Clone the Repository

```bash
git clone https://github.com/Afomiat/fintech-review-analytics.git
cd fintech-review-analytics
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `torch` (~123MB) and the DistilBERT model (~268MB) download on first run. Subsequent runs use local cache.

---

## Task 1: Data Collection & Preprocessing

### Pipeline Overview
Google Play Store
↓
scrape_reviews.py       → data/raw/reviews_raw.csv
↓
preprocess_reviews.py   → data/raw/reviews_clean.csv
↓
validate_data.py        → ALL CHECKS PASSED ✓

### Running the Pipeline

```bash
python scripts/scrape_reviews.py
python scripts/preprocess_reviews.py
python scripts/validate_data.py
```

### What Each Script Does

**`scrape_reviews.py`**
- Connects to Google Play Store using `google-play-scraper`
- Requests 600 reviews per bank (accounts for duplicates removed in preprocessing)
- Collects: review text, star rating, date, bank name, source
- Saves raw output to `data/raw/reviews_raw.csv`

**`preprocess_reviews.py`**
- Removes duplicate reviews (same text from same bank)
- Drops rows missing review text or rating
- Normalizes dates to `YYYY-MM-DD`
- Keeps required columns: `review, rating, date, bank, source`
- Saves to `data/raw/reviews_clean.csv`

**`validate_data.py`**
- Checks total reviews >= 1,200
- Checks each bank >= 400 reviews
- Checks all required columns present
- Checks missing data < 5%
- Checks date format is `YYYY-MM-DD`
- Checks ratings between 1 and 5
- Checks source is always `'Google Play'`

### Scraping Methodology

| Parameter | Value |
|-----------|-------|
| Library | `google-play-scraper` |
| Country | Ethiopia (`et`) |
| Language | English (`en`) |
| Sort order | Newest first |
| Requested per bank | 600 |
| Date range | November 2024 – May 2026 |

---

## Task 2: Sentiment & Thematic Analysis

### Pipeline Overview
data/raw/reviews_clean.csv
↓
sentiment_analysis.py   → data/processed/reviews_with_sentiment.csv
↓
thematic_analysis.py    → data/processed/reviews_analyzed.csv

### Running the Pipeline

```bash
python scripts/sentiment_analysis.py
python scripts/thematic_analysis.py
```

### What Each Script Does

**`sentiment_analysis.py`**
- Runs DistilBERT as primary sentiment tool
- Runs VADER as secondary tool for comparison
- Assigns `sentiment_label` and `sentiment_score` to every review
- Reports breakdown per bank and per star rating
- Saves to `data/processed/reviews_with_sentiment.csv`

**`thematic_analysis.py`**
- Extracts TF-IDF keywords per bank
- Assigns each review to one of 6 themes
- Reports theme distribution and sentiment within each theme
- Saves to `data/processed/reviews_analyzed.csv`

### Sentiment Tool Selection Rationale

| Tool | Type | Strengths | Weaknesses |
|------|------|-----------|------------|
| DistilBERT | Transformer | Context-aware, handles negation, state-of-the-art | Requires torch, slower |
| VADER | Lexicon | Fast, interpretable | Misses context, struggles with broken grammar |

**DistilBERT selected as primary.** Key examples where VADER failed:

| Review | DistilBERT | VADER |
|--------|-----------|-------|
| "It's not allowing me to transfer money" | NEGATIVE (99.7%) | NEUTRAL |
| "IT'S NOT WORK ON HUAWEI DEVICES" | NEGATIVE (99.97%) | NEUTRAL |

Agreement rate: **59.5%** — disagreements consistently showed DistilBERT correct.

### Theme Taxonomy

| Theme | Sample Keywords | Business Relevance |
|-------|----------------|-------------------|
| Transaction Performance | transfer, payment, slow, speed | Core banking function |
| App Stability | crash, not working, fix, update | Retention risk |
| Account Access | login, OTP, password, fingerprint | Security & access |
| User Experience | easy, nice, interface, smooth | Product quality |
| Customer Service | support, help, response, agent | Support quality |
| Feature Requests | add, need, want, suggest | Product roadmap |

### Sentiment Coverage

| Metric | Value |
|--------|-------|
| Reviews analyzed | 1,450 / 1,450 |
| Coverage | 100% |
| KPI requirement | 90% minimum |
| Status | ✓ Passed |

---

## Task 3: Database Engineering

### Pipeline Overview
data/processed/reviews_analyzed.csv
↓
insert_data.py   → PostgreSQL bank_reviews database
↓
verification queries → ALL CHECKS PASSED ✓

### Database Setup

```bash
# Create the database
psql -U postgres -c "CREATE DATABASE bank_reviews;"

# Create tables
psql -U postgres -d bank_reviews -f scripts/schema.sql

# Insert data
python scripts/insert_data.py
```

### Schema Design

**banks table**

| Column | Type | Constraint |
|--------|------|------------|
| bank_id | SERIAL | PRIMARY KEY |
| bank_name | VARCHAR(100) | NOT NULL |
| app_name | VARCHAR(100) | NOT NULL |

**reviews table**

| Column | Type | Constraint |
|--------|------|------------|
| review_id | INTEGER | PRIMARY KEY |
| bank_id | INTEGER | FOREIGN KEY → banks |
| review_text | TEXT | |
| rating | INTEGER | CHECK 1–5 |
| review_date | DATE | |
| sentiment_label | VARCHAR(20) | |
| sentiment_score | FLOAT | |
| vader_label | VARCHAR(20) | |
| vader_score | FLOAT | |
| identified_theme | VARCHAR(50) | |
| source | VARCHAR(50) | |

### Verification Results

| Query | Result |
|-------|--------|
| Total reviews | 1,450 |
| CBE reviews | 456 |
| BOA reviews | 498 |
| Dashen reviews | 496 |
| Avg rating — CBE | 3.93★ |
| Avg rating — BOA | 3.29★ |
| Avg rating — Dashen | 3.78★ |
| Null values (all key columns) | 0 |
| KPI (1,000+ entries) | ✓ Passed |

---

## Task 4: Insights & Recommendations

### Running the Analysis

```bash
# Open final report notebook
notebooks/final_report.ipynb
```

### Visualizations Produced

| Plot | File |
|------|------|
| Rating distribution per bank | `data/plots/rating_distribution.png` |
| Sentiment distribution by bank | `data/plots/sentiment_by_bank.png` |
| Theme distribution by bank | `data/plots/themes_by_bank.png` |
| Sentiment trend over time | `data/plots/sentiment_over_time.png` |
| Top keywords per bank | `data/plots/top_keywords.png` |

### Satisfaction Drivers

| Bank | Driver 1 | Driver 2 |
|------|----------|----------|
| CBE | User Experience (94% positive) | Customer Service (56% positive) |
| BOA | User Experience (91% positive) | Transaction speed when working |
| Dashen | User Experience (88% positive) | Transaction speed (fast keyword dominant) |

### Pain Points

| Bank | Pain Point 1 | Pain Point 2 |
|------|-------------|-------------|
| CBE | App Stability (75% negative) | Transaction Performance (60% negative) |
| BOA | App Stability (91% negative) | Feature Requests (92% negative) |
| Dashen | App Stability (90% negative) | Account Access (64% negative) |

### Bank-Specific Recommendations

**Commercial Bank of Ethiopia**
- Fix app stability after updates — top negative keyword is "update"
- Reduce transfer failure rate — 60% of Transaction Performance reviews negative
- Leverage customer service strength (94% positive) as competitive differentiator
- Improve OTP delivery reliability — 73% negative Account Access

**Bank of Abyssinia**
- Emergency app stability program — 91% negative is crisis level
- Add missing features — fingerprint login, notifications, budget tracking
- Rebuild customer service — only 17% positive, lowest of all three banks
- Fix transaction performance — slow transfers driving 1-star reviews

**Dashen Bank**
- Fix login and OTP reliability — 64% negative Account Access
- Address app stability — strong UX undermined by crashes
- Build on Super App strengths — users love the concept
- Improve transaction loading speed — 61% negative Transaction Performance

---

## Data Quality Report

| Metric | Value |
|--------|-------|
| Total reviews collected | 1,450 |
| Reviews — CBE | 456 |
| Reviews — BOA | 498 |
| Reviews — Dashen | 496 |
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

> The strong skew toward 1-star and 5-star ratings reflects negativity/positivity bias. Middle ratings are underrepresented.

---

## Key Findings

### Sentiment by Bank

| Bank | Positive | Negative | Neutral | Avg Confidence |
|------|----------|----------|---------|----------------|
| CBE | 57.0% | 41.4% | 1.5% | 0.968 |
| BOA | 43.8% | 55.6% | 0.6% | 0.960 |
| Dashen | 56.5% | 43.1% | 0.4% | 0.971 |

### Sentiment by Star Rating

| Stars | Positive % |
|-------|------------|
| 1★ | 9.1% |
| 2★ | 13.6% |
| 3★ | 29.5% |
| 4★ | 45.2% |
| 5★ | 77.8% |

### Universal Pattern

- **App Stability** — biggest pain point across all banks (75–91% negative)
- **User Experience** — biggest strength across all banks (88–94% positive)
- **BOA** — clear underperformer across every metric

---

## Limitations

1. **Duplicate reviews** — scraper loops back on large requests; mitigated by requesting 600 and deduplicating
2. **English only** — Amharic reviews excluded; findings may not represent all Ethiopian users
3. **Rate limiting** — 2-second delay between banks mitigates but counts may vary on reruns
4. **Keyword theme matching** — context-blind; corrected partially by sentiment within theme
5. **Short reviews** — 33-39% too short to theme meaningfully; labeled General
6. **Rating vs text contradictions** — DistilBERT classifies text correctly; star rating treated separately
7. **DistilBERT binary** — only POSITIVE/NEGATIVE; NEUTRAL assigned when confidence < 0.6

---

## CI/CD Pipeline

Every push to `main` triggers GitHub Actions:

1. Spins up Ubuntu virtual machine
2. Installs Python 3.10
3. Runs `pip install -r requirements.txt`
4. Verifies key packages import correctly

Configuration: `.github/workflows/unittests.yml`

---

## Contributing

This project follows [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | New functionality |
| `fix:` | Bug fix |
| `docs:` | Documentation update |
| `refactor:` | Code restructure |
| `chore:` | Setup or config |
| `test:` | Tests |

Branch strategy: one branch per task, merged via Pull Request to `main`.

---

*Built by [Afomiat](https://github.com/Afomiat) · Omega Consultancy Data Engineering Challenge · May 2026*

