from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import models
from database import engine
from routers import books, borrowers, transactions, analytics

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management System API",
    description="Phase 2 – Library Management System with ETL Pipeline & Analytics",
    version="2.0.0",
)

# CORS Middleware — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(books.router)
app.include_router(borrowers.router)
app.include_router(transactions.router)
app.include_router(analytics.router)   # ← Phase 2


@app.get("/")
def root():
    return {
        "message": "Library Management System API is running",
        "version": "2.0.0",
        "phase":   "Phase 2 – ETL Pipeline & Analytics",
        "docs":    "/docs",
    }
