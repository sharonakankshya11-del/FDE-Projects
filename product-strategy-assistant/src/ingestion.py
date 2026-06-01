"""Data ingestion and structured analysis.

Turns uploaded files (CSV sales/usage data + free-text docs such as market
research or competitor notes) into:
  * a structured analytics summary (computed directly, no LLM needed)
  * a list of text chunks with metadata, ready for the vector store
"""
from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

# Lightweight keyword sentiment for the structured layer. The Customer Feedback
# agent performs deeper LLM analysis on top of this.
POSITIVE_HINTS = [
    "excellent", "highly recommend", "very satisfied", "great value",
    "exceeded", "easy to use", "reliable", "good overall",
]
NEGATIVE_HINTS = [
    "not satisfied", "would not buy", "issues", "below expectations",
    "could be better", "poor", "disappointed",
]


def classify_sentiment(text: str) -> str:
    t = str(text).lower()
    if any(h in t for h in NEGATIVE_HINTS):
        return "negative"
    if any(h in t for h in POSITIVE_HINTS):
        return "positive"
    return "neutral"


@dataclass
class IngestedData:
    dataframe: Optional[pd.DataFrame] = None
    structured_summary: Dict[str, Any] = field(default_factory=dict)
    documents: List[Dict[str, Any]] = field(default_factory=list)  # {text, metadata}
    raw_text_sources: List[str] = field(default_factory=list)

    @property
    def has_sales_data(self) -> bool:
        return self.dataframe is not None and not self.dataframe.empty


def _read_csv(content: bytes) -> pd.DataFrame:
    return pd.read_csv(io.BytesIO(content))


def _extract_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""


def _extract_docx(content: bytes) -> str:
    try:
        import docx  # python-docx

        doc = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    except Exception:
        return ""


def _chunk(text: str, source: str, size: int = 900, overlap: int = 150) -> List[Dict[str, Any]]:
    text = " ".join(text.split())
    chunks, start, idx = [], 0, 0
    while start < len(text):
        piece = text[start : start + size]
        chunks.append({"text": piece, "metadata": {"source": source, "chunk": idx}})
        start += size - overlap
        idx += 1
    return chunks


def _summarise_sales(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute structured KPIs from a sales/analytics dataframe."""
    summary: Dict[str, Any] = {}
    cols = {c.lower(): c for c in df.columns}

    def col(name: str) -> Optional[str]:
        return cols.get(name.lower())

    rev, profit = col("revenue_usd"), col("profit_usd")
    cost, units = col("cost_usd"), col("units_sold")
    rating, returns = col("customer_rating"), col("returns")
    product, category = col("product_name"), col("category")
    region, date = col("region"), col("date")
    new_cust, mkt = col("new_customers"), col("marketing_spend_usd")
    review = col("review")

    summary["rows"] = int(len(df))
    if date:
        summary["date_range"] = [str(df[date].min()), str(df[date].max())]

    if rev:
        summary["total_revenue"] = round(float(df[rev].sum()), 2)
    if profit:
        summary["total_profit"] = round(float(df[profit].sum()), 2)
        if rev and df[rev].sum():
            summary["overall_margin_pct"] = round(100 * df[profit].sum() / df[rev].sum(), 1)
    if units:
        summary["total_units"] = int(df[units].sum())
    if returns and units and df[units].sum():
        summary["return_rate_pct"] = round(100 * df[returns].sum() / df[units].sum(), 2)
    if rating:
        summary["avg_rating"] = round(float(df[rating].mean()), 2)
    if mkt and rev and df[mkt].sum():
        summary["revenue_per_marketing_dollar"] = round(df[rev].sum() / df[mkt].sum(), 2)
    if new_cust:
        summary["total_new_customers"] = int(df[new_cust].sum())

    def top_table(group: str, value: str, n: int = 10) -> List[Dict[str, Any]]:
        g = df.groupby(group).agg(
            revenue=(value, "sum"),
            units=(units, "sum") if units else (value, "count"),
        )
        if profit:
            g["profit"] = df.groupby(group)[profit].sum()
            g["margin_pct"] = (100 * g["profit"] / g["revenue"]).round(1)
        if rating:
            g["avg_rating"] = df.groupby(group)[rating].mean().round(2)
        g = g.sort_values("revenue", ascending=False).head(n).round(2)
        return g.reset_index().to_dict(orient="records")

    if product and rev:
        summary["by_product"] = top_table(product, rev)
    if category and rev:
        summary["by_category"] = top_table(category, rev)
    if region and rev:
        summary["by_region"] = top_table(region, rev)

    # Sentiment distribution + worst-rated products
    if review:
        df = df.copy()
        df["_sentiment"] = df[review].apply(classify_sentiment)
        summary["sentiment_counts"] = df["_sentiment"].value_counts().to_dict()
    if product and rating:
        worst = (
            df.groupby(product)[rating].mean().sort_values().head(3).round(2).to_dict()
        )
        summary["lowest_rated_products"] = worst
    if product and returns:
        hi_ret = (
            df.groupby(product)[returns].sum().sort_values(ascending=False).head(3).to_dict()
        )
        summary["highest_return_products"] = {k: int(v) for k, v in hi_ret.items()}

    return summary


def _sales_to_documents(df: pd.DataFrame, summary: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build retrievable text documents from sales rows + aggregates."""
    docs: List[Dict[str, Any]] = []
    cols = {c.lower(): c for c in df.columns}
    review = cols.get("review")
    product = cols.get("product_name")
    rating = cols.get("customer_rating")
    region = cols.get("region")

    # One document per unique review tied to product/region/rating context.
    if review and product:
        seen = set()
        for _, row in df.iterrows():
            text = str(row[review]).strip()
            key = (str(row[product]), text)
            if not text or key in seen:
                continue
            seen.add(key)
            meta = {"source": "customer_review", "product": str(row[product])}
            ctx = f"Customer review for {row[product]}"
            if region:
                ctx += f" in the {row[region]} region"
            if rating:
                ctx += f" (rating {row[rating]}/5)"
            docs.append({"text": f"{ctx}: {text}", "metadata": meta})

    # Aggregate "fact" documents so the chatbot can answer KPI questions.
    facts = []
    for k in ("total_revenue", "total_profit", "overall_margin_pct", "avg_rating",
              "return_rate_pct", "total_units", "total_new_customers"):
        if k in summary:
            facts.append(f"{k.replace('_', ' ')}: {summary[k]}")
    for label in ("by_product", "by_category", "by_region"):
        for rec in summary.get(label, [])[:5]:
            facts.append(f"{label} -> {rec}")
    if facts:
        docs.append({"text": "Sales KPI summary. " + " | ".join(facts),
                     "metadata": {"source": "kpi_summary"}})
    return docs


def ingest_files(files: List[Dict[str, Any]]) -> IngestedData:
    """`files` is a list of {name, content(bytes)}."""
    data = IngestedData()
    for f in files:
        name = f["name"].lower()
        content = f["content"]
        if name.endswith(".csv"):
            df = _read_csv(content)
            data.dataframe = df if data.dataframe is None else data.dataframe
            data.structured_summary = _summarise_sales(df)
            data.documents += _sales_to_documents(df, data.structured_summary)
        elif name.endswith((".txt", ".md")):
            text = content.decode("utf-8", errors="ignore")
            data.raw_text_sources.append(text)
            data.documents += _chunk(text, f["name"])
        elif name.endswith(".pdf"):
            text = _extract_pdf(content)
            if text:
                data.raw_text_sources.append(text)
                data.documents += _chunk(text, f["name"])
        elif name.endswith(".docx"):
            text = _extract_docx(content)
            if text:
                data.raw_text_sources.append(text)
                data.documents += _chunk(text, f["name"])
    return data
