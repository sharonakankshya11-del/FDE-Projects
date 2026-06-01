"""Smoke + unit tests. Run with:  pytest -q"""
from pathlib import Path

from src.config import DATA_DIR
from src.ingestion import classify_sentiment, ingest_files
from src.orchestrator import AGENT_PIPELINE, run_analysis
from src.report_generator import generate_report
from src.vector_store import VectorStore


def _sample():
    p = DATA_DIR / "Sample_Sales_Data.csv"
    return ingest_files([{"name": p.name, "content": p.read_bytes()}])


def test_sentiment():
    assert classify_sentiment("Excellent product, highly recommend.") == "positive"
    assert classify_sentiment("Would not buy again.") == "negative"
    assert classify_sentiment("Works as expected.") == "neutral"


def test_ingestion_summary():
    data = _sample()
    s = data.structured_summary
    assert s["rows"] == 120
    assert s["total_revenue"] > 0
    assert "by_product" in s and len(s["by_product"]) > 0
    assert data.documents, "expected retrievable documents"


def test_vector_store_offline_search():
    data = _sample()
    vs = VectorStore()
    vs.add_documents(data.documents)
    hits = vs.search("returns and quality problems", k=3)
    assert isinstance(hits, list) and len(hits) > 0


def test_pipeline_runs_offline():
    """Without an API key, agents return the offline notice but the graph completes."""
    data = _sample()
    state = {
        "structured_summary": data.structured_summary,
        "documents": data.documents,
        "product_context": "test",
        "trace": [],
    }
    result = run_analysis(state)
    for agent in AGENT_PIPELINE:
        assert agent.output_key in result
    assert len(result.get("trace", [])) == len(AGENT_PIPELINE)


def test_report_generation(tmp_path):
    data = _sample()
    insights = {a.output_key: f"### {a.name}\n- point one\n- point two" for a in AGENT_PIPELINE}
    path = generate_report(insights, "test ctx", data.structured_summary,
                           filename="test_report.pdf")
    assert Path(path).exists() and Path(path).stat().st_size > 1000
