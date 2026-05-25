"""
ETL Pipeline Entry-Point
========================
Run from the backend/ directory:

    python run_etl.py           # use cached CSV files (or generate if missing)
    python run_etl.py --force   # regenerate CSV dataset files before loading
"""

from etl.pipeline import run_pipeline
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Library Management System – ETL Pipeline')
    parser.add_argument(
        '--force', action='store_true',
        help='Force regeneration of CSV dataset files before loading'
    )
    args = parser.parse_args()
    run_pipeline(force_generate=args.force)
