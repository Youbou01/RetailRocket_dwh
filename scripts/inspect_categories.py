
from pathlib import Path

import pandas as pd

data_dir = Path(__file__).resolve().parent.parent / "data"

# Read only category-related product properties
parts = []

for filename in [
    data_dir / "item_properties_part1.csv",
    data_dir / "item_properties_part2.csv",
]:
    df = pd.read_csv(filename)
    category_rows = df[df["property"].astype(str) == "categoryid"]
    parts.append(category_rows)

categories = pd.concat(parts, ignore_index=True)

print("Category property records:", len(categories))
print("Products with category information:", categories["itemid"].nunique())
print("Distinct category values:", categories["value"].nunique())
print("\nMost common category values:")
print(categories["value"].value_counts().head(10))

tree = pd.read_csv(data_dir / "category_tree.csv")

print("\nCategory tree rows:", len(tree))
print("Unique categories:", tree["categoryid"].nunique())
print("Categories without a parent:", tree["parentid"].isna().sum())
print("Distinct parent categories:", tree["parentid"].nunique())
