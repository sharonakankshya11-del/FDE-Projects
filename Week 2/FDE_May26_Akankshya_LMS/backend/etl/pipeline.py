"""
ETL Pipeline Orchestrator — Library Management System Phase 2

Run from the backend/ directory:
    python run_etl.py
        OR
    python -m etl.pipeline

Flow:
    1. Generate CSV dataset files (if missing)
    2. Extract  → read CSVs into DataFrames
    3. Transform→ clean, validate, deduplicate
    4. Load     → insert into SQLite, fix availability flags
    5. Persist ETL log → data/etl_log.json
"""

import sys
import os
import json
from datetime import datetime

# Ensure backend/ directory is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.generate_dataset import generate_all
from etl.extract          import extract_books, extract_borrowers, extract_transactions
from etl.transform        import transform_books, transform_borrowers, transform_transactions
from etl.load             import load_all

DATA_DIR    = os.path.join(os.path.dirname(__file__), '..', 'data')
ETL_LOG     = os.path.join(DATA_DIR, 'etl_log.json')


def run_pipeline(force_generate: bool = False) -> dict:
    start = datetime.utcnow()
    divider = '=' * 55
    print(f"\n{divider}")
    print(f"  LMS ETL Pipeline  |  {start.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(divider)

    # ── Step 1: Generate dataset ──────────────────────────
    print("\n[Step 1] Dataset generation")
    generate_all(force=force_generate)

    # ── Step 2: Extract ───────────────────────────────────
    print("\n[Step 2] Extract")
    books_raw       = extract_books()
    borrowers_raw   = extract_borrowers()
    transactions_raw = extract_transactions()

    # ── Step 3: Transform ─────────────────────────────────
    print("\n[Step 3] Transform")
    books_clean       = transform_books(books_raw)
    borrowers_clean   = transform_borrowers(borrowers_raw)
    transactions_clean = transform_transactions(
        transactions_raw, books_clean, borrowers_clean
    )

    # ── Step 4: Load ──────────────────────────────────────
    print("\n[Step 4] Load")
    counts = load_all(books_clean, borrowers_clean, transactions_clean)

    # ── Summary ───────────────────────────────────────────
    end      = datetime.utcnow()
    duration = round((end - start).total_seconds(), 2)

    print(f"\n{divider}")
    print(f"  ETL Complete  |  {duration}s")
    print(f"  Books:        {counts['books']}")
    print(f"  Borrowers:    {counts['borrowers']}")
    print(f"  Transactions: {counts['transactions']}")
    print(divider + "\n")

    log = {
        'last_run':            end.isoformat(),
        'duration_seconds':    duration,
        'books_loaded':        counts['books'],
        'borrowers_loaded':    counts['borrowers'],
        'transactions_loaded': counts['transactions'],
        'status':              'success',
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ETL_LOG, 'w') as f:
        json.dump(log, f, indent=2)

    return log


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run the LMS ETL pipeline')
    parser.add_argument('--force', action='store_true',
                        help='Force regeneration of CSV dataset files')
    args = parser.parse_args()
    run_pipeline(force_generate=args.force)
