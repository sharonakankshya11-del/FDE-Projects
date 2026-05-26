# 🎓 AI Multi-Agent Smart Learning Assistant
### Powered by LangGraph · GPT-4o-mini · ChromaDB

A production-style multi-agent AI system that helps you learn concepts, retrieve study materials, generate explanations, validate responses, and evaluate output quality.

---

## 📁 Project Structure

```
smart_learning_assistant/
├── main.py                        # CLI entry point
├── requirements.txt
├── .env.example                   # → copy to .env and add your key
│
├── core/
│   ├── state.py                   # Shared AgentState (TypedDict)
│   └── graph.py                   # LangGraph workflow orchestration
│
├── agents/
│   ├── security_agent.py          # Input validation & guardrails
│   ├── supervisor_agent.py        # Intent detection & routing
│   ├── retrieval_agent.py         # Hybrid search (semantic + BM25 + RRF)
│   ├── generation_agent.py        # LLM response generation
│   ├── reviewer_agent.py          # Hallucination & quality checks
│   ├── correction_agent.py        # Self-correction (reflection loop)
│   └── response_agent.py          # Final response assembly
│
├── evaluation/
│   └── evaluator.py               # DeepEval + custom metrics
│
├── utils/
│   ├── ingest.py                  # PDF/text → ChromaDB ingestion
│   └── logger.py                  # Rich logging + analytics
│
└── data/
    ├── sample_docs/               # Put your PDFs/notes here
    ├── chroma_db/                 # Auto-created vector store
    └── logs/                      # Audit logs + analytics.jsonl
```

---

## ⚙️ Setup

### 1. Clone / open in VS Code
Open this folder in VS Code.

### 2. Create virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 5. (Optional) Ingest your study materials
```bash
python main.py --ingest ./data/sample_docs/
# Or a specific PDF:
python main.py --ingest ./my_lecture_notes.pdf
```

---

## 🚀 Running the Assistant

### Interactive Chat Mode
```bash
python main.py
```

**Chat commands:**
| Command | Action |
|---------|--------|
| `trace` | Toggle agent trace visibility |
| `clear` | Reset conversation history |
| `analytics` | View session statistics |
| `quit` | Exit |

### Single Query Mode
```bash
python main.py --query "Explain Transformers in simple words"
python main.py --query "Quiz me on Multi-Agent Systems"
python main.py --query "Summarize my notes on RAG"
```

### VS Code — F5 Launch Configs
Use the **Run and Debug** panel (`Ctrl+Shift+D`) — pre-configured launch profiles are included.

---

## 🏗️ Architecture

### Agent Pipeline (LangGraph)

```
User Query
    │
    ▼
[1] Security Agent        ← Prompt injection, harmful content filter
    │
    ▼
[2] Supervisor Agent      ← Intent detection, workflow selection
    │
    ▼
[3] Retrieval Agent       ← Semantic search + BM25 + RRF fusion
    │
    ▼
[4] Generation Agent      ← GPT-4o-mini with retrieved context
    │
    ▼
[5] Reviewer Agent        ← Faithfulness, relevance, hallucination checks
    │
    ├─ FAIL (< 2 retries) → [6] Correction Agent → back to Reviewer
    │
    └─ PASS
         │
         ▼
[7] Response Agent        ← Assembles final output + follow-up topics
    │
    ▼
Final Response (with confidence score, sources, eval metrics)
```

### Workflow Types (selected by Supervisor)
| Type | When used |
|------|-----------|
| `sequential` | Standard Q&A, summarisation |
| `parallel` | Multi-source retrieval tasks |
| `reflection` | Complex/nuanced queries needing high accuracy |

---

## 🔍 Retrieval Pipeline

1. **Embedding generation** — `text-embedding-3-small`
2. **Semantic search** — ChromaDB vector similarity
3. **BM25 keyword search** — on same document set
4. **Reciprocal Rank Fusion (RRF)** — combines both result lists
5. **Context selection** — top-K chunks passed to LLM

---

## 🛡️ Security Features

- Regex-based **prompt injection detection**
- **Harmful keyword filtering**
- **Input sanitisation** (control chars, length cap)
- **Tool-access control** (all tool calls gated through agent nodes)

---

## 📊 Evaluation

The **Reviewer Agent** checks every response for:
- **Faithfulness** — is the answer grounded in retrieved context?
- **Relevance** — does it answer the user's question?
- **Precision** — is unnecessary content minimised?
- **Hallucination** — were unsupported facts invented?
- **Safety** — is the response appropriate?

The **DeepEval** framework is integrated in `evaluation/evaluator.py` for deeper metric analysis. Falls back to lightweight heuristic evaluation if DeepEval is not available.

---

## 📈 Evaluation Criteria Mapping

| Criteria | Weight | Implementation |
|----------|--------|----------------|
| Multi-Agent Workflow Design | 30% | LangGraph graph with 7 agents, reflection loop |
| Security & Guardrails | 20% | Security agent with injection/harmful detection |
| Evaluation System | 25% | Reviewer agent + DeepEval integration |
| Retrieval Enhancements | 15% | Hybrid search (BM25 + semantic) + RRF |
| Innovation & Scalability | 10% | Reflection workflow, analytics, modular design |

---

## 🧩 Adding More Agents

To add a new agent (e.g., a Quiz Agent):

1. Create `agents/quiz_agent.py` with a function `quiz_agent(state: AgentState) -> AgentState`
2. Register it in `core/graph.py`: `builder.add_node("quiz", quiz_agent)`
3. Add routing edges as needed
4. Update `supervisor_agent.py` prompts to include `"quiz"` in `agents_to_run`

---

## 📦 Tech Stack

| Layer | Technology |
|-------|------------|
| Agent Framework | LangGraph |
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | ChromaDB |
| Keyword Search | BM25 (rank-bm25) |
| Evaluation | DeepEval |
| CLI | Rich |
| Environment | python-dotenv |
