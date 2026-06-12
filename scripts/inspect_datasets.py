"""Quick inspection of downloaded datasets."""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

# 1. SC Judgements (Chunked)
print("=" * 60)
print("1. SC JUDGEMENTS (CHUNKED) - Ready for RAG")
print("=" * 60)
p = DATA_DIR / "judgments" / "supreme_court" / "hf_chunked" / "train.parquet"
if p.exists():
    df = pd.read_parquet(p)
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(df.head(2).to_string(max_colwidth=100))
print()

# 2. Indian Legal Acts (Central)
print("=" * 60)
print("2. INDIAN LEGAL ACTS (CENTRAL)")
print("=" * 60)
p = DATA_DIR / "legislation" / "hf_acts" / "central.parquet"
if p.exists():
    df = pd.read_parquet(p)
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(df.head(2).to_string(max_colwidth=100))
print()

# 3. Legal Chunks (RAG-ready)
print("=" * 60)
print("3. LEGAL CHUNKS (RAG-ready)")
print("=" * 60)
p = DATA_DIR / "judgments" / "hf_legal_chunks" / "train.parquet"
if p.exists():
    df = pd.read_parquet(p)
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(df.head(2).to_string(max_colwidth=100))
print()

# 4. MyScheme Govt Schemes
print("=" * 60)
print("4. MYSCHEME GOVT SCHEMES")
print("=" * 60)
p = DATA_DIR / "schemes" / "hf_myscheme" / "train.parquet"
if p.exists():
    df = pd.read_parquet(p)
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(df.head(2).to_string(max_colwidth=100))
print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
total = 0
for name, path in [
    ("SC Judgements Chunked", DATA_DIR / "judgments" / "supreme_court" / "hf_chunked" / "train.parquet"),
    ("Legal Acts (Central)", DATA_DIR / "legislation" / "hf_acts" / "central.parquet"),
    ("Legal Chunks", DATA_DIR / "judgments" / "hf_legal_chunks" / "train.parquet"),
    ("Govt Schemes", DATA_DIR / "schemes" / "hf_myscheme" / "train.parquet"),
]:
    if path.exists():
        count = len(pd.read_parquet(path))
        total += count
        print(f"  {name}: {count:,} rows")
print(f"\n  TOTAL: {total:,} rows ready for processing")
