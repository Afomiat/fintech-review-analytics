
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load actual reviews
df = pd.read_csv('data/raw/reviews_clean.csv')

# Pick 10 real reviews to test on — mix of ratings
samples = df.sample(10, random_state=42)[['review', 'rating', 'bank']]

analyzer = SentimentIntensityAnalyzer()

print("VADER OUTPUT ON REAL REVIEWS")
print("=" * 70)

for _, row in samples.iterrows():
    scores = analyzer.polarity_scores(row['review'])
    compound = scores['compound']

    if compound >= 0.05:
        label = 'POSITIVE'
    elif compound <= -0.05:
        label = 'NEGATIVE'
    else:
        label = 'NEUTRAL'

    print(f"\nReview:   {row['review'][:80]}")
    print(f"Rating:   {row['rating']} stars")
    print(f"Bank:     {row['bank']}")
    print(f"Label:    {label}")
    print(f"Compound: {compound:.4f}")
    print(f"Scores:   {scores}")