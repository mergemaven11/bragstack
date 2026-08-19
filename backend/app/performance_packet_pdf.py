from __future__ import annotations

import io
import re
from html import escape
from typing import Any, Iterable

from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
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
PAPER = colors.HexColor("#FFFEFA")
WHITE = colors.white

PAGE_WIDTH, PAGE_HEIGHT = LETTER
MARGIN_X = 0.62 * inch
MARGIN_TOP = 0.58 * inch
MARGIN_BOTTOM = 0.58 * inch
CONTENT_WIDTH = PAGE_WIDTH - (MARGIN_X * 2)


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle(
            "PacketCoverKicker",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=TEAL_2,
            spaceAfter=10,
            uppercase=True,
        ),
        "cover_name": ParagraphStyle(
            "PacketCoverName",
            parent=base["Title"],
            fontName="Times-Bold",
            fontSize=31,
            leading=33,
            textColor=INK,
            spaceAfter=8,
        ),
        "cover_role": ParagraphStyle(
            "PacketCoverRole",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#454E54"),
            spaceAfter=8,
        ),
        "cover_period": ParagraphStyle(
            "PacketCoverPeriod",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=15,
            leading=19,
            textColor=INK,
        ),
        "section_kicker": ParagraphStyle(
            "PacketSectionKicker",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=10,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "section_title": ParagraphStyle(
            "PacketSectionTitle",
            parent=base["Heading1"],
            fontName="Times-Bold",
            fontSize=23,
            leading=26,
            textColor=INK,
            spaceAfter=10,
        ),
        "subhead": ParagraphStyle(
            "PacketSubhead",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=13,
            leading=16,
            textColor=INK,
            spaceBefore=4,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "PacketBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.6,
            leading=12.2,
            textColor=colors.HexColor("#505A60"),
            spaceAfter=6,
        ),
        "body_small": ParagraphStyle(
            "PacketBodySmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10.2,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "metric": ParagraphStyle(
            "PacketMetric",
            parent=base["Normal"],
            fontName="Times-Bold",
            fontSize=19,
            leading=21,
            textColor=TEAL,
            alignment=TA_CENTER,
        ),
        "metric_label": ParagraphStyle(
            "PacketMetricLabel",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.4,
            leading=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "receipt_label": ParagraphStyle(
            "PacketReceiptLabel",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=6.8,
            leading=8,
            textColor=MUTED,
            spaceAfter=2,
        ),
        "receipt_title": ParagraphStyle(
            "PacketReceiptTitle",
            parent=base["Heading2"],
            fontName="Times-Bold",
            fontSize=17,
            leading=20,
            textColor=INK,
            spaceAfter=8,
        ),
    }


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe(value: Any) -> str:
    return escape(_clean(value))


def _humanize(value: str) -> str:
    return _clean(value).replace("-", " ").replace("_", " ").title()


def _period_display(period: dict[str, Any]) -> str:
    if period.get("start_date") and period.get("end_date"):
        return f"{period['start_date']} — {period['end_date']}"
    return period.get("label") or "All recorded work"


def _safe_filename_part(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value or "").strip("-")
    return cleaned or fallback


def make_packet_filename(packet: dict[str, Any]) -> str:
    subject = packet.get("subject", {})
    period = packet.get("period", {})
    subject_part = _safe_filename_part(_clean(subject.get("name")), "bragstack-member")
    if period.get("start_date") and period.get("end_date"):
        period_part = f"{period['start_date']}-to-{period['end_date']}"
    else:
        period_part = "all-time"
    return f"{subject_part}-performance-review-{period_part}.pdf"


def _section_header(story: list, styles: dict[str, ParagraphStyle], index: str, title: str) -> None:
    story.append(Paragraph(escape(index), styles["section_kicker"]))
    story.append(Paragraph(escape(title), styles["section_title"]))
    story.append(HRFlowable(width="100%", thickness=1.7, color=TEAL, spaceAfter=12))


def _stat_table(scorecard: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    values = [
        (scorecard.get("accomplishments", 0), "Accomplishments"),
        (scorecard.get("impact_receipts", 0), "Impact Receipts"),
        (scorecard.get("evidence_items", 0), "Evidence Items"),
        (scorecard.get("skills_demonstrated", 0), "Skills Demonstrated"),
    ]
    cells = []
    for value, label in values:
        cells.append([
            Paragraph(escape(str(value)), styles["metric"]),
            Paragraph(escape(label), styles["metric_label"]),
        ])
    table = Table([cells], colWidths=[CONTENT_WIDTH / 4] * 4)
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.7, LINE),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return table


def _coverage_table(scorecard: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    rows = [
        ("Impact Receipt coverage", scorecard.get("receipt_coverage_percent", 0), "Accomplishments converted to structured proof"),
        ("Quantified result coverage", scorecard.get("quantified_result_coverage_percent", 0), "Receipts containing a measurable result"),
        ("Evidence coverage", scorecard.get("evidence_coverage_percent", 0), "Receipts supported by evidence"),
        ("Verification coverage", scorecard.get("verification_coverage_percent", 0), "Receipts with confirmed contribution"),
    ]
    data = [[Paragraph("<b>Measure</b>", styles["body_small"]), Paragraph("<b>Coverage</b>", styles["body_small"]), Paragraph("<b>Meaning</b>", styles["body_small"])]]
    for label, value, note in rows:
        data.append([
            Paragraph(escape(label), styles["body_small"]),
            Paragraph(f"<b>{int(value or 0)}%</b>", styles["body_small"]),
            Paragraph(escape(note), styles["body_small"]),
        ])
    table = Table(data, colWidths=[2.2 * inch, 0.8 * inch, CONTENT_WIDTH - 3 * inch], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                ("TEXTCOLOR", (0, 0), (-1, 0), TEAL),
                ("GRID", (0, 0), (-1, -1), 0.4, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _bars(items: Iterable[tuple[str, int]], *, width: float = CONTENT_WIDTH, max_items: int = 8) -> Drawing:
    items = list(items)[:max_items]
    row_h = 20
    height = max(28, len(items) * row_h + 6)
    drawing = Drawing(width, height)
    if not items:
        drawing.add(String(0, height - 14, "No data for this period.", fontName="Helvetica", fontSize=8, fillColor=MUTED))
        return drawing

    max_value = max(value for _, value in items) or 1
    label_w = 135
    count_w = 28
    bar_w = max(120, width - label_w - count_w - 12)

    for index, (label, value) in enumerate(items):
        y = height - ((index + 1) * row_h) + 4
        drawing.add(String(0, y + 4, str(label)[:26], fontName="Helvetica", fontSize=7.3, fillColor=INK))
        drawing.add(Rect(label_w, y + 2, bar_w, 7, fillColor=colors.HexColor("#E8E5DC"), strokeColor=None))
        fill_w = max(6, bar_w * (float(value) / max_value))
        drawing.add(Rect(label_w, y + 2, fill_w, 7, fillColor=TEAL_2, strokeColor=None))
        drawing.add(String(label_w + bar_w + 8, y + 3, str(value), fontName="Helvetica-Bold", fontSize=7, fillColor=TEAL))
    return drawing


def _link_or_text(reference: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    reference = _clean(reference)
    if reference.startswith("https://") or reference.startswith("http://"):
        safe = escape(reference)
        return Paragraph(f'<link href="{safe}" color="#1F5559"><u>{safe}</u></link>', styles["body_small"])
    return Paragraph(escape(reference or "—"), styles["body_small"])


def _draw_page_footer(canvas, doc, packet: dict[str, Any]) -> None:
    canvas.saveState()
    period = _period_display(packet.get("period", {}))
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_X, 0.42 * inch, PAGE_WIDTH - MARGIN_X, 0.42 * inch)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.6)
    canvas.drawString(MARGIN_X, 0.27 * inch, "BragStack · Career Evidence System")
    canvas.drawCentredString(PAGE_WIDTH / 2, 0.27 * inch, period[:72])
    canvas.drawRightString(PAGE_WIDTH - MARGIN_X, 0.27 * inch, f"Page {doc.page}")
    if packet.get("confidential"):
        canvas.setFont("Helvetica-Bold", 6.4)
        canvas.setFillColor(TEAL)
        canvas.drawRightString(PAGE_WIDTH - MARGIN_X, PAGE_HEIGHT - 0.34 * inch, "CONFIDENTIAL")
    canvas.restoreState()


def _receipt_page(story: list, styles: dict[str, ParagraphStyle], record: dict[str, Any], page_index: int) -> None:
    story.append(PageBreak())
    _section_header(story, styles, f"07.{page_index:02d} · IMPACT RECEIPT", record.get("reference") or "Impact Receipt")
    story.append(Paragraph(_safe(record.get("accomplishment")), styles["receipt_title"]))
    meta = [
        [Paragraph("<b>Date</b>", styles["receipt_label"]), Paragraph(_safe(record.get("entry_date") or "—"), styles["body_small"]), Paragraph("<b>Status</b>", styles["receipt_label"]), Paragraph("Verified" if record.get("verified") else "Self-documented", styles["body_small"])],
    ]
    meta_table = Table(meta, colWidths=[0.55 * inch, 2.0 * inch, 0.55 * inch, CONTENT_WIDTH - 3.1 * inch])
    meta_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("BOX", (0, 0), (-1, -1), 0.5, LINE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    for label, value in (("Contribution", record.get("contribution")), ("Result", record.get("result"))):
        if value:
            story.append(Paragraph(escape(label.upper()), styles["receipt_label"]))
            story.append(Paragraph(_safe(value), styles["body"]))
            story.append(Spacer(1, 3))

    skills = record.get("skills") or []
    if skills:
        story.append(Paragraph("SKILLS DEMONSTRATED", styles["receipt_label"]))
        story.append(Paragraph(escape(" · ".join(skills)), styles["body_small"]))
        story.append(Spacer(1, 5))

    confirmations = [item for item in record.get("confirmations", []) if item.get("status") == "confirmed"]
    if confirmations:
        story.append(Paragraph("VERIFIED RECOGNITION", styles["receipt_label"]))
        for item in confirmations:
            who = item.get("name") or "Confirmed contributor"
            role = item.get("role")
            kind = _humanize(item.get("type") or "confirmation")
            text = f"{who}{f' · {role}' if role else ''} · {kind}"
            story.append(Paragraph(_safe(text), styles["body_small"]))
        story.append(Spacer(1, 5))

    credit = record.get("credit") or []
    if credit:
        story.append(Paragraph("SHARED CREDIT", styles["receipt_label"]))
        for item in credit:
            text = f"{item.get('name') or 'Contributor'} — {item.get('contribution') or ''}"
            story.append(Paragraph(_safe(text), styles["body_small"]))
        story.append(Spacer(1, 5))

    evidence = record.get("evidence") or []
    story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=5, spaceAfter=8))
    story.append(Paragraph(f"EVIDENCE · {len(evidence)} ITEM{'S' if len(evidence) != 1 else ''}", styles["receipt_label"]))
    if evidence:
        rows = [[Paragraph("<b>Evidence</b>", styles["body_small"]), Paragraph("<b>Type</b>", styles["body_small"]), Paragraph("<b>Reference</b>", styles["body_small"])]]
        for item in evidence:
            rows.append([
                Paragraph(_safe(item.get("title") or "Evidence item"), styles["body_small"]),
                Paragraph(_safe(_humanize(item.get("type") or "other")), styles["body_small"]),
                _link_or_text(item.get("reference") or "", styles),
            ])
        table = Table(rows, colWidths=[2.7 * inch, 1.15 * inch, CONTENT_WIDTH - 3.85 * inch], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.append(table)
    else:
        story.append(Paragraph("No supporting evidence is attached to this receipt yet.", styles["body_small"]))


def build_performance_packet_pdf(packet: dict[str, Any]) -> bytes:
    styles = _styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=packet.get("title") or "BragStack Performance Review Packet",
        author="BragStack",
        subject="Evidence-backed performance review packet",
    )

    story: list = []
    subject = packet.get("subject", {})
    context = packet.get("context", {})
    period = packet.get("period", {})
    scorecard = packet.get("scorecard", {})

    # Cover
    story.append(Spacer(1, 0.42 * inch))
    story.append(Paragraph("BRAGSTACK · PERFORMANCE REVIEW PACKET", styles["cover_kicker"]))
    story.append(Spacer(1, 0.26 * inch))
    story.append(Paragraph(_safe(subject.get("name") or "BragStack Member"), styles["cover_name"]))
    story.append(Paragraph(_safe(subject.get("role") or "Professional"), styles["cover_role"]))
    organization = _clean(context.get("organization"))
    career_area = _clean(context.get("career_area"))
    if organization:
        story.append(Paragraph(_safe(organization), styles["body"]))
    if career_area:
        story.append(Paragraph(_safe(career_area), styles["body_small"]))
    story.append(Spacer(1, 0.18 * inch))
    story.append(HRFlowable(width=0.85 * inch, thickness=3, color=GOLD, spaceAfter=18))
    story.append(Paragraph("REVIEW PERIOD", styles["section_kicker"]))
    story.append(Paragraph(_safe(_period_display(period)), styles["cover_period"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(_stat_table(scorecard, styles))
    story.append(Spacer(1, 0.32 * inch))
    story.append(Paragraph("Evidence-backed career record generated from documented accomplishments, Impact Receipts, supporting evidence, and confirmations.", styles["body_small"]))

    # Executive scorecard
    story.append(PageBreak())
    _section_header(story, styles, "01 · EXECUTIVE SCORECARD", "Proof at a glance")
    story.append(Paragraph("A transparent summary of documented work for this review period. Coverage measures are calculated from actual records rather than an opaque AI score.", styles["body"]))
    story.append(_stat_table(scorecard, styles))
    story.append(Spacer(1, 12))
    story.append(_coverage_table(scorecard, styles))
    story.append(Spacer(1, 10))
    depth = scorecard.get("evidence_depth", 0)
    assertions = scorecard.get("confirmed_assertions", 0)
    story.append(Paragraph(f"<b>Evidence depth:</b> {escape(str(depth))}× average supporting items per Impact Receipt · <b>Confirmed assertions:</b> {escape(str(assertions))}", styles["body"]))

    # Impact analytics
    story.append(PageBreak())
    _section_header(story, styles, "02 · IMPACT ANALYTICS", "How the work is distributed")
    analytics = packet.get("impact_analytics", {})
    story.append(Paragraph("Work themes", styles["subhead"]))
    story.append(_bars((analytics.get("categories") or {}).items()))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Most demonstrated skills", styles["subhead"]))
    story.append(_bars((analytics.get("top_skills") or {}).items()))
    activity = analytics.get("activity_by_month") or {}
    if activity:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Activity by month", styles["subhead"]))
        story.append(_bars(activity.items(), max_items=12))

    # Signature accomplishments
    story.append(PageBreak())
    _section_header(story, styles, "03 · SIGNATURE ACCOMPLISHMENTS", "The strongest documented work")
    accomplishments = packet.get("signature_accomplishments") or []
    if accomplishments:
        for index, item in enumerate(accomplishments[:8], 1):
            story.append(Paragraph(f"{index:02d} · {_safe(item.get('title'))}", styles["subhead"]))
            meta = " · ".join(filter(None, [_clean(item.get("category")), _clean(item.get("entry_date"))]))
            if meta:
                story.append(Paragraph(_safe(meta), styles["body_small"]))
            if item.get("result"):
                story.append(Paragraph(_safe(item.get("result")), styles["body"]))
            signals = []
            if item.get("verified"):
                signals.append("Verified")
            if item.get("has_receipt"):
                signals.append("Impact Receipt")
            if item.get("evidence_count"):
                signals.append(f"{item['evidence_count']} evidence")
            if signals:
                story.append(Paragraph(_safe(" · ".join(signals)), styles["body_small"]))
            story.append(HRFlowable(width="100%", thickness=0.4, color=LINE, spaceBefore=3, spaceAfter=7))
    else:
        story.append(Paragraph("No signature accomplishments are available for this period yet.", styles["body"]))

    # Measurable results
    story.append(PageBreak())
    _section_header(story, styles, "04 · MEASURABLE RESULTS", "Outcomes with quantified signals")
    results = packet.get("measurable_results") or []
    if results:
        rows = [[Paragraph("<b>Signal</b>", styles["body_small"]), Paragraph("<b>Result</b>", styles["body_small"]), Paragraph("<b>Accomplishment</b>", styles["body_small"])]]
        for item in results[:12]:
            rows.append([
                Paragraph(_safe(item.get("metric_display") or "—"), styles["body_small"]),
                Paragraph(_safe(item.get("result") or ""), styles["body_small"]),
                Paragraph(_safe(item.get("title") or ""), styles["body_small"]),
            ])
        table = Table(rows, colWidths=[0.9 * inch, 3.2 * inch, CONTENT_WIDTH - 4.1 * inch], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.append(table)
    else:
        story.append(Paragraph("No quantified outcomes were documented for this period. Results remain visible elsewhere in the packet without inventing metrics.", styles["body"]))

    # Skills and growth
    story.append(PageBreak())
    _section_header(story, styles, "05 · SKILLS & GROWTH", "Demonstrated capabilities over time")
    skill_details = packet.get("skill_details") or []
    if skill_details:
        rows = [[Paragraph("<b>Skill</b>", styles["body_small"]), Paragraph("<b>Uses</b>", styles["body_small"]), Paragraph("<b>First seen</b>", styles["body_small"]), Paragraph("<b>Most recent</b>", styles["body_small"])]]
        for item in skill_details[:20]:
            rows.append([
                Paragraph(_safe(item.get("skill")), styles["body_small"]),
                Paragraph(_safe(item.get("count")), styles["body_small"]),
                Paragraph(_safe(item.get("first_seen") or "—"), styles["body_small"]),
                Paragraph(_safe(item.get("last_seen") or "—"), styles["body_small"]),
            ])
        table = Table(rows, colWidths=[2.5 * inch, 0.6 * inch, 1.25 * inch, CONTENT_WIDTH - 4.35 * inch], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.append(table)
    else:
        story.append(Paragraph("No skill evidence is available for this review period yet.", styles["body"]))

    # Contribution and recognition
    story.append(PageBreak())
    _section_header(story, styles, "06 · CONTRIBUTION & RECOGNITION", "How the work was carried and confirmed")
    contributions = packet.get("contribution_records") or []
    if contributions:
        for item in contributions[:12]:
            status = "Verified" if item.get("verified") else "Self-documented"
            story.append(Paragraph(f"{_safe(item.get('reference'))} · {_safe(status)}", styles["section_kicker"]))
            story.append(Paragraph(_safe(item.get("accomplishment")), styles["subhead"]))
            if item.get("contribution"):
                story.append(Paragraph(f"<b>Contribution:</b> {_safe(item.get('contribution'))}", styles["body"]))
            if item.get("result"):
                story.append(Paragraph(f"<b>Result:</b> {_safe(item.get('result'))}", styles["body"]))
            confirmations = [c for c in item.get("confirmations", []) if c.get("status") == "confirmed"]
            if confirmations:
                names = ", ".join(c.get("name") or "Confirmed contributor" for c in confirmations)
                story.append(Paragraph(f"<b>Recognition:</b> {_safe(names)}", styles["body_small"]))
            story.append(HRFlowable(width="100%", thickness=0.4, color=LINE, spaceAfter=7))
    else:
        story.append(Paragraph("No structured contribution records are available for this period yet.", styles["body"]))

    # One physical receipt page per receipt.
    receipt_records = packet.get("receipt_records") or []
    for index, record in enumerate(receipt_records, 1):
        _receipt_page(story, styles, record, index)

    # Evidence index
    story.append(PageBreak())
    _section_header(story, styles, "08 · EVIDENCE INDEX", "Supporting material referenced by the packet")
    evidence_index = packet.get("evidence_index") or []
    if evidence_index:
        rows = [[Paragraph("<b>Receipt</b>", styles["body_small"]), Paragraph("<b>Evidence</b>", styles["body_small"]), Paragraph("<b>Type</b>", styles["body_small"]), Paragraph("<b>Reference</b>", styles["body_small"])]]
        for item in evidence_index:
            rows.append([
                Paragraph(_safe(item.get("receipt_reference")), styles["body_small"]),
                Paragraph(_safe(item.get("title") or "Evidence item"), styles["body_small"]),
                Paragraph(_safe(_humanize(item.get("type") or "other")), styles["body_small"]),
                _link_or_text(item.get("reference") or "", styles),
            ])
        table = Table(rows, colWidths=[1.05 * inch, 2.25 * inch, 1.05 * inch, CONTENT_WIDTH - 4.35 * inch], repeatRows=1)
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.append(table)
    else:
        story.append(Paragraph("No supporting evidence items are attached to this packet yet.", styles["body"]))

    # Review summary
    story.append(PageBreak())
    _section_header(story, styles, "09 · REVIEW SUMMARY", "Evidence-backed review narrative")
    story.append(Paragraph(_safe(packet.get("review_summary")), styles["body"]))
    story.append(Spacer(1, 10))
    talking_points = packet.get("talking_points") or []
    if talking_points:
        story.append(Paragraph("Review talking points", styles["subhead"]))
        for item in talking_points:
            story.append(Paragraph(f"• <b>{_safe(item.get('title'))}</b> — {_safe(item.get('result') or item.get('category') or '')}", styles["body"]))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph("This packet summarizes documented work and supporting proof. It is not an automated performance rating, employment decision, or promotion determination.", styles["body_small"]))

    doc.build(
        story,
        onFirstPage=lambda canvas, doc_obj: _draw_page_footer(canvas, doc_obj, packet),
        onLaterPages=lambda canvas, doc_obj: _draw_page_footer(canvas, doc_obj, packet),
    )
    return buffer.getvalue()
