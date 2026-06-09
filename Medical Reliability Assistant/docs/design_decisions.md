# Design Decisions & Trade-offs

## 1. Vector Database: Pinecone

**Decision:** Pinecone serverless over Chroma, Qdrant, or pgvector.

**Reasoning:**
- Serverless removes infrastructure management entirely — zero DevOps overhead for a 20k-vector index.
- Native metadata filtering enables pre-filtering by `equipment_type`, `hospital_unit`, `severity` before vector scoring, dramatically improving precision.
- Managed scaling; adding more datasets doesn't require provisioning.

**Trade-off:** Requires network call (latency ~30-80ms per query vs. ~1ms for embedded Chroma). Acceptable given that retrieval is one step in a multi-second agent pipeline. Pinecone also requires an account and API key, unlike Chroma's zero-setup.

---

## 2. Chunking: RecursiveCharacterTextSplitter (512 tokens, 64 overlap)

**Decision:** Recursive splitting at 512 chars with 64-char overlap.

**Reasoning:**
- Our incident narratives are ~200-400 chars, so most docs fit in one chunk — this preserves full semantic context per chunk.
- The recursive strategy tries paragraph → sentence → word boundaries in order, producing cleaner splits than fixed-size splitting.
- 64-char overlap ensures no information is lost at chunk boundaries.

**Trade-off:** Very short docs (like simple operational logs) produce one chunk that duplicates the full doc. This is correct behaviour; the overhead is negligible.

**Alternative considered:** Semantic chunking (split on embedding similarity drops). Rejected — adds latency and complexity without benefit for documents already near-sentence-size.

---

## 3. Hybrid Retrieval vs. Semantic-Only

**Decision:** BM25 (keyword) + Pinecone (vector) fused with Reciprocal Rank Fusion (k=60).

**Reasoning:**
- Semantic-only search misses on exact equipment model codes (e.g., "M14860"), failure acronyms (HDF, PWF, TWF), and unit names ("ICU-3") — all common in maintenance queries.
- BM25 catches exact technical terms; vector search catches synonyms and conceptual matches.
- RRF is parameter-light (one constant, k=60) and robust — it doesn't require tuning separate score scales for BM25 and cosine similarity, which operate on different numeric ranges.

**Trade-off:** Maintaining a BM25 corpus in memory (~20MB for 20k docs) adds startup time and memory footprint. This is acceptable for a single-host deployment.

---

## 4. Cross-Encoder Reranking

**Decision:** `cross-encoder/ms-marco-MiniLM-L-6-v2` applied to top-20 RRF results, returning top-5.

**Reasoning:**
- Bi-encoder (embedding) retrieval optimises for speed over precision; it encodes query and document independently. Cross-encoders see (query, document) together, enabling far more accurate relevance judgement.
- The 20→5 funnel means the expensive cross-encoder only scores 20 pairs per query, keeping p95 latency under 500ms.

**Trade-off:** Adds ~200-400ms latency and requires local GPU/CPU model (~60MB). For cloud deployment, this could be replaced with Cohere Rerank API.

---

## 5. Agent Orchestration: LangGraph Hierarchical Supervisor

**Decision:** LangGraph `StateGraph` with a supervisor node routing between four specialist agents.

**Reasoning:**
- Typed shared state (`AgentState` Pydantic model) gives compile-time safety and makes A2A communication explicit and inspectable.
- Conditional edges encode routing logic declaratively — easy to audit and extend.
- Built-in checkpoint support (SQLite) enables human-in-the-loop interruption without losing agent state.
- Hierarchical design (supervisor coordinates specialists) maps cleanly to the domain: different aspects of an equipment reliability question (retrieval, analysis, maintenance patterns, recommendation) benefit from separate, focused prompts.

**Alternative considered:** CrewAI, AutoGen. Rejected — both abstract away the state machine, making HITL interruption and checkpoint resumption harder to implement explicitly.

**Fallback mechanism:** Every agent node is wrapped in `_with_timeout()` which catches `asyncio.TimeoutError` and `Exception`, calls `state.trigger_fallback()`, and returns a degraded-but-safe state. The supervisor routes to a fallback compilation node if `state.fallback_triggered` and key outputs are empty.

---

## 6. Equipment Anomaly Correlation Strategy

**Decision:** Z-score statistical analysis on five sensor fields across retrieved incidents.

**Reasoning:**
- Z-score requires only mean and standard deviation — computable over the retrieved subset, not the full 20k-row corpus.
- Flagging at |z| > 2.5 (≈1.2% of a normal distribution) provides high specificity for genuine outliers.
- Results are immediately explainable: "Process temperature z-score = 3.1 (direction: high)" is interpretable by an engineer without ML knowledge.

**Enhancement path:** IQR-based detection for non-normal distributions (e.g., tool wear accumulation, which is monotonically increasing). Implemented in `anomaly_detector.py` as `detect_anomalies_from_params()`.

---

## 7. Operational Reliability Guardrails

**Input guardrails:**
1. Length bounds (5–1000 chars) — prevents empty/excessively long queries.
2. Injection pattern detection (regex) — blocks prompt injection attempts.
3. Topic relevance (Claude Haiku LLM classifier) — blocks off-topic queries with a fast, cheap model call.

**Output guardrails:**
1. Minimum length check — prevents empty recommendations reaching users.
2. Harmful pattern detection (regex) — blocks any output containing drug dosages, patient clinical diagnoses, or surgical recommendations beyond the system's scope.
3. Hallucination check (Claude Haiku) — flags "high" hallucination risk when recommendation makes claims unsupported by retrieved context.
4. Confidence calibration warning — adds user-visible warning when confidence < 60%.

**Design principle:** Input guardrails fail-open for LLM errors (topic classifier failure allows the query through — better to answer a borderline query than block a valid one). Output guardrails fail-safe (harmful content is always blocked, not passed through with a warning).

---

## 8. PII Middleware

Microsoft Presidio is the de-facto standard for PII detection in enterprise NLP. It recognises 40+ entity types (names, MRNs, phone numbers, emails, SSNs, locations) using NLP + pattern matching. Running as ASGI middleware means PII masking happens transparently before any downstream processing — the original query never reaches the agents, Pinecone, or the LLM.

Regex fallback ensures the system remains protective even if Presidio is unavailable.

---

## 9. LLM Model Selection

| Task | Model | Reasoning |
|------|-------|-----------|
| Final recommendation | Claude Sonnet | Highest quality synthesis; cost justified for final output |
| Correlation analysis | Claude Haiku | Fast, cheap; analytical structured task |
| Maintenance patterns | Claude Haiku | Summarisation task; doesn't need full Sonnet capability |
| Input topic classification | Claude Haiku | Binary classification; Haiku is sufficient |
| Hallucination check | Claude Haiku | Structured JSON output; fast |
| Evaluation judge | Claude Sonnet | Quality evaluation requires nuanced judgment |

This split reduces cost by ~4× vs. using Sonnet for all tasks.

---

## 10. Evaluation Methodology

**Standard metrics (DeepEval):**
- Answer Relevancy, Faithfulness, Context Precision/Recall/Relevancy, Answer Correctness.
- All run against 20 golden Q&A pairs (hand-crafted for domain correctness).

**Custom G-Eval metrics:**
- **Tone:** Checks for professional clinical engineering language — critical for a system used by biomedical engineers in safety-sensitive contexts.
- **Accuracy:** Validates that cited thresholds (temperature differentials, torque limits, wear thresholds) align with the retrieved context.
- **Conciseness:** Penalises over-long responses that obscure actionable guidance.

**LLM-as-judge:** Claude Sonnet scores each test case, chosen over GPT-4 for consistency with the system's primary model. Same model as judge introduces confirmation bias risk; mitigated by the structured DeepEval rubric and separate golden dataset.
