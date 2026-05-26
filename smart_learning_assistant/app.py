"""
app.py  —  Smart Learning Assistant  |  Beautiful Streamlit UI
Hierarchical Multi-Agent Workflow  ·  LangGraph + GPT-4o-mini
Tabs: Chat  |  📊 Evaluation Report
"""

import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from core.graph import run_query
from evaluation.evaluator import evaluate_response

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem 2rem !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0f172a 0%,#1e1b4b 50%,#0f172a 100%);
    border-right: 1px solid rgba(255,255,255,0.08);
}
[data-testid="stSidebar"] * { color:#e2e8f0 !important; }
[data-testid="stSidebarContent"] { padding:1.5rem 1.2rem; }

/* Hero */
.hero {
    background:linear-gradient(135deg,#0f172a 0%,#1e1b4b 40%,#312e81 100%);
    border-radius:16px; padding:1.6rem 2rem; margin-bottom:1.4rem;
    border:1px solid rgba(99,102,241,0.3);
    box-shadow:0 4px 32px rgba(99,102,241,0.15);
}
.hero h1 { margin:0; font-size:1.7rem; font-weight:700;
    background:linear-gradient(90deg,#a5b4fc,#e879f9,#38bdf8);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hero p  { margin:6px 0 0 0; color:#94a3b8; font-size:0.92rem; }

/* Pipeline strip */
.pipeline {
    display:flex; align-items:center; gap:6px;
    background:rgba(15,23,42,0.6);
    border:1px solid rgba(255,255,255,0.08);
    border-radius:10px; padding:10px 16px; margin-bottom:1.2rem; flex-wrap:wrap;
}
.pipe-node {
    background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.35);
    border-radius:20px; padding:4px 12px;
    font-size:0.78rem; font-weight:600; color:#a5b4fc; white-space:nowrap;
}
.pipe-arrow { color:#475569; font-size:0.85rem; }
.pipe-node.active {
    background:rgba(99,102,241,0.35); border-color:#6366f1; color:#e0e7ff;
    box-shadow:0 0 12px rgba(99,102,241,0.4);
}

/* Chat bubbles */
.msg-user { display:flex; justify-content:flex-end; }
.msg-user .bubble {
    background:linear-gradient(135deg,#4f46e5,#7c3aed); color:#fff;
    border-radius:18px 18px 4px 18px; padding:12px 18px; max-width:72%;
    font-size:0.93rem; box-shadow:0 4px 16px rgba(79,70,229,0.35); line-height:1.55;
}
.msg-ai { display:flex; align-items:flex-start; gap:12px; }
.ai-avatar {
    width:38px; height:38px; border-radius:50%; flex-shrink:0;
    background:linear-gradient(135deg,#0ea5e9,#6366f1);
    display:flex; align-items:center; justify-content:center;
    font-size:1.1rem; box-shadow:0 2px 10px rgba(14,165,233,0.4);
}
.msg-ai .bubble {
    background:#1e293b; border:1px solid rgba(255,255,255,0.08); color:#e2e8f0;
    border-radius:4px 18px 18px 18px; padding:14px 18px; max-width:80%;
    font-size:0.93rem; box-shadow:0 4px 20px rgba(0,0,0,0.25); line-height:1.6;
}

/* Meta card */
.meta-card {
    background:rgba(15,23,42,0.8); border:1px solid rgba(99,102,241,0.2);
    border-radius:12px; padding:14px 18px; margin-top:10px;
}
.meta-row { display:flex; gap:20px; flex-wrap:wrap; margin-bottom:10px; align-items:center; }

/* Badges */
.badge { display:inline-flex; align-items:center; gap:5px;
    padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:600; }
.badge-intent   { background:rgba(59,130,246,0.18); color:#93c5fd; border:1px solid rgba(59,130,246,0.3); }
.badge-workflow { background:rgba(16,185,129,0.18); color:#6ee7b7; border:1px solid rgba(16,185,129,0.3); }
.badge-agent    { background:rgba(168,85,247,0.18); color:#d8b4fe; border:1px solid rgba(168,85,247,0.3); }
.badge-pass     { background:rgba(34,197,94,0.18);  color:#86efac; border:1px solid rgba(34,197,94,0.3); }
.badge-fail     { background:rgba(239,68,68,0.18);  color:#fca5a5; border:1px solid rgba(239,68,68,0.3); }

/* Score bars */
.score-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin-top:8px; }
.score-item { text-align:center; }
.score-label { font-size:0.68rem; color:#64748b; text-transform:uppercase; letter-spacing:.05em; margin-bottom:4px; }
.score-val   { font-size:1.1rem; font-weight:700; }
.score-bar   { height:4px; border-radius:2px; background:rgba(255,255,255,0.07); margin-top:4px; overflow:hidden; }
.score-fill  { height:100%; border-radius:2px; }

/* DeepEval section */
.deepeval-section {
    margin-top:10px; padding-top:10px;
    border-top:1px solid rgba(99,102,241,0.15);
}
.deepeval-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-top:6px; }
.deepeval-item {
    background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.2);
    border-radius:8px; padding:10px; text-align:center;
}
.deepeval-metric { font-size:0.68rem; color:#64748b; text-transform:uppercase; letter-spacing:.06em; margin-bottom:4px; }
.deepeval-val    { font-size:1.3rem; font-weight:800; }
.deepeval-status { font-size:0.7rem; margin-top:2px; }

/* Guardrail checks */
.guardrail-section {
    margin-top:10px; padding:10px 12px;
    border-radius:8px; border:1px solid rgba(255,255,255,0.07);
}
.guardrail-section.input-g  { background:rgba(14,165,233,0.06); border-color:rgba(14,165,233,0.2); }
.guardrail-section.output-g { background:rgba(234,179,8,0.05);  border-color:rgba(234,179,8,0.2); }
.guardrail-title { font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:.1em; margin-bottom:8px; }
.guardrail-title.input-g  { color:#38bdf8; }
.guardrail-title.output-g { color:#fbbf24; }
.guardrail-grid { display:flex; flex-wrap:wrap; gap:6px; }
.g-check {
    display:inline-flex; align-items:center; gap:4px;
    padding:3px 9px; border-radius:12px; font-size:0.72rem; font-weight:500;
}
.g-check.pass { background:rgba(34,197,94,0.12); color:#86efac; border:1px solid rgba(34,197,94,0.25); }
.g-check.fail { background:rgba(239,68,68,0.12);  color:#fca5a5; border:1px solid rgba(239,68,68,0.25); }
.g-check.warn { background:rgba(234,179,8,0.12);  color:#fde68a; border:1px solid rgba(234,179,8,0.25); }

/* Report cards */
.report-card {
    background:#1e293b; border:1px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:16px 20px; margin-bottom:12px;
}
.report-card-pass { border-left:4px solid #22c55e; }
.report-card-fail { border-left:4px solid #ef4444; }

/* Stat tiles */
.stat-tile {
    background:linear-gradient(135deg,rgba(99,102,241,0.12),rgba(139,92,246,0.08));
    border:1px solid rgba(99,102,241,0.25); border-radius:12px;
    padding:18px 16px; text-align:center;
}
.stat-num   { font-size:2rem; font-weight:800; }
.stat-label { font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:.08em; margin-top:2px; }

/* Conf */
.conf-block { display:flex; flex-direction:column; align-items:center; }
.conf-num   { font-size:1.6rem; font-weight:800; }
.conf-lbl   { font-size:0.7rem; color:#64748b; letter-spacing:.08em; text-transform:uppercase; }

/* Source chip */
.source-chip {
    display:inline-block; background:rgba(14,165,233,0.12);
    border:1px solid rgba(14,165,233,0.25); border-radius:6px;
    padding:3px 10px; font-size:0.75rem; color:#7dd3fc; margin:2px;
}

/* Welcome */
.welcome {
    background:rgba(15,23,42,0.7); border:1px dashed rgba(99,102,241,0.3);
    border-radius:16px; padding:2rem; text-align:center; color:#94a3b8;
}
.welcome h3 { color:#a5b4fc; margin-bottom:.5rem; }

/* Input */
[data-testid="stChatInput"] textarea {
    background:#1e293b !important; border:1px solid rgba(99,102,241,0.4) !important;
    border-radius:12px !important; color:#e2e8f0 !important;
}
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-thumb { background:rgba(99,102,241,0.4); border-radius:3px; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("messages", []), ("history", []), ("example_query", "")]:
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:0.5rem 0 1.2rem'>
        <div style='font-size:2.8rem'>🎓</div>
        <div style='font-size:1.1rem;font-weight:700;color:#a5b4fc'>Smart Learning</div>
        <div style='font-size:0.78rem;color:#475569;margin-top:2px'>Hierarchical Multi-Agent AI</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='color:#6366f1;font-size:0.72rem;font-weight:700;letter-spacing:.1em;margin-bottom:8px'>⬡ AGENT HIERARCHY</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);border-radius:10px;padding:12px 14px;font-size:0.8rem;line-height:2;color:#94a3b8'>
        🔒 <b style='color:#38bdf8'>Input Guardrail</b> — 6 input checks<br>
        &nbsp;&nbsp;&nbsp;<span style='font-size:0.72rem;color:#475569'>length · injection · harmful · PII · profanity · topic</span><br>
        🧠 <b style='color:#a5b4fc'>Supervisor</b> — intent &amp; routing<br>
        &nbsp;&nbsp;&nbsp;↳ 📚 <b style='color:#c4b5fd'>Retrieval</b> — semantic search<br>
        &nbsp;&nbsp;&nbsp;↳ ✍️ <b style='color:#c4b5fd'>Generation</b> — LLM answer<br>
        &nbsp;&nbsp;&nbsp;↳ 🔍 <b style='color:#c4b5fd'>Reviewer</b> — quality check<br>
        &nbsp;&nbsp;&nbsp;↳ 📤 <b style='color:#c4b5fd'>Response</b> — final assembly<br>
        🔒 <b style='color:#fbbf24'>Output Guardrail</b> — 6 output checks<br>
        &nbsp;&nbsp;&nbsp;<span style='font-size:0.72rem;color:#475569'>PII · toxicity · confidence · length · hallucination · disclaimer</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='color:#6366f1;font-size:0.72rem;font-weight:700;letter-spacing:.1em;margin:16px 0 8px'>💡 TRY THESE</div>", unsafe_allow_html=True)
    examples = [
        ("📖", "Explain what a Transformer model is"),
        ("📝", "Generate a quiz on Retrieval-Augmented Generation"),
        ("📄", "Summarize AI fundamentals document"),
        ("🗒️", "Create study notes on LangGraph agents"),
        ("🗺️", "Recommend topics after learning NLP basics"),
    ]
    for icon, ex in examples:
        if st.button(f"{icon}  {ex}", key=f"ex_{ex[:15]}", use_container_width=True):
            st.session_state["example_query"] = ex

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    if st.button("🗑️  Clear Conversation", use_container_width=True, type="secondary"):
        st.session_state["messages"] = []
        st.session_state["history"]  = []
        st.rerun()

    st.markdown("""
    <div style='margin-top:2rem;padding-top:1.2rem;border-top:1px solid rgba(255,255,255,0.06);
                font-size:0.72rem;color:#334155;text-align:center;line-height:1.8'>
        LangGraph · GPT-4o-mini · ChromaDB<br>
        <span style='color:#4f46e5'>Hierarchical Workflow</span>
    </div>""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎓 Smart Learning Assistant</h1>
    <p>Hierarchical Multi-Agent pipeline &nbsp;·&nbsp;
       Explain · Quiz · Summarize · Notes · Recommend</p>
</div>""", unsafe_allow_html=True)

st.markdown("""
<div class="pipeline">
    <span class="pipe-node" style="border-color:rgba(14,165,233,0.5);color:#38bdf8">🔒 Input Guard</span>
    <span class="pipe-arrow">→</span>
    <span class="pipe-node active">🧠 Supervisor</span><span class="pipe-arrow">→</span>
    <span class="pipe-node">📚 Retrieval</span><span class="pipe-arrow">→</span>
    <span class="pipe-node">✍️ Generation</span><span class="pipe-arrow">→</span>
    <span class="pipe-node">🔍 Reviewer</span><span class="pipe-arrow">→</span>
    <span class="pipe-node">📤 Response</span><span class="pipe-arrow">→</span>
    <span class="pipe-node" style="border-color:rgba(234,179,8,0.5);color:#fbbf24">🔒 Output Guard</span>
</div>""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_chat, tab_eval, tab_arch = st.tabs(["💬  Chat", "📊  Evaluation Report", "🏗️  Architecture"])


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def score_color(v: float) -> str:
    if v >= 0.80: return "#22c55e"
    if v >= 0.60: return "#f59e0b"
    return "#ef4444"


def render_guardrail_section(title: str, css_cls: str, checks: dict):
    """Render a guardrail check grid (input or output)."""
    if not checks:
        return
    pills = ""
    for name, result in checks.items():
        ok      = result.get("passed", True)
        detail  = result.get("detail", "")
        label   = name.replace("_", " ").title()
        # PII redaction: warn (not hard fail) — show in amber
        if name == "pii_leakage" and not ok:
            cls = "warn"
        elif name == "disclaimer":
            cls = "pass"
        else:
            cls = "pass" if ok else "fail"
        icon = "✓" if ok else ("⚠" if cls == "warn" else "✗")
        pills += f'<span class="g-check {cls}" title="{detail}">{icon} {label}</span>'
    st.markdown(f"""
    <div class="guardrail-section {css_cls}">
        <div class="guardrail-title {css_cls}">🔒 {title}</div>
        <div class="guardrail-grid">{pills}</div>
    </div>""", unsafe_allow_html=True)


def render_meta(meta: dict):
    """Render the per-response metadata + reviewer + DeepEval + guardrail cards."""
    intent   = meta.get("intent", "—")
    wf       = meta.get("workflow", "hierarchical")
    conf     = meta.get("confidence", 0.0)
    agents   = meta.get("agents_run", [])
    scores   = meta.get("eval_scores", {})       # reviewer scores
    deep     = meta.get("deepeval_scores", {})   # DeepEval scores
    sources  = meta.get("sources", [])
    passed   = meta.get("review_passed", False)
    in_checks  = meta.get("input_guardrail_checks", {})
    out_checks = meta.get("output_guardrail_checks", {})

    conf_color = score_color(conf)
    agent_pills = "".join(f'<span class="badge badge-agent">✓ {a}</span> ' for a in agents)
    source_chips = "".join(f'<span class="source-chip">📄 {s}</span>' for s in sources) \
                   if sources else "<span style='color:#475569;font-size:0.78rem'>no documents retrieved</span>"

    # Reviewer score bars
    scores_html = ""
    for label, val in scores.items():
        col = score_color(val)
        scores_html += f"""
        <div class="score-item">
            <div class="score-label">{label}</div>
            <div class="score-val" style="color:{col}">{val:.2f}</div>
            <div class="score-bar"><div class="score-fill" style="width:{int(val*100)}%;background:{col}"></div></div>
        </div>"""

    # DeepEval metric cards
    DEEP_THRESHOLDS = {"faithfulness":0.6,"answerrelevancy":0.6,"contextualrelevancy":0.5}
    deep_html = ""
    for metric, val in deep.items():
        col   = score_color(val)
        thr   = DEEP_THRESHOLDS.get(metric, 0.6)
        ok    = val >= thr
        icon  = "✅" if ok else "❌"
        label = metric.replace("answerrelevancy","Answer Relevancy") \
                      .replace("contextualrelevancy","Ctx Relevancy") \
                      .replace("faithfulness","Faithfulness")
        deep_html += f"""
        <div class="deepeval-item">
            <div class="deepeval-metric">{label}</div>
            <div class="deepeval-val" style="color:{col}">{val:.2f}</div>
            <div class="deepeval-status">{icon} {'PASS' if ok else 'FAIL'} (thr {thr})</div>
        </div>"""

    pass_badge = ('pass' if passed else 'fail')
    pass_label = ('✅ PASS' if passed else '❌ FAIL')

    st.markdown(f"""
    <div class="meta-card">
      <div class="meta-row">
        <div>
          <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">Intent</div>
          <span class="badge badge-intent">🎯 {intent.replace("_"," ")}</span>
        </div>
        <div>
          <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">Workflow</div>
          <span class="badge badge-workflow">⬡ {wf}</span>
        </div>
        <div>
          <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">Review</div>
          <span class="badge badge-{pass_badge}">{pass_label}</span>
        </div>
        <div class="conf-block">
          <div class="conf-num" style="color:{conf_color}">{conf:.0%}</div>
          <div class="conf-lbl">Confidence</div>
        </div>
      </div>

      <div style="margin-bottom:8px">
        <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Agents Delegated by Supervisor</div>
        {agent_pills}
      </div>

      <div style="margin-bottom:12px">
        <div style="font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">Sources</div>
        {source_chips}
      </div>

      {'<div><div style="font-size:0.68rem;color:#94a3b8;font-weight:600;margin-bottom:6px">🔍 Reviewer Scores</div><div class="score-grid">' + scores_html + '</div></div>' if scores else ''}

      {'<div class="deepeval-section"><div style="font-size:0.68rem;color:#94a3b8;font-weight:600;margin-bottom:6px">🧪 DeepEval Metrics</div><div class="deepeval-grid">' + deep_html + '</div></div>' if deep_html else ''}
    </div>
    """, unsafe_allow_html=True)

    # Guardrail panels (rendered outside the card for visual separation)
    if in_checks:
        render_guardrail_section("Input Guardrail Checks", "input-g", in_checks)
    if out_checks:
        render_guardrail_section("Output Guardrail Checks", "output-g", out_checks)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ═══════════════════════════════════════════════════════════════════════════════

with tab_chat:

    if not st.session_state["messages"]:
        st.markdown("""
        <div class="welcome">
            <h3>👋 Welcome! Ask me anything to learn.</h3>
            <p style="font-size:0.88rem">I can <b style="color:#a5b4fc">explain concepts</b>,
            generate <b style="color:#a5b4fc">quizzes</b>,
            <b style="color:#a5b4fc">summarize documents</b>,
            create <b style="color:#a5b4fc">study notes</b>, or
            <b style="color:#a5b4fc">recommend topics</b>.<br>
            Use the sidebar examples or type your question below.</p>
        </div>""", unsafe_allow_html=True)
    else:
        for msg in st.session_state["messages"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="msg-user"><div class="bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="msg-ai"><div class="ai-avatar">🤖</div><div class="bubble">{msg["content"]}</div></div>', unsafe_allow_html=True)
                if "meta" in msg and msg["meta"]:
                    render_meta(msg["meta"])
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    prefill    = st.session_state.pop("example_query", "") or ""
    user_input = st.chat_input("Ask a learning question…") or prefill

    if user_input:
        st.markdown(f'<div class="msg-user"><div class="bubble">{user_input}</div></div>', unsafe_allow_html=True)
        st.session_state["messages"].append({"role": "user", "content": user_input})

        with st.spinner("🧠 Supervisor routing agents…"):
            try:
                result = run_query(user_input, history=st.session_state["history"])

                final   = result.get("final_response", "")
                intent  = result.get("intent", "general_question")
                wf_type = result.get("workflow_type", "hierarchical")
                agents  = result.get("agents_to_run", [])
                conf    = result.get("confidence_score", 0.0)
                scores  = result.get("eval_scores", {})
                sources = result.get("sources", [])
                passed  = result.get("review_passed", False)
                ctx     = result.get("retrieval_context", "")
                err     = result.get("error")
                response_text = final if not err else f"⚠️ {err}"

                # ── DeepEval (fallback heuristic, fast) ───────────────────────
                deep_scores = {}
                try:
                    de = evaluate_response(user_input, response_text, ctx)
                    deep_scores = de.get("scores", {})
                except Exception:
                    pass

                path_agents = ["input_guardrail", "supervisor"] + agents + ["output_guardrail"]
                meta = {
                    "intent":    intent,   "workflow":      wf_type,
                    "confidence": conf,    "agents_run":    path_agents,
                    "eval_scores": scores, "deepeval_scores": deep_scores,
                    "sources":   sources,  "review_passed": passed,
                    "input_guardrail_checks":  result.get("input_guardrail_checks", {}),
                    "output_guardrail_checks": result.get("output_guardrail_checks", {}),
                    "output_guardrail_passed": result.get("output_guardrail_passed", True),
                }

            except Exception as exc:
                response_text = f"❌ Pipeline error: {exc}"
                meta = {}

        st.markdown(f'<div class="msg-ai"><div class="ai-avatar">🤖</div><div class="bubble">{response_text}</div></div>', unsafe_allow_html=True)
        if meta:
            render_meta(meta)

        st.session_state["messages"].append({"role":"assistant","content":response_text,"meta":meta})
        st.session_state["history"].extend([
            {"role":"user","content":user_input},
            {"role":"assistant","content":response_text},
        ])
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EVALUATION REPORT
# ═══════════════════════════════════════════════════════════════════════════════

with tab_eval:

    REPORT_PATH = os.path.join(os.path.dirname(__file__), "data/logs/eval_report.json")

    if not os.path.exists(REPORT_PATH):
        st.warning("⚠️ No evaluation report found. Run `python run_eval_report.py` first.")
        st.stop()

    with open(REPORT_PATH) as f:
        report = json.load(f)

    # ── Aggregate stats ───────────────────────────────────────────────────────
    total       = len(report)
    passed_list = [r for r in report if r.get("review_passed")]
    failed_list = [r for r in report if not r.get("review_passed")]
    pass_rate   = len(passed_list) / total if total else 0

    all_conf    = [r.get("confidence_score", 0) for r in report]
    avg_conf    = sum(all_conf) / len(all_conf) if all_conf else 0

    all_lat     = [r.get("latency_s", 0) for r in report]
    avg_lat     = sum(all_lat) / len(all_lat) if all_lat else 0

    metric_keys = ["faithfulness", "relevance", "precision", "hallucination", "safety"]
    avg_metrics = {}
    for mk in metric_keys:
        vals = [r.get("eval_scores", {}).get(mk, 0) for r in report if r.get("eval_scores")]
        avg_metrics[mk] = round(sum(vals) / len(vals), 3) if vals else 0.0

    # ── Intent accuracy ───────────────────────────────────────────────────────
    correct_intent = sum(1 for r in report if r.get("detected_intent") == r.get("intent_label"))
    intent_accuracy = correct_intent / total if total else 0

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='margin-bottom:1.2rem'>
        <div style='font-size:1.4rem;font-weight:700;color:#a5b4fc'>📊 Evaluation Report</div>
        <div style='color:#475569;font-size:0.85rem;margin-top:2px'>
            Hierarchical Workflow · 6 test cases · Reviewer + DeepEval metrics
        </div>
    </div>""", unsafe_allow_html=True)

    # ── KPI tiles ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    tiles = [
        (c1, f"{len(passed_list)}/{total}", "Tests Passed",  "#22c55e"),
        (c2, f"{pass_rate:.0%}",            "Pass Rate",     "#22c55e" if pass_rate >= 0.8 else "#f59e0b"),
        (c3, f"{avg_conf:.0%}",             "Avg Confidence",score_color(avg_conf)),
        (c4, f"{intent_accuracy:.0%}",      "Intent Accuracy",score_color(intent_accuracy)),
        (c5, f"{avg_lat:.1f}s",             "Avg Latency",   "#38bdf8"),
    ]
    for col, num, lbl, col_hex in tiles:
        with col:
            st.markdown(f"""
            <div class="stat-tile">
                <div class="stat-num" style="color:{col_hex}">{num}</div>
                <div class="stat-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── Average metric bars ───────────────────────────────────────────────────
    st.markdown("<div style='font-size:0.9rem;font-weight:600;color:#94a3b8;margin-bottom:8px'>🔍 Reviewer — Average Scores Across All Tests</div>", unsafe_allow_html=True)

    metric_cols = st.columns(len(avg_metrics))
    for i, (mk, mv) in enumerate(avg_metrics.items()):
        col_hex = score_color(mv)
        with metric_cols[i]:
            st.markdown(f"""
            <div style='text-align:center;background:rgba(15,23,42,0.6);border:1px solid rgba(255,255,255,0.07);
                        border-radius:10px;padding:12px 8px'>
                <div style='font-size:0.68rem;color:#475569;text-transform:uppercase;letter-spacing:.07em'>{mk}</div>
                <div style='font-size:1.6rem;font-weight:800;color:{col_hex}'>{mv:.2f}</div>
                <div style='height:5px;background:rgba(255,255,255,0.06);border-radius:3px;margin-top:6px;overflow:hidden'>
                    <div style='height:100%;width:{int(mv*100)}%;background:{col_hex};border-radius:3px'></div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    # ── DeepEval aggregate ────────────────────────────────────────────────────
    st.markdown("<div style='font-size:0.9rem;font-weight:600;color:#94a3b8;margin-bottom:8px'>🧪 DeepEval — Metrics Thresholds Reference</div>", unsafe_allow_html=True)
    DEEP_THRESHOLDS = {"faithfulness": 0.6, "answerrelevancy": 0.6, "contextualrelevancy": 0.5}
    deep_cols = st.columns(3)
    deep_labels = {"faithfulness":"Faithfulness","answerrelevancy":"Answer Relevancy","contextualrelevancy":"Contextual Relevancy"}
    for i, (metric, thr) in enumerate(DEEP_THRESHOLDS.items()):
        with deep_cols[i]:
            passing = [r for r in report if r.get("eval_scores", {}).get("faithfulness",0) >= thr]
            rate = len(passing) / total if total else 0
            col_hex = score_color(rate)
            st.markdown(f"""
            <div class="deepeval-item" style="padding:14px">
                <div style='font-size:0.7rem;color:#6366f1;font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px'>
                    🧪 {deep_labels[metric]}
                </div>
                <div style='font-size:1.4rem;font-weight:800;color:{col_hex}'>{rate:.0%}</div>
                <div style='font-size:0.72rem;color:#475569;margin-top:4px'>Pass Rate at threshold ≥ {thr}</div>
                <div style='height:4px;background:rgba(255,255,255,0.06);border-radius:2px;margin-top:8px;overflow:hidden'>
                    <div style='height:100%;width:{int(rate*100)}%;background:{col_hex};border-radius:2px'></div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    # ── Per-test-case cards ───────────────────────────────────────────────────
    st.markdown("<div style='font-size:0.9rem;font-weight:600;color:#94a3b8;margin-bottom:10px'>📋 Per Test Case Results</div>", unsafe_allow_html=True)

    for r in report:
        review_passed = r.get("review_passed", False)
        card_cls = "report-card-pass" if review_passed else "report-card-fail"
        conf     = r.get("confidence_score", 0.0)
        conf_c   = score_color(conf)
        es       = r.get("eval_scores", {})
        detected = r.get("detected_intent", "—")
        expected = r.get("intent_label", "—")
        intent_ok = detected == expected
        agents   = r.get("agents_to_run", [])

        score_bars = ""
        for mk, mv in es.items():
            c = score_color(mv)
            score_bars += f"""
            <div style='text-align:center'>
                <div style='font-size:0.62rem;color:#475569;text-transform:uppercase;letter-spacing:.05em'>{mk}</div>
                <div style='font-size:0.9rem;font-weight:700;color:{c}'>{mv:.2f}</div>
            </div>"""

        agent_pills = "".join(f'<span class="badge badge-agent" style="font-size:0.68rem;padding:2px 8px">✓ {a}</span> ' for a in agents)

        st.markdown(f"""
        <div class="report-card {card_cls}">
            <div style='display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px'>
                <div>
                    <span style='font-size:0.72rem;color:#6366f1;font-weight:700'>{r["id"]}</span>
                    <span style='font-size:0.72rem;color:#475569;margin-left:8px'>{r.get("latency_s","—")}s</span>
                    <div style='font-size:0.9rem;color:#e2e8f0;font-weight:500;margin-top:4px'>{r["query"]}</div>
                </div>
                <div style='text-align:right;flex-shrink:0;margin-left:16px'>
                    <span class="badge badge-{'pass' if review_passed else 'fail'}">{'✅ PASS' if review_passed else '❌ FAIL'}</span>
                    <div style='font-size:1.4rem;font-weight:800;color:{conf_c};margin-top:4px'>{conf:.0%}</div>
                    <div style='font-size:0.65rem;color:#475569'>confidence</div>
                </div>
            </div>
            <div style='display:flex;gap:16px;align-items:center;margin-bottom:8px;flex-wrap:wrap'>
                <div>
                    <span style='font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:.07em'>Expected Intent</span>
                    <span class="badge badge-intent" style='margin-left:6px;font-size:0.68rem'>🎯 {expected.replace("_"," ")}</span>
                </div>
                <div>
                    <span style='font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:.07em'>Detected Intent</span>
                    <span class="badge {'badge-pass' if intent_ok else 'badge-fail'}" style='margin-left:6px;font-size:0.68rem'>
                        {'✅' if intent_ok else '❌'} {detected.replace("_"," ")}
                    </span>
                </div>
                <div>
                    <span style='font-size:0.65rem;color:#475569;text-transform:uppercase;letter-spacing:.07em'>Agents</span>
                    <span style='margin-left:6px'>{agent_pills}</span>
                </div>
            </div>
            <div style='display:flex;gap:16px;flex-wrap:wrap'>{score_bars}</div>
        </div>""", unsafe_allow_html=True)

    # ── Summary table ─────────────────────────────────────────────────────────
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.9rem;font-weight:600;color:#94a3b8;margin-bottom:8px'>📑 Summary Table</div>", unsafe_allow_html=True)

    import pandas as pd
    rows = []
    for r in report:
        es = r.get("eval_scores", {})
        rows.append({
            "ID":         r["id"],
            "Intent (expected)": r.get("intent_label","—"),
            "Intent (detected)": r.get("detected_intent","—"),
            "Workflow":   r.get("workflow_type","—"),
            "Confidence": f"{r.get('confidence_score',0):.0%}",
            "Faithfulness": f"{es.get('faithfulness',0):.2f}",
            "Relevance":    f"{es.get('relevance',0):.2f}",
            "Precision":    f"{es.get('precision',0):.2f}",
            "Hallucination":f"{es.get('hallucination',0):.2f}",
            "Safety":       f"{es.get('safety',0):.2f}",
            "Review":       "✅ PASS" if r.get("review_passed") else "❌ FAIL",
            "Latency (s)":  r.get("latency_s","—"),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Download ──────────────────────────────────────────────────────────────
    st.download_button(
        label="⬇️  Download Full Report (JSON)",
        data=json.dumps(report, indent=2),
        file_name="eval_report.json",
        mime="application/json",
        use_container_width=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════════

with tab_arch:

    st.markdown("""
    <div style='margin-bottom:1.2rem'>
        <div style='font-size:1.4rem;font-weight:700;color:#a5b4fc'>🏗️ System Architecture</div>
        <div style='color:#475569;font-size:0.85rem;margin-top:2px'>
            Hierarchical Multi-Agent Workflow · LangGraph · GPT-4o-mini · ChromaDB
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Full pipeline diagram ─────────────────────────────────────────────────
    st.markdown("""
<style>
.arch-wrap  { font-family:'Inter',sans-serif; color:#e2e8f0; }
.arch-row   { display:flex; align-items:stretch; gap:0; margin:0; }
.arch-col   { display:flex; flex-direction:column; align-items:center; }
.arch-arrow-v  { color:#475569; font-size:1.1rem; line-height:1; margin:2px 0; text-align:center; }
.arch-arrow-h  { color:#475569; font-size:1rem; align-self:center; padding:0 4px; }

/* Node boxes */
.anode {
    border-radius:10px; padding:10px 16px; text-align:center;
    font-size:0.82rem; font-weight:600; min-width:130px;
    border:1px solid; position:relative;
}
.anode-user     { background:rgba(99,102,241,0.15); border-color:rgba(99,102,241,0.4); color:#a5b4fc; }
.anode-guard-in { background:rgba(14,165,233,0.12); border-color:rgba(14,165,233,0.45); color:#38bdf8; }
.anode-super    { background:rgba(139,92,246,0.15); border-color:rgba(139,92,246,0.45); color:#c4b5fd; }
.anode-agent    { background:rgba(16,185,129,0.12); border-color:rgba(16,185,129,0.35); color:#6ee7b7; }
.anode-review   { background:rgba(245,158,11,0.12); border-color:rgba(245,158,11,0.35); color:#fcd34d; }
.anode-guard-out{ background:rgba(234,179,8,0.12);  border-color:rgba(234,179,8,0.4);   color:#fbbf24; }
.anode-output   { background:rgba(239,68,68,0.1);   border-color:rgba(239,68,68,0.3);   color:#fca5a5; }
.anode-store    { background:rgba(15,23,42,0.6);    border-color:rgba(255,255,255,0.12); color:#94a3b8; }
.anode-ext      { background:rgba(30,41,59,0.8);    border-color:rgba(255,255,255,0.1);  color:#64748b; }

.anode-label { font-size:0.68rem; color:#475569; margin-top:3px; font-weight:400; }

/* Section containers */
.arch-section {
    background:rgba(15,23,42,0.5); border:1px solid rgba(255,255,255,0.06);
    border-radius:14px; padding:16px 20px; margin-bottom:14px;
}
.arch-section-title {
    font-size:0.68rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.1em; margin-bottom:12px;
}

/* Path boxes */
.path-box {
    border:1px dashed rgba(255,255,255,0.1); border-radius:8px;
    padding:10px 14px; flex:1;
}

/* Check list */
.check-list { display:flex; flex-wrap:wrap; gap:5px; margin-top:6px; }
.check-pill {
    font-size:0.7rem; padding:2px 9px; border-radius:10px; font-weight:500;
}
.cp-blue { background:rgba(14,165,233,0.15); color:#38bdf8; border:1px solid rgba(14,165,233,0.25); }
.cp-amber{ background:rgba(234,179,8,0.12);  color:#fbbf24; border:1px solid rgba(234,179,8,0.25); }
.cp-green{ background:rgba(16,185,129,0.12); color:#6ee7b7; border:1px solid rgba(16,185,129,0.25); }
.cp-purple{background:rgba(139,92,246,0.15); color:#c4b5fd; border:1px solid rgba(139,92,246,0.3); }
</style>

<div class="arch-wrap">

<!-- ── Layer 1: Entry ── -->
<div class="arch-section">
  <div class="arch-section-title" style="color:#6366f1">① Entry Layer</div>
  <div style="display:flex;gap:12px;flex-wrap:wrap">
    <div class="anode anode-user" style="min-width:160px">
      <div>🖥️ Streamlit Web UI</div>
      <div class="anode-label">app.py · port 8501</div>
    </div>
    <div class="arch-arrow-h">or</div>
    <div class="anode anode-user" style="min-width:160px">
      <div>⌨️ CLI</div>
      <div class="anode-label">main.py · Rich terminal</div>
    </div>
  </div>
</div>

<div style="text-align:center;color:#475569;font-size:1.1rem;margin:-6px 0">↓ user_query</div>

<!-- ── Layer 2: Input Guardrail ── -->
<div class="arch-section" style="border-color:rgba(14,165,233,0.25)">
  <div class="arch-section-title" style="color:#38bdf8">② Input Guardrail  <span style="color:#475569;font-weight:400">— agents/input_guardrail.py</span></div>
  <div style="display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap">
    <div>
      <div class="anode anode-guard-in">🔒 Input Guardrail</div>
    </div>
    <div style="flex:1;min-width:260px">
      <div style="font-size:0.72rem;color:#475569;margin-bottom:5px">6 checks — short-circuits on first failure:</div>
      <div class="check-list">
        <span class="check-pill cp-blue">① Length (3–2000 chars)</span>
        <span class="check-pill cp-blue">② Prompt Injection (12 regex)</span>
        <span class="check-pill cp-blue">③ Harmful Content (18 phrases)</span>
        <span class="check-pill cp-blue">④ PII Detection (email/phone/SSN…)</span>
        <span class="check-pill cp-blue">⑤ Profanity Filter</span>
        <span class="check-pill cp-blue">⑥ Topic Relevance (LLM-based)</span>
      </div>
    </div>
  </div>
  <div style="margin-top:8px;font-size:0.75rem;color:#475569">
    ✓ Pass → sanitized_query forwarded &nbsp;|&nbsp; ✗ Fail → final_response set, route to END
  </div>
</div>

<div style="text-align:center;color:#475569;font-size:1.1rem;margin:-6px 0">↓ sanitized_query</div>

<!-- ── Layer 3: Supervisor ── -->
<div class="arch-section" style="border-color:rgba(139,92,246,0.3)">
  <div class="arch-section-title" style="color:#c4b5fd">③ Supervisor Agent  <span style="color:#475569;font-weight:400">— agents/supervisor_agent.py · GPT-4o-mini</span></div>
  <div style="display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap">
    <div class="anode anode-super">🧠 Supervisor</div>
    <div style="flex:1;min-width:260px">
      <div style="font-size:0.72rem;color:#475569;margin-bottom:5px">Detects intent → decides agent delegation:</div>
      <div class="check-list">
        <span class="check-pill cp-purple">explain_concept → retrieval+gen+review</span>
        <span class="check-pill cp-purple">generate_quiz → retrieval+gen+review</span>
        <span class="check-pill cp-purple">summarize_document → retrieval+gen+review</span>
        <span class="check-pill cp-purple">generate_notes → retrieval+gen+review</span>
        <span class="check-pill cp-purple">general_question → retrieval+gen+review</span>
        <span class="check-pill cp-amber">recommend_topics → gen+review (no retrieval)</span>
      </div>
    </div>
  </div>
</div>

<div style="text-align:center;color:#475569;font-size:1.1rem;margin:-6px 0">↓ agents_to_run</div>

<!-- ── Layer 4: Agent Execution Paths ── -->
<div class="arch-section" style="border-color:rgba(16,185,129,0.25)">
  <div class="arch-section-title" style="color:#6ee7b7">④ Agent Execution  <span style="color:#475569;font-weight:400">— Hierarchical delegation</span></div>
  <div style="display:flex;gap:12px;flex-wrap:wrap">

    <!-- Path A -->
    <div class="path-box" style="border-color:rgba(14,165,233,0.2)">
      <div style="font-size:0.72rem;color:#38bdf8;font-weight:700;margin-bottom:8px">PATH A — retrieval needed (5 intents)</div>
      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap">
        <div class="anode anode-agent" style="min-width:100px;font-size:0.78rem">
          📚 Retrieval<div class="anode-label">ChromaDB semantic<br>text-embedding-3-small<br>TOP_K = 5</div>
        </div>
        <span style="color:#475569">→</span>
        <div class="anode anode-agent" style="min-width:100px;font-size:0.78rem">
          ✍️ Generation<div class="anode-label">GPT-4o-mini<br>intent-specific prompts<br>temp = 0.3</div>
        </div>
      </div>
    </div>

    <!-- Path B -->
    <div class="path-box" style="border-color:rgba(234,179,8,0.2)">
      <div style="font-size:0.72rem;color:#fbbf24;font-weight:700;margin-bottom:8px">PATH B — no retrieval (recommend_topics)</div>
      <div class="anode anode-agent" style="min-width:100px;font-size:0.78rem">
        ✍️ Generation<div class="anode-label">GPT-4o-mini<br>model knowledge only<br>temp = 0.3</div>
      </div>
    </div>
  </div>

  <!-- Both paths → Reviewer → Response -->
  <div style="margin-top:12px;display:flex;align-items:center;gap:10px;flex-wrap:wrap">
    <span style="color:#475569;font-size:0.8rem">Both paths converge →</span>
    <div class="anode anode-review" style="font-size:0.78rem">
      🔍 Reviewer<div class="anode-label">GPT-4o-mini · temp=0<br>faithfulness ≥ 0.7<br>relevance ≥ 0.7<br>no hallucination</div>
    </div>
    <span style="color:#475569">→</span>
    <div class="anode anode-agent" style="font-size:0.78rem">
      📤 Response<div class="anode-label">follow-up suggestions<br>source assembly<br>conversation history</div>
    </div>
  </div>
</div>

<div style="text-align:center;color:#475569;font-size:1.1rem;margin:-6px 0">↓ final_response</div>

<!-- ── Layer 5: Output Guardrail ── -->
<div class="arch-section" style="border-color:rgba(234,179,8,0.3)">
  <div class="arch-section-title" style="color:#fbbf24">⑤ Output Guardrail  <span style="color:#475569;font-weight:400">— agents/output_guardrail.py</span></div>
  <div style="display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap">
    <div class="anode anode-guard-out">🔒 Output Guardrail</div>
    <div style="flex:1;min-width:260px">
      <div style="font-size:0.72rem;color:#475569;margin-bottom:5px">6 checks — all run, multiple failures accumulated:</div>
      <div class="check-list">
        <span class="check-pill cp-amber">① PII Leakage → auto-redact</span>
        <span class="check-pill cp-amber">② Toxicity → replace with fallback</span>
        <span class="check-pill cp-amber">③ Confidence Gate (≥ 30%)</span>
        <span class="check-pill cp-amber">④ Length (20–15000 chars)</span>
        <span class="check-pill cp-amber">⑤ Hallucination Flag (from reviewer)</span>
        <span class="check-pill cp-amber">⑥ Disclaimer Inject (no sources)</span>
      </div>
    </div>
  </div>
</div>

<div style="text-align:center;color:#475569;font-size:1.1rem;margin:-6px 0">↓ validated response</div>

<!-- ── Layer 6: Output ── -->
<div class="arch-section">
  <div class="arch-section-title" style="color:#f472b6">⑥ Output Layer</div>
  <div style="display:flex;gap:12px;flex-wrap:wrap">
    <div class="anode anode-output">🖥️ UI Response<div class="anode-label">chat bubble + metadata card<br>guardrail checks · scores</div></div>
    <div class="anode anode-store">📊 Analytics Log<div class="anode-label">data/logs/analytics.jsonl</div></div>
    <div class="anode anode-store">📝 Audit Log<div class="anode-label">data/logs/assistant.log</div></div>
  </div>
</div>

</div><!-- end arch-wrap -->
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    # ── Supporting infrastructure ─────────────────────────────────────────────
    st.markdown("<div style='font-size:0.9rem;font-weight:600;color:#94a3b8;margin-bottom:10px'>🔧 Supporting Infrastructure</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    infra = [
        (c1, "🗄️ ChromaDB", "Vector Store", ["text-embedding-3-small", "Persistent: ./data/chroma_db", "Collection: learning_materials", "TOP_K = 5 docs"]),
        (c2, "🤖 OpenAI API", "LLM + Embeddings", ["GPT-4o-mini (generation)", "GPT-4o-mini (supervisor)", "GPT-4o-mini (reviewer)", "text-embedding-3-small"]),
        (c3, "🧪 DeepEval", "Evaluation Framework", ["Faithfulness ≥ 0.6", "Answer Relevancy ≥ 0.6", "Contextual Relevancy ≥ 0.5", "Fallback: heuristic scorer"]),
        (c4, "⚙️ LangGraph", "Orchestration", ["StateGraph", "Conditional edges", "AgentState TypedDict", "Append-only history"]),
    ]
    for col, title, subtitle, items in infra:
        with col:
            items_html = "".join(f"<li style='font-size:0.75rem;color:#64748b;margin-bottom:2px'>{i}</li>" for i in items)
            st.markdown(f"""
            <div style='background:rgba(15,23,42,0.7);border:1px solid rgba(255,255,255,0.08);
                        border-radius:10px;padding:14px;height:100%'>
                <div style='font-size:0.95rem;font-weight:700;color:#e2e8f0'>{title}</div>
                <div style='font-size:0.72rem;color:#6366f1;margin-bottom:8px'>{subtitle}</div>
                <ul style='padding-left:16px;margin:0'>{items_html}</ul>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    # ── File map ──────────────────────────────────────────────────────────────
    st.markdown("<div style='font-size:0.9rem;font-weight:600;color:#94a3b8;margin-bottom:10px'>📁 Codebase Map</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(15,23,42,0.8);border:1px solid rgba(255,255,255,0.07);
                border-radius:12px;padding:16px 20px;font-size:0.8rem;
                font-family:monospace;line-height:2;color:#94a3b8'>
        <span style='color:#6366f1'>smart_learning_assistant/</span><br>
        ├── <span style='color:#38bdf8'>app.py</span>              <span style='color:#334155'>← Streamlit UI (Chat · Eval · Architecture)</span><br>
        ├── <span style='color:#38bdf8'>main.py</span>             <span style='color:#334155'>← CLI entry point</span><br>
        ├── <span style='color:#a5b4fc'>core/</span><br>
        │&nbsp;&nbsp;&nbsp;├── <span style='color:#c4b5fd'>graph.py</span>        <span style='color:#334155'>← LangGraph pipeline + routing</span><br>
        │&nbsp;&nbsp;&nbsp;└── <span style='color:#c4b5fd'>state.py</span>        <span style='color:#334155'>← Shared AgentState TypedDict</span><br>
        ├── <span style='color:#a5b4fc'>agents/</span><br>
        │&nbsp;&nbsp;&nbsp;├── <span style='color:#38bdf8'>input_guardrail.py</span>  <span style='color:#334155'>← 6 input checks</span><br>
        │&nbsp;&nbsp;&nbsp;├── <span style='color:#c4b5fd'>supervisor_agent.py</span> <span style='color:#334155'>← intent detection + delegation</span><br>
        │&nbsp;&nbsp;&nbsp;├── <span style='color:#6ee7b7'>retrieval_agent.py</span>  <span style='color:#334155'>← ChromaDB semantic search</span><br>
        │&nbsp;&nbsp;&nbsp;├── <span style='color:#6ee7b7'>generation_agent.py</span> <span style='color:#334155'>← GPT-4o-mini, 6 intent prompts</span><br>
        │&nbsp;&nbsp;&nbsp;├── <span style='color:#fcd34d'>reviewer_agent.py</span>   <span style='color:#334155'>← quality + hallucination check</span><br>
        │&nbsp;&nbsp;&nbsp;├── <span style='color:#6ee7b7'>response_agent.py</span>   <span style='color:#334155'>← final assembly + follow-ups</span><br>
        │&nbsp;&nbsp;&nbsp;└── <span style='color:#fbbf24'>output_guardrail.py</span> <span style='color:#334155'>← 6 output checks</span><br>
        ├── <span style='color:#a5b4fc'>evaluation/</span><br>
        │&nbsp;&nbsp;&nbsp;└── <span style='color:#c4b5fd'>evaluator.py</span>    <span style='color:#334155'>← DeepEval + fallback heuristic</span><br>
        ├── <span style='color:#a5b4fc'>utils/</span><br>
        │&nbsp;&nbsp;&nbsp;├── <span style='color:#c4b5fd'>ingest.py</span>       <span style='color:#334155'>← PDF/text → ChromaDB ingestion</span><br>
        │&nbsp;&nbsp;&nbsp;└── <span style='color:#c4b5fd'>logger.py</span>       <span style='color:#334155'>← Rich logging + analytics JSONL</span><br>
        └── <span style='color:#a5b4fc'>data/</span><br>
        &nbsp;&nbsp;&nbsp;&nbsp;├── <span style='color:#334155'>chroma_db/</span>      ← persistent vector store<br>
        &nbsp;&nbsp;&nbsp;&nbsp;├── <span style='color:#334155'>sample_docs/</span>    ← ai_fundamentals.txt<br>
        &nbsp;&nbsp;&nbsp;&nbsp;└── <span style='color:#334155'>logs/</span>           ← assistant.log · analytics.jsonl
    </div>
    """, unsafe_allow_html=True)

    # ── State flow ────────────────────────────────────────────────────────────
    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.9rem;font-weight:600;color:#94a3b8;margin-bottom:10px'>🔄 AgentState Key Fields Flow</div>", unsafe_allow_html=True)

    state_rows = [
        ("input_guardrail",  "#38bdf8", ["user_query", "sanitized_query", "is_safe", "security_reason", "input_guardrail_checks"]),
        ("supervisor",       "#c4b5fd", ["intent", "workflow_type", "agents_to_run"]),
        ("retrieval",        "#6ee7b7", ["retrieved_docs", "retrieval_context", "sources"]),
        ("generation",       "#6ee7b7", ["generated_response"]),
        ("reviewer",         "#fcd34d", ["review_passed", "review_feedback", "eval_scores", "confidence_score"]),
        ("response",         "#6ee7b7", ["final_response", "follow_up_topics", "conversation_history"]),
        ("output_guardrail", "#fbbf24", ["output_guardrail_passed", "output_guardrail_checks", "output_guardrail_reason"]),
    ]
    for agent, color, fields in state_rows:
        fields_html = " ".join(f'<span style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);border-radius:5px;padding:1px 7px;font-size:0.71rem;color:#94a3b8;font-family:monospace">{f}</span>' for f in fields)
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px;flex-wrap:wrap'>
            <span style='background:rgba(15,23,42,0.8);border:1px solid {color}33;border-radius:6px;
                         padding:3px 10px;font-size:0.75rem;font-weight:700;color:{color};
                         min-width:140px;text-align:center'>{agent}</span>
            <span style='color:#334155;font-size:0.8rem'>→ sets</span>
            {fields_html}
        </div>""", unsafe_allow_html=True)
