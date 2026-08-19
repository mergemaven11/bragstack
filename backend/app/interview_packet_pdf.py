from __future__ import annotations

import io
import re
from html import escape
from typing import Any

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
GOLD = colors.HexColor("#B68B4C")
INK = colors.HexColor("#172126")
MUTED = colors.HexColor("#667176")
LIGHT = colors.HexColor("#F3F1EA")
LINE = colors.HexColor("#DEDAD0")
PAGE_WIDTH, PAGE_HEIGHT = LETTER
MARGIN_X = 0.62 * inch
MARGIN_TOP = 0.58 * inch
MARGIN_BOTTOM = 0.58 * inch
CONTENT_WIDTH = PAGE_WIDTH - (MARGIN_X * 2)


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle(
            "InterviewKicker", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=8, leading=10, textColor=TEAL, spaceAfter=5,
        ),
        "cover_name": ParagraphStyle(
            "InterviewCoverName", parent=base["Title"], fontName="Times-Bold",
            fontSize=31, leading=34, textColor=INK, spaceAfter=8,
        ),
        "title": ParagraphStyle(
            "InterviewTitle", parent=base["Heading1"], fontName="Times-Bold",
            fontSize=23, leading=27, textColor=INK, spaceAfter=10,
        ),
        "subhead": ParagraphStyle(
            "InterviewSubhead", parent=base["Heading2"], fontName="Times-Bold",
            fontSize=14, leading=17, textColor=INK, spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "InterviewBody", parent=base["BodyText"], fontName="Helvetica",
            fontSize=8.8, leading=12.5, textColor=colors.HexColor("#4F5A60"), spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "InterviewSmall", parent=base["BodyText"], fontName="Helvetica",
            fontSize=7.5, leading=10.2, textColor=MUTED, spaceAfter=4,
        ),
        "label": ParagraphStyle(
            "InterviewLabel", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=6.8, leading=8, textColor=MUTED, spaceAfter=2,
        ),
    }


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


def make_interview_packet_filename(packet: dict[str, Any]) -> str:
    subject = packet.get("subject", {})
    period = packet.get("period", {})
    subject_part = _safe_filename_part(_clean(subject.get("name")), "bragstack-member")
    if period.get("start_date") and period.get("end_date"):
        period_part = f"{period['start_date']}-to-{period['end_date']}"
    else:
        period_part = "all-time"
    return f"{subject_part}-interview-packet-{period_part}.pdf"


def _draw_footer(canvas, doc, packet: dict[str, Any]) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_X, 0.42 * inch, PAGE_WIDTH - MARGIN_X, 0.42 * inch)
    canvas.setFont("Helvetica", 6.6)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, 0.27 * inch, "BragStack · Career Evidence System")
    canvas.drawCentredString(PAGE_WIDTH / 2, 0.27 * inch, _period_display(packet.get("period", {}))[:72])
    canvas.drawRightString(PAGE_WIDTH - MARGIN_X, 0.27 * inch, f"Page {doc.page}")
    if packet.get("confidential"):
        canvas.setFont("Helvetica-Bold", 6.4)
        canvas.setFillColor(TEAL)
        canvas.drawRightString(PAGE_WIDTH - MARGIN_X, PAGE_HEIGHT - 0.34 * inch, "CONFIDENTIAL")
    canvas.restoreState()


def _section(story: list, styles: dict[str, ParagraphStyle], kicker: str, title: str) -> None:
    story.append(Paragraph(escape(kicker.upper()), styles["kicker"]))
    story.append(Paragraph(escape(title), styles["title"]))
    story.append(HRFlowable(width="100%", thickness=1.6, color=TEAL, spaceAfter=12))


def _story_block(item: dict[str, Any], styles: dict[str, ParagraphStyle], number: int) -> Table:
    rows = [
        [Paragraph(f"STORY {number:02d}", styles["label"]), Paragraph(_safe(item.get("category") or "Accomplishment"), styles["small"])],
        [Paragraph(_safe(item.get("title")), styles["subhead"]), ""],
    ]

    detail_parts = []
    if item.get("contribution"):
        detail_parts.append(Paragraph("CONTRIBUTION", styles["label"]))
        detail_parts.append(Paragraph(_safe(item.get("contribution")), styles["body"]))
    if item.get("result"):
        detail_parts.append(Paragraph("RESULT", styles["label"]))
        detail_parts.append(Paragraph(_safe(item.get("result")), styles["body"]))
    if item.get("skills"):
        detail_parts.append(Paragraph("SKILLS", styles["label"]))
        detail_parts.append(Paragraph(escape(" · ".join(item.get("skills", []))), styles["small"]))

    proof = f"{item.get('proof_status', 'Documented')} · {item.get('evidence_count', 0)} evidence item"
    if item.get("evidence_count", 0) != 1:
        proof += "s"
    detail_parts.append(Spacer(1, 3))
    detail_parts.append(Paragraph(escape(proof), styles["small"]))

    prompts = item.get("prep_prompts", [])
    if prompts:
        detail_parts.append(Spacer(1, 4))
        detail_parts.append(Paragraph("PREP QUESTIONS", styles["label"]))
        for prompt in prompts:
            detail_parts.append(Paragraph(f"• {_safe(prompt)}", styles["small"]))

    evidence = item.get("evidence", [])
    if evidence:
        detail_parts.append(Spacer(1, 4))
        detail_parts.append(Paragraph("EXPORTED EVIDENCE REFERENCES", styles["label"]))
        for evidence_item in evidence:
            reference = _clean(evidence_item.get("reference"))
            label = _clean(evidence_item.get("title")) or "Evidence item"
            if reference.startswith("https://") or reference.startswith("http://"):
                ref_safe = escape(reference)
                detail_parts.append(
                    Paragraph(
                        f'{escape(label)} · <link href="{ref_safe}" color="#173F43"><u>{ref_safe}</u></link>',
                        styles["small"],
                    )
                )
            else:
                detail_parts.append(Paragraph(escape(f"{label} · {reference or 'Stored in BragStack'}"), styles["small"]))

    rows.append([detail_parts, ""])
    table = Table(rows, colWidths=[CONTENT_WIDTH - 1.05 * inch, 1.05 * inch])
    table.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 1), (-1, 1)),
                ("SPAN", (0, 2), (-1, 2)),
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.6, LINE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def build_interview_packet_pdf(packet: dict[str, Any]) -> bytes:
    styles = _styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=packet.get("title") or "BragStack Interview Packet",
        author="BragStack",
        subject="Evidence-backed interview preparation packet",
    )

    subject = packet.get("subject", {})
    target = packet.get("target", {})
    scorecard = packet.get("scorecard", {})
    stories = packet.get("interview_stories", [])
    story: list = []

    story.append(Spacer(1, 0.72 * inch))
    story.append(Paragraph("BRAGSTACK · INTERVIEW PACKET", styles["kicker"]))
    story.append(Paragraph(_safe(subject.get("name") or "BragStack Member"), styles["cover_name"]))
    story.append(Paragraph(_safe(subject.get("role") or "Professional"), styles["subhead"]))
    target_text = " · ".join(value for value in [_clean(target.get("role")), _clean(target.get("organization"))] if value)
    if target_text:
        story.append(Spacer(1, 8))
        story.append(Paragraph("INTERVIEW TARGET", styles["label"]))
        story.append(Paragraph(escape(target_text), styles["subhead"]))
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=16))
    story.append(Paragraph(_safe(packet.get("interview_summary")), styles["body"]))
    story.append(Spacer(1, 12))

    metrics = [
        ["Selected stories", scorecard.get("accomplishments", 0)],
        ["Measurable results", scorecard.get("quantified_result_coverage_percent", 0)],
        ["Evidence coverage", scorecard.get("evidence_coverage_percent", 0)],
        ["Skills represented", scorecard.get("skills_demonstrated", 0)],
    ]
    metric_cells = []
    for label, value in metrics:
        display = f"{value}%" if "coverage" in label.lower() or label == "Measurable results" else str(value)
        metric_cells.append([Paragraph(f"<b>{escape(display)}</b>", styles["subhead"]), Paragraph(escape(label), styles["small"])])
    metric_table = Table([metric_cells], colWidths=[CONTENT_WIDTH / 4] * 4)
    metric_table.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.5, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.4, LINE), ("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    story.append(metric_table)

    story.append(PageBreak())
    _section(story, styles, "01 · Selected stories", "Examples to bring into the room")
    if stories:
        for index, item in enumerate(stories, start=1):
            story.append(_story_block(item, styles, index))
            story.append(Spacer(1, 10))
            if index % 2 == 0 and index != len(stories):
                story.append(PageBreak())
                _section(story, styles, "01 · Selected stories", "Interview stories · continued")
    else:
        story.append(Paragraph("No accomplishments were selected for this packet.", styles["body"]))

    story.append(PageBreak())
    _section(story, styles, "02 · Skills & preparation", "What your selected work demonstrates")
    skill_details = packet.get("skill_details", [])
    if skill_details:
        rows = [[Paragraph("<b>Skill</b>", styles["small"]), Paragraph("<b>Selected stories</b>", styles["small"])]]
        for item in skill_details[:12]:
            rows.append([Paragraph(_safe(item.get("skill")), styles["small"]), Paragraph(str(item.get("count", 0)), styles["small"])])
        skills_table = Table(rows, colWidths=[CONTENT_WIDTH - 1.2 * inch, 1.2 * inch], repeatRows=1)
        skills_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("GRID", (0, 0), (-1, -1), 0.4, LINE), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        story.append(skills_table)
        story.append(Spacer(1, 14))

    story.append(Paragraph("PREP BEFORE THE INTERVIEW", styles["label"]))
    unique_prompts: list[str] = []
    for item in stories:
        for prompt in item.get("prep_prompts", []):
            if prompt not in unique_prompts:
                unique_prompts.append(prompt)
    if unique_prompts:
        for prompt in unique_prompts[:12]:
            story.append(Paragraph(f"• {_safe(prompt)}", styles["body"]))
    else:
        story.append(Paragraph("Your selected stories already include contribution, results, and skills. Practice telling them concisely in your own words.", styles["body"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph("INTERVIEW NOTE", styles["label"]))
    story.append(
        Paragraph(
            "BragStack organizes documented work; it does not invent missing STAR details, claims, metrics, or evidence. Use the prompts above to add only facts you can support.",
            styles["body"],
        )
    )

    doc.build(
        story,
        onFirstPage=lambda canvas, doc_obj: _draw_footer(canvas, doc_obj, packet),
        onLaterPages=lambda canvas, doc_obj: _draw_footer(canvas, doc_obj, packet),
    )
    return buffer.getvalue()
