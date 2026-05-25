"""
ETL Transform Phase
Cleans and validates data before loading into the database.

Transformations applied:
  Books      – drop nulls on key fields, deduplicate ISBN, standardise status
  Borrowers  – drop nulls, deduplicate email, lowercase email, fill phone
  Transactions – deduplicate, validate FK refs, parse dates, drop bad rows
"""

import pandas as pd
from datetime import datetime


# ─────────────────────────────────────────────────────────────
def transform_books(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Drop rows with missing essential fields
    df = df.dropna(subset=['title', 'author', 'category', 'isbn', 'book_id'])

    # Drop duplicate ISBNs (keep first)
    df = df.drop_duplicates(subset=['isbn'], keep='first')

    # Drop duplicate book_ids
    df = df.drop_duplicates(subset=['book_id'], keep='first')

    # Strip whitespace
    for col in ['title', 'author', 'category', 'isbn']:
        df[col] = df[col].astype(str).str.strip()

    # Standardise category casing
    df['category'] = df['category'].str.title()

    # Standardise availability_status
    df['availability_status'] = df['availability_status'].fillna('available')
    valid = ['available', 'borrowed']
    df['availability_status'] = df['availability_status'].apply(
        lambda x: x if x in valid else 'available'
    )

    after = len(df)
    print(f"  [Transform] books        : {before} → {after} rows (removed {before - after})")
    return df.reset_index(drop=True)


# ─────────────────────────────────────────────────────────────
def transform_borrowers(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Drop missing essential fields
    df = df.dropna(subset=['borrower_name', 'email', 'borrower_id'])

    # Deduplicate email (keep first)
    df['email'] = df['email'].astype(str).str.strip().str.lower()
    df = df.drop_duplicates(subset=['email'], keep='first')

    # Deduplicate borrower_id
    df = df.drop_duplicates(subset=['borrower_id'], keep='first')

    # Fill missing phone
    df['phone'] = df['phone'].fillna('000-0000').astype(str).str.strip()

    # Strip name whitespace
    df['borrower_name'] = df['borrower_name'].astype(str).str.strip()

    after = len(df)
    print(f"  [Transform] borrowers    : {before} → {after} rows (removed {before - after})")
    return df.reset_index(drop=True)


# ─────────────────────────────────────────────────────────────
def transform_transactions(
    df: pd.DataFrame,
    books_df: pd.DataFrame,
    borrowers_df: pd.DataFrame,
) -> pd.DataFrame:
    before = len(df)

    # Drop missing IDs
    df = df.dropna(subset=['transaction_id', 'book_id', 'borrower_id'])

    # Deduplicate transaction_id
    df = df.drop_duplicates(subset=['transaction_id'], keep='first')

    # Keep only rows with valid FK references
    valid_books    = set(books_df['book_id'].astype(int).tolist())
    valid_borrowers = set(borrowers_df['borrower_id'].astype(int).tolist())
    df = df[df['book_id'].astype(int).isin(valid_books)]
    df = df[df['borrower_id'].astype(int).isin(valid_borrowers)]

    # Parse borrow_date
    df['borrow_date'] = pd.to_datetime(df['borrow_date'], errors='coerce')
    df = df.dropna(subset=['borrow_date'])   # drop rows with unparseable borrow_date

    # Parse return_date (empty string → NaT)
    df['return_date'] = df['return_date'].replace('', pd.NA)
    df['return_date'] = pd.to_datetime(df['return_date'], errors='coerce')

    # Remove logically impossible rows (return before borrow)
    bad_mask = df['return_date'].notna() & (df['return_date'] < df['borrow_date'])
    df = df[~bad_mask]

    after = len(df)
    print(f"  [Transform] transactions : {before} → {after} rows (removed {before - after})")
    return df.reset_index(drop=True)
