from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import anthropic
import json
import io
from datetime import datetime

router = APIRouter()
client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-20250514"


@router.post("/generate-markdown")
async def generate_report(payload: dict):
    """Generate a full executive strategy report as Markdown."""
    analysis = payload.get("analysis", {})
    if not analysis:
        raise HTTPException(status_code=400, detail="No analysis data provided")

    prompt = f"""Based on the following multi-agent analysis results, generate a comprehensive
executive-level Product Strategy Report in professional Markdown format.

Analysis Data:
{json.dumps(analysis, indent=2)[:5000]}

The report must include:
1. Executive Summary
2. Data Analysis Highlights (with key metrics)
3. Customer Insights & Sentiment Analysis
4. Market Research & Opportunities
5. SWOT Analysis (formatted as a 2x2 table)
6. Feature Prioritization (MoSCoW table)
7. Strategic Recommendations & Pillars
8. 12-Month Product Roadmap (Q1-Q4)
9. KPIs & Success Metrics
10. Conclusion & Next Steps

Use professional language suitable for C-suite stakeholders. Include specific numbers and metrics."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}],
    )

    report_md = response.content[0].text
    date_str = datetime.now().strftime("%Y-%m-%d")

    return {
        "report": report_md,
        "filename": f"product-strategy-report-{date_str}.md",
        "generated_at": datetime.now().isoformat(),
    }
