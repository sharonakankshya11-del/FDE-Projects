from pathlib import Path

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
from database import engine, get_db, SessionLocal
import models, crud, schemas
from routers import tickets

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Helpdesk Ticket Management System",
    description="Phase 1 – Internal IT Helpdesk API built with FastAPI + SQLite",
    version="1.0.0",
)

frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets.router)

# ── Seed sample data on first run ──────────────────────────────────────────
def seed_data():
    db = SessionLocal()
    try:
        if db.query(models.Ticket).count() == 0:
            samples = [
                {"employee_name": "Rahul Sharma",   "department": "Engineering", "issue_category": "VPN Issue",             "description": "Unable to connect to company VPN from home network. Getting error 602 on Windows 11.",                           "priority": "High",     "status": "In Progress",  "resolution_notes": "Checking VPN gateway logs. Resetting credentials.",   "created_at": datetime.utcnow() - timedelta(days=2)},
                {"employee_name": "Ananya Iyer",    "department": "HR",          "issue_category": "Password Reset",        "description": "Forgot Windows login password after returning from 2-week leave. Cannot access workstation.",                     "priority": "Medium",   "status": "Resolved",     "resolution_notes": "Password reset via Active Directory. User confirmed.",  "created_at": datetime.utcnow() - timedelta(days=4)},
                {"employee_name": "Karthik Nair",   "department": "Finance",     "issue_category": "Software Installation", "description": "Need MS Office 2021 installed on workstation for quarterly audit report preparation.",                            "priority": "Low",      "status": "Open",         "resolution_notes": "",                                                      "created_at": datetime.utcnow() - timedelta(hours=3)},
                {"employee_name": "Priya Menon",    "department": "Marketing",   "issue_category": "Laptop Issue",          "description": "Laptop randomly shuts down during video calls. Battery indicator shows 40% but dies suddenly.",                  "priority": "Critical", "status": "Open",         "resolution_notes": "",                                                      "created_at": datetime.utcnow() - timedelta(hours=1)},
                {"employee_name": "Suresh Kumar",   "department": "Operations",  "issue_category": "Email Access",          "description": "Cannot access shared mailbox support@company.com. Getting access denied error in Outlook.",                     "priority": "Medium",   "status": "Closed",       "resolution_notes": "Mailbox permissions granted. Verified access.",         "created_at": datetime.utcnow() - timedelta(days=6)},
                {"employee_name": "Divya Reddy",    "department": "Sales",       "issue_category": "Network Connectivity",  "description": "Wi-Fi drops every 10-15 minutes in Meeting Room B. Issue affects all devices in that room.",                     "priority": "High",     "status": "In Progress",  "resolution_notes": "Access point reset. Monitoring for 24h.",               "created_at": datetime.utcnow() - timedelta(days=1)},
                {"employee_name": "Arjun Pillai",   "department": "IT",          "issue_category": "Hardware Request",      "description": "Requesting dual monitor setup for the new UI design project. Current single screen is insufficient.",            "priority": "Low",      "status": "Open",         "resolution_notes": "",                                                      "created_at": datetime.utcnow() - timedelta(hours=5)},
                {"employee_name": "Sneha Patel",    "department": "Legal",       "issue_category": "Software Installation", "description": "Adobe Acrobat Pro needed for contract review and digital signature workflows. Urgent for compliance.",           "priority": "High",     "status": "Resolved",     "resolution_notes": "Adobe Acrobat Pro installed and license activated.",     "created_at": datetime.utcnow() - timedelta(days=3)},
                {"employee_name": "Mohan Das",      "department": "Engineering", "issue_category": "VPN Issue",             "description": "VPN connects but cannot access internal GitLab server. Other internal tools work fine.",                         "priority": "High",     "status": "Open",         "resolution_notes": "",                                                      "created_at": datetime.utcnow() - timedelta(hours=8)},
                {"employee_name": "Lakshmi Rao",    "department": "HR",          "issue_category": "Email Access",          "description": "New joiner cannot receive emails. Account created 2 days ago but inbox is not working.",                        "priority": "Critical", "status": "In Progress",  "resolution_notes": "Checking Exchange server settings for new account.",    "created_at": datetime.utcnow() - timedelta(hours=2)},
            ]
            for s in samples:
                t = models.Ticket(**s)
                db.add(t)
            db.commit()
    finally:
        db.close()

seed_data()

# ── Extra endpoints ─────────────────────────────────────────────────────────
@app.get("/search", response_model=List[schemas.TicketOut], tags=["Search"])
def search_tickets(
    keyword:  Optional[str] = Query(default="", description="Search in name, description, category"),
    status:   Optional[str] = Query(default="", description="Filter by status"),
    category: Optional[str] = Query(default="", description="Filter by issue category"),
    priority: Optional[str] = Query(default="", description="Filter by priority"),
    db: Session = Depends(get_db),
):
    return crud.search_tickets(db, keyword, status, category, priority)

@app.get("/stats", tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/app")

@app.get("/health", tags=["Health"])
def health():
    return {"message": "Helpdesk TMS API is running", "docs": "/docs", "version": "1.0.0"}
