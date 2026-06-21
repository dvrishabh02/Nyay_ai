"""
Nyay.AI — Data Ingestion Pipeline

Converts raw legal data (parquets, text files) into a searchable
FAISS + BM25 index. Runs offline, no LLM or API keys needed.

Usage:
    python scripts/build_index.py --all
"""
