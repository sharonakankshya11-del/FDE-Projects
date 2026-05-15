from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

PRIORITIES   = ["Low", "Medium", "High", "Critical"]
STATUSES     = ["Open", "In Progress", "Resolved", "Closed"]
CATEGORIES   = [
    "VPN Issue", "Password Reset", "Software Installation",
    "Laptop Issue", "Email Access", "Network Connectivity", "Hardware Request"
]
DEPARTMENTS  = [
    "Engineering", "HR", "Finance", "Marketing",
    "Operations", "Sales", "IT", "Legal"
]

class TicketCreate(BaseModel):
    employee_name:   str = Field(..., min_length=1, max_length=100)
    department:      str = Field(..., min_length=1)
    issue_category:  str = Field(..., min_length=1)
    description:     str = Field(..., min_length=5)
    priority:        str = Field(default="Medium")

class TicketUpdate(BaseModel):
    status:           Optional[str] = None
    resolution_notes: Optional[str] = None
    description:      Optional[str] = None
    priority:         Optional[str] = None
    issue_category:   Optional[str] = None
    department:       Optional[str] = None

class TicketOut(BaseModel):
    ticket_id:        int
    employee_name:    str
    department:       str
    issue_category:   str
    description:      str
    priority:         str
    status:           str
    resolution_notes: str
    created_at:       datetime

    class Config:
        orm_mode = True
