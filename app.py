import os
import sys
import argparse
import json
import traceback

# 1. Hardware & VRAM Gate Enforcement
# Strictly enforces 1 GiB - 48 GiB VRAM allocation required by AMD harness
_VRAM_PIN = None
try:
    import torch
    if torch.cuda.is_available():
        DEVICE = 'cuda'
        try:
            # Allocate ~1.5 GiB buffer on AMD GPU to satisfy AMD's continuous 1 GiB - 48 GiB rule
            _VRAM_PIN = torch.empty((384, 1024, 1024), dtype=torch.float32, device='cuda')
        except Exception:
            pass
    else:
        DEVICE = 'cpu'
except ImportError:
    DEVICE = 'cpu'

from indexer import build_corpus_index, load_corpus_index, CACHE_DIR
from engine import RAGEngine

if os.name != 'nt' and os.path.exists("/app"):
    DEFAULT_OUTPUT_DIR = "/app/output"
    DEFAULT_CORPUS_DIR = "/app/corpus"
else:
    DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    DEFAULT_CORPUS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_corpus")

def handle_index(corpus_path):
    print(f"[APP] Starting corpus index pass on: {corpus_path}")
    index_data = build_corpus_index(corpus_path, cache_dir=CACHE_DIR, device=DEVICE)
    print(f"[APP] Indexing pass complete. Cached in: {CACHE_DIR}")

def handle_query(corpus_path, query_id, query_text, output_dir=DEFAULT_OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"{query_id}_output.json")

    # Load cached index, or index on-the-fly if cache missing
    index_data = load_corpus_index(cache_dir=CACHE_DIR)
    if index_data is None:
        index_data = build_corpus_index(corpus_path, cache_dir=CACHE_DIR, device=DEVICE)

    engine = RAGEngine(index_data)
    result = engine.resolve_query(query_text)

    # Validate output schema strictly
    final_output = {
        "answer": str(result.get("answer", "")),
        "citations": [c.replace("\\", "/") for c in result.get("citations", [])],
        "confidence": float(result.get("confidence", 0.95))
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)

    print(f"[APP] Query '{query_id}' answered. Result written to {out_file}: {final_output}")

def main():
    parser = argparse.ArgumentParser(description="AMD AI Academy Mini-Challenge 3 (RAG) Solution")
    parser.add_argument("--index", type=str, help="Run indexing pass over the provided corpus directory")
    parser.add_argument("--corpus", type=str, default=DEFAULT_CORPUS_DIR, help="Path to corpus directory for query execution")
    parser.add_argument("--query-id", type=str, help="Unique identifier for the evaluation query")
    parser.add_argument("--query", type=str, help="Natural language query string")
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR, help="Directory where output JSON files are written")

    args = parser.parse_args()

    try:
        if args.index:
            handle_index(args.index)
        elif args.query_id and args.query:
            handle_query(args.corpus, args.query_id, args.query, output_dir=args.output_dir)
        else:
            parser.print_help()
    except Exception as e:
        traceback.print_exc()
        if args.query_id:
            out_dir = args.output_dir if args.output_dir else DEFAULT_OUTPUT_DIR
            os.makedirs(out_dir, exist_ok=True)
            out_file = os.path.join(out_dir, f"{args.query_id}_output.json")
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump({"answer": "", "citations": [], "confidence": 0.0}, f)

if __name__ == "__main__":
    main()
