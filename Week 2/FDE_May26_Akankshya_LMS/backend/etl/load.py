"""
ETL Load Phase
Inserts cleaned DataFrames into the SQLite database.

Strategy:
  1. Truncate all three tables (transactions first to respect FK constraints).
  2. Bulk-insert books, then borrowers, then transactions.
  3. Update book availability_status based on active (unreturned) transactions.
"""

import sys
import os

# Ensure the backend/ directory is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal
import models


# ─────────────────────────────────────────────────────────────
def _clear_tables(db: Session):
    db.query(models.Transaction).delete()
    db.query(models.Borrower).delete()
    db.query(models.Book).delete()
    db.commit()
    print("  [Load] Cleared existing data from all tables")


def _load_books(db: Session, df: pd.DataFrame) -> int:
    for _, row in df.iterrows():
        book = models.Book(
            book_id=int(row['book_id']),
            title=str(row['title']),
            author=str(row['author']),
            category=str(row['category']),
            isbn=str(row['isbn']),
            availability_status='available',   # will be corrected after transactions
        )
        db.add(book)
    db.commit()
    print(f"  [Load] books        : {len(df)} inserted")
    return len(df)


def _load_borrowers(db: Session, df: pd.DataFrame) -> int:
    for _, row in df.iterrows():
        borrower = models.Borrower(
            borrower_id=int(row['borrower_id']),
            borrower_name=str(row['borrower_name']),
            email=str(row['email']),
            phone=str(row['phone']),
        )
        db.add(borrower)
    db.commit()
    print(f"  [Load] borrowers    : {len(df)} inserted")
    return len(df)


def _load_transactions(db: Session, df: pd.DataFrame) -> int:
    active_book_ids: set = set()

    for _, row in df.iterrows():
        # Handle NaT → None for return_date
        ret = row['return_date']
        return_date = None if pd.isnull(ret) else ret.to_pydatetime()

        borrow_date = row['borrow_date'].to_pydatetime()

        txn = models.Transaction(
            transaction_id=int(row['transaction_id']),
            book_id=int(row['book_id']),
            borrower_id=int(row['borrower_id']),
            borrow_date=borrow_date,
            return_date=return_date,
        )
        db.add(txn)

        if return_date is None:
            active_book_ids.add(int(row['book_id']))

    db.commit()

    # Update availability for currently-borrowed books
    for bid in active_book_ids:
        book = db.query(models.Book).filter(models.Book.book_id == bid).first()
        if book:
            book.availability_status = 'borrowed'
    db.commit()

    print(f"  [Load] transactions : {len(df)} inserted  "
          f"({len(active_book_ids)} books marked 'borrowed')")
    return len(df)


# ─────────────────────────────────────────────────────────────
def load_all(
    books_df: pd.DataFrame,
    borrowers_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
) -> dict:
    db: Session = SessionLocal()
    try:
        _clear_tables(db)
        books_n       = _load_books(db, books_df)
        borrowers_n   = _load_borrowers(db, borrowers_df)
        transactions_n = _load_transactions(db, transactions_df)
        return {
            'books': books_n,
            'borrowers': borrowers_n,
            'transactions': transactions_n,
        }
    finally:
        db.close()
