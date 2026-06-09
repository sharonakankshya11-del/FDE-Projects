"""
scripts/run_ingest.py
CLI script to run the full data ingestion pipeline.
Usage: python scripts/run_ingest.py --csv1 data/ai4i2020.csv --csv2 data/predictive_maintenance.csv
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.data.ingest import run_ingestion


def main():
    parser = argparse.ArgumentParser(description="Ingest medical equipment data into ChromaDB")
    parser.add_argument("--csv1", required=True, help="Path to ai4i2020.csv")
    parser.add_argument("--csv2", required=True, help="Path to predictive_maintenance.csv")
    args = parser.parse_args()

    if not os.path.exists(args.csv1):
        print(f"ERROR: File not found: {args.csv1}")
        sys.exit(1)
    if not os.path.exists(args.csv2):
        print(f"ERROR: File not found: {args.csv2}")
        sys.exit(1)

    print(f"Starting ingestion...")
    print(f"  Dataset 1: {args.csv1}")
    print(f"  Dataset 2: {args.csv2}")

    total = run_ingestion(args.csv1, args.csv2)
    print(f"\n✓ Ingestion complete. {total} vectors in ChromaDB.")


if __name__ == "__main__":
    main()
