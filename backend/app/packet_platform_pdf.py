from __future__ import annotations

import io
import re
from html import escape
from typing import Any

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

PAGE_WIDTH, PAGE_HEIGHT = LETTER
MARGIN_X = 0.62 * inch
CONTENT_WIDTH = PAGE_WIDTH - 2 * MARGIN_X

THEMES = {
    "classic-dossier": {
        "accent": colors.HexColor("#173F43"),
        "accent2": colors.HexColor("#B68B4C"),
        "ink": colors.HexColor("#172126"),
        "muted": colors.HexColor("#667176"),
        "light": colors.HexColor("#F3F1EA"),
        "line": colors.HexColor("#DEDAD0"),
        "heading": "Times-Bold",
        "body": "Helvetica",
    },
    "modern-minimal": {
        "accent": colors.HexColor("#243B53"),
        "accent2": colors.HexColor("#3E7C8F"),
        "ink": colors.HexColor("#16202A"),
        "muted": colors.HexColor("#697986"),
        "light": colors.HexColor("#F3F7F9"),
        "line": colors.HexColor("#D9E2E8"),
        "heading": "Helvetica-Bold",
        "body": "Helvetica",
    },
    "executive-report": {
        "accent": colors.HexColor("#342A32"),
        "accent2": colors.HexColor("#8A5A44"),
        "ink": colors.HexColor("#211C20"),
        "muted": colors.HexColor("#726A70"),
        "light": colors.HexColor("#F5F1F0"),
        "line": colors.HexColor("#DDD5D2"),
        "heading": "Times-Bold",
        "body": "Helvetica",
    },
}


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe(value: Any) -> str:
    return escape(_clean(value))


def _filename_part(value: str, fallback: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", value or "").strip("-") or fallback


def make_platform_packet_filename(packet: dict[str, Any]) -> str:
    name = _filename_part(_clean(packet.get("subject", {}).get("name")), "bragstack-member")
    period = packet.get("period", {})
    if period.get("start_date") and period.get("end_date"):
        period_part = f"{period['start_date']}-to-{period['end_date']}"
    else:
        period_part = "all-time"
    return f"{name}-performance-review-{period_part}.pdf"


def _styles(theme: dict[str, Any]) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle("V12Kicker", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=7.4, leading=9, textColor=theme["accent"], spaceAfter=5),
        "cover": ParagraphStyle("V12Cover", parent=base["Title"], fontName=theme["heading"], fontSize=30, leading=33, textColor=theme["ink"], spaceAfter=8),
        "cover_role": ParagraphStyle("V12CoverRole", parent=base["Normal"], fontName=theme["body"], fontSize=13, leading=17, textColor=theme["muted"], spaceAfter=5),
        "title": ParagraphStyle("V12Title", parent=base["Heading1"], fontName=theme["heading"], fontSize=22, leading=25, textColor=theme["ink"], spaceAfter=9),
        "subhead": ParagraphStyle("V12Subhead", parent=base["Heading2"], fontName=theme["heading"], fontSize=12.5, leading=15, textColor=theme["ink"], spaceAfter=4),
        "body": ParagraphStyle("V12Body", parent=base["BodyText"], fontName=theme["body"], fontSize=8.5, leading=12, textColor=theme["muted"], spaceAfter=6),
        "small": ParagraphStyle("V12Small", parent=base["BodyText"], fontName=theme["body"], fontSize=7.2, leading=9.6, textColor=theme["muted"], spaceAfter=3),
        "metric": ParagraphStyle("V12Metric", parent=base["Normal"], fontName=theme["heading"], fontSize=17, leading=19, textColor=theme["accent"], alignment=TA_CENTER),
        "metric_label": ParagraphStyle("V12MetricLabel", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=6.1, leading=8, textColor=theme["muted"], alignment=TA_CENTER),
        "note": ParagraphStyle("V12Note", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=7.6, leading=10.4, textColor=theme["muted"], leftIndent=8, borderPadding=7, borderColor=theme["line"], borderWidth=0.5, backColor=theme["light"], spaceBefore=4, spaceAfter=8),
    }


def _period(packet: dict[str, Any]) -> str:
    period = packet.get("period", {})
    if period.get("start_date") and period.get("end_date"):
        return f"{period['start_date']} — {period['end_date']}"
    return period.get("label") or "All recorded work"


def _page_header(story: list, styles: dict, theme: dict, kicker: str, title: str) -> None:
    story.append(Paragraph(_safe(kicker.upper()), styles["kicker"]))
    story.append(Paragraph(_safe(title), styles["title"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=theme["accent"], spaceAfter=11))


def _stat_table(packet: dict[str, Any], styles: dict, theme: dict) -> Table:
    score = packet.get("scorecard", {})
    metrics = [
        (score.get("accomplishments", 0), "Accomplishments"),
        (score.get("impact_receipts", 0), "Impact Receipts"),
        (score.get("evidence_items", 0), "Evidence Items"),
        (score.get("skills_demonstrated", 0), "Skills"),
    ]
    cells = [[Paragraph(_safe(value), styles["metric"]), Paragraph(_safe(label), styles["metric_label"])] for value, label in metrics]
    table = Table([cells], colWidths=[CONTENT_WIDTH / 4] * 4)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.6, theme["line"]),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, theme["line"]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def _simple_table(rows: list[list[Any]], widths: list[float], styles: dict, theme: dict) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), theme["light"]),
        ("GRID", (0, 0), (-1, -1), 0.35, theme["line"]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def _annotation(story: list, packet: dict[str, Any], key: str, styles: dict) -> None:
    annotations = packet.get("annotations", {})
    if not annotations.get("include_in_export"):
        return
    note = (annotations.get("item_notes") or {}).get(key)
    if note:
        story.append(Paragraph(f"<b>User-authored context:</b> {_safe(note)}", styles["note"]))


def _draw_footer(canvas, doc, packet: dict[str, Any], theme: dict) -> None:
    canvas.saveState()
    canvas.setStrokeColor(theme["line"])
    canvas.line(MARGIN_X, 0.42 * inch, PAGE_WIDTH - MARGIN_X, 0.42 * inch)
    canvas.setFont("Helvetica", 6.4)
    canvas.setFillColor(theme["muted"])
    provenance = packet.get("branding", {}).get("provenance") or "BragStack · Career Evidence System"
    canvas.drawString(MARGIN_X, 0.27 * inch, provenance[:70])
    canvas.drawCentredString(PAGE_WIDTH / 2, 0.27 * inch, _period(packet)[:62])
    canvas.drawRightString(PAGE_WIDTH - MARGIN_X, 0.27 * inch, f"Page {doc.page}")
    if packet.get("confidential"):
        canvas.setFont("Helvetica-Bold", 6.2)
        canvas.setFillColor(theme["accent"])
        canvas.drawRightString(PAGE_WIDTH - MARGIN_X, PAGE_HEIGHT - 0.34 * inch, "CONFIDENTIAL")
    canvas.restoreState()


def build_platform_packet_pdf(packet: dict[str, Any]) -> bytes:
    theme_name = packet.get("render_config", {}).get("theme") or "classic-dossier"
    theme = THEMES.get(theme_name, THEMES["classic-dossier"])
    styles = _styles(theme)
    sections = set(packet.get("render_config", {}).get("sections") or [])
    annotations = packet.get("annotations", {})
    branding = packet.get("branding", {})

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=0.58 * inch,
        bottomMargin=0.58 * inch,
        title=packet.get("title") or "BragStack Performance Review Packet",
        author="BragStack",
        subject="Configurable evidence-backed career packet",
    )
    story: list = []

    # Required cover
    story.append(Spacer(1, 0.4 * inch))
    brand = _clean(branding.get("brand_name")) or "BRAGSTACK"
    story.append(Paragraph(_safe(f"{brand} · PERFORMANCE REVIEW PACKET"), styles["kicker"]))
    story.append(Spacer(1, 0.22 * inch))
    subject = packet.get("subject", {})
    context = packet.get("context", {})
    story.append(Paragraph(_safe(subject.get("name") or "BragStack Member"), styles["cover"]))
    story.append(Paragraph(_safe(subject.get("role") or "Professional"), styles["cover_role"]))
    for line in [context.get("organization"), branding.get("department_label"), context.get("career_area")]:
        if _clean(line):
            story.append(Paragraph(_safe(line), styles["body"]))
    story.append(Spacer(1, 0.12 * inch))
    story.append(HRFlowable(width=0.9 * inch, thickness=3, color=theme["accent2"], spaceAfter=15))
    story.append(Paragraph("REVIEW PERIOD", styles["kicker"]))
    story.append(Paragraph(_safe(_period(packet)), styles["subhead"]))
    if _clean(branding.get("review_cycle_label")):
        story.append(Paragraph(_safe(f"Review cycle · {branding['review_cycle_label']}"), styles["body"]))
    if _clean(branding.get("reviewer_name")):
        story.append(Paragraph(_safe(f"Prepared for · {branding['reviewer_name']}"), styles["body"]))
    story.append(Spacer(1, 0.18 * inch))
    story.append(_stat_table(packet, styles, theme))
    if annotations.get("include_in_export") and _clean(annotations.get("packet_note")):
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"<b>User-authored packet context:</b> {_safe(annotations['packet_note'])}", styles["note"]))

    # Required scorecard
    story.append(PageBreak())
    _page_header(story, styles, theme, "01 · Executive Scorecard", "Proof at a glance")
    story.append(Paragraph("Coverage measures describe documented evidence. They do not assign an opaque performance or readiness score.", styles["body"]))
    story.append(_stat_table(packet, styles, theme))
    score = packet.get("scorecard", {})
    rows = [[Paragraph("<b>Measure</b>", styles["small"]), Paragraph("<b>Coverage</b>", styles["small"])]]
    for label, key in [
        ("Impact Receipt coverage", "receipt_coverage_percent"),
        ("Quantified result coverage", "quantified_result_coverage_percent"),
        ("Evidence coverage", "evidence_coverage_percent"),
        ("Verified Recognition coverage", "verification_coverage_percent"),
    ]:
        rows.append([Paragraph(_safe(label), styles["small"]), Paragraph(_safe(f"{score.get(key, 0)}%"), styles["small"])])
    story.append(Spacer(1, 10))
    story.append(_simple_table(rows, [4.8 * inch, CONTENT_WIDTH - 4.8 * inch], styles, theme))

    if "impact-analytics" in sections:
        story.append(PageBreak())
        _page_header(story, styles, theme, "02 · Impact Analytics", "How the work shows up")
        analytics = packet.get("impact_analytics", {})
        for heading, values in [("Work themes", analytics.get("categories", {})), ("Demonstrated skills", analytics.get("top_skills", {}))]:
            story.append(Paragraph(_safe(heading), styles["subhead"]))
            rows = [[Paragraph("<b>Theme</b>", styles["small"]), Paragraph("<b>Records</b>", styles["small"])]]
            for label, count in list((values or {}).items())[:10]:
                rows.append([Paragraph(_safe(label), styles["small"]), Paragraph(_safe(count), styles["small"])])
            story.append(_simple_table(rows, [5.1 * inch, CONTENT_WIDTH - 5.1 * inch], styles, theme))
            story.append(Spacer(1, 10))

    if "signature-accomplishments" in sections:
        story.append(PageBreak())
        _page_header(story, styles, theme, "03 · Signature Accomplishments", "Work selected for the conversation")
        for index, item in enumerate(packet.get("signature_accomplishments", []) or [], 1):
            story.append(Paragraph(_safe(f"{index:02d} · {item.get('title') or 'Accomplishment'}"), styles["subhead"]))
            meta = " · ".join(filter(None, [_clean(item.get("category")), _clean(item.get("entry_date"))]))
            if meta:
                story.append(Paragraph(_safe(meta), styles["small"]))
            if item.get("result"):
                story.append(Paragraph(_safe(item["result"]), styles["body"]))
            _annotation(story, packet, str(item.get("entry_id")), styles)
            story.append(HRFlowable(width="100%", thickness=0.35, color=theme["line"], spaceAfter=7))

    if "measurable-results" in sections:
        story.append(PageBreak())
        _page_header(story, styles, theme, "04 · Measurable Results", "Outcomes with numbers behind them")
        rows = [[Paragraph("<b>Signal</b>", styles["small"]), Paragraph("<b>Result</b>", styles["small"]), Paragraph("<b>Accomplishment</b>", styles["small"])]]
        for item in (packet.get("measurable_results", []) or [])[:12]:
            rows.append([
                Paragraph(_safe(item.get("metric_display") or "Measured"), styles["small"]),
                Paragraph(_safe(item.get("result")), styles["small"]),
                Paragraph(_safe(item.get("title")), styles["small"]),
            ])
        story.append(_simple_table(rows, [0.9 * inch, 3.0 * inch, CONTENT_WIDTH - 3.9 * inch], styles, theme))

    if "skills-growth" in sections:
        story.append(PageBreak())
        _page_header(story, styles, theme, "05 · Skills & Growth", "Capabilities demonstrated in real work")
        rows = [[Paragraph("<b>Skill</b>", styles["small"]), Paragraph("<b>Uses</b>", styles["small"]), Paragraph("<b>First shown</b>", styles["small"]), Paragraph("<b>Most recent</b>", styles["small"])]]
        for item in (packet.get("skill_details", []) or [])[:20]:
            rows.append([
                Paragraph(_safe(item.get("skill")), styles["small"]),
                Paragraph(_safe(item.get("count")), styles["small"]),
                Paragraph(_safe(item.get("first_seen") or "—"), styles["small"]),
                Paragraph(_safe(item.get("last_seen") or "—"), styles["small"]),
            ])
        story.append(_simple_table(rows, [2.6 * inch, 0.6 * inch, 1.35 * inch, CONTENT_WIDTH - 4.55 * inch], styles, theme))

    if "contribution-recognition" in sections:
        story.append(PageBreak())
        _page_header(story, styles, theme, "06 · Contribution & Verified Recognition", "What you moved forward and who confirmed it")
        for item in (packet.get("contribution_records", []) or [])[:12]:
            story.append(Paragraph(_safe(item.get("accomplishment")), styles["subhead"]))
            if item.get("contribution"):
                story.append(Paragraph(f"<b>Contribution:</b> {_safe(item['contribution'])}", styles["body"]))
            if item.get("result"):
                story.append(Paragraph(f"<b>Result:</b> {_safe(item['result'])}", styles["body"]))
            recognition = item.get("recognition") or []
            if recognition:
                labels = [entry.get("label") for entry in recognition if entry.get("label")]
                story.append(Paragraph(f"<b>Verified Recognition:</b> {_safe(' · '.join(labels))}", styles["small"]))
            _annotation(story, packet, str(item.get("reference")), styles)
            story.append(HRFlowable(width="100%", thickness=0.35, color=theme["line"], spaceAfter=7))

    if "impact-receipts" in sections:
        for index, receipt in enumerate(packet.get("receipt_records", []) or [], 1):
            story.append(PageBreak())
            _page_header(story, styles, theme, f"07.{index:02d} · Impact Receipt", receipt.get("reference") or "Impact Receipt")
            story.append(Paragraph(_safe(receipt.get("accomplishment")), styles["subhead"]))
            if receipt.get("contribution"):
                story.append(Paragraph(f"<b>Contribution:</b> {_safe(receipt['contribution'])}", styles["body"]))
            if receipt.get("result"):
                story.append(Paragraph(f"<b>Result:</b> {_safe(receipt['result'])}", styles["body"]))
            recognition = receipt.get("recognition") or []
            if recognition:
                story.append(Paragraph("VERIFIED RECOGNITION", styles["kicker"]))
                for entry in recognition:
                    detail = " · ".join(filter(None, [entry.get("label"), entry.get("name"), entry.get("role")]))
                    story.append(Paragraph(_safe(detail), styles["small"]))
            evidence = receipt.get("evidence") or []
            story.append(Spacer(1, 6))
            story.append(Paragraph(_safe(f"Evidence · {len(evidence)} item{'s' if len(evidence) != 1 else ''}"), styles["kicker"]))
            for evidence_item in evidence:
                story.append(Paragraph(_safe(f"{evidence_item.get('title') or 'Evidence item'} · {evidence_item.get('type') or 'other'} · {evidence_item.get('reference') or 'Stored in BragStack'}"), styles["small"]))
            _annotation(story, packet, str(receipt.get("id")), styles)

    if "evidence-index" in sections:
        story.append(PageBreak())
        _page_header(story, styles, theme, "08 · Evidence Index", "Source material behind the claims")
        rows = [[Paragraph("<b>Receipt</b>", styles["small"]), Paragraph("<b>Evidence</b>", styles["small"]), Paragraph("<b>Type</b>", styles["small"]), Paragraph("<b>Reference</b>", styles["small"])]]
        for item in packet.get("evidence_index", []) or []:
            rows.append([
                Paragraph(_safe(item.get("receipt_reference")), styles["small"]),
                Paragraph(_safe(item.get("title")), styles["small"]),
                Paragraph(_safe(item.get("type")), styles["small"]),
                Paragraph(_safe(item.get("reference") or "Stored in BragStack"), styles["small"]),
            ])
        story.append(_simple_table(rows, [1.0 * inch, 2.3 * inch, 1.1 * inch, CONTENT_WIDTH - 4.4 * inch], styles, theme))

    if "review-summary" in sections:
        story.append(PageBreak())
        _page_header(story, styles, theme, "09 · Review Summary", "The case, assembled")
        story.append(Paragraph(_safe(packet.get("review_summary")), styles["body"]))
        talking = packet.get("talking_points", []) or []
        if talking:
            story.append(Paragraph("Review talking points", styles["subhead"]))
            for index, item in enumerate(talking[:8], 1):
                text = f"{index}. {item.get('title') or 'Accomplishment'}"
                if item.get("result"):
                    text += f" — {item['result']}"
                story.append(Paragraph(_safe(text), styles["body"]))

    doc.build(
        story,
        onFirstPage=lambda canvas, document: _draw_footer(canvas, document, packet, theme),
        onLaterPages=lambda canvas, document: _draw_footer(canvas, document, packet, theme),
    )
    return buffer.getvalue()
