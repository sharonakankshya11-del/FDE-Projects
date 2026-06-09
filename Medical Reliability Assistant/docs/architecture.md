# Architecture: Medical Equipment Reliability Intelligence Assistant

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React/Vite)                        │
│  ChatInterface  ·  DeviceHealthDashboard  ·  HumanReviewPanel       │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTP (JSON)
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FASTAPI MICROSERVICE                            │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────────┐ │
│  │PII Middleware│  │Input Guardrail│  │Output Guardrail            │ │
│  │(Presidio)   │  │(LLM+Heuristic)│  │(Hallucination+Safety)      │ │
│  └──────┬──────┘  └──────┬───────┘  └────────────┬───────────────┘ │
│         │                │                        │                 │
│         ▼                ▼                        ▼                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          LANGGRAPH HIERARCHICAL SUPERVISOR                   │  │
│  │                                                              │  │
│  │  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐   │  │
│  │  │Retrieval Agent│  │Analysis Agent│  │Maintenance Agent │   │  │
│  │  │              │  │              │  │                  │   │  │
│  │  │• Hybrid Search│  │• Z-score/IQR │  │• Failure patterns│   │  │
│  │  │• RRF Fusion  │  │• Escalation  │  │• Recurrence freq │   │  │
│  │  │• Cross-encoder│  │• LLM correl. │  │• Schedule advice │   │  │
│  │  │  reranking   │  │              │  │                  │   │  │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │  │
│  │         └─────────────────┴──────────────────┘             │  │
│  │                                │                            │  │
│  │                                ▼                            │  │
│  │                  ┌──────────────────────────┐               │  │
│  │                  │  Recommendation Agent    │               │  │
│  │                  │  • Root-cause synthesis  │               │  │
│  │                  │  • Claude Sonnet (full)  │               │  │
│  │                  │  • Citations + confidence│               │  │
│  │                  └────────────┬─────────────┘               │  │
│  │                               │                             │  │
│  │                               ▼                             │  │
│  │                   ┌──────────────────────┐                  │  │
│  │                   │  Human-in-the-Loop   │ ◄── /api/review  │  │
│  │                   │  Approve/Edit/Reject │                  │  │
│  │                   └──────────────────────┘                  │  │
│  │                                                              │  │
│  │  [SQLite Checkpoints: LangGraph state persisted per session] │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    DATA LAYER                                │  │
│  │                                                              │  │
│  │  ┌──────────────┐  ┌────────────────┐  ┌──────────────────┐ │  │
│  │  │   Pinecone   │  │  BM25 (memory) │  │  Cross-encoder   │ │  │
│  │  │ Vector Index │  │  rank_bm25     │  │  ms-marco-MiniLM │ │  │
│  │  │ 1536-dim     │  │  keyword search│  │  reranking       │ │  │
│  │  │ cosine sim   │  │                │  │                  │ │  │
│  │  └──────────────┘  └────────────────┘  └──────────────────┘ │  │
│  │         └──────────────────┘                                 │  │
│  │               RRF Fusion (k=60)                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                         INGESTION PIPELINE                          │
│                                                                     │
│  ai4i2020.csv (10k rows)                                           │
│  predictive_maintenance.csv (10k rows)                             │
│       │                                                             │
│       ▼                                                             │
│  Narrative Generator → NL incident documents with medical framing  │
│       │                                                             │
│       ▼                                                             │
│  RecursiveCharacterTextSplitter (chunk_size=512, overlap=64)       │
│       │                                                             │
│       ▼                                                             │
│  OpenAI text-embedding-3-small (batch=100) → 1536-dim vectors      │
│       │                                                             │
│       ├──► Pinecone upsert (with metadata: device, unit, severity) │
│       └──► BM25 index build (in-memory, warmed at startup)         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                       EVALUATION FRAMEWORK                          │
│                                                                     │
│  DeepEval + Claude Sonnet as judge                                 │
│                                                                     │
│  Standard metrics: AnswerRelevancy · Faithfulness                  │
│                    ContextualPrecision · ContextualRecall          │
│                    ContextualRelevancy · AnswerCorrectness         │
│                                                                     │
│  Custom G-Eval: Tone · Accuracy · Conciseness                     │
│                                                                     │
│  20 hand-crafted golden Q&A pairs (golden_dataset.py)             │
└─────────────────────────────────────────────────────────────────────┘
```

## A2A Communication Flow

```
User Query
    │
    ▼
Supervisor (LangGraph StateGraph)
    │
    ├─ [Message: "→ Dispatching to Retrieval Agent"]
    │
    ▼
Retrieval Agent ──► state.retrieved_incidents
    │               state.retrieval_context
    │               state.add_message(RETRIEVAL, "Retrieved N incidents...")
    │
    ▼
Analysis Agent ──► state.anomalies
    │              state.correlation_summary
    │              state.failure_probability
    │              state.trigger_escalation(...) [if high severity]
    │              state.add_message(ANALYSIS, "Failure prob: 0.87...")
    │
    ▼
Maintenance Agent ──► state.maintenance_patterns
    │                 state.similar_cases_count
    │                 state.add_message(MAINTENANCE, "N cases analysed")
    │
    ▼
Recommendation Agent ──► state.recommendation
    │                    state.root_cause
    │                    state.confidence
    │                    state.citations
    │                    state.add_message(RECOMMENDATION, "Confidence: 85%")
    │
    ▼
Output Guardrail ──► state.output_safe (True/False)
    │                state.output_warning
    │
    ▼
Human-in-the-Loop ──► state.awaiting_human_review = True
    │                 [GRAPH PAUSED — SQLite checkpoint saved]
    │                 /api/review called by engineer
    │
    ▼
Apply Review ──► state.final_response
    │
    ▼
Response to Frontend
```
