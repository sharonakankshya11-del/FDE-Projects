"""Generate a sample executive PDF report from the command line.

Usage:
    python scripts/generate_sample_report.py            # uses bundled sample data
    python scripts/generate_sample_report.py mydata.csv # uses your own CSV

If OPENAI_API_KEY is set, the real multi-agent pipeline runs.
Otherwise a realistic, data-grounded sample report is produced so the repo
always ships with a valid 'Sample Generated Report (PDF)'.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DATA_DIR, settings  # noqa: E402
from src.ingestion import ingest_files  # noqa: E402
from src.orchestrator import AGENT_PIPELINE, run_analysis  # noqa: E402
from src.report_generator import generate_report  # noqa: E402

PRODUCT_CONTEXT = (
    "Consumer-electronics brand selling 10 products across 5 categories and 5 regions; "
    "strategic goal is to grow profit while protecting customer satisfaction."
)

# Realistic, data-grounded content used when no API key is configured.
SAMPLE_INSIGHTS = {
    "executive_summary": (
        "The portfolio is healthy and profitable: $4.73M revenue at a 40.2% blended margin "
        "over the Jan–Apr 2026 window, a 4.39/5 average rating and a low 2.6% return rate. "
        "Growth and profit are heavily concentrated in Electronics (47% of revenue, 42.7% "
        "margin), led almost single-handedly by Laptop Air. Sentiment is positive overall "
        "(61 positive vs. 24 negative reviews) but three products — Smart Speaker, FitBand "
        "Pro and Wireless Keyboard — drag on ratings, and PowerBank Max, SmartWatch X and "
        "FitBand Pro account for the most returns.\n\n"
        "### Top 3 Recommendations\n"
        "- **Protect and extend the Electronics franchise** — it funds the business; reduce "
        "single-product dependence on Laptop Air by accelerating Tablet Lite.\n"
        "- **Fix the quality tail** — targeted QA and messaging on FitBand Pro and PowerBank "
        "Max to cut returns and lift ratings.\n"
        "- **Reallocate marketing to the East region and high-margin West**, which already "
        "return the most revenue and margin per dollar spent.\n\n"
        "Executed together, these moves should lift blended margin by 1–2 pts and reduce "
        "returns on the weakest products within two quarters."
    ),
    "customer_feedback": (
        "### Overall sentiment\n"
        "Of 120 review-bearing transactions, sentiment skews positive (61 positive, 35 "
        "neutral, 24 negative); average rating is **4.39/5**.\n\n"
        "### Strengths customers praise\n"
        "- Strong value perception on Electronics (Laptop Air, Tablet Lite) — repeated "
        "\"great value\" and \"highly recommend\" themes.\n"
        "- Reliability and ease of use on Accessories and Audio (NoiseBuds Air rates 4.51).\n"
        "- High satisfaction on premium items when expectations are met.\n\n"
        "### Pain points\n"
        "- Build-quality and post-purchase issues cluster on **FitBand Pro** (4.22 avg).\n"
        "- \"Customer support could be better\" recurs on **Smart Speaker** (4.21 avg).\n"
        "- Inconsistent experience on **Wireless Keyboard** (4.26 avg).\n\n"
        "### Products at risk\n"
        "Lowest-rated: Smart Speaker (4.21), FitBand Pro (4.22), Wireless Keyboard (4.26). "
        "Highest returns: PowerBank Max (95), SmartWatch X (80), FitBand Pro (73).\n\n"
        "### Recommendations\n"
        "- Launch a quality task-force on FitBand Pro and PowerBank Max.\n"
        "- Audit Smart Speaker support journey; add proactive setup guidance.\n"
        "- Tighten Wireless Keyboard QC and update product-page expectations."
    ),
    "market_research": (
        "### Revenue & profit drivers\n"
        "Electronics dominates at **$2.25M revenue / 42.7% margin** (Laptop Air alone is "
        "$1.73M). Smart Home ($0.88M) and Wearables ($0.78M) follow but at ~37–38% margins.\n\n"
        "### Regional patterns\n"
        "East is the largest market ($1.43M) while **West delivers the best margin (43.4%) "
        "and rating (4.5)** — an efficient, satisfied region worth doubling down on.\n\n"
        "### Margin observations\n"
        "Accessories and Wearables move the most units (6,217 and 5,758) but at the lowest "
        "margins, so volume is not translating into proportional profit.\n\n"
        "### Takeaways\n"
        "- Profit concentration in Electronics is both a strength and a risk.\n"
        "- West is the model region; replicate its mix elsewhere.\n"
        "- Low-margin, high-volume categories need pricing or cost review."
    ),
    "competitor_analysis": (
        "### Positioning\n"
        "- **Electronics** — premium positioning supported by strong ratings; defensible.\n"
        "- **Accessories/Audio** — value/mid-market; exposed to commodity price competition.\n"
        "- **Smart Home/Wearables** — mid-market with quality vulnerabilities competitors "
        "can exploit.\n\n"
        "### Strong vs. vulnerable\n"
        "Strong where ratings and margins align (Laptop Air, NoiseBuds Air). Vulnerable on "
        "FitBand Pro and Smart Speaker, where weaker satisfaction invites competitor switching.\n\n"
        "### Threats to watch\n"
        "- Price-aggressive accessory rivals compressing already-thin margins.\n"
        "- Wearable competitors with stronger reliability reputations.\n\n"
        "### Differentiation moves\n"
        "- Lean into the value-for-money Electronics narrative.\n"
        "- Use service/warranty as a wedge where rivals are weak.\n\n"
        "*Assumption: no competitor documents were supplied; positioning inferred from price, "
        "margin and rating proxies.*"
    ),
    "swot": (
        "### Strengths\n"
        "- 40.2% blended margin and $4.73M revenue.\n"
        "- Flagship Laptop Air with 43.9% margin and 4.51 rating.\n"
        "- Low overall return rate (2.6%) and positive sentiment.\n\n"
        "### Weaknesses\n"
        "- Heavy dependence on a single product/category.\n"
        "- Quality tail: FitBand Pro, PowerBank Max, Smart Speaker.\n"
        "- Low-margin Accessories/Wearables despite high volume.\n\n"
        "### Opportunities\n"
        "- Scale Tablet Lite as a second Electronics engine.\n"
        "- Replicate West-region efficiency nationally.\n"
        "- Convert high new-customer inflow (9,309) into retention.\n\n"
        "### Threats\n"
        "- Margin compression in commoditised accessories.\n"
        "- Competitor switching on weak-satisfaction products.\n"
        "- Concentration risk if Laptop Air demand softens."
    ),
    "opportunities": (
        "Ranked product opportunities (scored on Impact, Confidence, Strategic-fit):\n\n"
        "| Opportunity | Impact | Confidence | Fit | Score |\n"
        "|---|---|---|---|---|\n"
        "| Accelerate Tablet Lite as 2nd Electronics engine | 9 | 8 | 9 | 88 |\n"
        "| Quality fix programme (FitBand/PowerBank) | 8 | 9 | 8 | 85 |\n"
        "| Replicate West-region playbook nationally | 8 | 7 | 9 | 80 |\n"
        "| Retention programme for new customers | 7 | 7 | 8 | 73 |\n"
        "| Reprice/cost-down low-margin accessories | 6 | 7 | 7 | 66 |\n\n"
        "Top opportunity: accelerating Tablet Lite directly reduces dependence on Laptop Air "
        "while staying in the highest-margin category, making it the best risk-adjusted bet."
    ),
    "feature_prioritization": (
        "RICE-scored initiatives (RICE = Reach × Impact × Confidence ÷ Effort):\n\n"
        "| Feature | Reach | Impact | Confidence | Effort | RICE |\n"
        "|---|---|---|---|---|---|\n"
        "| FitBand Pro quality & firmware fix | 8 | 4 | 90% | 2 | 14.4 |\n"
        "| Tablet Lite line extension | 7 | 5 | 80% | 3 | 9.3 |\n"
        "| Smart Speaker support overhaul | 6 | 3 | 85% | 2 | 7.7 |\n"
        "| New-customer onboarding & retention | 9 | 3 | 70% | 3 | 6.3 |\n"
        "| PowerBank returns-reduction packaging | 7 | 3 | 80% | 3 | 5.6 |\n"
        "| West-region playbook rollout | 6 | 4 | 60% | 4 | 3.6 |\n\n"
        "**Build now:** FitBand fix, Tablet Lite extension. "
        "**Next:** Smart Speaker support, onboarding. "
        "**Later:** PowerBank packaging, regional rollout."
    ),
    "strategy": (
        "### Strategic Action Plan\n"
        "- **Grow the Electronics franchise** — owner: Product; KPI: Electronics revenue +20% "
        "with Tablet Lite share rising.\n"
        "- **Cut the quality tail** — owner: Quality/Eng; KPI: returns on FitBand/PowerBank "
        "−30%, ratings ≥4.5.\n"
        "- **Scale the West playbook** — owner: GTM; KPI: blended margin +1.5 pts.\n"
        "- **Activate retention** — owner: Growth; KPI: repeat-purchase rate +10%.\n\n"
        "### Product Roadmap\n"
        "**Now (0–3 mo):** FitBand quality fix; Smart Speaker support overhaul; instrument "
        "returns reasons.\n"
        "**Next (3–9 mo):** Tablet Lite line extension; onboarding/retention programme; "
        "accessory repricing test.\n"
        "**Later (9–18 mo):** national West-region rollout; premium service tier; portfolio "
        "diversification beyond Laptop Air."
    ),
}


def main() -> None:
    csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DATA_DIR / "Sample_Sales_Data.csv"
    files = [{"name": csv_path.name, "content": csv_path.read_bytes()}]
    data = ingest_files(files)

    if settings.has_api_key:
        print("OPENAI_API_KEY found — running the live multi-agent pipeline…")
        state = {
            "structured_summary": data.structured_summary,
            "documents": data.documents,
            "product_context": PRODUCT_CONTEXT,
            "trace": [],
        }
        result = run_analysis(state, progress_cb=lambda n: print(f"  ✓ {n}"))
        insights = {a.output_key: result.get(a.output_key, "") for a in AGENT_PIPELINE}
    else:
        print("No OPENAI_API_KEY — writing the bundled data-grounded sample report.")
        insights = SAMPLE_INSIGHTS

    path = generate_report(insights, PRODUCT_CONTEXT, data.structured_summary,
                           filename="Sample_Generated_Report.pdf")
    print(f"\nReport written to: {path}")


if __name__ == "__main__":
    main()
