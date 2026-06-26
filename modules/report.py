"""
report.py
Phase 2 feature: "PDF Report" — renders the ATS analysis as a downloadable
PDF instead of making the user copy text out of the app.
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def build_pdf_report(jd_info: dict, ats_result: dict, strengths_weaknesses: dict = None,
                      roadmap: list = None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                             topMargin=2*cm, bottomMargin=2*cm,
                             leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=20)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], spaceBefore=14)
    body = styles["BodyText"]

    elements = []
    elements.append(Paragraph("ResumeIQ AI — ATS Compatibility Report", title_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(
        f"Job Title: {jd_info.get('job_title', 'N/A')} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Company: {jd_info.get('company', 'N/A')}", body))
    elements.append(Spacer(1, 0.5*cm))

    # Overall score
    elements.append(Paragraph(f"Overall ATS Score: {ats_result['overall']}%", h2))
    breakdown = ats_result["breakdown"]
    table_data = [["Metric", "Score"]] + [
        [k.replace("_", " ").title(), f"{v}%"] for k, v in breakdown.items()
    ]
    t = Table(table_data, colWidths=[8*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.5*cm))

    # Eligibility
    if "eligibility" in ats_result:
        elig = ats_result["eligibility"]
        status = "ELIGIBLE" if elig["eligible"] else "NOT ELIGIBLE"
        elements.append(Paragraph(f"Eligibility: {status}", h2))
        elements.append(Paragraph(elig["reason"], body))
        if elig.get("recommendation"):
            elements.append(Paragraph(f"Recommendation: {elig['recommendation']}", body))
        elements.append(Spacer(1, 0.3*cm))

    # Keyword gap
    gap = ats_result["keyword_gap"]
    elements.append(Paragraph("Keyword Gap Analysis", h2))
    elements.append(Paragraph(f"<b>Matched:</b> {', '.join(gap['matched']) or 'None'}", body))
    elements.append(Paragraph(f"<b>Missing:</b> {', '.join(gap['missing']) or 'None'}", body))
    elements.append(Spacer(1, 0.3*cm))

    # Strengths / weaknesses
    if strengths_weaknesses:
        elements.append(Paragraph("Strengths", h2))
        elements.append(ListFlowable(
            [ListItem(Paragraph(s, body)) for s in strengths_weaknesses.get("strengths", [])],
            bulletType="bullet"))
        elements.append(Paragraph("Weaknesses", h2))
        elements.append(ListFlowable(
            [ListItem(Paragraph(w, body)) for w in strengths_weaknesses.get("weaknesses", [])],
            bulletType="bullet"))

    # Roadmap
    if roadmap:
        elements.append(Paragraph("Skill Roadmap", h2))
        for week in roadmap:
            elements.append(Paragraph(
                f"<b>Week {week['week']}:</b> {', '.join(week['skills'])} — {week['focus']}",
                body))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
