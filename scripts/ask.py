#!/usr/bin/env python3
"""
Nyay.AI — RAG CLI

Ask a legal question and get a grounded, cited answer from the index via
hybrid retrieval → cross-encoder rerank → Groq generation.

Requires GROQ_API_KEY in .env (see .env.example).

Usage:
    python scripts/ask.py "Can my landlord evict me without notice?"
    python scripts/ask.py "How do I file a consumer complaint?" --top 6
    python scripts/ask.py --interactive
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.config import RERANK_TOP_N
from rag.models import RAGResponse
from rag.pipeline import RAGPipeline


def print_response(resp: RAGResponse):
    print("\n" + "=" * 70)
    print(f"Q: {resp.question}")
    print("=" * 70)
    print(f"\n{resp.answer}\n")
    print(f"Confidence: {resp.confidence}  |  {resp.latency_ms} ms")
    if resp.citations:
        print("\nSources cited:")
        for c in resp.citations:
            print(f"  [{c.n}] {c.title}  ({c.source} / {c.doc_type})")
    print()


def interactive(pipeline: RAGPipeline, top_n: int):
    print("\nNyay.AI interactive mode (type 'quit' to exit)\n")
    while True:
        try:
            q = input("Ask > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if not q or q.lower() == "quit":
            break
        print_response(pipeline.ask(q, top_n=top_n))


def main():
    parser = argparse.ArgumentParser(description="Nyay.AI — RAG CLI")
    parser.add_argument("question", nargs="?", help="Legal question to answer")
    parser.add_argument("--top", type=int, default=RERANK_TOP_N, help="Chunks fed to the LLM")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    if not args.question and not args.interactive:
        parser.print_help()
        return

    pipeline = RAGPipeline()  # loads models once

    if args.interactive:
        interactive(pipeline, args.top)
    else:
        print_response(pipeline.ask(args.question, top_n=args.top))


if __name__ == "__main__":
    main()
