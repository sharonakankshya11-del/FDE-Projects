from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import crud, schemas

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("/", response_model=List[schemas.TicketOut], summary="Get all tickets")
def read_all_tickets(db: Session = Depends(get_db)):
    return crud.get_all_tickets(db)

@router.get("/{ticket_id}", response_model=schemas.TicketOut, summary="Get ticket by ID")
def read_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found")
    return ticket

@router.post("/", response_model=schemas.TicketOut, status_code=201, summary="Create a new ticket")
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    return crud.create_ticket(db, ticket)

@router.put("/{ticket_id}", response_model=schemas.TicketOut, summary="Update a ticket")
def update_ticket(ticket_id: int, data: schemas.TicketUpdate, db: Session = Depends(get_db)):
    ticket = crud.update_ticket(db, ticket_id, data)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found")
    return ticket

@router.delete("/{ticket_id}", summary="Delete a ticket")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.delete_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket #{ticket_id} not found")
    return {"message": f"Ticket #{ticket_id} deleted successfully"}
