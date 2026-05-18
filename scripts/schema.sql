

-- Drop tables if they exist (for clean recreation)
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS banks;

-- ── Banks Table ───────────────────────────────────────────────


CREATE TABLE banks (
    bank_id   SERIAL PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    app_name  VARCHAR(100) NOT NULL
);

-- ── Reviews Table ─────────────────────────────────────────────


CREATE TABLE reviews (
    review_id        INTEGER PRIMARY KEY,
    bank_id          INTEGER NOT NULL REFERENCES banks(bank_id),
    review_text      TEXT,
    rating           INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_date      DATE,
    sentiment_label  VARCHAR(20),
    sentiment_score  FLOAT,
    vader_label      VARCHAR(20),
    vader_score      FLOAT,
    identified_theme VARCHAR(50),
    source           VARCHAR(50)
);