from __future__ import annotations

import io
from html import escape
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.performance_packet_pdf import (
    CONTENT_WIDTH,
    INK,
    LIGHT,
    LINE,
    MARGIN_BOTTOM,
    MARGIN_TOP,
    MARGIN_X,
    MUTED,
    TEAL,
    _draw_page_footer,
    _link_or_text,
    _period_display,
    _safe_filename_part,
    _section_header,
    _styles,
)


def make_certification_packet_filename(packet: dict[str, Any]) -> str:
    subject = packet.get("subject", {})
    review = packet.get("credential_review", {})
    period = packet.get("period", {})
    subject_part = _safe_filename_part(str(subject.get("name") or ""), "bragstack-member")
    credential_part = _safe_filename_part(str(review.get("credential_name") or ""), "credential-review")
    if period.get("start_date") and period.get("end_date"):
        period_part = f"{period['start_date']}-to-{period['end_date']}"
    else:
        period_part = "all-time"
    return f"{subject_part}-{credential_part}-{period_part}.pdf"


def _status_table(summary: dict[str, Any], styles) -> Table:
    data = [[
        Paragraph("<b>Self-added</b>", styles["body_small"]),
        Paragraph("<b>Confirmed</b>", styles["body_small"]),
        Paragraph("<b>Organization-issued</b>", styles["body_small"]),
        Paragraph("<b>Total evidence</b>", styles["body_small"]),
    ], [
        Paragraph(str(summary.get("self_added", 0)), styles["metric"]),
        Paragraph(str(summary.get("confirmed", 0)), styles["metric"]),
        Paragraph(str(summary.get("organization_issued", 0)), styles["metric"]),
        Paragraph(str(summary.get("supporting_items", 0)), styles["metric"]),
    ]]
    table = Table(data, colWidths=[CONTENT_WIDTH / 4] * 4)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def build_certification_packet_pdf(packet: dict[str, Any]) -> bytes:
    styles = _styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=packet.get("title") or "BragStack Certification & Licensure Packet",
        author="BragStack",
        subject="Evidence-backed certification and licensure packet",
    )
    story = []
    subject = packet.get("subject", {})
    review = packet.get("credential_review", {})
    summary = packet.get("credential_evidence_summary", {})

    story.append(Spacer(1, 0.45 * inch))
    story.append(Paragraph("BRAGSTACK · CAREER EVIDENCE SYSTEM", styles["cover_kicker"]))
    story.append(Paragraph("Certification &amp; Licensure Packet", styles["cover_name"]))
    story.append(Paragraph(escape(str(subject.get("name") or "BragStack Member")), styles["cover_role"]))
    if subject.get("role"):
        story.append(Paragraph(escape(str(subject["role"])), styles["cover_role"]))
    story.append(Spacer(1, 0.22 * inch))
    if review.get("credential_name"):
        story.append(Paragraph(escape(str(review["credential_name"])), styles["section_title"]))
    if review.get("issuing_body"):
        story.append(Paragraph(f"Issuing / reviewing body: {escape(str(review['issuing_body']))}", styles["body"]))
    story.append(Paragraph(escape(str(review.get("review_type") or "Certification / Licensure Review")), styles["body"]))
    story.append(Paragraph(escape(_period_display(packet.get("period", {}))), styles["cover_period"]))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(
        "Evidence status reflects BragStack trust signals only. Self-added credentials are not presented as independently verified.",
        styles["body"],
    ))
    story.append(PageBreak())

    _section_header(story, styles, "01 · REVIEW OVERVIEW", "Credential evidence at a glance")
    story.append(Paragraph(escape(str(packet.get("review_summary") or "")), styles["body"]))
    story.append(Spacer(1, 8))
    story.append(_status_table(summary, styles))
    if review.get("requirement_notes"):
        story.append(Spacer(1, 14))
        story.append(Paragraph("REVIEW REQUIREMENTS / NOTES", styles["section_kicker"]))
        story.append(Paragraph(escape(str(review["requirement_notes"])), styles["body"]))

    story.append(PageBreak())
    _section_header(story, styles, "02 · CREDENTIAL EVIDENCE", "Certificates, licenses & credential records")
    credential_items = packet.get("credential_evidence", [])
    if credential_items:
        for item in credential_items:
            story.append(Paragraph(escape(str(item.get("title") or "Credential evidence")), styles["subhead"]))
            story.append(Paragraph(
                f"{escape(str(item.get('evidence_status') or 'Self-added'))} · {escape(str(item.get('type') or 'Evidence'))}",
                styles["body_small"],
            ))
            if item.get("description"):
                story.append(Paragraph(escape(str(item["description"])), styles["body"]))
            if item.get("reference"):
                story.append(_link_or_text(str(item["reference"]), styles))
            story.append(Spacer(1, 8))
    else:
        story.append(Paragraph(
            "No evidence item in this review period is currently categorized as a certificate, license, credential, or continuing-education record.",
            styles["body"],
        ))

    story.append(PageBreak())
    _section_header(story, styles, "03 · COMPETENCIES", "Documented capabilities")
    competencies = packet.get("competency_records", [])
    if competencies:
        data = [[Paragraph("<b>Capability</b>", styles["body_small"]), Paragraph("<b>Demonstrations</b>", styles["body_small"])]]
        for item in competencies[:24]:
            data.append([
                Paragraph(escape(str(item.get("skill") or "Capability")), styles["body_small"]),
                Paragraph(str(item.get("count", 0)), styles["body_small"]),
            ])
        table = Table(data, colWidths=[CONTENT_WIDTH - 1.2 * inch, 1.2 * inch], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
            ("GRID", (0, 0), (-1, -1), 0.4, LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
    else:
        story.append(Paragraph("No competency records are documented for this period yet.", styles["body"]))

    story.append(PageBreak())
    _section_header(story, styles, "04 · EXPERIENCE", "Accomplishments & supervised experience record")
    for item in packet.get("experience_records", [])[:20]:
        story.append(Paragraph(escape(str(item.get("accomplishment") or "Documented experience")), styles["subhead"]))
        if item.get("contribution"):
            story.append(Paragraph(escape(str(item["contribution"])), styles["body"]))
        if item.get("result"):
            story.append(Paragraph(f"<b>Result:</b> {escape(str(item['result']))}", styles["body"]))
        story.append(Paragraph(
            "Confirmed contribution" if item.get("verified") else "Self-documented contribution",
            styles["body_small"],
        ))
        story.append(Spacer(1, 7))

    story.append(PageBreak())
    _section_header(story, styles, "05 · EVIDENCE INDEX", "Supporting documentation")
    evidence = packet.get("supporting_evidence", [])
    if evidence:
        for item in evidence:
            story.append(Paragraph(escape(str(item.get("title") or "Evidence item")), styles["subhead"]))
            story.append(Paragraph(
                f"Status: {escape(str(item.get('evidence_status') or 'Self-added'))} · Type: {escape(str(item.get('type') or 'Evidence'))}",
                styles["body_small"],
            ))
            if item.get("description"):
                story.append(Paragraph(escape(str(item["description"])), styles["body_small"]))
            if item.get("reference"):
                story.append(_link_or_text(str(item["reference"]), styles))
            story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No supporting evidence is attached for this review period yet.", styles["body"]))

    def footer(canvas, document):
        _draw_page_footer(canvas, document, packet)

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
