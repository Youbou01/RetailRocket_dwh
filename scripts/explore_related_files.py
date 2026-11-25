
from pathlib import Path

import pandas as pd

data_dir = Path(__file__).resolve().parent.parent / "data"

files = [
    data_dir / "item_properties_part1.csv",
    data_dir / "item_properties_part2.csv",
    data_dir / "category_tree.csv",
]

for filename in files:

    print("\n" + "=" * 60)
    print("FILE:", filename)
    print("=" * 60)

    # Read only the first five records
    sample = pd.read_csv(filename, nrows=5)

    print("\nColumns:")
    print(sample.columns.tolist())

    print("\nData types:")
    print(sample.dtypes)

    print("\nFirst five rows:")
    print(sample.to_string(index=False))

    # Count all records without loading the entire file
    total_rows = 0

    for chunk in pd.read_csv(filename, chunksize=500000):
        total_rows += len(chunk)

    print("\nTotal records:", total_rows)
