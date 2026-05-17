
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv('data/raw/reviews_clean.csv')

banks = df['bank'].unique()

for bank in banks:
    bank_reviews = df[df['bank'] == bank]['review'].tolist()
    
    print(f"\n{'='*60}")
    print(f"TOP KEYWORDS: {bank}")
    print(f"Total reviews: {len(bank_reviews)}")
    print('='*60)

    # All reviews for this bank
    vectorizer = TfidfVectorizer(
        max_features=30,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=3
    )

    matrix = vectorizer.fit_transform(bank_reviews)
    feature_names = vectorizer.get_feature_names_out()

    import numpy as np
    scores = matrix.sum(axis=0).A1
    word_scores = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)

    print("\nALL REVIEWS - Top 20 keywords:")
    for word, score in word_scores[:20]:
        print(f"  {word:<30} {score:.3f}")

    # Negative reviews only
    negative = df[(df['bank'] == bank) & (df['rating'] <= 2)]['review'].tolist()
    if len(negative) >= 3:
        vec_neg = TfidfVectorizer(
            max_features=20, stop_words='english',
            ngram_range=(1, 2), min_df=2
        )
        mat_neg = vec_neg.fit_transform(negative)
        names_neg = vec_neg.get_feature_names_out()
        scores_neg = mat_neg.sum(axis=0).A1
        neg_words = sorted(zip(names_neg, scores_neg), key=lambda x: x[1], reverse=True)

        print(f"\nNEGATIVE REVIEWS ONLY ({len(negative)} reviews) - Top 15 keywords:")
        for word, score in neg_words[:15]:
            print(f"  {word:<30} {score:.3f}")

    # Positive reviews only
    positive = df[(df['bank'] == bank) & (df['rating'] >= 4)]['review'].tolist()
    if len(positive) >= 3:
        vec_pos = TfidfVectorizer(
            max_features=20, stop_words='english',
            ngram_range=(1, 2), min_df=2
        )
        mat_pos = vec_pos.fit_transform(positive)
        names_pos = vec_pos.get_feature_names_out()
        scores_pos = mat_pos.sum(axis=0).A1
        pos_words = sorted(zip(names_pos, scores_pos), key=lambda x: x[1], reverse=True)

        print(f"\nPOSITIVE REVIEWS ONLY ({len(positive)} reviews) - Top 15 keywords:")
        for word, score in pos_words[:15]:
            print(f"  {word:<30} {score:.3f}")