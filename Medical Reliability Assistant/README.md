# 🏥 AI-Powered Medical Equipment Reliability Intelligence Assistant

A production-grade multi-agent RAG system for hospital biomedical engineers to investigate equipment reliability issues using natural language.

---

## Architecture Overview

```
User Query (React Frontend)
        │
        ▼
[PII Middleware] ──► Mask PHI before processing
        │
        ▼
[Input Guardrails] ──► Validate, classify, sanitize
        │
        ▼
[Supervisor Agent] ──► LangGraph hierarchical orchestrator
        │
   ┌────┴────┬──────────┬──────────────┐
   ▼         ▼          ▼              ▼
[Retrieval] [Analysis] [Maintenance] [Recommendation]
  Agent      Agent       Agent         Agent
   │
   ├── Pinecone (vector search)
   ├── BM25 (keyword search)
   └── RRF fusion + Cross-encoder rerank
        │
        ▼
[Output Guardrails] ──► Safety, hallucination check
        │
        ▼
[Human-in-the-Loop] ──► Review / Edit / Approve / Reject
        │
        ▼
Response + DeepEval scores
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI + Uvicorn |
| Agents | LangGraph (hierarchical supervisor) |
| Vector Store | Pinecone |
| Embeddings | OpenAI `text-embedding-3-small` |
| Chunking | RecursiveCharacterTextSplitter |
| Hybrid Search | BM25 (rank_bm25) + Pinecone vector, fused with RRF |
| Reranking | Cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) |
| LLM | Claude `claude-sonnet-4-20250514` |
| Evaluation | DeepEval (Claude as judge) |
| Guardrails | Input + Output (custom + Guardrails AI) |
| PII | Presidio middleware |
| Frontend | React (Vite + JSX) |

---

## Project Structure

```
medical-reliability-assistant/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── supervisor.py          # Hierarchical supervisor (LangGraph)
│   │   │   ├── retrieval_agent.py     # Hybrid search + rerank
│   │   │   ├── analysis_agent.py      # Anomaly detection + correlation
│   │   │   ├── maintenance_agent.py   # Maintenance pattern recognition
│   │   │   ├── recommendation_agent.py# Root-cause + explainable fix
│   │   │   ├── state.py               # Shared typed state + A2A messages
│   │   │   └── checkpointer.py        # LangGraph checkpoint persistence
│   │   ├── api/
│   │   │   ├── routes.py              # FastAPI endpoints
│   │   │   └── schemas.py             # Pydantic request/response models
│   │   ├── core/
│   │   │   ├── config.py              # Settings (env vars)
│   │   │   ├── embeddings.py          # OpenAI text-embedding-3-small
│   │   │   ├── pinecone_client.py     # Pinecone index management
│   │   │   ├── hybrid_search.py       # BM25 + vector + RRF
│   │   │   └── reranker.py            # Cross-encoder reranking
│   │   ├── data/
│   │   │   ├── ingest.py              # CSV → incident narratives → Pinecone
│   │   │   ├── narrative_generator.py # Row → NL incident document
│   │   │   └── golden_dataset.py      # DeepEval golden Q&A pairs
│   │   ├── evaluation/
│   │   │   ├── deepeval_suite.py      # Full eval suite
│   │   │   └── llm_judge.py           # LLM-as-judge (Claude)
│   │   ├── guardrails/
│   │   │   ├── input_guardrails.py    # Query validation + topic check
│   │   │   └── output_guardrails.py   # Hallucination + safety check
│   │   ├── middleware/
│   │   │   └── pii_middleware.py      # Presidio PII masking
│   │   └── utils/
│   │       ├── logger.py
│   │       └── anomaly_detector.py    # Z-score / IQR anomaly detection
│   ├── scripts/
│   │   └── run_ingest.py              # CLI: python scripts/run_ingest.py
│   ├── main.py                        # FastAPI app entry point
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── IncidentCard.jsx
│   │   │   ├── DeviceHealthDashboard.jsx
│   │   │   ├── HumanReviewPanel.jsx
│   │   │   └── EvalMetricsPanel.jsx
│   │   ├── pages/
│   │   │   └── App.jsx
│   │   ├── hooks/
│   │   │   └── useQuery.js
│   │   ├── utils/
│   │   │   └── api.js
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── docs/
    ├── architecture.md
    └── design_decisions.md
```

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- Pinecone account (free tier works)
- Anthropic API key
- OpenAI API key (for embeddings only)

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and fill in your keys
cp .env.example .env
```

Edit `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=medical-equipment
PINECONE_ENVIRONMENT=us-east-1-aws
```

### 3. Ingest Data

```bash
# Place ai4i2020.csv and predictive_maintenance.csv in backend/data/
python scripts/run_ingest.py --csv1 data/ai4i2020.csv --csv2 data/predictive_maintenance.csv

# Expected output:
# ✓ Loaded 10000 rows from ai4i2020.csv
# ✓ Loaded 10000 rows from predictive_maintenance.csv
# ✓ Generated 20000 incident narratives
# ✓ Chunked into 20000 documents
# ✓ Upserted to Pinecone index: medical-equipment
```

### 4. Start Backend

```bash
uvicorn main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:5173
```

---

## API Usage Examples

### Query the assistant

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "MRI machine showing heat dissipation failures in ICU",
    "equipment_type": "MRI",
    "hospital_unit": "ICU",
    "severity": "high",
    "session_id": "eng-001"
  }'
```

### Search incidents only

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ventilator power failure recurring",
    "top_k": 5,
    "equipment_type": "ventilator"
  }'
```

### Human review — approve recommendation

```bash
curl -X POST http://localhost:8000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "eng-001",
    "action": "approve",
    "edited_response": null
  }'
```

### Run evaluation suite

```bash
curl -X POST http://localhost:8000/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{"run_full_suite": true}'
```

---

## Sample Maintenance Query & Response

**Query:** "Infusion pump alerts increasing in Ward B, tool wear above 180 minutes"

**Response:**
```json
{
  "recommendation": "Based on 7 similar historical incidents: ...",
  "root_cause": "Overstress failure pattern (OSF) triggered by high torque at elevated tool wear",
  "confidence": 0.87,
  "retrieved_incidents": [...],
  "escalation_triggered": true,
  "eval_scores": {
    "answer_relevancy": 0.91,
    "faithfulness": 0.88,
    "context_precision": 0.84
  }
}
```

---

## Evaluation Framework

DeepEval metrics (Claude as judge):

| Metric | Target |
|--------|--------|
| Answer Relevancy | ≥ 0.85 |
| Faithfulness | ≥ 0.85 |
| Context Precision | ≥ 0.80 |
| Context Recall | ≥ 0.80 |
| Context Relevancy | ≥ 0.80 |
| Answer Correctness | ≥ 0.80 |
| Tone (G-Eval) | ≥ 0.85 |
| Accuracy (G-Eval) | ≥ 0.85 |
| Conciseness (G-Eval) | ≥ 0.80 |
