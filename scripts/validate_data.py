
import pandas as pd
import sys


def validate(path: str) -> bool:
    """
    Runs all validation checks.
    Returns True if all pass, False if any fail.
    """
    df = pd.read_csv(path)
    passed = True

    print("RUNNING VALIDATION CHECKS\n")

    # Check 1: Minimum total reviews
    total = len(df)
    check = total >= 1200
    print(f"{'✓' if check else '✗'} Total reviews >= 1200: {total}")
    passed = passed and check

    # Check 2: Minimum per bank
    counts = df['bank'].value_counts()
    for bank, count in counts.items():
        check = count >= 400
        print(f"{'✓' if check else '✗'} {bank} >= 400 reviews: {count}")
        passed = passed and check

    # Check 3: Required columns exist
    required = ['review', 'rating', 'date', 'bank', 'source']
    actual = list(df.columns)
    check = required == actual
    print(f"{'✓' if check else '✗'} Required columns present: {actual}")
    passed = passed and check

    # Check 4: Missing data < 5%
    missing_pct = (df.isnull().sum().sum() / df.size) * 100
    check = missing_pct < 5.0
    print(f"{'✓' if check else '✗'} Missing data < 5%: {missing_pct:.2f}%")
    passed = passed and check

    # Check 5: Date format is YYYY-MM-DD
    try:
        pd.to_datetime(df['date'], format='%Y-%m-%d')
        print(f"✓ Date format is YYYY-MM-DD")
    except Exception:
        print(f"✗ Date format is NOT YYYY-MM-DD")
        passed = False

    # Check 6: Ratings are 1-5
    valid_ratings = df['rating'].between(1, 5).all()
    check = valid_ratings
    print(f"{'✓' if check else '✗'} All ratings between 1 and 5")
    passed = passed and check

    # Check 7: Source column is always 'Google Play'
    check = (df['source'] == 'Google Play').all()
    print(f"{'✓' if check else '✗'} Source column is always 'Google Play'")
    passed = passed and check

    print(f"\n{'ALL CHECKS PASSED' if passed else 'SOME CHECKS FAILED'}")
    return passed


if __name__ == '__main__':
    success = validate('data/raw/reviews_clean.csv')
    sys.exit(0 if success else 1)