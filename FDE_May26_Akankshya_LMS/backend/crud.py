from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from datetime import datetime, timedelta
from typing import Optional, List
import models
import schemas


# ── Books ──────────────────────────────────────────────────────────────────────

def get_books(db: Session):
    return db.query(models.Book).all()


def get_book(db: Session, book_id: int):
    return db.query(models.Book).filter(models.Book.book_id == book_id).first()


def create_book(db: Session, book: schemas.BookCreate):
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book: schemas.BookUpdate):
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    for key, value in book.model_dump(exclude_unset=True).items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int):
    db_book = get_book(db, book_id)
    if not db_book:
        return None
    db.delete(db_book)
    db.commit()
    return db_book


def search_books(
    db: Session,
    query: Optional[str] = None,
    category: Optional[str] = None,
    author: Optional[str] = None,
):
    q = db.query(models.Book)
    if query:
        q = q.filter(
            or_(
                models.Book.title.ilike(f"%{query}%"),
                models.Book.author.ilike(f"%{query}%"),
                models.Book.category.ilike(f"%{query}%"),
                models.Book.isbn.ilike(f"%{query}%"),
            )
        )
    if category:
        q = q.filter(models.Book.category.ilike(f"%{category}%"))
    if author:
        q = q.filter(models.Book.author.ilike(f"%{author}%"))
    return q.all()


# ── Borrowers ──────────────────────────────────────────────────────────────────

def get_borrowers(db: Session):
    return db.query(models.Borrower).all()


def get_borrower(db: Session, borrower_id: int):
    return db.query(models.Borrower).filter(
        models.Borrower.borrower_id == borrower_id
    ).first()


def create_borrower(db: Session, borrower: schemas.BorrowerCreate):
    db_borrower = models.Borrower(**borrower.model_dump())
    db.add(db_borrower)
    db.commit()
    db.refresh(db_borrower)
    return db_borrower


def update_borrower(db: Session, borrower_id: int, borrower: schemas.BorrowerUpdate):
    db_borrower = get_borrower(db, borrower_id)
    if not db_borrower:
        return None
    for key, value in borrower.model_dump(exclude_unset=True).items():
        setattr(db_borrower, key, value)
    db.commit()
    db.refresh(db_borrower)
    return db_borrower


def delete_borrower(db: Session, borrower_id: int):
    db_borrower = get_borrower(db, borrower_id)
    if not db_borrower:
        return None
    db.delete(db_borrower)
    db.commit()
    return db_borrower


# ── Transactions ───────────────────────────────────────────────────────────────

def get_transactions(db: Session):
    return db.query(models.Transaction).all()


def borrow_book(db: Session, borrow_req: schemas.BorrowRequest):
    book = get_book(db, borrow_req.book_id)
    if not book or book.availability_status != "available":
        return None, "Book is not available"
    borrower = get_borrower(db, borrow_req.borrower_id)
    if not borrower:
        return None, "Borrower not found"
    transaction = models.Transaction(
        book_id=borrow_req.book_id,
        borrower_id=borrow_req.borrower_id,
        borrow_date=datetime.utcnow(),
    )
    book.availability_status = "borrowed"
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction, None


def return_book(db: Session, return_req: schemas.ReturnRequest):
    transaction = db.query(models.Transaction).filter(
        models.Transaction.transaction_id == return_req.transaction_id
    ).first()
    if not transaction:
        return None, "Transaction not found"
    if transaction.return_date:
        return None, "Book already returned"
    transaction.return_date = datetime.utcnow()
    book = get_book(db, transaction.book_id)
    if book:
        book.availability_status = "available"
    db.commit()
    db.refresh(transaction)
    return transaction, None


# ── Dashboard Stats ────────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session):
    total_books       = db.query(models.Book).count()
    available_books   = db.query(models.Book).filter(models.Book.availability_status == "available").count()
    borrowed_books    = db.query(models.Book).filter(models.Book.availability_status == "borrowed").count()
    total_borrowers   = db.query(models.Borrower).count()
    recent_transactions = (
        db.query(models.Transaction)
        .order_by(models.Transaction.borrow_date.desc())
        .limit(5)
        .all()
    )
    return {
        "total_books":          total_books,
        "available_books":      available_books,
        "borrowed_books":       borrowed_books,
        "total_borrowers":      total_borrowers,
        "recent_transactions":  recent_transactions,
    }


# ── Analytics (Phase 2) ────────────────────────────────────────────────────────

def get_analytics_summary(db: Session) -> dict:
    """High-level KPIs for the analytics dashboard."""
    total   = db.query(models.Transaction).count()
    active  = db.query(models.Transaction).filter(models.Transaction.return_date.is_(None)).count()
    returned = db.query(models.Transaction).filter(models.Transaction.return_date.isnot(None)).count()

    cutoff = datetime.utcnow() - timedelta(days=14)
    overdue = db.query(models.Transaction).filter(
        models.Transaction.return_date.is_(None),
        models.Transaction.borrow_date < cutoff,
    ).count()

    # Average borrow duration (returned transactions only)
    returned_txns = db.query(models.Transaction).filter(
        models.Transaction.return_date.isnot(None)
    ).all()
    if returned_txns:
        avg_days = sum(
            (t.return_date - t.borrow_date).days for t in returned_txns
        ) / len(returned_txns)
    else:
        avg_days = 0.0

    # Most popular category by borrow count
    top_cat_row = (
        db.query(
            models.Book.category,
            func.count(models.Transaction.transaction_id).label("cnt"),
        )
        .join(models.Transaction, models.Book.book_id == models.Transaction.book_id)
        .group_by(models.Book.category)
        .order_by(func.count(models.Transaction.transaction_id).desc())
        .first()
    )
    top_cat = top_cat_row[0] if top_cat_row else "N/A"

    return {
        "total_transactions":       total,
        "active_borrows":           active,
        "overdue_count":            overdue,
        "returned_count":           returned,
        "avg_borrow_duration_days": round(avg_days, 1),
        "most_popular_category":    top_cat,
    }


def get_most_borrowed_books(db: Session, limit: int = 10) -> List[dict]:
    """Top `limit` books by total borrow count."""
    rows = (
        db.query(
            models.Book.book_id,
            models.Book.title,
            models.Book.author,
            models.Book.category,
            func.count(models.Transaction.transaction_id).label("borrow_count"),
        )
        .join(models.Transaction, models.Book.book_id == models.Transaction.book_id)
        .group_by(models.Book.book_id)
        .order_by(func.count(models.Transaction.transaction_id).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "book_id":     r.book_id,
            "title":       r.title,
            "author":      r.author,
            "category":    r.category,
            "borrow_count": r.borrow_count,
        }
        for r in rows
    ]


def get_category_stats(db: Session) -> List[dict]:
    """Borrow counts and unique-book counts grouped by category."""
    rows = (
        db.query(
            models.Book.category,
            func.count(models.Transaction.transaction_id).label("borrow_count"),
            func.count(func.distinct(models.Book.book_id)).label("unique_books"),
        )
        .join(models.Transaction, models.Book.book_id == models.Transaction.book_id)
        .group_by(models.Book.category)
        .order_by(func.count(models.Transaction.transaction_id).desc())
        .all()
    )
    return [
        {
            "category":    r.category,
            "borrow_count": r.borrow_count,
            "unique_books": r.unique_books,
        }
        for r in rows
    ]


def get_monthly_trends(db: Session) -> List[dict]:
    """Month-over-month borrow and return counts."""
    borrow_rows = (
        db.query(
            func.strftime('%Y-%m', models.Transaction.borrow_date).label("month"),
            func.count(models.Transaction.transaction_id).label("borrow_count"),
        )
        .group_by(func.strftime('%Y-%m', models.Transaction.borrow_date))
        .order_by(func.strftime('%Y-%m', models.Transaction.borrow_date))
        .all()
    )

    return_rows = (
        db.query(
            func.strftime('%Y-%m', models.Transaction.return_date).label("month"),
            func.count(models.Transaction.transaction_id).label("return_count"),
        )
        .filter(models.Transaction.return_date.isnot(None))
        .group_by(func.strftime('%Y-%m', models.Transaction.return_date))
        .all()
    )
    return_map = {r.month: r.return_count for r in return_rows}

    return [
        {
            "month":        r.month,
            "borrow_count": r.borrow_count,
            "return_count": return_map.get(r.month, 0),
        }
        for r in borrow_rows
    ]


def get_overdue_transactions(db: Session) -> List[dict]:
    """All unreturned transactions where borrow_date > 14 days ago."""
    cutoff = datetime.utcnow() - timedelta(days=14)
    txns = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.return_date.is_(None),
            models.Transaction.borrow_date < cutoff,
        )
        .order_by(models.Transaction.borrow_date.asc())
        .all()
    )
    now = datetime.utcnow()
    return [
        {
            "transaction_id": t.transaction_id,
            "book_id":        t.book_id,
            "book_title":     t.book.title       if t.book     else "Unknown",
            "borrower_id":    t.borrower_id,
            "borrower_name":  t.borrower.borrower_name if t.borrower else "Unknown",
            "borrow_date":    t.borrow_date.isoformat(),
            "days_overdue":   max((now - t.borrow_date).days - 14, 0),
        }
        for t in txns
    ]
