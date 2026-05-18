

import psycopg2
import pandas as pd


# ── Database Configuration ────────────────────────────────────────────────────
# Update PASSWORD to match your PostgreSQL password

DB_CONFIG = {
    'host':     'localhost',
    'database': 'bank_reviews',
    'user':     'postgres',
    'password': 'postgres'   
}

DATA_PATH = 'data/processed/reviews_analyzed.csv'

# ── Bank Metadata ─────────────────────────────────────────────────────────────
# Maps bank names in CSV to their app IDs

BANKS = [
    ('Commercial Bank of Ethiopia', 'com.combanketh.mobilebanking'),
    ('Bank of Abyssinia',           'com.boa.boaMobileBanking'),
    ('Dashen Bank',                 'com.cr2.amolelight'),
]


# ── Helper Functions ──────────────────────────────────────────────────────────

def connect():
    """
    Opens a connection to PostgreSQL.
    Returns connection and cursor objects.
    """
    conn   = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("✓ Connected to PostgreSQL — bank_reviews database")
    return conn, cursor


def clear_tables(cursor):
    """
    Clears existing data before inserting.
    Allows script to be run multiple times without duplicate errors.
    ORDER matters — reviews first because it references banks.
    """
    cursor.execute("DELETE FROM reviews;")
    cursor.execute("DELETE FROM banks;")
    cursor.execute("ALTER SEQUENCE banks_bank_id_seq RESTART WITH 1;")
    print("✓ Existing data cleared")


def insert_banks(cursor) -> dict:
    """
    Inserts the three banks into the banks table.

    Returns:
        Dictionary mapping bank_name → bank_id
        Used to look up bank_id when inserting reviews
    """
    bank_id_map = {}

    for bank_name, app_name in BANKS:
        cursor.execute(
            """
            INSERT INTO banks (bank_name, app_name)
            VALUES (%s, %s)
            RETURNING bank_id;
            """,
            (bank_name, app_name)
        )
        bank_id = cursor.fetchone()[0]
        bank_id_map[bank_name] = bank_id
        print(f"  Inserted bank: {bank_name} → bank_id={bank_id}")

    print(f"✓ {len(BANKS)} banks inserted")
    return bank_id_map


def insert_reviews(cursor, df: pd.DataFrame, bank_id_map: dict):
    """
    Inserts all reviews into the reviews table.

    Args:
        cursor:      PostgreSQL cursor
        df:          DataFrame with analyzed reviews
        bank_id_map: maps bank_name → bank_id
    """
    inserted  = 0
    skipped   = 0
    total     = len(df)

    for _, row in df.iterrows():
        bank_name = row['bank']

        # Skip if bank not in our map (shouldn't happen)
        if bank_name not in bank_id_map:
            print(f"  WARNING: unknown bank '{bank_name}' — skipping")
            skipped += 1
            continue

        bank_id = bank_id_map[bank_name]

        # Handle the column name — could be 'review' or 'review_text'
        if 'review_text' in df.columns:
            review_text = row['review_text']
        else:
            review_text = row['review']

        try:
            cursor.execute(
                """
                INSERT INTO reviews (
                    review_id,
                    bank_id,
                    review_text,
                    rating,
                    review_date,
                    sentiment_label,
                    sentiment_score,
                    vader_label,
                    vader_score,
                    identified_theme,
                    source
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    int(row['review_id']),
                    bank_id,
                    str(review_text) if pd.notna(review_text) else None,
                    int(row['rating']),
                    str(row['date']),
                    str(row['sentiment_label']),
                    float(row['sentiment_score']),
                    str(row['vader_label']),
                    float(row['vader_score']),
                    str(row['identified_theme']),
                    str(row['source'])
                )
            )
            inserted += 1

            # Progress every 200 rows
            if inserted % 200 == 0:
                print(f"  Inserted {inserted}/{total} reviews")

        except Exception as e:
            print(f"  ERROR on review_id {row['review_id']}: {e}")
            skipped += 1

    print(f"✓ {inserted} reviews inserted, {skipped} skipped")


def verify_data(cursor):
    """
    Runs verification queries to confirm data integrity.
    These are the exact queries required by the project brief.
    """
    print("\nVERIFICATION QUERIES")
    print("=" * 50)

    # Query 1: Count reviews per bank
    print("\n1. Reviews per bank:")
    cursor.execute("""
        SELECT b.bank_name, COUNT(r.review_id) as review_count
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_name
        ORDER BY review_count DESC;
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:<35} {row[1]} reviews")

    # Query 2: Average rating per bank
    print("\n2. Average rating per bank:")
    cursor.execute("""
        SELECT b.bank_name, ROUND(AVG(r.rating)::numeric, 2) as avg_rating
        FROM banks b
        LEFT JOIN reviews r ON b.bank_id = r.bank_id
        GROUP BY b.bank_name
        ORDER BY avg_rating DESC;
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:<35} {row[1]} stars")

    # Query 3: Sentiment distribution
    print("\n3. Sentiment distribution:")
    cursor.execute("""
        SELECT sentiment_label, COUNT(*) as count
        FROM reviews
        GROUP BY sentiment_label
        ORDER BY count DESC;
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]:<15} {row[1]} reviews")

    # Query 4: Check for nulls in key columns
    print("\n4. Null check on key columns:")
    cursor.execute("""
        SELECT
            SUM(CASE WHEN review_text     IS NULL THEN 1 ELSE 0 END) as null_reviews,
            SUM(CASE WHEN rating          IS NULL THEN 1 ELSE 0 END) as null_ratings,
            SUM(CASE WHEN sentiment_label IS NULL THEN 1 ELSE 0 END) as null_sentiment,
            SUM(CASE WHEN identified_theme IS NULL THEN 1 ELSE 0 END) as null_themes
        FROM reviews;
    """)
    row = cursor.fetchone()
    print(f"   Null review_text:      {row[0]}")
    print(f"   Null rating:           {row[1]}")
    print(f"   Null sentiment_label:  {row[2]}")
    print(f"   Null identified_theme: {row[3]}")

    # Query 5: Total reviews
    cursor.execute("SELECT COUNT(*) FROM reviews;")
    total = cursor.fetchone()[0]
    status = "✓" if total >= 1000 else "✗"
    print(f"\n{status} Total reviews in database: {total} (KPI: 1,000 minimum)")



def main():
    # Step 1: Load data
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} reviews from {DATA_PATH}")
    print(f"Columns: {list(df.columns)}")

    # Step 2: Connect
    conn, cursor = connect()

    try:
        # Step 3: Clear existing data
        clear_tables(cursor)

        # Step 4: Insert banks
        print("\nInserting banks...")
        bank_id_map = insert_banks(cursor)

        # Step 5: Insert reviews
        print(f"\nInserting {len(df)} reviews...")
        insert_reviews(cursor, df, bank_id_map)

        # Step 6: Commit all changes
        conn.commit()
        print("\n✓ All changes committed to database")

        # Step 7: Verify
        verify_data(cursor)

    except Exception as e:
        # If anything fails, roll back all changes
        conn.rollback()
        print(f"\nERROR: {e}")
        print("All changes rolled back")

    finally:
        cursor.close()
        conn.close()
        print("\n✓ Database connection closed")


if __name__ == '__main__':
    main()