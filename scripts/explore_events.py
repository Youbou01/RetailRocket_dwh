
from pathlib import Path

import pandas as pd

# 1. Load the original dataset
events_file = Path(__file__).resolve().parent.parent / "data" / "events.csv"
df = pd.read_csv(events_file)

# 2. General information
print("\n========== GENERAL INFORMATION ==========")

print("Number of rows:", len(df))
print("Number of columns:", len(df.columns))

print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

# 3. Missing values
print("\n========== MISSING VALUES ==========")

print(df.isnull().sum())

# 4. Duplicate records
print("\n========== DUPLICATES ==========")

print("Exact duplicate rows:", df.duplicated().sum())

# 5. Event distribution
print("\n========== EVENT DISTRIBUTION ==========")

print(df["event"].value_counts(dropna=False))

# 6. Visitors and products
print("\n========== UNIQUE VALUES ==========")

print("Unique visitors:", df["visitorid"].nunique())
print("Unique products:", df["itemid"].nunique())
print("Unique transactions:", df["transactionid"].nunique())

# 7. Date range
print("\n========== DATE RANGE ==========")

dates = pd.to_datetime(
    df["timestamp"],
    unit="ms",
    utc=True
)

print("First event:", dates.min())
print("Last event:", dates.max())

# 8. Transaction ID validation
print("\n========== TRANSACTION VALIDATION ==========")

print(
    df.groupby("event")["transactionid"]
      .apply(lambda x: x.isnull().sum())
)

print("\nEvents with missing transaction IDs:")
print(df[df["transactionid"].isnull()]["event"].value_counts())

print("\nEvents with transaction IDs:")
print(df[df["transactionid"].notnull()]["event"].value_counts())
# Load only transaction-related records
transactions = df[df["event"] == "transaction"]

print("Transaction event rows:", len(transactions))

print(
    "Unique transaction IDs:",
    transactions["transactionid"].nunique()
)

print(
    "Transaction IDs appearing multiple times:",
    (transactions["transactionid"].value_counts() > 1).sum()
)

print("\nMost frequent transaction IDs:")
print(transactions["transactionid"].value_counts().head(10))