"""
run_eval_report.py
Runs evaluation queries across all 6 intents and writes results to
data/logs/eval_report.json
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from core.graph import run_query

TEST_CASES = [
    {
        "id": "TC-01",
        "intent_label": "explain_concept",
        "query": "Explain what a Transformer model is in deep learning.",
    },
    {
        "id": "TC-02",
        "intent_label": "generate_quiz",
        "query": "Generate a quiz on Retrieval-Augmented Generation (RAG).",
    },
    {
        "id": "TC-03",
        "intent_label": "summarize_document",
        "query": "Summarize the key ideas in the AI fundamentals document.",
    },
    {
        "id": "TC-04",
        "intent_label": "generate_notes",
        "query": "Create structured study notes on LangGraph multi-agent systems.",
    },
    {
        "id": "TC-05",
        "intent_label": "recommend_topics",
        "query": "Recommend what topics I should learn after understanding NLP basics.",
    },
    {
        "id": "TC-06",
        "intent_label": "general_question",
        "query": "What is the difference between supervised and unsupervised learning?",
    },
]

results = []
for tc in TEST_CASES:
    print(f"Running {tc['id']}: {tc['query'][:55]}...")
    t0 = time.time()
    try:
        state = run_query(tc["query"])
        elapsed = round(time.time() - t0, 2)
        results.append({
            "id":             tc["id"],
            "intent_label":   tc["intent_label"],
            "query":          tc["query"],
            "detected_intent": state.get("intent", "—"),
            "workflow_type":  state.get("workflow_type", "—"),
            "agents_to_run":  state.get("agents_to_run", []),
            "review_passed":  state.get("review_passed", False),
            "revision_count": state.get("revision_count", 0),
            "confidence_score": state.get("confidence_score", 0.0),
            "eval_scores":    state.get("eval_scores", {}),
            "sources_count":  len(state.get("sources", [])),
            "is_safe":        state.get("is_safe", True),
            "error":          state.get("error"),
            "latency_s":      elapsed,
        })
        es = state.get("eval_scores", {})
        print(f"  ✓ conf={state.get('confidence_score',0):.2f}  "
              f"faith={es.get('faithfulness',0):.2f}  "
              f"rel={es.get('relevance',0):.2f}  "
              f"passed={state.get('review_passed')}  {elapsed}s")
    except Exception as exc:
        elapsed = round(time.time() - t0, 2)
        print(f"  ✗ ERROR: {exc}")
        results.append({
            "id": tc["id"], "intent_label": tc["intent_label"],
            "query": tc["query"], "error": str(exc), "latency_s": elapsed,
        })

os.makedirs("data/logs", exist_ok=True)
with open("data/logs/eval_report.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n✅ Report saved to data/logs/eval_report.json")
