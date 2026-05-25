"""
ETL Extract Phase
Reads CSV files into pandas DataFrames for downstream transformation.
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def extract_books() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, 'books.csv')
    df = pd.read_csv(path, dtype=str)
    df['book_id'] = pd.to_numeric(df['book_id'], errors='coerce')
    print(f"  [Extract] books        : {len(df)} rows")
    return df


def extract_borrowers() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, 'borrowers.csv')
    df = pd.read_csv(path, dtype=str)
    df['borrower_id'] = pd.to_numeric(df['borrower_id'], errors='coerce')
    print(f"  [Extract] borrowers    : {len(df)} rows")
    return df


def extract_transactions() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, 'transactions.csv')
    # Keep return_date as string first so empty strings don't break parsing
    df = pd.read_csv(path, dtype=str)
    df['transaction_id'] = pd.to_numeric(df['transaction_id'], errors='coerce')
    df['book_id']        = pd.to_numeric(df['book_id'],        errors='coerce')
    df['borrower_id']    = pd.to_numeric(df['borrower_id'],    errors='coerce')
    print(f"  [Extract] transactions : {len(df)} rows")
    return df
