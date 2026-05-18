import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer




THEME_KEYWORDS = {
    'Transaction Performance': [
        'transfer', 'transaction', 'payment', 'send money',
        'slow', 'speed', 'fast', 'loading', 'delay', 'pending',
        'timeout', 'processing', 'balance', 'deposit', 'withdraw',
        'money transfer', 'time taking', 'takes time'
    ],
    'App Stability': [
        'crash', 'crashes', 'crashing', 'not working', 'doesnt work',
        'doesn work', 'work', 'working', 'fix', 'fixed', 'bug',
        'update', 'version', 'error', 'force close', 'freezes',
        'unable', 'keep', 'stop', 'stopped', 'broken'
    ],
    'Account Access': [
        'login', 'log in', 'password', 'otp', 'fingerprint',
        'sign in', 'authentication', 'access', 'locked', 'reset',
        'verification', 'code', 'expire', 'session', 'logout',
        'account', 'open account', 'register', 'biometric'
    ],
    'User Experience': [
        'interface', 'design', 'ui', 'button', 'navigation',
        'layout', 'screen', 'display', 'theme', 'dark mode',
        'font', 'menu', 'easy', 'difficult', 'confusing',
        'simple', 'nice', 'beautiful', 'smooth', 'user friendly'
    ],
    'Customer Service': [
        'support', 'help', 'service', 'response', 'agent',
        'call', 'complaint', 'contact', 'feedback', 'reply',
        'staff', 'customer care', 'hotline', 'resolve',
        'customer support', 'no response', 'poor service'
    ],
    'Feature Requests': [
        'add', 'need', 'want', 'request', 'feature', 'wish',
        'suggest', 'improve', 'should', 'please', 'hope',
        'budget', 'notification', 'statement', 'history',
        'fingerprint login', 'face id', 'dark mode', 'widget'
    ],
    'App Stability': [
    'open', 'launch', 'install', 'load', 'loading',
    'blank', 'black screen', 'restart', 'hang', 'stuck',
    'problem', 'issue', 'bad', 'terrible', 'worst', 'awful'
],

'User Experience': [
    'good', 'great', 'excellent', 'amazing', 'best',
    'perfect', 'love', 'like', 'nice', 'super',
    'recommend', 'helpful', 'convenient', 'useful'
],
}



def assign_theme(review_text: str) -> str:

    if not isinstance(review_text, str) or review_text.strip() == '':
        return 'General'

    text_lower = review_text.lower()

    for theme, keywords in THEME_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return theme

    return 'General'


def extract_top_keywords(reviews: list, top_n: int = 15) -> list:
  
    if len(reviews) < 3:
        return []

    vectorizer = TfidfVectorizer(
        max_features=100,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2
    )

    try:
        matrix       = vectorizer.fit_transform(reviews)
        feature_names = vectorizer.get_feature_names_out()
        scores       = matrix.sum(axis=0).A1
        word_scores  = sorted(
            zip(feature_names, scores),
            key=lambda x: x[1],
            reverse=True
        )
        return word_scores[:top_n]
    except Exception as e:
        print(f"  TF-IDF error: {e}")
        return []


def report_themes(df: pd.DataFrame) -> None:
  
    print("\nTHEME ANALYSIS BY BANK")
    print("=" * 65)

    for bank in df['bank'].unique():
        bank_df      = df[df['bank'] == bank]
        total        = len(bank_df)
        theme_counts = bank_df['identified_theme'].value_counts()

        print(f"\n{'─'*65}")
        print(f"{bank} ({total} reviews)")
        print(f"{'─'*65}")

        # Theme distribution
        print(f"\n  Theme Distribution:")
        for theme, count in theme_counts.items():
            pct = count / total * 100
            bar = '█' * int(pct / 3)
            print(f"  {theme:<25} {count:>4} ({pct:.1f}%) {bar}")

        # Top keywords for this bank
        print(f"\n  Top Keywords (TF-IDF):")
        keywords = extract_top_keywords(bank_df['review'].tolist())
        for word, score in keywords[:10]:
            print(f"    {word:<28} {score:.3f}")

        # Sentiment within each theme — business insight
        print(f"\n  Sentiment by Theme:")
        for theme in theme_counts.index:
            theme_df = bank_df[bank_df['identified_theme'] == theme]
            neg_pct  = (theme_df['sentiment_label'] == 'NEGATIVE').mean() * 100
            pos_pct  = (theme_df['sentiment_label'] == 'POSITIVE').mean() * 100
            print(f"  {theme:<25} pos:{pos_pct:.0f}%  neg:{neg_pct:.0f}%")


def validate_themes(df: pd.DataFrame) -> None:
 
    print(f"\nTHEME VALIDATION")
    print("=" * 40)

    all_pass = True
    for bank in df['bank'].unique():
        bank_df        = df[df['bank'] == bank]
        theme_count    = bank_df['identified_theme'].nunique()
        general_pct    = (bank_df['identified_theme'] == 'General').mean() * 100
        meets_kpi      = theme_count >= 3

        status = "✓" if meets_kpi else "✗"
        print(f"\n{status} {bank}:")
        print(f"    Distinct themes: {theme_count} (KPI: 3 minimum)")
        print(f"    Unmatched (General): {general_pct:.1f}%")

        if not meets_kpi:
            all_pass = False

    print(f"\n{'ALL THEME CHECKS PASSED' if all_pass else 'SOME CHECKS FAILED'}")



def main():
    os.makedirs('data/processed', exist_ok=True)

    INPUT_PATH  = 'data/processed/reviews_with_sentiment.csv'
    OUTPUT_PATH = 'data/processed/reviews_analyzed.csv'

    # Step 1: Load sentiment results
    df = pd.read_csv(INPUT_PATH)
    print(f"Loaded {len(df)} reviews with sentiment labels")

    # Step 2: Assign themes
    print("\nAssigning themes...")
    df['identified_theme'] = df['review'].apply(assign_theme)
    print(f"  Done — {df['identified_theme'].nunique()} distinct themes found")

    # Step 3: Full report
    report_themes(df)

    # Step 4: Validate KPIs
    validate_themes(df)

    # Step 5: Select final output columns
 # Rename review to review_text to match required schema
    df = df.rename(columns={'review': 'review_text'})

    output_cols = [
        'review_id',
        'review_text',
        'rating',
        'date',
        'bank',
        'source',
        'sentiment_label',
        'sentiment_score',
        'vader_label',
        'vader_score',
        'identified_theme'
    ]
    df = df[output_cols]

    # Step 6: Save
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved to: {OUTPUT_PATH}")
    print(f"Shape:    {df.shape}")
    print(f"Columns:  {list(df.columns)}")


if __name__ == '__main__':
    main()