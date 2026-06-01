# 🤖 AI-Powered Product Strategy Assistant

A **Multi-Agent AI system** that analyzes business data and generates strategic product insights for Product Managers.

## Architecture

```
product-strategy-assistant/
├── backend/                     # FastAPI + Multi-Agent System
│   ├── agents/
│   │   └── orchestrator.py      # 6 AI agents pipeline
│   ├── routers/
│   │   ├── analysis.py          # File upload & analysis
│   │   ├── chat.py              # Interactive Q&A
│   │   └── report.py            # Report generation
│   ├── main.py                  # FastAPI app entry
│   └── requirements.txt
└── frontend/                    # React UI
    ├── src/
    │   ├── pages/
    │   │   ├── UploadPage.jsx   # Data upload with agent progress
    │   │   ├── DashboardPage.jsx # Analytics & visualizations
    │   │   ├── ChatPage.jsx     # AI chat interface
    │   │   └── ReportPage.jsx   # Executive report generator
    │   ├── components/
    │   │   └── Sidebar.jsx
    │   ├── App.jsx
    │   └── App.css
    └── package.json
```

## 6 AI Agents

| # | Agent | Responsibility |
|---|-------|---------------|
| 1 | **Data Analyst** | Parse sales metrics, trends, top performers |
| 2 | **Customer Feedback** | Sentiment analysis, NPS, complaints, praises |
| 3 | **Market Research** | Identify opportunities, category trends, growth areas |
| 4 | **SWOT Analysis** | Synthesize strengths, weaknesses, opportunities, threats |
| 5 | **Feature Prioritization** | RICE/MoSCoW scoring of feature requests |
| 6 | **Strategy Recommendation** | Executive roadmap, KPIs, strategic pillars |

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Anthropic API key

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here  # Windows: set ANTHROPIC_API_KEY=your_key_here

# Start the server
uvicorn main:app --reload --port 8000
```

The API will be live at: http://localhost:8000
Swagger docs: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start
```

The app will open at: http://localhost:3000

## Usage

1. **Upload** a CSV file (e.g. `Sample_Sales_Data.csv`) on the Upload page
2. Watch **6 AI agents** process your data in real time
3. Explore the **Dashboard** with charts, SWOT, features, roadmap
4. **Chat** with the AI advisor about your strategy
5. **Generate** a downloadable executive report

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analysis/upload` | Upload CSV and run full analysis |
| POST | `/api/analysis/text` | Analyze raw text data |
| POST | `/api/chat/message` | Chat with context-aware AI |
| POST | `/api/report/generate-markdown` | Generate executive report |

## Sample Data

The included `Sample_Sales_Data.csv` contains:
- Sales transactions by product, region, category
- Customer ratings and reviews
- Revenue, cost, profit metrics
- Marketing spend data

## Technologies

- **AI**: Claude (claude-sonnet-4) via Anthropic API
- **Backend**: FastAPI + Python
- **Frontend**: React + Recharts + React Markdown
- **Styling**: Custom CSS with dark theme

## Outputs

- 📊 Revenue & category charts
- 🔍 SWOT analysis (2×2 grid)
- ⚡ Feature prioritization (MoSCoW)
- 🗺 12-month product roadmap (Q1–Q4)
- 💬 KPIs & success metrics
- 📄 Downloadable executive report (.md)
