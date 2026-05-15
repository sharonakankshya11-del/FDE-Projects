# 🎫 HDMS — Helpdesk Ticket Management System

**Phase 1 · Internal IT Support · Built with FastAPI + SQLite + Vanilla JS**

A full-stack helpdesk ticketing system that allows IT support teams to manage, track, and resolve employee support requests. Features a dark-mode dashboard with real-time stats, full CRUD operations, advanced search/filter, and a polished production-ready UI.

---

## 📁 Project Structure

```
HDMS/
├── backend/
│   ├── main.py              # FastAPI app entry point + seed data
│   ├── database.py          # SQLAlchemy engine + session
│   ├── models.py            # ORM model — Ticket table
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── crud.py              # All database operations
│   ├── requirements.txt     # Python dependencies
│   └── routers/
│       └── tickets.py       # /tickets CRUD endpoints
├── frontend/
│   └── index.html           # Complete single-file frontend app
├── database/
│   └── schema.sql           # SQLite schema + seed data
├── screenshots/             # UI screenshots for submission
├── docs/                    # Postman collection + API docs
└── README.md
```

---

## 🛠 Tech Stack

| Layer        | Technology            | Purpose                         |
|--------------|-----------------------|---------------------------------|
| Backend      | Python 3.10 + FastAPI | REST API with auto Swagger docs |
| ORM          | SQLAlchemy 2.0        | Database abstraction layer      |
| Validation   | Pydantic v1           | Request/response validation     |
| Database     | SQLite                | Lightweight file-based DB       |
| Frontend     | Vanilla JS + HTML/CSS | Zero-dependency single-file UI  |
| Fonts        | Syne + DM Sans        | Google Fonts                    |
| API Testing  | Postman               | Endpoint verification           |

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.10+
- A modern web browser (Chrome, Firefox, Edge)

### Backend Setup

```bash
# 1. Navigate to backend
cd HDMS/backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start the server
uvicorn main:app --reload
```

The API will start at: `http://localhost:8000`  
Swagger docs at: `http://localhost:8000/docs`  
ReDoc at: `http://localhost:8000/redoc`

> **Note**: The database (`helpdesk.db`) and 10 sample tickets are created automatically on first run.

### Frontend Setup

No build step required. Simply open in a browser:

```bash
# Option 1: Open directly
open HDMS/frontend/index.html   # macOS
start HDMS/frontend/index.html  # Windows

# Option 2: Serve with Python (avoids CORS on some browsers)
cd HDMS/frontend
python -m http.server 5500
# Then visit: http://localhost:5500
```

> Make sure the backend is running on `http://localhost:8000` before opening the frontend.

---

## 📡 API Endpoints

| Method   | Endpoint                  | Description              |
|----------|---------------------------|--------------------------|
| `GET`    | `/tickets/`               | Get all tickets          |
| `GET`    | `/tickets/{id}`           | Get ticket by ID         |
| `POST`   | `/tickets/`               | Create new ticket        |
| `PUT`    | `/tickets/{id}`           | Update existing ticket   |
| `DELETE` | `/tickets/{id}`           | Delete a ticket          |
| `GET`    | `/search`                 | Search + filter tickets  |
| `GET`    | `/stats`                  | Dashboard statistics     |

### Example: Create a Ticket

```http
POST /tickets/
Content-Type: application/json

{
  "employee_name": "John Smith",
  "department": "Engineering",
  "issue_category": "VPN Issue",
  "description": "Cannot connect to VPN after OS update.",
  "priority": "High"
}
```

### Example: Search Tickets

```http
GET /search?keyword=vpn&status=Open&priority=High
```

### Example: Update Status

```http
PUT /tickets/1
Content-Type: application/json

{
  "status": "Resolved",
  "resolution_notes": "VPN client reinstalled. Issue resolved."
}
```

---

## 🗄 Data Model

### Ticket

| Field             | Type     | Description                                        |
|-------------------|----------|----------------------------------------------------|
| `ticket_id`       | Integer  | Auto-incremented primary key                       |
| `employee_name`   | String   | Name of the reporting employee                     |
| `department`      | String   | Employee's department                              |
| `issue_category`  | String   | VPN Issue, Password Reset, Software Installation… |
| `description`     | Text     | Detailed description of the problem               |
| `priority`        | String   | Low / Medium / High / Critical                     |
| `status`          | String   | Open / In Progress / Resolved / Closed             |
| `resolution_notes`| Text     | IT team notes on how the issue was resolved        |
| `created_at`      | DateTime | Auto-set on ticket creation                        |

---

## 🎨 Features

- **Dashboard** — Live metrics (total, open, in-progress, resolved, critical), bar charts by priority/status/category, recent tickets table
- **Ticket List** — Card grid with real-time client-side filter by status, priority, and category
- **Create Ticket** — Validated form with all 9 fields, instant feedback
- **Edit Ticket** — Update status, priority, resolution notes, category
- **Delete Ticket** — Confirmation modal before permanent deletion
- **Search** — Full-text search via backend `/search` endpoint with multi-filter support
- **View Detail** — Full ticket details in modal with resolution notes
- **Auto-seed** — 10 sample tickets generated on first run
- **Dark Mode UI** — Professional dark theme with Syne + DM Sans typography

---

## 📋 Allowed Values

**Priorities**: `Low`, `Medium`, `High`, `Critical`  
**Statuses**: `Open`, `In Progress`, `Resolved`, `Closed`  
**Categories**: `VPN Issue`, `Password Reset`, `Software Installation`, `Laptop Issue`, `Email Access`, `Network Connectivity`, `Hardware Request`  
**Departments**: `Engineering`, `HR`, `Finance`, `Marketing`, `Operations`, `Sales`, `IT`, `Legal`

---

## 📸 Screenshots

See `screenshots/` folder for:
- Dashboard overview
- Ticket list with filters
- Create ticket form
- Edit ticket modal
- Search results
- Swagger API docs

---

## 📦 Postman Collection

Import `docs/HDMS.postman_collection.json` into Postman to test all 7 endpoints with pre-built request examples.

---

*Built for Phase 1 — Internal IT Helpdesk, AFDE Submission*
>>>>>>> b53f7b5 (Initial commit: HDMS project)
