"""
Analytics Router — Phase 2
Provides ETL-powered analytics endpoints for the Library Management System.

Endpoints:
  GET /analytics/summary          – high-level KPIs
  GET /analytics/most-borrowed    – top N most-borrowed books
  GET /analytics/category-stats   – category-wise borrowing breakdown
  GET /analytics/monthly-trends   – month-over-month borrow / return counts
  GET /analytics/overdue          – list of currently overdue transactions
  GET /analytics/etl-status       – last ETL pipeline run metadata
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def analytics_summary(db: Session = Depends(get_db)):
    """Overall KPIs: total transactions, active borrows, overdue count, etc."""
    return crud.get_analytics_summary(db)


@router.get("/most-borrowed")
def most_borrowed(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Top `limit` most-borrowed books with borrow counts."""
    return crud.get_most_borrowed_books(db, limit=limit)


@router.get("/category-stats")
def category_stats(db: Session = Depends(get_db)):
    """Borrow count and unique-books count per book category."""
    return crud.get_category_stats(db)


@router.get("/monthly-trends")
def monthly_trends(db: Session = Depends(get_db)):
    """Month-over-month borrow and return counts (all recorded months)."""
    return crud.get_monthly_trends(db)


@router.get("/overdue")
def overdue_transactions(db: Session = Depends(get_db)):
    """All transactions that are currently overdue (>14 days, not returned)."""
    return crud.get_overdue_transactions(db)


@router.get("/etl-status")
def etl_status():
    """Metadata from the last ETL pipeline run (from data/etl_log.json)."""
    import os, json
    log_path = os.path.join(
        os.path.dirname(__file__), '..', 'data', 'etl_log.json'
    )
    if os.path.exists(log_path):
        with open(log_path) as f:
            return json.load(f)
    return {
        "status": "ETL pipeline has not been run yet",
        "last_run": None,
        "books_loaded": 0,
        "borrowers_loaded": 0,
        "transactions_loaded": 0,
    }
