"""
Exploration script — run this ONCE to understand what the scraper returns.
This is not part of the final pipeline. It's for learning.
"""

from google_play_scraper import reviews, Sort
import json

# Scrape just 3 reviews to see what the raw data looks like
result, continuation_token = reviews(
    'com.combanketh.mobilebanking',
    lang='en',
    country='et',
    sort=Sort.NEWEST,
    count=3
)

# Print the raw result — look at every field available
print("NUMBER OF REVIEWS RETURNED:", len(result))
print("\nFIRST REVIEW (RAW):")
print(json.dumps(result[0], indent=2, default=str))
# default=str handles datetime objects that can't be serialized to JSON

print("\nALL AVAILABLE KEYS:")
print(list(result[0].keys()))