# Q1: parse customers-100000.csv and get some insights
# file is small (~17MB) so just load everything with pandas

import pandas as pd

df = pd.read_csv("../data/customers-100000.csv")

print("rows:", len(df))
print("columns:", list(df.columns))
print()

# check data quality
print("null values per column:")
print(df.isnull().sum())
print()
print("duplicate rows:", df.duplicated().sum())
print("duplicate customer id:", df["Customer Id"].duplicated().sum())
print()

# which country has the most customers
print("top 10 countries:")
print(df["Country"].value_counts().head(10))
print()

# which company has the most customers
print("top 10 companies:")
print(df["Company"].value_counts().head(10))
print()

# subscription trend per year
df["Subscription Date"] = pd.to_datetime(df["Subscription Date"])
print("subscriptions per year:")
print(df["Subscription Date"].dt.year.value_counts().sort_index())
print()
print("first subscription:", df["Subscription Date"].min().date())
print("last subscription :", df["Subscription Date"].max().date())
print()

# email domain
df["domain"] = df["Email"].str.split("@").str[1]
print("top 10 email domains:")
print(df["domain"].value_counts().head(10))
