# Q2: parse customers-2000000.csv (~350MB) with low memory
#
# idea: don't load the whole file. read it chunk by chunk,
# count what we need, then throw the chunk away.
# memory only holds 1 chunk (+ the counters) at a time.

import pandas as pd
from collections import Counter

FILE = "../data/customers-2000000.csv"
CHUNK_SIZE = 100_000   # rows per chunk

total_rows = 0
country_count = Counter()
company_count = Counter()
year_count = Counter()

# only read the columns we need -> less memory
reader = pd.read_csv(FILE, chunksize=CHUNK_SIZE,
                     usecols=["Company", "Country", "Subscription Date"])

for chunk in reader:
    total_rows += len(chunk)

    # add this chunk's counts to the running total
    country_count.update(chunk["Country"].value_counts().to_dict())
    company_count.update(chunk["Company"].value_counts().to_dict())

    years = chunk["Subscription Date"].str[:4]   # "2021-05-14" -> "2021"
    year_count.update(years.value_counts().to_dict())

    print("processed", total_rows, "rows")

print()
print("total rows:", total_rows)
print()
print("top 10 countries:")
for country, n in country_count.most_common(10):
    print(" ", country, n)
print()
print("top 10 companies:")
for company, n in company_count.most_common(10):
    print(" ", company, n)
print()
print("subscriptions per year:")
for year in sorted(year_count):
    print(" ", year, year_count[year])
