import os
import sys
import json
import shutil
import csv

# Add current dir to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from indexer import build_corpus_index
from engine import RAGEngine

SAMPLE_QUESTIONS = [
    {
        "id": "query_01",
        "question": "What is the maximum junction temperature of the TQ-40?",
        "expected_answer": "94",
        "expected_citations": ["specs/tq40_datasheet_r2.pdf"]
    },
    {
        "id": "query_02",
        "question": "In which quarter does the TQ-60 enter customer sampling?",
        "expected_answer": "Q3 FY27",
        "expected_citations": ["planning/roadmap_fy27.docx"]
    },
    {
        "id": "query_03",
        "question": "What is the part number of the field-replaceable fan assembly for the TQ-40?",
        "expected_answer": "ORR-FAN-2214-B",
        "expected_citations": ["support/rma_parts.xlsx"]
    },
    {
        "id": "query_04",
        "question": "Which firmware version fixed ticket ORR-1847?",
        "expected_answer": "4.3.2",
        "expected_citations": ["support/bug_database.csv"]
    },
    {
        "id": "query_05",
        "question": "What error code is logged when the thermal throttle engages?",
        "expected_answer": "E7731",
        "expected_citations": ["logs/prod_inference_2026-09-02.log"]
    },
    {
        "id": "query_06",
        "question": "What is the default batch timeout, in seconds, in the ingest service?",
        "expected_answer": "180",
        "expected_citations": ["engineering/ingest_service.py"]
    },
    {
        "id": "query_07",
        "question": "Which backplane pin carries THERM_ALERT# on the TQ-40?",
        "expected_answer": "B14",
        "expected_citations": ["specs/backplane_pinout.png"]
    },
    {
        "id": "query_08",
        "question": "What board revision is printed on the asset label?",
        "expected_answer": "REV-C2",
        "expected_citations": ["support/asset_label.jpg"]
    },
    {
        "id": "query_09",
        "question": "The production log shows a thermal throttle incident. Which firmware release fixed the underlying defect?",
        "expected_answer": "4.3.2",
        "expected_citations": ["logs/prod_inference_2026-09-02.log", "support/bug_database.csv"]
    },
    {
        "id": "query_10",
        "question": "What is the unit price of the TQ-40 at 10,000 unit volume?",
        "expected_answer": "",
        "expected_citations": []
    }
]

def normalize_answer(ans):
    if ans is None:
        return ""
    s = str(ans).upper()
    for ch in [" ", "-", ".", "_", "·", "°", "C", "DEG"]:
        s = s.replace(ch, "")
    return s.strip()

def run_local_evaluation():
    print("=" * 70)
    print("AMD AI ACADEMY - MINI-CHALLENGE 3 (RAG) VERIFICATION HARNESS")
    print("=" * 70)

    corpus_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_corpus")
    cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_cache")
    
    # 1. Indexing Pass
    print("\n[STEP 1] Running Indexing Pass on sample corpus...")
    index_data = build_corpus_index(corpus_dir, cache_dir=cache_dir, device='cpu')
    print(f"Indexed {len(index_data['chunks'])} chunks across {len(index_data['files'])} files.")

    # 2. Evaluation Pass
    print("\n[STEP 2] Running Query Answering & Exact Citation Verification...")
    engine = RAGEngine(index_data)

    total_score = 0
    max_score = len(SAMPLE_QUESTIONS) * 20

    for idx, item in enumerate(SAMPLE_QUESTIONS, 1):
        q_id = item["id"]
        q_text = item["question"]
        expected_ans = item["expected_answer"]
        expected_cites = sorted([c.replace("\\", "/") for c in item["expected_citations"]])

        result = engine.resolve_query(q_text)
        got_ans = result.get("answer", "")
        got_cites = sorted([c.replace("\\", "/") for c in result.get("citations", [])])

        norm_expected = normalize_answer(expected_ans)
        norm_got = normalize_answer(got_ans)

        ans_match = (norm_expected == norm_got)
        cites_match = (expected_cites == got_cites)

        passed = ans_match and cites_match
        pts = 20 if passed else 0
        total_score += pts

        status_str = "PASS (+20 pts)" if passed else "FAIL (0 pts)"
        print(f"\nQuestion {idx} [{q_id}]: {status_str}")
        print(f"  Query:      {q_text}")
        print(f"  Answer:     Expected: '{expected_ans}' | Got: '{got_ans}' [Match: {ans_match}]")
        print(f"  Citations:  Expected: {expected_cites} | Got: {got_cites} [Match: {cites_match}]")

    print("\n" + "=" * 70)
    print(f"FINAL SCORE: {total_score} / {max_score} POINTS ({'PERFECT 100%' if total_score == max_score else 'ACTION REQUIRED'})")
    print("=" * 70)

if __name__ == "__main__":
    run_local_evaluation()
