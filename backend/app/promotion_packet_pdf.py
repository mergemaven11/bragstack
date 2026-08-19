from __future__ import annotations

import io
import re
from html import escape
from typing import Any

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

TEAL = colors.HexColor("#173F43")
TEAL_2 = colors.HexColor("#1F5559")
GOLD = colors.HexColor("#B68B4C")
INK = colors.HexColor("#172126")
MUTED = colors.HexColor("#667176")
LIGHT = colors.HexColor("#F3F1EA")
LINE = colors.HexColor("#DEDAD0")
PAGE_WIDTH, PAGE_HEIGHT = LETTER
MARGIN_X = 0.62 * inch
CONTENT_WIDTH = PAGE_WIDTH - (MARGIN_X * 2)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe(value: Any) -> str:
    return escape(_clean(value))


def _period_display(period: dict[str, Any]) -> str:
    if period.get("start_date") and period.get("end_date"):
        return f"{period['start_date']} — {period['end_date']}"
    return period.get("label") or "All recorded work"


def _safe_filename_part(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value or "").strip("-")
    return cleaned or fallback


def make_promotion_packet_filename(packet: dict[str, Any]) -> str:
    subject = packet.get("subject", {})
    period = packet.get("period", {})
    subject_part = _safe_filename_part(_clean(subject.get("name")), "bragstack-member")
    if period.get("start_date") and period.get("end_date"):
        period_part = f"{period['start_date']}-to-{period['end_date']}"
    else:
        period_part = "all-time"
    return f"{subject_part}-promotion-packet-{period_part}.pdf"


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle(
            "PromotionKicker",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.4,
            leading=9.5,
            textColor=TEAL_2,
            spaceAfter=4,
        ),
        "cover_name": ParagraphStyle(
            "PromotionCoverName",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=31,
            leading=33,
            textColor=INK,
            spaceAfter=8,
        ),
        "cover_role": ParagraphStyle(
            "PromotionCoverRole",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#454E54"),
            spaceAfter=5,
        ),
        "title": ParagraphStyle(
            "PromotionTitle",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=23,
            leading=26,
            textColor=INK,
            spaceAfter=9,
        ),
        "subhead": ParagraphStyle(
            "PromotionSubhead",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=13,
            leading=16,
            textColor=INK,
            spaceBefore=3,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "PromotionBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#505A60"),
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "PromotionSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.3,
            leading=9.8,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "metric": ParagraphStyle(
            "PromotionMetric",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=18,
            leading=20,
            textColor=TEAL,
            alignment=1,
        ),
        "metric_label": ParagraphStyle(
            "PromotionMetricLabel",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.2,
            leading=8,
            textColor=MUTED,
            alignment=1,
        ),
    }


def _section_header(story: list, styles: dict[str, ParagraphStyle], index: str, title: str) -> None:
    story.append(Paragraph(_safe(index), styles["kicker"]))
    story.append(Paragraph(_safe(title), styles["title"]))
    story.append(HRFlowable(width="100%", thickness=1.7, color=TEAL, spaceAfter=12))


def _footer(canvas, doc, packet: dict[str, Any]) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_X, 0.42 * inch, PAGE_WIDTH - MARGIN_X, 0.42 * inch)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(MARGIN_X, 0.27 * inch, "BragStack · Career Evidence System")
    canvas.drawCentredString(PAGE_WIDTH / 2, 0.27 * inch, _period_display(packet.get("period", {}))[:70])
    canvas.drawRightString(PAGE_WIDTH - MARGIN_X, 0.27 * inch, f"Page {doc.page}")
    if packet.get("confidential"):
        canvas.setFillColor(TEAL)
        canvas.setFont("Helvetica-Bold", 6.4)
        canvas.drawRightString(PAGE_WIDTH - MARGIN_X, PAGE_HEIGHT - 0.34 * inch, "CONFIDENTIAL")
    canvas.restoreState()


def _metrics_table(scorecard: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    values = [
        (scorecard.get("accomplishments", 0), "Accomplishments"),
        (scorecard.get("impact_receipts", 0), "Impact Receipts"),
        (scorecard.get("evidence_items", 0), "Evidence Items"),
        (scorecard.get("confirmed_assertions", 0), "Confirmed Signals"),
    ]
    cells = []
    for value, label in values:
        cells.append([
            Paragraph(_safe(value), styles["metric"]),
            Paragraph(_safe(label), styles["metric_label"]),
        ])
    table = Table([cells], colWidths=[CONTENT_WIDTH / 4] * 4)
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table


def _bars(items: dict[str, int], styles: dict[str, ParagraphStyle], limit: int = 8) -> Drawing:
    entries = list(items.items())[:limit]
    row_h = 19
    height = max(28, len(entries) * row_h + 6)
    drawing = Drawing(CONTENT_WIDTH, height)
    if not entries:
        drawing.add(String(0, height - 14, "No data for this period.", fontName="Helvetica", fontSize=8, fillColor=MUTED))
        return drawing
    maximum = max(value for _, value in entries) or 1
    label_w = 140
    bar_w = CONTENT_WIDTH - label_w - 35
    for index, (label, value) in enumerate(entries):
        y = height - ((index + 1) * row_h) + 4
        drawing.add(String(0, y + 4, str(label)[:28], fontName="Helvetica", fontSize=7.2, fillColor=INK))
        drawing.add(Rect(label_w, y + 2, bar_w, 7, fillColor=colors.HexColor("#E8E5DC"), strokeColor=None))
        drawing.add(Rect(label_w, y + 2, max(6, bar_w * (float(value) / maximum)), 7, fillColor=TEAL_2, strokeColor=None))
        drawing.add(String(label_w + bar_w + 8, y + 3, str(value), fontName="Helvetica-Bold", fontSize=7, fillColor=TEAL))
    return drawing


def _link_or_text(reference: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    reference = _clean(reference)
    if reference.startswith("https://") or reference.startswith("http://"):
        value = escape(reference)
        return Paragraph(f'<link href="{value}" color="#1F5559"><u>{value}</u></link>', styles["small"])
    return Paragraph(_safe(reference or "—"), styles["small"])


def build_promotion_packet_pdf(packet: dict[str, Any]) -> bytes:
    styles = _styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=0.58 * inch,
        bottomMargin=0.58 * inch,
        title="BragStack Promotion Packet",
        author="BragStack",
        subject="Evidence-backed promotion packet",
    )

    story: list = []
    subject = packet.get("subject", {})
    context = packet.get("context", {})
    target = packet.get("target", {})
    scorecard = packet.get("scorecard", {})
    promotion_case = packet.get("promotion_case", {})

    # Cover
    story.append(Spacer(1, 0.42 * inch))
    story.append(Paragraph("BRAGSTACK · PROMOTION PACKET", styles["kicker"]))
    story.append(Spacer(1, 0.28 * inch))
    story.append(Paragraph(_safe(subject.get("name") or "BragStack Member"), styles["cover_name"]))
    story.append(Paragraph(_safe(subject.get("role") or "Professional"), styles["cover_role"]))
    if context.get("organization"):
        story.append(Paragraph(_safe(context.get("organization")), styles["body"]))
    if context.get("career_area"):
        story.append(Paragraph(_safe(context.get("career_area")), styles["small"]))
    story.append(Spacer(1, 0.16 * inch))
    story.append(HRFlowable(width=0.85 * inch, thickness=3, color=GOLD, spaceAfter=18))
    story.append(Paragraph("PROGRESSION TARGET", styles["kicker"]))
    target_text = " · ".join(value for value in [_clean(target.get("role")), _clean(target.get("level"))] if value) or "Promotion / increased scope"
    story.append(Paragraph(_safe(target_text), styles["subhead"]))
    story.append(Paragraph("REVIEW PERIOD", styles["kicker"]))
    story.append(Paragraph(_safe(_period_display(packet.get("period", {}))), styles["body"]))
    story.append(Spacer(1, 0.18 * inch))
    story.append(_metrics_table(scorecard, styles))
    story.append(Spacer(1, 0.28 * inch))
    story.append(Paragraph("An evidence-backed progression dossier. BragStack presents documented work and proof; it does not assign promotion readiness or make an employment decision.", styles["small"]))

    # Case overview
    story.append(PageBreak())
    _section_header(story, styles, "01 · PROMOTION CASE", "The evidence-backed case")
    story.append(Paragraph(_safe(packet.get("promotion_summary")), styles["body"]))
    story.append(_metrics_table(scorecard, styles))
    story.append(Spacer(1, 14))
    coverage_rows = [
        ["Structured proof", f"{scorecard.get('receipt_coverage_percent', 0)}%", "Accomplishments represented by Impact Receipts"],
        ["Measurable impact", f"{scorecard.get('quantified_result_coverage_percent', 0)}%", "Receipts with quantified outcomes"],
        ["Evidence coverage", f"{scorecard.get('evidence_coverage_percent', 0)}%", "Receipts supported by evidence"],
        ["Verification", f"{scorecard.get('verification_coverage_percent', 0)}%", "Receipts with confirmed contribution"],
    ]
    table = Table(
        [[Paragraph("<b>Area</b>", styles["small"]), Paragraph("<b>Coverage</b>", styles["small"]), Paragraph("<b>What it means</b>", styles["small"])]]
        + [[Paragraph(_safe(a), styles["small"]), Paragraph(f"<b>{_safe(b)}</b>", styles["small"]), Paragraph(_safe(c), styles["small"])] for a, b, c in coverage_rows],
        colWidths=[1.65 * inch, 0.8 * inch, CONTENT_WIDTH - 2.45 * inch],
        repeatRows=1,
    )
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(table)

    # Demonstrated impact
    story.append(PageBreak())
    _section_header(story, styles, "02 · DEMONSTRATED IMPACT", "The work supporting progression")
    impact = promotion_case.get("demonstrated_impact") or []
    if impact:
        for index, item in enumerate(impact[:8], 1):
            story.append(Paragraph(f"{index:02d} · {_safe(item.get('title'))}", styles["subhead"]))
            meta = " · ".join(filter(None, [_clean(item.get("category")), _clean(item.get("entry_date"))]))
            if meta:
                story.append(Paragraph(_safe(meta), styles["small"]))
            if item.get("result"):
                story.append(Paragraph(_safe(item.get("result")), styles["body"]))
            signals = []
            if item.get("verified"):
                signals.append("Verified")
            if item.get("evidence_count"):
                signals.append(f"{item['evidence_count']} evidence")
            if item.get("skills"):
                signals.extend(item.get("skills", [])[:4])
            if signals:
                story.append(Paragraph(_safe(" · ".join(signals)), styles["small"]))
            story.append(HRFlowable(width="100%", thickness=0.4, color=LINE, spaceAfter=7))
    else:
        story.append(Paragraph("No documented impact is available for this period yet.", styles["body"]))

    # Scope and ownership
    story.append(PageBreak())
    _section_header(story, styles, "03 · SCOPE & OWNERSHIP", "How responsibility shows up in the record")
    ownership = promotion_case.get("scope_and_ownership") or []
    if ownership:
        for item in ownership[:10]:
            status = "Verified" if item.get("verified") else "Self-documented"
            story.append(Paragraph(f"{_safe(item.get('reference'))} · {_safe(status)}", styles["kicker"]))
            story.append(Paragraph(_safe(item.get("accomplishment")), styles["subhead"]))
            if item.get("contribution"):
                story.append(Paragraph(f"<b>Contribution:</b> {_safe(item.get('contribution'))}", styles["body"]))
            if item.get("result"):
                story.append(Paragraph(f"<b>Result:</b> {_safe(item.get('result'))}", styles["body"]))
            story.append(HRFlowable(width="100%", thickness=0.4, color=LINE, spaceAfter=7))
    else:
        story.append(Paragraph("Add Impact Receipts to make scope and ownership easier to review.", styles["body"]))

    # Growth and capabilities
    story.append(PageBreak())
    _section_header(story, styles, "04 · GROWTH & CAPABILITIES", "Demonstrated skills over time")
    analytics = packet.get("impact_analytics", {})
    story.append(Paragraph("Most demonstrated capabilities", styles["subhead"]))
    story.append(_bars(analytics.get("top_skills") or {}, styles))
    story.append(Spacer(1, 12))
    skill_details = promotion_case.get("growth_and_capabilities") or []
    if skill_details:
        rows = [[Paragraph("<b>Capability</b>", styles["small"]), Paragraph("<b>Uses</b>", styles["small"]), Paragraph("<b>First seen</b>", styles["small"]), Paragraph("<b>Most recent</b>", styles["small"])]]
        for item in skill_details[:18]:
            rows.append([
                Paragraph(_safe(item.get("skill")), styles["small"]),
                Paragraph(_safe(item.get("count")), styles["small"]),
                Paragraph(_safe(item.get("first_seen") or "—"), styles["small"]),
                Paragraph(_safe(item.get("last_seen") or "—"), styles["small"]),
            ])
        table = Table(rows, colWidths=[2.45 * inch, 0.55 * inch, 1.3 * inch, CONTENT_WIDTH - 4.3 * inch], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.append(table)

    # Recognition and case strengthening
    story.append(PageBreak())
    _section_header(story, styles, "05 · RECOGNITION & NEXT PROOF", "What is confirmed—and what could strengthen the case")
    recognition = promotion_case.get("verified_recognition") or []
    story.append(Paragraph("Verified recognition", styles["subhead"]))
    if recognition:
        for item in recognition[:8]:
            story.append(Paragraph(f"<b>{_safe(item.get('accomplishment'))}</b> · {_safe(item.get('reference'))}", styles["body"]))
            confirmed = [c for c in item.get("confirmations", []) if c.get("status") == "confirmed"]
            if confirmed:
                labels = []
                for confirmation in confirmed:
                    label = confirmation.get("name") or "Confirmed contributor"
                    if confirmation.get("role"):
                        label += f" · {confirmation['role']}"
                    labels.append(label)
                story.append(Paragraph(_safe("; ".join(labels)), styles["small"]))
    else:
        story.append(Paragraph("No independent confirmations are attached to this review period yet. Verification is optional and should only be requested when appropriate.", styles["body"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Strengthen the case", styles["subhead"]))
    for item in promotion_case.get("strengthening_actions") or []:
        story.append(Paragraph(f"<b>{_safe(item.get('area'))}</b> — {_safe(item.get('action'))}", styles["body"]))
        story.append(Paragraph(_safe(item.get("why")), styles["small"]))

    # Evidence appendix
    story.append(PageBreak())
    _section_header(story, styles, "06 · EVIDENCE INDEX", "Traceable proof behind the promotion case")
    evidence = packet.get("evidence_index") or []
    if evidence:
        rows = [[Paragraph("<b>Receipt</b>", styles["small"]), Paragraph("<b>Evidence</b>", styles["small"]), Paragraph("<b>Type</b>", styles["small"]), Paragraph("<b>Reference</b>", styles["small"])]]
        for item in evidence:
            rows.append([
                Paragraph(_safe(item.get("receipt_reference")), styles["small"]),
                Paragraph(_safe(item.get("title") or "Evidence item"), styles["small"]),
                Paragraph(_safe(_clean(item.get("type")).replace("-", " ").title()), styles["small"]),
                _link_or_text(item.get("reference") or "", styles),
            ])
        table = Table(rows, colWidths=[1.05 * inch, 2.2 * inch, 1.05 * inch, CONTENT_WIDTH - 4.3 * inch], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.append(table)
    else:
        story.append(Paragraph("No evidence items are attached to this packet yet.", styles["body"]))

    # Closing summary
    story.append(PageBreak())
    _section_header(story, styles, "07 · CONVERSATION SUMMARY", "Use the proof—keep the decision human")
    story.append(Paragraph(_safe(packet.get("promotion_summary")), styles["body"]))
    talking_points = packet.get("talking_points") or []
    if talking_points:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Promotion conversation talking points", styles["subhead"]))
        for item in talking_points:
            story.append(Paragraph(f"• <b>{_safe(item.get('title'))}</b> — {_safe(item.get('result') or item.get('category') or '')}", styles["body"]))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=2, color=TEAL, spaceAfter=9))
    story.append(Paragraph("This packet is an evidence organizer. It does not determine job level, readiness, compensation, promotion eligibility, or an employment outcome.", styles["small"]))

    doc.build(
        story,
        onFirstPage=lambda canvas, doc_obj: _footer(canvas, doc_obj, packet),
        onLaterPages=lambda canvas, doc_obj: _footer(canvas, doc_obj, packet),
    )
    return buffer.getvalue()
