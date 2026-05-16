import pandas as pd

INPUT_PATH  = 'data/raw/reviews_raw.csv'
OUTPUT_PATH = 'data/raw/reviews_clean.csv'

def load_data(path: str) -> pd.DataFrame:
    
    df = pd.read_csv(path)
    print("RAW DATA LOADED")
    print(f" Shape: {df.shape}")
    print(f" Columns: {list(df.columns)}")
    print(f"\n First 5 rows:")
    print(df.head())
    print(f"\nData types:")
    print(df.dtypes)

    return df


def report_missing(df: pd.DataFrame, stage: str) -> None:

    print(f"\nMISSING VALUE REPORT: {stage}:")
    missing = df.isnull().sum()
    pct = (missing / len(df) * 100).round(2)
    report = pd.DataFrame({'count': missing, 'percent':pct})
    print(report)

def remove_duplicates(df:pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=['review','bank'])
    after = len(df)

    print(f"\nDUPLICATES REMOVED: {before - after}")
    print(f"  Rows before: {before}")
    print(f"  Rows after:  {after}")

    return df    

def handle_missing(df:pd.DataFrame) -> pd.DataFrame:
    
    before = len(df)
    df = df.dropna(subset=['review', 'rating'])
    after = len(df)

    print(f"\nROWS DROPPEND (missing review or rating): {before - after}")
   

    return df    

def normalize_dates(df:pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    print(f"\nDATES NORMALIZED to YYYY-MM-DD")
    print(f"  Sample dates: {df['date'].head(3).tolist()}")

    return df

def validate_final(df: pd.DataFrame) -> None:
    """Final checks before saving."""
    print(f"\n{'='*50}")
    print("FINAL VALIDATION")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"\nReviews per bank:")
    print(df['bank'].value_counts())
    print(f"\nRating distribution:")
    print(df['rating'].value_counts().sort_index())
    print(f"\nMissing values:")
    print(df.isnull().sum())
    print(f"\nDate range:")
    print(f"  Earliest: {df['date'].min()}")
    print(f"  Latest:   {df['date'].max()}")

    # Check for minimum review count
    counts = df['bank'].value_counts()
    for bank, count in counts.items():
        status = "✓" if count >= 400 else "✗ BELOW MINIMUM"
        print(f"  {status} {bank}: {count} reviews")

def main():
    # Step 1: Load
    df = load_data(INPUT_PATH)

    # Step 2: Report missing values before any changes
    report_missing(df, stage='before cleaning')

    # Step 3: Remove duplicates
    df = remove_duplicates(df)

    # Step 4: Drop rows missing critical fields
    df = handle_missing(df)

    # Step 5: Normalize dates
    df = normalize_dates(df)

    # Step 6: Keep only the required columns in the correct order
    required_columns = ['review', 'rating', 'date', 'bank', 'source']
    df = df[required_columns]

    # Step 7: Report missing values after cleaning
    report_missing(df, stage='after cleaning')

    # Step 8: Validate
    validate_final(df)

    # Step 9: Save
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nClean data saved to: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()