"""
Multi-Agent Orchestrator
Coordinates 6 specialized agents to analyze business data and generate strategic insights.
"""
import anthropic
import json
from typing import Any

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"


def run_agent(name: str, system_prompt: str, user_message: str) -> str:
    """Run a single agent and return its text output."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


# ── Agent 1: Data Analyst ──────────────────────────────────────────────────────
DATA_ANALYST_PROMPT = """You are a Data Analyst Agent specializing in business data interpretation.
Your job is to parse raw CSV/JSON sales and product data and extract key numerical patterns,
trends, top/bottom performers, and anomalies. Return a structured JSON summary with:
- summary (string)
- top_products (list of {name, revenue, units})
- revenue_by_region (dict)
- revenue_by_category (dict)
- avg_customer_rating (float)
- key_trends (list of strings)
- alerts (list of strings)
Always respond ONLY with valid JSON."""


def data_analyst_agent(raw_data: str) -> dict:
    result = run_agent("DataAnalyst", DATA_ANALYST_PROMPT,
                       f"Analyze this business data and return JSON:\n\n{raw_data[:4000]}")
    try:
        return json.loads(result)
    except Exception:
        return {"summary": result, "key_trends": [], "alerts": []}


# ── Agent 2: Customer Feedback Agent ──────────────────────────────────────────
FEEDBACK_AGENT_PROMPT = """You are a Customer Feedback Agent. You specialize in NLP-based
sentiment analysis, theme extraction, and customer experience insights from reviews and feedback.
Analyze the provided reviews and return a JSON with:
- overall_sentiment (positive/neutral/negative)
- sentiment_score (0-10)
- top_complaints (list of strings)
- top_praises (list of strings)
- feature_requests (list of strings)
- customer_segments (list of strings)
- nps_estimate (int -100 to 100)
Always respond ONLY with valid JSON."""


def customer_feedback_agent(data_summary: dict, raw_reviews: str) -> dict:
    msg = f"Data context: {json.dumps(data_summary)}\n\nReviews:\n{raw_reviews[:3000]}"
    result = run_agent("CustomerFeedback", FEEDBACK_AGENT_PROMPT, msg)
    try:
        return json.loads(result)
    except Exception:
        return {"overall_sentiment": "neutral", "top_complaints": [], "top_praises": []}


# ── Agent 3: Market Research Agent ────────────────────────────────────────────
MARKET_AGENT_PROMPT = """You are a Market Research Agent. Based on product data, categories,
and performance metrics, you identify market opportunities, sizing estimates, and growth trends.
Return JSON with:
- market_summary (string)
- growth_opportunities (list of {area, potential, rationale})
- market_risks (list of strings)
- category_trends (dict of category -> trend description)
- recommended_markets (list of strings)
Always respond ONLY with valid JSON."""


def market_research_agent(data_summary: dict, feedback: dict) -> dict:
    msg = f"Sales data: {json.dumps(data_summary)}\nFeedback: {json.dumps(feedback)}"
    result = run_agent("MarketResearch", MARKET_AGENT_PROMPT, msg)
    try:
        return json.loads(result)
    except Exception:
        return {"market_summary": result, "growth_opportunities": [], "market_risks": []}


# ── Agent 4: SWOT Analysis Agent ──────────────────────────────────────────────
SWOT_AGENT_PROMPT = """You are a SWOT Analysis Agent. You synthesize all available business
intelligence to produce a comprehensive SWOT analysis.
Return JSON with:
- strengths (list of strings)
- weaknesses (list of strings)
- opportunities (list of strings)
- threats (list of strings)
- strategic_summary (string, 2-3 sentences)
Always respond ONLY with valid JSON."""


def swot_analysis_agent(data: dict, feedback: dict, market: dict) -> dict:
    msg = f"Data: {json.dumps(data)}\nFeedback: {json.dumps(feedback)}\nMarket: {json.dumps(market)}"
    result = run_agent("SWOT", SWOT_AGENT_PROMPT, msg)
    try:
        return json.loads(result)
    except Exception:
        return {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}


# ── Agent 5: Feature Prioritization Agent ─────────────────────────────────────
FEATURE_AGENT_PROMPT = """You are a Feature Prioritization Agent using RICE and MoSCoW frameworks.
Based on customer requests, market data, and SWOT analysis, produce a prioritized feature backlog.
Return JSON with:
- must_have (list of {feature, rationale, impact_score})
- should_have (list of {feature, rationale, impact_score})
- could_have (list of {feature, rationale, impact_score})
- wont_have (list of strings)
- top_priority_feature (string)
Always respond ONLY with valid JSON."""


def feature_prioritization_agent(feedback: dict, market: dict, swot: dict) -> dict:
    msg = f"Feedback: {json.dumps(feedback)}\nMarket: {json.dumps(market)}\nSWOT: {json.dumps(swot)}"
    result = run_agent("FeaturePrioritization", FEATURE_AGENT_PROMPT, msg)
    try:
        return json.loads(result)
    except Exception:
        return {"must_have": [], "should_have": [], "could_have": [], "wont_have": []}


# ── Agent 6: Strategy Recommendation Agent ────────────────────────────────────
STRATEGY_AGENT_PROMPT = """You are a Chief Strategy Officer Agent. You synthesize all
analysis from previous agents into a final, executive-grade strategic plan.
Return JSON with:
- executive_summary (string, 3-4 sentences)
- strategic_pillars (list of {pillar, description, actions: list})
- roadmap_q1 (list of strings)
- roadmap_q2 (list of strings)
- roadmap_q3 (list of strings)
- roadmap_q4 (list of strings)
- kpis (list of {metric, target, timeline})
- opportunity_score (int 1-100)
- risk_level (low/medium/high)
Always respond ONLY with valid JSON."""


def strategy_recommendation_agent(data: dict, feedback: dict, market: dict,
                                   swot: dict, features: dict) -> dict:
    msg = (f"Data Analysis: {json.dumps(data)}\n"
           f"Customer Feedback: {json.dumps(feedback)}\n"
           f"Market Research: {json.dumps(market)}\n"
           f"SWOT: {json.dumps(swot)}\n"
           f"Feature Priorities: {json.dumps(features)}")
    result = run_agent("Strategy", STRATEGY_AGENT_PROMPT, msg)
    try:
        return json.loads(result)
    except Exception:
        return {"executive_summary": result, "strategic_pillars": []}


# ── Main Orchestration Pipeline ───────────────────────────────────────────────
def run_full_analysis(raw_data: str, raw_reviews: str = "") -> dict:
    """Run all 6 agents in sequence and return consolidated results."""
    print("🤖 Agent 1: Data Analyst running...")
    data_insights = data_analyst_agent(raw_data)

    print("💬 Agent 2: Customer Feedback running...")
    feedback_insights = customer_feedback_agent(data_insights, raw_reviews or raw_data)

    print("📊 Agent 3: Market Research running...")
    market_insights = market_research_agent(data_insights, feedback_insights)

    print("🔍 Agent 4: SWOT Analysis running...")
    swot_insights = swot_analysis_agent(data_insights, feedback_insights, market_insights)

    print("⚡ Agent 5: Feature Prioritization running...")
    feature_insights = feature_prioritization_agent(feedback_insights, market_insights, swot_insights)

    print("🎯 Agent 6: Strategy Recommendation running...")
    strategy = strategy_recommendation_agent(
        data_insights, feedback_insights, market_insights, swot_insights, feature_insights
    )

    return {
        "agents_completed": 6,
        "data_analysis": data_insights,
        "customer_feedback": feedback_insights,
        "market_research": market_insights,
        "swot_analysis": swot_insights,
        "feature_prioritization": feature_insights,
        "strategy_recommendation": strategy,
    }
