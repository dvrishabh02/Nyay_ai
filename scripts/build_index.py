#!/usr/bin/env python3
"""
Nyay.AI — Index Builder

Main entry point for the data ingestion pipeline.
Converts raw legal data into searchable FAISS + BM25 indices.

Usage:
    # Full build (parse → chunk → filter → enrich → embed → index)
    python scripts/build_index.py --all

    # Only specific sources
    python scripts/build_index.py --sources sc_chunked central_acts

    # List available sources
    python scripts/build_index.py --list

No LLM or API keys required. Runs fully offline.
"""

import argparse
import json
import pickle
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from loguru import logger

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.config import (
    INDEX_DIR,
    MANIFEST_FILE,
    METADATA_FILE,
    PARQUET_SOURCES,
    PROCESSED_DIR,
)
from ingestion.models import Chunk, ChunkMetadata
from ingestion.parsers import ParquetParser
from ingestion.chunkers import LegalChunker
from ingestion.quality import QualityFilter
from ingestion.enrichers import MetadataEnricher
from ingestion.embedders import E5Embedder
from ingestion.indexers import FaissBuilder, BM25Builder


def list_sources():
    """Print all available data sources."""
    print("\nAvailable data sources:")
    print("-" * 60)
    for key, src in PARQUET_SOURCES.items():
        exists = "✅" if src["path"].exists() else "❌"
        chunked = "pre-chunked" if src["pre_chunked"] else "needs chunking"
        print(f"  {exists} {key:<20} {chunked:<16} {src['description']}")
    print()


def parse_sources(source_keys: list[str]) -> list[dict]:
    """Step 1: Load raw documents from parquet files."""
    parser = ParquetParser()
    all_docs = []

    for key in source_keys:
        src = PARQUET_SOURCES[key]
        if not src["path"].exists():
            logger.warning(f"Skipping {key}: file not found at {src['path']}")
            continue

        docs = parser.parse(src["path"])
        # Tag each doc with source info
        for doc in docs:
            doc["source_key"] = key
            doc["doc_type"] = src["doc_type"]
            doc["court"] = src["court"]
            doc["pre_chunked"] = src["pre_chunked"]
        all_docs.extend(docs)

    logger.info(f"Total documents parsed: {len(all_docs)}")
    return all_docs


def chunk_documents(documents: list[dict]) -> list[Chunk]:
    """Step 2: Split documents into chunks (or wrap pre-chunked ones)."""
    chunker = LegalChunker()
    all_chunks = []

    for doc in documents:
        source = doc["source_key"]
        meta = ChunkMetadata(
            doc_type=doc["doc_type"],
            court=doc["court"],
            title=doc.get("title"),
            source=source,
        )

        if doc["pre_chunked"]:
            # Already a chunk — just wrap it
            chunk = chunker.wrap_pre_chunked(
                text=doc["text"],
                source=source,
                doc_idx=doc["row_idx"],
                metadata=meta,
            )
            all_chunks.append(chunk)
        else:
            # Needs splitting
            chunks = chunker.chunk_document(
                text=doc["text"],
                source=source,
                doc_idx=doc["row_idx"],
                metadata=meta,
            )
            all_chunks.extend(chunks)

    logger.info(f"Total chunks after splitting: {len(all_chunks)}")
    return all_chunks


def filter_chunks(chunks: list[Chunk]) -> list[Chunk]:
    """Step 3: Apply quality filters (length, dedup, empty)."""
    qf = QualityFilter()
    passed = qf.filter_chunks(chunks)
    qf.log_stats()
    return passed


def enrich_chunks(chunks: list[Chunk]) -> list[Chunk]:
    """Step 4: Add domain and jurisdiction metadata."""
    enricher = MetadataEnricher()
    return enricher.enrich(chunks)


def embed_chunks(chunks: list[Chunk]) -> np.ndarray:
    """Step 5: Generate embeddings using e5-base-v2."""
    embedder = E5Embedder()
    return embedder.embed_chunks(chunks)


def build_indices(chunks: list[Chunk], embeddings: np.ndarray):
    """Step 6: Build and save FAISS + BM25 indices + metadata."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # FAISS index
    faiss_builder = FaissBuilder()
    faiss_index = faiss_builder.build(embeddings)
    faiss_builder.save(faiss_index)

    # BM25 index
    bm25_builder = BM25Builder()
    bm25_index = bm25_builder.build(chunks)
    bm25_builder.save(bm25_index)

    # Metadata (chunk text + metadata for retrieval)
    metadata = [chunk.to_dict() for chunk in chunks]
    with open(METADATA_FILE, "wb") as f:
        pickle.dump(metadata, f)
    meta_size = METADATA_FILE.stat().st_size / (1024 * 1024)
    logger.info(f"Metadata saved: {METADATA_FILE} ({meta_size:.1f} MB)")

    # Save raw embeddings as backup
    embeddings_path = INDEX_DIR / "embeddings.npy"
    np.save(embeddings_path, embeddings)
    emb_size = embeddings_path.stat().st_size / (1024 * 1024)
    logger.info(f"Embeddings backup saved: {embeddings_path} ({emb_size:.1f} MB)")


def save_manifest(chunks: list[Chunk], source_keys: list[str], duration_secs: float):
    """Save build stats for tracking and debugging."""
    # Count chunks per source
    source_counts = {}
    for chunk in chunks:
        src = chunk.metadata.source
        source_counts[src] = source_counts.get(src, 0) + 1

    # Count chunks per domain
    domain_counts = {}
    for chunk in chunks:
        domain = chunk.metadata.domain
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    manifest = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round(duration_secs, 1),
        "total_chunks": len(chunks),
        "sources_processed": source_keys,
        "chunks_per_source": source_counts,
        "chunks_per_domain": domain_counts,
        "embedding_model": "intfloat/e5-base-v2",
        "embedding_dim": 768,
        "chunk_size_tokens": 700,
        "chunk_overlap_tokens": 105,
        "index_files": {
            "index.faiss": f"{(INDEX_DIR / 'index.faiss').stat().st_size / (1024*1024):.1f} MB",
            "bm25.pkl": f"{(INDEX_DIR / 'bm25.pkl').stat().st_size / (1024*1024):.1f} MB",
            "metadata.pkl": f"{(INDEX_DIR / 'metadata.pkl').stat().st_size / (1024*1024):.1f} MB",
        },
    }

    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Manifest saved: {MANIFEST_FILE}")


def save_processed_chunks(chunks: list[Chunk]):
    """Save intermediate chunks as JSON for debugging/inspection."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output = PROCESSED_DIR / "chunks.json"
    data = [chunk.to_dict() for chunk in chunks]
    with open(output, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Processed chunks saved: {output} ({len(data)} chunks)")


def run_pipeline(source_keys: list[str]):
    """Execute the full ingestion pipeline."""
    start = time.time()

    logger.info("=" * 60)
    logger.info("NYAY.AI — INDEX BUILD PIPELINE")
    logger.info(f"Sources: {source_keys}")
    logger.info("=" * 60)

    # Step 1: Parse
    logger.info("\n📂 Step 1/6: Parsing raw data...")
    documents = parse_sources(source_keys)
    if not documents:
        logger.error("No documents found. Aborting.")
        return

    # Step 2: Chunk
    logger.info("\n✂️  Step 2/6: Chunking documents...")
    chunks = chunk_documents(documents)

    # Step 3: Quality filter
    logger.info("\n🔍 Step 3/6: Applying quality filters...")
    chunks = filter_chunks(chunks)
    if not chunks:
        logger.error("All chunks filtered out. Aborting.")
        return

    # Step 4: Enrich metadata
    logger.info("\n🏷️  Step 4/6: Enriching metadata...")
    chunks = enrich_chunks(chunks)

    # Save intermediate chunks for inspection
    save_processed_chunks(chunks)

    # Step 5: Embed
    logger.info("\n🔢 Step 5/6: Generating embeddings (this takes a while)...")
    embeddings = embed_chunks(chunks)

    # Step 6: Build indices
    logger.info("\n📦 Step 6/6: Building FAISS + BM25 indices...")
    build_indices(chunks, embeddings)

    # Save manifest
    duration = time.time() - start
    save_manifest(chunks, source_keys, duration)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("BUILD COMPLETE")
    logger.info(f"  Chunks indexed: {len(chunks)}")
    logger.info(f"  Time taken: {duration/60:.1f} minutes")
    logger.info(f"  Index files: {INDEX_DIR}")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Nyay.AI Index Builder")
    parser.add_argument("--all", action="store_true", help="Process all available sources")
    parser.add_argument("--sources", nargs="+", help="Specific sources to process")
    parser.add_argument("--list", action="store_true", help="List available data sources")
    args = parser.parse_args()

    if args.list:
        list_sources()
        return

    if args.all:
        source_keys = [k for k, v in PARQUET_SOURCES.items() if v["path"].exists()]
    elif args.sources:
        # Validate source keys
        invalid = [s for s in args.sources if s not in PARQUET_SOURCES]
        if invalid:
            logger.error(f"Unknown sources: {invalid}. Use --list to see available sources.")
            return
        source_keys = args.sources
    else:
        parser.print_help()
        return

    run_pipeline(source_keys)


if __name__ == "__main__":
    main()
