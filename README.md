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

```
fintech-review-analytics/
│
├── .github/
│   └── workflows/
│       └── unittests.yml              # CI/CD pipeline — runs on every push to main
│
├── data/
│   ├── raw/                           # Local data files — never committed to GitHub
│   │   ├── reviews_raw.csv            # Output of scrape_reviews.py
│   │   └── reviews_clean.csv          # Output of preprocess_reviews.py
│   └── processed/                     # NLP output — never committed to GitHub
│       ├── reviews_with_sentiment.csv # Output of sentiment_analysis.py
│       └── reviews_analyzed.csv       # Output of thematic_analysis.py
│
├── notebooks/
│   ├── __init__.py
│   ├── explore_scraper.py             # Inspects raw scraper output
│   ├── explore_sentiment.py           # Tests VADER on sample reviews
│   └── explore_tfidf.py               # Explores TF-IDF keywords per bank
│
├── scripts/
│   ├── __init__.py
│   ├── scrape_reviews.py              # Scrapes reviews from Google Play Store
│   ├── preprocess_reviews.py          # Cleans, deduplicates, normalizes raw data
│   ├── validate_data.py               # Validates cleaned data against KPIs
│   ├── sentiment_analysis.py          # DistilBERT + VADER sentiment pipeline
│   ├── thematic_analysis.py           # TF-IDF keyword extraction + theme assignment
│   ├── schema.sql                     # PostgreSQL database schema
│   └── insert_data.py                 # Inserts reviewed data into PostgreSQL
│
├── src/
│   └── __init__.py                    # Reusable modules (populated in later tasks)
│
├── tests/
│   └── __init__.py                    # Unit tests (populated in later tasks)
│
├── .gitignore                         # Excludes data files, venv, and cache
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
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

> **Note:** `torch` (~123MB) and the DistilBERT model (~268MB) will be downloaded on first run. Subsequent runs use the local cache.

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

## Task 2: Sentiment & Thematic Analysis

### Pipeline Overview

```
data/raw/reviews_clean.csv
      ↓
sentiment_analysis.py   → data/processed/reviews_with_sentiment.csv
      ↓
thematic_analysis.py    → data/processed/reviews_analyzed.csv
```

### Running the Pipeline

```bash
# Step 1: Run sentiment analysis (DistilBERT + VADER)
python scripts/sentiment_analysis.py

# Step 2: Extract keywords and assign themes
python scripts/thematic_analysis.py
```

### What Each Script Does

**`sentiment_analysis.py`**
- Loads 1,450 clean reviews
- Runs DistilBERT (`distilbert-base-uncased-finetuned-sst-2-english`) as primary tool
- Runs VADER as secondary tool for comparison and validation
- Assigns each review: `sentiment_label` (POSITIVE/NEGATIVE/NEUTRAL) and `sentiment_score`
- Reports sentiment breakdown per bank and per star rating
- Saves output to `data/processed/reviews_with_sentiment.csv`

**`thematic_analysis.py`**
- Loads sentiment-labeled reviews
- Extracts top TF-IDF keywords per bank (single words and two-word phrases)
- Assigns each review to one of 6 themes based on keyword matching
- Reports theme distribution and sentiment breakdown within each theme
- Saves final output to `data/processed/reviews_analyzed.csv`

### Sentiment Tool Selection Rationale

Two tools were used and compared:

| Tool | Type | Strengths | Weaknesses |
|------|------|-----------|------------|
| DistilBERT | Transformer (neural network) | Understands context and negation, handles informal text, state-of-the-art accuracy | Requires torch (~123MB), slower to run |
| VADER | Lexicon (rule-based) | Fast, no heavy dependencies, interpretable scores | Misses context, struggles with broken grammar and emojis |

**DistilBERT was selected as primary** because it correctly handles cases VADER misses:

| Review | DistilBERT | VADER |
|--------|-----------|-------|
| "It's not allowing me to transfer money" | NEGATIVE (99.7%) | NEUTRAL |
| "IT'S NOT WORK ON HUAWEI DEVICES" | NEGATIVE (99.97%) | NEUTRAL |
| "not bad but could be better" | NEGATIVE (context-aware) | NEUTRAL |

Overall agreement between tools: **59.5%**. Disagreements consistently showed DistilBERT was correct — VADER over-assigns NEUTRAL on informal and grammatically broken text.

### Theme Taxonomy

Themes were defined by first running TF-IDF keyword exploration on the actual dataset, then grouping discovered keywords into business-relevant categories. Keywords reflect what users actually wrote.

| Theme | Sample Keywords | Business Relevance |
|-------|----------------|-------------------|
| Transaction Performance | transfer, payment, slow, speed, loading, delay | Core banking function |
| App Stability | crash, not working, fix, update, bug, error | Retention risk |
| Account Access | login, OTP, password, fingerprint, locked | Security & access |
| User Experience | easy, nice, interface, smooth, good, great | Product quality |
| Customer Service | support, help, response, complaint, agent | Support quality |
| Feature Requests | add, need, want, suggest, improve | Product roadmap |

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

**Prerequisites:**
- PostgreSQL 17+ installed and running locally
- `bank_reviews` database created

```bash
# Step 1: Create the database
psql -U postgres -c "CREATE DATABASE bank_reviews;"

# Step 2: Create tables from schema file
psql -U postgres -d bank_reviews -f scripts/schema.sql

# Step 3: Insert all review data
python scripts/insert_data.py
```

### Schema Design

Two tables with a one-to-many relationship.
One bank has many reviews. Each review belongs to one bank.

**banks table**

| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| bank_id | SERIAL | PRIMARY KEY | Auto-generated unique ID |
| bank_name | VARCHAR(100) | NOT NULL | Full bank name |
| app_name | VARCHAR(100) | NOT NULL | Google Play app ID |

**reviews table**

| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| review_id | INTEGER | PRIMARY KEY | From CSV review_id |
| bank_id | INTEGER | FOREIGN KEY → banks | Links review to bank |
| review_text | TEXT | | Raw review content |
| rating | INTEGER | CHECK 1–5 | Star rating |
| review_date | DATE | | Date of review |
| sentiment_label | VARCHAR(20) | | POSITIVE/NEGATIVE/NEUTRAL |
| sentiment_score | FLOAT | | DistilBERT confidence |
| vader_label | VARCHAR(20) | | VADER sentiment label |
| vader_score | FLOAT | | VADER compound score |
| identified_theme | VARCHAR(50) | | Business theme |
| source | VARCHAR(50) | | Always 'Google Play' |

### Verification Results

All verification queries passed after insertion:

| Query | Result |
|-------|--------|
| Total reviews inserted | 1,450 |
| CBE reviews | 456 |
| BOA reviews | 498 |
| Dashen reviews | 496 |
| Avg rating — CBE | 3.93★ |
| Avg rating — BOA | 3.29★ |
| Avg rating — Dashen | 3.78★ |
| Null review_text | 0 |
| Null rating | 0 |
| Null sentiment_label | 0 |
| Null identified_theme | 0 |
| KPI (1,000+ entries) | ✓ Passed |

### What Each Script Does

**`schema.sql`**
- Drops and recreates both tables cleanly
- Defines all column types and constraints
- Establishes the foreign key relationship between tables
- Can be run to recreate the database on any machine

**`insert_data.py`**
- Connects to PostgreSQL using psycopg2
- Clears existing data to allow clean reruns
- Inserts 3 banks into the banks table
- Inserts 1,450 reviews into the reviews table
- Runs 4 verification queries and prints results

---

## Data Quality Report

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

> **Note:** The strong skew toward 1-star and 5-star ratings reflects negativity/positivity bias in user-generated review data. Users are most likely to leave a review after an extremely positive or negative experience. Middle ratings are underrepresented.

---

## Key Findings

### Sentiment by Bank

| Bank | Positive | Negative | Neutral | Avg Confidence |
|------|----------|----------|---------|----------------|
| Commercial Bank of Ethiopia | 57.0% | 41.4% | 1.5% | 0.968 |
| Bank of Abyssinia | 43.8% | 55.6% | 0.6% | 0.960 |
| Dashen Bank | 56.5% | 43.1% | 0.4% | 0.971 |

> BOA has the highest negative sentiment (55.6%), consistent with its lowest Play Store rating (3.4★). Dashen and CBE are close, consistent with their similar ratings (4.1★ and 4.2★).

### Sentiment Validates Star Ratings

| Stars | Positive % |
|-------|------------|
| 1★ | 9.1% |
| 2★ | 13.6% |
| 3★ | 29.5% |
| 4★ | 45.2% |
| 5★ | 77.8% |

Positive percentage increases consistently with star rating — confirms the DistilBERT model is correctly classifying sentiment.

### Pain Points by Bank

| Theme | CBE Negative | BOA Negative | Dashen Negative |
|-------|-------------|-------------|-----------------|
| App Stability | 75% | 91% | 90% |
| Transaction Performance | 60% | 76% | 61% |
| Account Access | 73% | 70% | 64% |
| Feature Requests | 56% | 92% | 58% |

App Stability is the single biggest complaint across all three banks. BOA's App Stability score (91% negative) indicates a critical reliability issue.

### Strengths by Bank

| Theme | CBE Positive | BOA Positive | Dashen Positive |
|-------|-------------|-------------|-----------------|
| User Experience | 94% | 91% | 88% |
| Customer Service | 56% | 17% | 40% |

User Experience is the consistent strength across all banks — users appreciate the interface design even when functionality fails. CBE leads in Customer Service satisfaction.

### Bank-Specific Recommendations

**Commercial Bank of Ethiopia**
- Prioritize stability fixes — 75% of App Stability reviews are negative
- Investigate transfer failure patterns — 60% of Transaction Performance reviews are negative
- Leverage strong customer service reputation (94% positive) as a differentiator

**Bank of Abyssinia**
- App Stability is a crisis — 91% negative, highest of all three banks
- Feature gap is significant — 92% of Feature Request reviews are negative, users feel the app is incomplete
- Customer Service needs improvement — only 17% positive, lowest of all three banks

**Dashen Bank**
- App Stability (90% negative) needs urgent attention despite strong UX scores
- Account Access issues (64% negative) suggest login/OTP reliability problems
- Strong User Experience foundation (88% positive) — build on this with stability improvements

---

## Limitations

### 1. Duplicate Reviews from Scraper
The `google-play-scraper` library returns duplicate reviews when requesting large counts. Requested 600 per bank; received ~480 clean after deduplication.

### 2. English Reviews Only
The scraper is configured with `lang='en'`. Reviews in Amharic or other languages are excluded, biasing findings toward English-speaking users who may not represent the full Ethiopian user base.

### 3. Rate Limiting
Rapid requests can trigger Google rate limiting. A 2-second delay between banks mitigates this. Counts may vary slightly on repeated runs.

### 4. Theme Assignment by Keyword Matching
Keyword matching cannot understand context. A review containing "transfer" is assigned Transaction Performance even if used positively. Sentiment within each theme partially corrects for this.

### 5. Short Reviews Without Specific Topics
Approximately 33-39% of reviews across all banks are very short ("nice", "good", "worst") with no specific topic. These fall into the General category and cannot be meaningfully themed without more context.

### 6. Rating vs Text Contradictions
Some reviews have star ratings that contradict the review text (e.g., 4 stars with entirely negative text). DistilBERT correctly classifies the text sentiment — the star rating is treated as a separate signal.

### 7. DistilBERT Binary Classification
DistilBERT only outputs POSITIVE or NEGATIVE. NEUTRAL is assigned when confidence falls below 0.6. Some genuinely neutral reviews may be forced into a binary category at high confidence.

---

## CI/CD Pipeline

Every push to `main` and every Pull Request targeting `main` triggers an automated pipeline via GitHub Actions that:

1. Spins up a fresh Ubuntu virtual machine
2. Installs Python 3.10
3. Runs `pip install -r requirements.txt`
4. Verifies key packages import correctly

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
