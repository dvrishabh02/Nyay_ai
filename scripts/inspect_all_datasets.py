"""Inspect all downloaded datasets — row counts, columns, sample data."""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

total_rows = 0
datasets = []

for parquet_file in sorted(DATA_DIR.rglob("*.parquet")):
    rel = parquet_file.relative_to(DATA_DIR)
    try:
        df = pd.read_parquet(parquet_file)
        rows = len(df)
        total_rows += rows
        size_mb = parquet_file.stat().st_size / (1024 * 1024)
        datasets.append((str(rel), rows, size_mb, list(df.columns)))
    except Exception as e:
        datasets.append((str(rel), 0, 0, [f"ERROR: {e}"]))

print("=" * 80)
print("NYAY.AI — ALL DOWNLOADED DATASETS")
print("=" * 80)
print()

for rel, rows, size_mb, cols in datasets:
    print(f"  {rel}")
    print(f"    Rows: {rows:,}  |  Size: {size_mb:.1f} MB  |  Columns: {cols}")
    print()

print("=" * 80)
print(f"TOTAL: {total_rows:,} rows across {len(datasets)} files")
print(f"TOTAL SIZE: {sum(d[2] for d in datasets):.1f} MB")
print("=" * 80)
