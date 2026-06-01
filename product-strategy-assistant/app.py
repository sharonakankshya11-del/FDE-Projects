"""AI-Powered Product Strategy Assistant — Streamlit app.

Run locally:   streamlit run app.py
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.chat import answer_question
from src.config import DATA_DIR, settings
from src.ingestion import ingest_files
from src.orchestrator import AGENT_PIPELINE, run_analysis
from src.report_generator import generate_report
from src.vector_store import VectorStore

st.set_page_config(page_title="AI Product Strategy Assistant", page_icon="🧭", layout="wide")

st.markdown(
    """
    <style>
      .block-container {padding-top: 2rem;}
      .kpi {background:#f1f5f9;border-radius:12px;padding:14px 16px;text-align:center;}
      .kpi h2 {margin:0;color:#2563eb;font-size:1.5rem;}
      .kpi p {margin:0;color:#64748b;font-size:.8rem;}
      .agent-done {color:#16a34a;} .agent-pending {color:#94a3b8;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- session state ----------
ss = st.session_state
ss.setdefault("ingested", None)
ss.setdefault("vstore", None)
ss.setdefault("insights", {})
ss.setdefault("messages", [])
ss.setdefault("report_path", None)


# ---------- sidebar ----------
with st.sidebar:
    st.title("🧭 Strategy Assistant")
    st.caption("Multi-agent product strategy from your business data.")

    if settings.has_api_key:
        st.success(f"AI online · `{settings.llm_model}`")
    else:
        st.warning(
            "No `OPENAI_API_KEY` found. The dashboard and analytics still work; "
            "add a key in `.env` for AI-generated reports & chat."
        )

    st.divider()
    st.subheader("1 · Upload data")
    uploads = st.file_uploader(
        "CSV (sales/usage), plus optional .txt/.md/.pdf/.docx (market & competitor docs)",
        type=["csv", "txt", "md", "pdf", "docx"],
        accept_multiple_files=True,
    )
    use_sample = st.checkbox("Use bundled sample sales data", value=not uploads)

    product_context = st.text_area(
        "Product / company context (optional)",
        placeholder="e.g. We sell consumer electronics across 5 regions; goal is to grow profit.",
        height=80,
    )

    if st.button("📥 Ingest data", use_container_width=True):
        files = []
        if uploads:
            files = [{"name": f.name, "content": f.read()} for f in uploads]
        elif use_sample:
            p = DATA_DIR / "Sample_Sales_Data.csv"
            files = [{"name": p.name, "content": p.read_bytes()}]
        if not files:
            st.error("Upload a file or tick the sample data box.")
        else:
            with st.spinner("Ingesting & indexing…"):
                data = ingest_files(files)
                vstore = VectorStore()
                vstore.add_documents(data.documents)
                ss.ingested = data
                ss.vstore = vstore
                ss.insights = {}
                ss.report_path = None
            st.success(f"Ingested {len(files)} file(s) · {vstore.size} chunks indexed.")


# ---------- header ----------
st.title("AI-Powered Product Strategy Assistant")
st.caption(
    "Upload business data → a team of AI agents analyses it → get insights, a strategy, "
    "and a downloadable executive report."
)

if ss.ingested is None:
    st.info("👈 Start by ingesting data in the sidebar (or tick the sample data box).")
    st.subheader("How it works")
    st.markdown(
        "1. **Ingest** sales/usage CSVs and optional market/competitor documents.\n"
        "2. **Run the multi-agent analysis** — 8 specialist agents collaborate over shared state.\n"
        "3. **Review** customer, market, competitor, SWOT, opportunity, feature & strategy reports.\n"
        "4. **Chat** with your data and **download** the executive PDF."
    )
    st.stop()


data = ss.ingested
if data is None:
    st.stop()
summary = data.structured_summary

tab_dash, tab_run, tab_reports, tab_chat = st.tabs(
    ["📊 Data Dashboard", "🤖 Run Analysis", "📑 Insight Reports", "💬 Chat"]
)

# ---------- dashboard ----------
with tab_dash:
    if summary:
        kpi_defs = [
            ("total_revenue", "Total Revenue", "${:,.0f}"),
            ("total_profit", "Total Profit", "${:,.0f}"),
            ("overall_margin_pct", "Margin", "{}%"),
            ("avg_rating", "Avg Rating", "{}/5"),
            ("return_rate_pct", "Return Rate", "{}%"),
            ("total_new_customers", "New Customers", "{:,}"),
        ]
        cols = st.columns(len([k for k, _, _ in kpi_defs if k in summary]) or 1)
        ci = 0
        for key, label, fmt in kpi_defs:
            if key in summary:
                val = summary[key]
                shown = fmt.format(val) if isinstance(val, (int, float)) else val
                cols[ci].markdown(f"<div class='kpi'><h2>{shown}</h2><p>{label}</p></div>",
                                  unsafe_allow_html=True)
                ci += 1
        st.divider()

        if data.has_sales_data:
            df = data.dataframe
            c1, c2 = st.columns(2)
            if {"Product_Name", "Revenue_USD"}.issubset(df.columns):
                rev = df.groupby("Product_Name")["Revenue_USD"].sum().sort_values(ascending=False)
                c1.plotly_chart(px.bar(rev, title="Revenue by Product",
                                       labels={"value": "Revenue ($)", "Product_Name": ""}),
                                use_container_width=True)
            if {"Category", "Revenue_USD"}.issubset(df.columns):
                cat = df.groupby("Category")["Revenue_USD"].sum()
                c2.plotly_chart(px.pie(values=cat.values, names=cat.index,
                                       title="Revenue by Category"), use_container_width=True)
            c3, c4 = st.columns(2)
            if {"Region", "Profit_USD"}.issubset(df.columns):
                reg = df.groupby("Region")["Profit_USD"].sum().sort_values(ascending=False)
                c3.plotly_chart(px.bar(reg, title="Profit by Region",
                                       labels={"value": "Profit ($)", "Region": ""}),
                                use_container_width=True)
            if {"Date", "Revenue_USD"}.issubset(df.columns):
                tmp = df.copy()
                tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")
                ts = tmp.groupby("Date")["Revenue_USD"].sum()
                c4.plotly_chart(px.line(ts, title="Revenue over time",
                                        labels={"value": "Revenue ($)", "Date": ""}),
                                use_container_width=True)
            if "sentiment_counts" in summary:
                sc = summary["sentiment_counts"]
                st.plotly_chart(px.bar(x=list(sc.keys()), y=list(sc.values()),
                                       title="Customer sentiment distribution",
                                       labels={"x": "", "y": "reviews"}),
                                use_container_width=True)
            with st.expander("View raw data"):
                st.dataframe(df, use_container_width=True)
    else:
        st.info("No structured sales metrics detected — text documents were ingested for chat/RAG.")

# ---------- run analysis ----------
with tab_run:
    st.subheader("Multi-agent pipeline")
    st.caption("8 specialist agents collaborate over a shared state to produce the reports.")
    agent_names = [a.name for a in AGENT_PIPELINE]

    if st.button("🚀 Run full analysis", type="primary", use_container_width=True,
                 disabled=not settings.has_api_key):
        state = {
            "structured_summary": summary,
            "documents": data.documents,
            "product_context": product_context,
            "trace": [],
        }
        status = st.empty()
        bar = st.progress(0)
        done = {"n": 0}

        def cb(node_name: str):
            done["n"] += 1
            bar.progress(min(done["n"] / len(agent_names), 1.0))
            status.markdown(f"✅ **{node_name}** completed")

        with st.spinner("Agents working…"):
            result = run_analysis(state, progress_cb=cb)
        ss.insights = {a.output_key: result.get(a.output_key, "") for a in AGENT_PIPELINE}
        bar.progress(1.0)
        status.success("Analysis complete — see the Insight Reports tab.")

    if not settings.has_api_key:
        st.warning("Add an `OPENAI_API_KEY` to `.env` to run the AI agents.")

    st.divider()
    st.markdown("**Agent status**")
    for a in AGENT_PIPELINE:
        ok = bool(ss.insights.get(a.output_key))
        icon = "🟢" if ok else "⚪"
        st.markdown(f"{icon} {a.name}")

# ---------- reports ----------
with tab_reports:
    if not ss.insights:
        st.info("Run the analysis first (Run Analysis tab).")
    else:
        label_map = [
            ("📝 Executive Summary", "executive_summary"),
            ("🗣️ Customer Insights", "customer_feedback"),
            ("📈 Market Research", "market_research"),
            ("🥊 Competitor Analysis", "competitor_analysis"),
            ("🧩 SWOT", "swot"),
            ("💡 Opportunities", "opportunities"),
            ("✅ Feature Prioritization", "feature_prioritization"),
            ("🧭 Strategy & Roadmap", "strategy"),
        ]
        for label, key in label_map:
            body = ss.insights.get(key)
            if body:
                with st.expander(label, expanded=(key == "executive_summary")):
                    st.markdown(body)

        st.divider()
        if st.button("📄 Generate downloadable PDF report", use_container_width=True):
            with st.spinner("Building PDF…"):
                path = generate_report(ss.insights, product_context, summary)
                ss.report_path = path
        if ss.report_path:
            with open(ss.report_path, "rb") as fh:
                st.download_button("⬇️ Download Executive Report (PDF)", fh,
                                   file_name="Product_Strategy_Report.pdf",
                                   mime="application/pdf", use_container_width=True)

# ---------- chat ----------
with tab_chat:
    st.subheader("Ask the assistant")
    st.caption("Context-aware answers grounded in your data and the generated reports.")
    for m in ss.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("e.g. Which product has the worst returns and what should we do?"):
        ss.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                reply = answer_question(prompt, ss.vstore, ss.insights)
            st.markdown(reply)
        ss.messages.append({"role": "assistant", "content": reply})
