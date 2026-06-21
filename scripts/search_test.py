#!/usr/bin/env python3
"""
Nyay.AI — CLI Search Tester

Test retrieval quality after ingestion. No LLM or API keys needed.
Loads FAISS + BM25 indices and returns raw matched chunks.

Usage:
    # FAISS (dense/semantic) search
    python scripts/search_test.py "Can my landlord evict me?"

    # BM25 (keyword) search
    python scripts/search_test.py "Section 138 NI Act" --mode bm25

    # Hybrid (FAISS + BM25 combined via RRF)
    python scripts/search_test.py "tenant deposit refund" --mode hybrid

    # Show more results
    python scripts/search_test.py "bail conditions" --top 10

    # Interactive mode (keep querying without reloading)
    python scripts/search_test.py --interactive
"""

import argparse
import pickle
import sys
from pathlib import Path

import numpy as np
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.config import (
    BM25_INDEX_FILE,
    FAISS_INDEX_FILE,
    METADATA_FILE,
    EMBEDDING_MODEL,
    QUERY_PREFIX,
)
from ingestion.indexers import FaissBuilder, BM25Builder


def load_resources():
    """Load index files and embedding model. Done once."""
    logger.info("Loading FAISS index...")
    faiss_index = FaissBuilder.load()

    logger.info("Loading BM25 index...")
    bm25_index = BM25Builder.load()

    logger.info("Loading metadata...")
    with open(METADATA_FILE, "rb") as f:
        metadata = pickle.load(f)

    logger.info(f"Loading embedding model: {EMBEDDING_MODEL}...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBEDDING_MODEL)

    logger.info(f"Ready. {len(metadata)} chunks loaded.\n")
    return faiss_index, bm25_index, metadata, model


def search_faiss(query: str, model, faiss_index, metadata, top_k: int = 5):
    """Dense semantic search via FAISS."""
    embedding = model.encode([QUERY_PREFIX + query], normalize_embeddings=True)
    scores, indices = faiss_index.search(np.array(embedding, dtype=np.float32), top_k)
    return [(metadata[i], float(scores[0][rank])) for rank, i in enumerate(indices[0]) if i < len(metadata)]


def search_bm25(query: str, bm25_index, metadata, top_k: int = 5):
    """Sparse keyword search via BM25."""
    tokens = query.lower().split()
    scores = bm25_index.get_scores(tokens)
    top_indices = np.argsort(scores)[::-1][:top_k]
    return [(metadata[i], float(scores[i])) for i in top_indices if scores[i] > 0]


def search_hybrid(query: str, model, faiss_index, bm25_index, metadata, top_k: int = 5, k: int = 60):
    """Hybrid search combining FAISS + BM25 via Reciprocal Rank Fusion."""
    faiss_results = search_faiss(query, model, faiss_index, metadata, top_k=top_k * 2)
    bm25_results = search_bm25(query, bm25_index, metadata, top_k=top_k * 2)

    # RRF: score = sum(1 / (k + rank)) for each system
    rrf_scores: dict[str, float] = {}
    chunk_map: dict[str, dict] = {}

    for rank, (meta, _) in enumerate(faiss_results):
        cid = meta["chunk_id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0) + 1.0 / (k + rank + 1)
        chunk_map[cid] = meta

    for rank, (meta, _) in enumerate(bm25_results):
        cid = meta["chunk_id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0) + 1.0 / (k + rank + 1)
        chunk_map[cid] = meta

    sorted_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]
    return [(chunk_map[cid], rrf_scores[cid]) for cid in sorted_ids]


def print_results(results: list, mode: str):
    """Pretty-print search results."""
    if not results:
        print("  No results found.\n")
        return

    for i, (meta, score) in enumerate(results, 1):
        text_preview = meta["text"][:300].replace("\n", " ")
        print(f"  [{i}] Score: {score:.4f}")
        print(f"      Source: {meta.get('source', '?')} | Type: {meta.get('doc_type', '?')} | Domain: {meta.get('domain', '?')}")
        if meta.get("title"):
            print(f"      Title: {meta['title']}")
        print(f"      Text: {text_preview}...")
        print()


def interactive_mode(faiss_index, bm25_index, metadata, model, top_k: int):
    """Keep querying without reloading indices."""
    print("\n🔍 Interactive Search Mode (type 'quit' to exit)")
    print("   Prefix with 'bm25:' or 'hybrid:' to change mode (default: hybrid)\n")

    while True:
        try:
            query = input("Query > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not query or query.lower() == "quit":
            break

        # Detect mode from prefix
        if query.startswith("bm25:"):
            mode = "bm25"
            query = query[5:].strip()
        elif query.startswith("faiss:"):
            mode = "faiss"
            query = query[6:].strip()
        else:
            mode = "hybrid"
            query = query.replace("hybrid:", "").strip()

        if mode == "faiss":
            results = search_faiss(query, model, faiss_index, metadata, top_k)
        elif mode == "bm25":
            results = search_bm25(query, bm25_index, metadata, top_k)
        else:
            results = search_hybrid(query, model, faiss_index, bm25_index, metadata, top_k)

        print(f"\n--- {mode.upper()} results for: \"{query}\" ---\n")
        print_results(results, mode)


def main():
    parser = argparse.ArgumentParser(description="Nyay.AI — CLI Search Tester")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--mode", choices=["faiss", "bm25", "hybrid"], default="hybrid", help="Search mode")
    parser.add_argument("--top", type=int, default=5, help="Number of results")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    if not args.query and not args.interactive:
        parser.print_help()
        return

    # Load everything once
    faiss_index, bm25_index, metadata, model = load_resources()

    if args.interactive:
        interactive_mode(faiss_index, bm25_index, metadata, model, args.top)
        return

    # Single query
    if args.mode == "faiss":
        results = search_faiss(args.query, model, faiss_index, metadata, args.top)
    elif args.mode == "bm25":
        results = search_bm25(args.query, bm25_index, metadata, args.top)
    else:
        results = search_hybrid(args.query, model, faiss_index, bm25_index, metadata, args.top)

    print(f"\n--- {args.mode.upper()} results for: \"{args.query}\" ---\n")
    print_results(results, args.mode)


if __name__ == "__main__":
    main()
