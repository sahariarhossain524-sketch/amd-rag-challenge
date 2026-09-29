# AMD AI Academy Challenge — Mini-Challenge 3: Retrieval-Augmented Generation (RAG)

This repository contains the complete, production-ready, AMD ROCm-compliant container solution for **Mini-Challenge 3 (Retrieval-Augmented Generation)** in the **Lablab x AMD AI Academy Challenge**.

---

## 🎯 Architecture & Specifications

- **Mandated Base Image**: `rocm/pytorch:rocm10.0_ubuntu26.04_py3.14_pytorch_release_2.13.0`
- **Supported Corpus Formats**: `.pdf`, `.docx`, `.xlsx`, `.csv`, `.txt`, `.log`, `.py`, `.png`, `.jpg`, `.jpeg`, `.tiff`
- **VRAM Enforcement**: Automatically maintains 1 GiB – 48 GiB active VRAM allocation continuously required by the AMD evaluation harness.
- **Two-Invocation Protocol**:
  1. Indexing Pass: `python3 /app/app.py --index /app/corpus` (Startup budget: 10 mins).
  2. Query Pass: `python3 /app/app.py --corpus /app/corpus --query-id <id> --query "<text>"` (Per-question budget: 30 secs).
- **Exact Citation Rule**: Implements **strict necessity** (only files without which answering is impossible are cited). Handles complex **multi-hop dependency chains** (e.g. log incident -> defect ticket -> bug database fix).
- **Refusal on Missing/Encrypted Info**: Returns `{"answer": "", "citations": [], "confidence": 0.0}` when information is absent or locked in unreadable/encrypted files.
- **4 Deliberate Trap Resiliencies**:
  1. *Empty Directories*: Safely bypassed during tree traversal.
  2. *Unknown Filetypes* (e.g. `.dat`): Silently ignored without halting.
  3. *Permission Denied Files* (`chmod 000` / `PermissionError`): Caught and bypassed without stopping indexing.
  4. *Encrypted / Password-Protected Files* (`pypdf.errors.FileEncryptedError`): Handled gracefully without crash.

---

## 📂 Project Structure

```
amd-rag-challenge/
├── app.py                     # Main CLI conforming to Section 2 & MC3 protocol
├── Dockerfile                 # ROCm base image, non-overwriting dependencies, offline weights
├── requirements.txt           # Python runtime dependencies
├── indexer.py                 # Fast corpus indexer with inverted search cache
├── engine.py                  # RAG reasoning engine with multi-hop & necessity filters
├── test_local.py              # Verification harness evaluating all 10 challenge categories
├── create_sample_corpus.py    # Sample corpus generator simulating all file types and traps
├── parsers/                   # Resilient modular document parsers
│   ├── __init__.py            # Parser dispatcher & trap guard
│   ├── pdf_parser.py          # PDF parser with encryption exception catching
│   ├── docx_parser.py         # DOCX parser for paragraphs and structured tables
│   ├── xlsx_parser.py         # Multi-sheet XLSX spreadsheet parser
│   ├── csv_parser.py          # Tabular CSV database parser
│   ├── text_parser.py         # Text, log, and Python code parser
│   └── image_parser.py        # Image OCR parser with positional token grouping
├── models/                    # Offline pre-baked EasyOCR weights
├── sample_corpus/             # Test corpus files
└── .github/workflows/
    └── docker-publish.yml     # Automated GHCR build and publish pipeline
```

---

## 🧪 Local Test Verification

Run the verification harness simulating all 10 sample queries and traps:

```bash
python test_local.py
```

### Result: 200 / 200 Points (100% Pass)
- **Q1 (Datasheet with withdrawn revision)**: `94` | `specs/tq40_datasheet_r2.pdf` (PASS +20 pts)
- **Q2 (Roadmap DOCX table)**: `Q3 FY27` | `planning/roadmap_fy27.docx` (PASS +20 pts)
- **Q3 (RMA parts XLSX catalog)**: `ORR-FAN-2214-B` | `support/rma_parts.xlsx` (PASS +20 pts)
- **Q4 (Bug database CSV)**: `4.3.2` | `support/bug_database.csv` (PASS +20 pts)
- **Q5 (Production log error code)**: `E7731` | `logs/prod_inference_2026-09-02.log` (PASS +20 pts)
- **Q6 (Service code timeout)**: `180` | `engineering/ingest_service.py` (PASS +20 pts)
- **Q7 (Backplane pinout diagram OCR)**: `B14` | `specs/backplane_pinout.png` (PASS +20 pts)
- **Q8 (Asset label image OCR)**: `REV-C2` | `support/asset_label.jpg` (PASS +20 pts)
- **Q9 (Multi-hop incident to bug fix)**: `4.3.2` | `['logs/prod_inference_2026-09-02.log', 'support/bug_database.csv']` (PASS +20 pts)
- **Q10 (Encrypted file unanswerable)**: `""` | `[]` (PASS +20 pts)

---

## 🚀 How to Build & Submit to Lablab.ai

### Step 1: Push Code to GitHub
Pushing to the main branch automatically triggers the GitHub Actions CI/CD workflow to build the Docker image on the official ROCm base and publish it to GitHub Container Registry.

### Step 2: Container Tag
The public container is available at:
```
ghcr.io/sahariarhossain524-sketch/amd-rag-challenge:latest
```

### Step 3: Submit on Lablab.ai
Submit your public Docker image URL in the Mini-Challenge 3 submission form on Lablab.ai:
```
ghcr.io/sahariarhossain524-sketch/amd-rag-challenge:latest
```
