from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Ticket
from schemas import TicketCreate, TicketUpdate
from typing import Optional

def get_all_tickets(db: Session):
    return db.query(Ticket).order_by(Ticket.created_at.desc()).all()

def get_ticket(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

def create_ticket(db: Session, ticket: TicketCreate):
    db_ticket = Ticket(**ticket.dict())
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def update_ticket(db: Session, ticket_id: int, data: TicketUpdate):
    ticket = get_ticket(db, ticket_id)
    if ticket:
        for k, v in data.dict(exclude_unset=True).items():
            if v is not None:
                setattr(ticket, k, v)
        db.commit()
        db.refresh(ticket)
    return ticket

def delete_ticket(db: Session, ticket_id: int):
    ticket = get_ticket(db, ticket_id)
    if ticket:
        db.delete(ticket)
        db.commit()
    return ticket

def search_tickets(
    db: Session,
    keyword:  Optional[str] = "",
    status:   Optional[str] = "",
    category: Optional[str] = "",
    priority: Optional[str] = "",
):
    q = db.query(Ticket)
    if keyword:
        q = q.filter(
            or_(
                Ticket.description.ilike(f"%{keyword}%"),
                Ticket.employee_name.ilike(f"%{keyword}%"),
                Ticket.issue_category.ilike(f"%{keyword}%"),
            )
        )
    if status:
        q = q.filter(Ticket.status == status)
    if category:
        q = q.filter(Ticket.issue_category == category)
    if priority:
        q = q.filter(Ticket.priority == priority)
    return q.order_by(Ticket.created_at.desc()).all()

def get_stats(db: Session):
    all_tickets = db.query(Ticket).all()
    return {
        "total":       len(all_tickets),
        "open":        sum(1 for t in all_tickets if t.status == "Open"),
        "in_progress": sum(1 for t in all_tickets if t.status == "In Progress"),
        "resolved":    sum(1 for t in all_tickets if t.status == "Resolved"),
        "closed":      sum(1 for t in all_tickets if t.status == "Closed"),
        "critical":    sum(1 for t in all_tickets if t.priority == "Critical"),
        "by_category": {
            cat: sum(1 for t in all_tickets if t.issue_category == cat)
            for cat in [
                "VPN Issue", "Password Reset", "Software Installation",
                "Laptop Issue", "Email Access", "Network Connectivity", "Hardware Request"
            ]
        },
        "by_priority": {
            p: sum(1 for t in all_tickets if t.priority == p)
            for p in ["Low", "Medium", "High", "Critical"]
        },
    }
