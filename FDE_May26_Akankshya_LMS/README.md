# 📚 Library Management System — Phase 2

A full-stack Library Management System with ETL pipeline and transaction analytics.

---

## 🏗️ Project Structure

```
FDE_May26_Akankshya_LMS/
├── backend/
│   ├── main.py                  # FastAPI app (v2.0 – Phase 2)
│   ├── database.py              # SQLAlchemy + SQLite setup
│   ├── models.py                # ORM models (Book, Borrower, Transaction)
│   ├── schemas.py               # Pydantic validation + analytics schemas
│   ├── crud.py                  # DB operations + analytics queries
│   ├── requirements.txt         # Python dependencies
│   ├── run_etl.py               # ETL pipeline entry-point (Phase 2)
│   ├── routers/
│   │   ├── books.py             # CRUD endpoints
│   │   ├── borrowers.py         # CRUD endpoints
│   │   ├── transactions.py      # Borrow / Return endpoints
│   │   └── analytics.py        # Analytics endpoints (Phase 2)
│   ├── etl/                     # ETL package (Phase 2)
│   │   ├── generate_dataset.py  # Generates 50 books / 30 borrowers / 156 txns
│   │   ├── extract.py           # Extract CSVs into DataFrames
│   │   ├── transform.py         # Clean, deduplicate, validate
│   │   ├── load.py              # Load into SQLite DB
│   │   └── pipeline.py          # ETL orchestrator
│   └── data/                    # Generated dataset (Phase 2)
│       ├── books.csv            # 50 books, 8 categories
│       ├── borrowers.csv        # 30 borrowers
│       ├── transactions.csv     # 156 transactions
│       └── etl_log.json         # Last ETL run metadata
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Analytics.jsx    # Analytics dashboard (Phase 2)
│       │   ├── Dashboard.jsx
│       │   ├── Books.jsx
│       │   ├── Borrowers.jsx
│       │   ├── Transactions.jsx
│       │   └── Search.jsx
│       ├── services/
│       │   ├── analyticsService.js   # Analytics API calls (Phase 2)
│       │   ├── bookService.js
│       │   ├── borrowerService.js
│       │   └── transactionService.js
│       └── components/Navbar.jsx     # Updated with Analytics link
└── database/
    └── schema.sql
```

---

## 🚀 Setup & Running

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run ETL Pipeline (Phase 2)

Generates the dataset and loads 156 transactions into the database:

```bash
cd backend
python run_etl.py              # auto-generates CSV files if missing, then loads
python run_etl.py --force      # force regenerate CSV files then reload
```

### 3. Start Backend API

```bash
cd backend
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 4. Start Frontend

```bash
cd frontend
npm install
npm run dev                    # http://localhost:3000
```

---

## 📊 Phase 2 — ETL Pipeline

### ETL Workflow

```
CSV Files (data/)
    ↓
[Extract]   Read books.csv, borrowers.csv, transactions.csv into DataFrames
    ↓
[Transform] • Drop null rows on required fields
            • Deduplicate ISBNs / emails / IDs
            • Validate foreign-key references
            • Parse & validate date fields
            • Remove logically impossible rows (return < borrow)
    ↓
[Load]      • Clear existing DB tables
            • Insert books then borrowers then transactions
            • Update book availability_status based on active borrows
    ↓
etl_log.json  (run metadata persisted)
```

### Dataset Summary

| Entity       | Records |
|--------------|---------|
| Books        | 50      |
| Borrowers    | 30      |
| Transactions | 156     |

**Book categories:** Fiction · Technology · Science · History · Biography · Self-Help · Mystery · Non-Fiction
**Transaction breakdown:** 110 returned · 38 overdue · 8 active-not-overdue

---

## 🔌 API Endpoints

### Core (Phase 1)

| Method | Endpoint               | Description              |
|--------|------------------------|--------------------------|
| GET    | /books/                | List all books           |
| POST   | /books/                | Add a book               |
| PUT    | /books/{id}            | Update a book            |
| DELETE | /books/{id}            | Delete a book            |
| GET    | /borrowers/            | List all borrowers       |
| POST   | /borrowers/            | Add a borrower           |
| POST   | /borrow                | Borrow a book            |
| POST   | /return                | Return a book            |
| GET    | /transactions          | List all transactions    |
| GET    | /search                | Search books             |
| GET    | /dashboard             | Dashboard stats          |

### Analytics (Phase 2)

| Method | Endpoint                      | Description                          |
|--------|-------------------------------|--------------------------------------|
| GET    | /analytics/summary            | KPIs: totals, overdue, avg duration  |
| GET    | /analytics/most-borrowed      | Top 10 most-borrowed books           |
| GET    | /analytics/category-stats     | Category-wise borrow breakdown       |
| GET    | /analytics/monthly-trends     | Month-over-month borrow/return data  |
| GET    | /analytics/overdue            | All overdue transactions             |
| GET    | /analytics/etl-status         | Last ETL run metadata                |

---

## 📈 Analytics Features

### 1. Most Borrowed Books
Top 10 books ranked by total borrow count with category colour-coding.

### 2. Category-wise Borrowing
Breakdown by category showing borrow count + unique book count.

### 3. Monthly Borrowing Trends
Bar chart comparing monthly borrows vs returns over 24 months.

### 4. Overdue Analysis
Table of all transactions overdue >14 days with:
- Book title and borrower name
- Borrow date and days overdue
- Colour-coded severity (orange = 0-30 days, red = 30+ days)

---

## 🛠️ Tech Stack

| Layer     | Technology                              |
|-----------|-----------------------------------------|
| Backend   | FastAPI 0.115 · SQLAlchemy 2.0 · SQLite |
| ETL       | pandas 2.x · Python csv / json          |
| Frontend  | React 18 · Vite 5 · React Router v6     |
| Charts    | Pure CSS (no external chart library)    |
| HTTP      | Axios                                   |

---

## 🧪 Sample API Responses

```json
GET /analytics/summary
{
  "total_transactions": 156,
  "active_borrows": 46,
  "overdue_count": 38,
  "returned_count": 110,
  "avg_borrow_duration_days": 13.2,
  "most_popular_category": "Technology"
}
```

```json
GET /analytics/most-borrowed?limit=3
[
  { "book_id": 16, "title": "Structure and Interpretation of Computer Programs",
    "author": "Harold Abelson", "category": "Technology", "borrow_count": 7 },
  { "book_id": 43, "title": "Deep Work",
    "author": "Cal Newport", "category": "Self-Help", "borrow_count": 6 },
  { "book_id": 30, "title": "The Rise and Fall of the Third Reich",
    "author": "William Shirer", "category": "History", "borrow_count": 6 }
]
```
