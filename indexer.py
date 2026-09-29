import os
import json
import re
from collections import defaultdict
from parsers import parse_file

if os.name != 'nt' and os.path.exists("/app"):
    CACHE_DIR = "/app/index_cache"
else:
    CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index_cache")

INDEX_FILE = os.path.join(CACHE_DIR, "corpus_index.json")

def tokenize(text):
    """Tokenizes text into lowercase terms and preserved alphanumeric identifiers."""
    tokens = re.findall(r'[a-zA-Z0-9_\-\.\#]+', text)
    return [t.lower() for t in tokens if len(t) > 1]

def build_corpus_index(corpus_path, cache_dir=CACHE_DIR, device='cpu'):
    """
    Recursively scans and parses the entire corpus folder.
    Saves parsed chunks and an inverted term index into cache_dir.
    """
    os.makedirs(cache_dir, exist_ok=True)
    all_chunks = []
    file_metadata = {}
    inverted_index = defaultdict(list)

    # Walk directory tree
    for root, dirs, files in os.walk(corpus_path):
        for fname in sorted(files):
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, corpus_path).replace("\\", "/")

            # Record file metadata
            file_metadata[rel_path] = {
                "file_name": fname,
                "is_withdrawn": "withdrawn" in fname.lower() or "deprecated" in fname.lower()
            }

            chunks = parse_file(full_path, rel_path, device=device)
            if not chunks:
                continue

            for c in chunks:
                chunk_id = len(all_chunks)
                c["id"] = chunk_id
                all_chunks.append(c)

                tokens = set(tokenize(c.get("text", "")))
                for tok in tokens:
                    inverted_index[tok].append(chunk_id)

    index_data = {
        "corpus_path": corpus_path,
        "files": file_metadata,
        "chunks": all_chunks,
        "inverted_index": dict(inverted_index)
    }

    out_path = os.path.join(cache_dir, "corpus_index.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False)

    print(f"[INDEXER] Successfully indexed {len(all_chunks)} chunks from {len(file_metadata)} files.")
    return index_data

def load_corpus_index(cache_dir=CACHE_DIR):
    """Loads pre-built corpus index from cache."""
    out_path = os.path.join(cache_dir, "corpus_index.json")
    if not os.path.exists(out_path):
        return None
    with open(out_path, "r", encoding="utf-8") as f:
        return json.load(f)
