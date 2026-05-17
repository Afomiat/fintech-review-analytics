import os
import pandas as pd
from transformers import pipeline
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer



INPUT_PATH        = 'data/raw/reviews_clean.csv'
OUTPUT_PATH       = 'data/processed/reviews_with_sentiment.csv'
MODEL_NAME        = 'distilbert-base-uncased-finetuned-sst-2-english'
MAX_LENGTH        = 512
BATCH_SIZE        = 16
NEUTRAL_THRESHOLD = 0.6   # below this confidence = NEUTRAL



def load_reviews(path: str) -> pd.DataFrame:
  
    df = pd.read_csv(path)
    df['review_id'] = range(1, len(df) + 1)
    print(f"Loaded {len(df)} reviews")
    print(f"Per bank: {df['bank'].value_counts().to_dict()}")
    return df


def run_distilbert(df: pd.DataFrame) -> pd.DataFrame:
    
    print(f"\nLoading DistilBERT model: {MODEL_NAME}")
    print("(model is cached — loading from disk)")

    sentiment_pipe = pipeline(
        "sentiment-analysis",
        model=MODEL_NAME,
        truncation=True,
        max_length=MAX_LENGTH
    )

    print(f"Running DistilBERT on {len(df)} reviews in batches of {BATCH_SIZE}...")

    labels = []
    scores = []
    texts  = df['review'].tolist()
    total  = len(texts)

    for i in range(0, total, BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]

        # Clean each text — handle non-strings safely
        cleaned = [
            str(t)[:MAX_LENGTH] if isinstance(t, str) and t.strip() != ''
            else 'neutral'
            for t in batch
        ]

        results = sentiment_pipe(cleaned)

        for r in results:
            label = r['label']   # 'POSITIVE' or 'NEGATIVE'
            score = r['score']   # confidence 0.0 to 1.0

            # Low confidence = uncertain = NEUTRAL
            if score < NEUTRAL_THRESHOLD:
                label = 'NEUTRAL'

            labels.append(label)
            scores.append(round(score, 4))

        # Progress
        done = min(i + BATCH_SIZE, total)
        print(f"  {done}/{total} reviews processed", end='\r')

    print(f"  {total}/{total} reviews processed — done     ")

    df['sentiment_label'] = labels
    df['sentiment_score']  = scores
    return df


def run_vader(df: pd.DataFrame) -> pd.DataFrame:
   
    print("\nRunning VADER for comparison...")
    analyzer = SentimentIntensityAnalyzer()
    labels   = []
    scores   = []

    for review in df['review']:
        if not isinstance(review, str) or review.strip() == '':
            labels.append('NEUTRAL')
            scores.append(0.0)
            continue

        result   = analyzer.polarity_scores(review)
        compound = round(result['compound'], 4)

        if compound >= 0.05:
            labels.append('POSITIVE')
        elif compound <= -0.05:
            labels.append('NEGATIVE')
        else:
            labels.append('NEUTRAL')

        scores.append(compound)

    df['vader_label'] = labels
    df['vader_score']  = scores
    print(f"  VADER complete")
    return df


def compare_tools(df: pd.DataFrame) -> None:
    
    agreement     = (df['sentiment_label'] == df['vader_label']).mean() * 100
    disagreements = df[df['sentiment_label'] != df['vader_label']]

    print(f"\nTOOL COMPARISON:")
    print(f"  DistilBERT vs VADER agreement: {agreement:.1f}%")
    print(f"  Disagreements: {len(disagreements)} reviews")

    if len(disagreements) > 0:
        print(f"\n  Sample disagreements (first 3):")
        for _, row in disagreements.head(3).iterrows():
            print(f"    Review:     {str(row['review'])[:70]}")
            print(f"    DistilBERT: {row['sentiment_label']} ({row['sentiment_score']})")
            print(f"    VADER:      {row['vader_label']} ({row['vader_score']})")
            print()


def aggregate_by_bank(df: pd.DataFrame) -> None:
   
    print("\nSENTIMENT BY BANK (DistilBERT):")
    print("=" * 60)

    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        total   = len(bank_df)
        counts  = bank_df['sentiment_label'].value_counts()

        pos = counts.get('POSITIVE', 0)
        neg = counts.get('NEGATIVE', 0)
        neu = counts.get('NEUTRAL',  0)

        print(f"\n{bank} ({total} reviews):")
        print(f"  Positive: {pos:>4} ({pos/total*100:.1f}%)")
        print(f"  Negative: {neg:>4} ({neg/total*100:.1f}%)")
        print(f"  Neutral:  {neu:>4} ({neu/total*100:.1f}%)")
        print(f"  Avg confidence: {bank_df['sentiment_score'].mean():.4f}")


def aggregate_by_rating(df: pd.DataFrame) -> None:
    
    print("\nSENTIMENT SCORE BY STAR RATING:")
    print("(should increase as stars increase — validates model)")
    print("-" * 50)

    grouped = df.groupby('rating').agg(
        avg_score   =('sentiment_score', 'mean'),
        count       =('sentiment_score', 'count'),
        pct_positive=('sentiment_label', lambda x: (x == 'POSITIVE').mean() * 100)
    )

    for rating, row in grouped.iterrows():
        bar = '█' * int(row['pct_positive'] / 5)
        print(f"  {rating}★  avg:{row['avg_score']:.3f}  "
              f"pos%:{row['pct_positive']:.1f}%  {bar}  (n={int(row['count'])})")


def check_coverage(df: pd.DataFrame) -> None:
    labeled  = df['sentiment_label'].notna().sum()
    total    = len(df)
    coverage = labeled / total * 100
    status   = "✓" if coverage >= 90 else "✗"
    print(f"\n{status} Coverage: {labeled}/{total} ({coverage:.1f}%) — KPI: 90% minimum")



def main():
    os.makedirs('data/processed', exist_ok=True)

    # Step 1: Load
    df = load_reviews(INPUT_PATH)

    # Step 2: DistilBERT (primary)
    df = run_distilbert(df)

    # Step 3: VADER (comparison)
    df = run_vader(df)

    # Step 4: Compare tools
    compare_tools(df)

    # Step 5: Business aggregations
    aggregate_by_bank(df)
    aggregate_by_rating(df)

    # Step 6: Coverage check
    check_coverage(df)

    # Step 7: Save
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to: {OUTPUT_PATH}")
    print(f"Shape:    {df.shape}")
    print(f"Columns:  {list(df.columns)}")


if __name__ == '__main__':
    main()