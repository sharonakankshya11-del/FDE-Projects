"""Generate a downloadable executive PDF report from the agent outputs."""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Dict

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from .config import OUTPUT_DIR

BRAND = colors.HexColor("#2563eb")
DARK = colors.HexColor("#1e293b")
GREY = colors.HexColor("#64748b")

SECTIONS = [
    ("Executive Summary", "executive_summary"),
    ("Customer Insights Report", "customer_feedback"),
    ("Market Research Summary", "market_research"),
    ("Competitor Analysis Report", "competitor_analysis"),
    ("SWOT Analysis", "swot"),
    ("Product Opportunity Assessment", "opportunities"),
    ("Feature Prioritization Recommendations", "feature_prioritization"),
    ("Strategic Action Plan & Roadmap", "strategy"),
]


def _styles():
    ss = getSampleStyleSheet()
    ss.add(ParagraphStyle("PSCover", parent=ss["Title"], fontSize=26, textColor=DARK,
                          leading=30, alignment=TA_CENTER))
    ss.add(ParagraphStyle("PSCoverSub", parent=ss["Normal"], fontSize=12, textColor=GREY,
                          alignment=TA_CENTER))
    ss.add(ParagraphStyle("PSH1", parent=ss["Heading1"], fontSize=15, textColor=BRAND,
                          spaceBefore=10, spaceAfter=6))
    ss.add(ParagraphStyle("PSH2", parent=ss["Heading2"], fontSize=12, textColor=DARK,
                          spaceBefore=8, spaceAfter=4))
    ss.add(ParagraphStyle("PSBody", parent=ss["Normal"], fontSize=10, leading=15,
                          textColor=DARK, spaceAfter=4))
    ss.add(ParagraphStyle("PSBullet", parent=ss["PSBody"], leftIndent=14, bulletIndent=4))
    return ss


def _inline(text: str) -> str:
    """Minimal markdown inline -> reportlab markup, with HTML escaping."""
    text = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\s)(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", text)
    return text


def _md_table(lines, ss):
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells and not all(set(c) <= set("-: ") for c in cells):
            rows.append([Paragraph(_inline(c), ss["PSBody"]) for c in cells])
    if not rows:
        return None
    tbl = Table(rows, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tbl


def _md_to_flowables(md: str, ss):
    flow, buf, i = [], [], 0
    lines = md.split("\n")
    while i < len(lines):
        line = lines[i].rstrip()
        # group consecutive table rows
        if line.strip().startswith("|") and "|" in line.strip()[1:]:
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i]); i += 1
            t = _md_table(tbl_lines, ss)
            if t:
                flow.append(Spacer(1, 4)); flow.append(t); flow.append(Spacer(1, 6))
            continue
        if line.startswith("### "):
            flow.append(Paragraph(_inline(line[4:]), ss["PSH2"]))
        elif line.startswith("## "):
            flow.append(Paragraph(_inline(line[3:]), ss["PSH2"]))
        elif line.startswith("# "):
            flow.append(Paragraph(_inline(line[2:]), ss["PSH1"]))
        elif re.match(r"^\s*[-*]\s+", line):
            flow.append(Paragraph(_inline(re.sub(r"^\s*[-*]\s+", "", line)), ss["PSBullet"],
                                  bulletText="•"))
        elif re.match(r"^\s*\d+\.\s+", line):
            flow.append(Paragraph(_inline(line.strip()), ss["PSBullet"]))
        elif line.strip():
            flow.append(Paragraph(_inline(line.strip()), ss["PSBody"]))
        else:
            flow.append(Spacer(1, 4))
        i += 1
    return flow


def generate_report(insights: Dict[str, str], product_context: str = "",
                    summary: Dict | None = None, filename: str = "Product_Strategy_Report.pdf") -> str:
    ss = _styles()
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(str(path), pagesize=A4, topMargin=2 * cm, bottomMargin=2 * cm,
                            leftMargin=2 * cm, rightMargin=2 * cm,
                            title="AI Product Strategy Report")
    story = []

    # ---- Cover ----
    story += [Spacer(1, 5 * cm),
              Paragraph("AI-Powered Product Strategy Report", ss["PSCover"]),
              Spacer(1, 0.4 * cm),
              Paragraph("Generated by a multi-agent Product Strategy Assistant", ss["PSCoverSub"]),
              Spacer(1, 0.2 * cm),
              Paragraph(dt.datetime.now().strftime("%d %B %Y, %H:%M"), ss["PSCoverSub"])]
    if product_context:
        story += [Spacer(1, 1 * cm),
                  Paragraph(f"<b>Context:</b> {_inline(product_context)}", ss["PSCoverSub"])]

    # ---- KPI strip ----
    if summary:
        kpis = []
        labels = {"total_revenue": "Total Revenue ($)", "total_profit": "Total Profit ($)",
                  "overall_margin_pct": "Margin (%)", "avg_rating": "Avg Rating",
                  "return_rate_pct": "Return Rate (%)", "total_units": "Units Sold"}
        for k, lbl in labels.items():
            if k in summary:
                kpis.append([Paragraph(f"<b>{summary[k]:,}</b>" if isinstance(summary[k], (int, float))
                                       else f"<b>{summary[k]}</b>", ss["PSBody"]),
                             Paragraph(lbl, ss["PSBody"])])
        if kpis:
            story += [Spacer(1, 1.2 * cm), Paragraph("Key Metrics", ss["PSCoverSub"])]
            t = Table([[c[0] for c in kpis], [c[1] for c in kpis]], hAlign="CENTER")
            t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 9),
                                   ("TEXTCOLOR", (0, 0), (-1, 0), BRAND),
                                   ("TEXTCOLOR", (0, 1), (-1, 1), GREY),
                                   ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
            story.append(t)
    story.append(PageBreak())

    # ---- Sections ----
    for title, key in SECTIONS:
        body = insights.get(key)
        if not body:
            continue
        story.append(Paragraph(title, ss["PSH1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=BRAND, spaceAfter=6))
        story += _md_to_flowables(body, ss)
        story.append(Spacer(1, 0.5 * cm))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return str(path)


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(GREY)
    canvas.drawString(2 * cm, 1.2 * cm, "AI-Powered Product Strategy Assistant")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()
