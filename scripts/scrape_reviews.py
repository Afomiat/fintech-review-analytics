import time 
import pandas as pd
from google_play_scraper import reviews, Sort

APPS = [
    ('com.combanketh.mobilebanking', 'Commercial Bank of Ethiopia'),
    ('com.boa.boaMobileBanking',     'Bank of Abyssinia'),
    ('com.dashen.dashensuperapp',    'Dashen Bank'),    
]

REVIEWS_PER_BANK = 600   
DELAY_SECONDS = 2        
OUTPUT_PATH = 'data/raw/reviews_raw.csv'

def scrape_bank_review(app_id: str, bank_name: str, count: int) -> list[dict]:

    print(f"\nScraping {bank_name}...")
    print(f" App ID: {app_id}")
    print(f" Requesting {count} Reviews...")

    try:
        result,_ = reviews(
            app_id,
            lang='en',
            country='et',
            sort=Sort.NEWEST,
            count=count,
        )

    except Exception as e:
        print(f"Error scraping {bank_name}: {e}")
        result = []


    print(f" Received {len(result)} reviews.")
    

    records = []
    for r in result:
        record = {
            'review': r.get('content'),
            'rating': r.get('score'),
            'date': r.get('at'),
            'bank':bank_name,
            'source':'Google Play'
        }
        records.append(record)
    return records
    
    
def main():
    all_records = []

    for app_id, bank_name in APPS:
        records = scrape_bank_review(app_id, bank_name, REVIEWS_PER_BANK)
        all_records.extend(records)

        print(f"Waiting {DELAY_SECONDS} seconds before next bank...")
        time.sleep(DELAY_SECONDS)
    
    df = pd.DataFrame(all_records)
    print(f"\n{'='*50}")
    print(f"TOTAL RECORDS COLLECTED: {len(df)}")
    print(f"Reviews per bank:")
    print(df['bank'].value_counts())

    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nRaw data saved to: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()