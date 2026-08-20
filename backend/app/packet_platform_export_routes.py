from __future__ import annotations

import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.packet_audit import record_packet_export
from app.packet_platform import parse_csv, parse_item_notes, parse_sections
from app.packet_platform_pdf import build_platform_packet_pdf, make_platform_packet_filename
from app.packet_platform_routes import build_platform_packet
from app.performance_packet_routes import _parse_period
from app.plans import require_feature

router = APIRouter(prefix="/packets", tags=["packets"])


@router.get("/performance-review-v12.pdf")
def download_performance_review_packet_v12_pdf(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    career_area: str | None = Query(None, max_length=120),
    role_title: str | None = Query(None, max_length=160),
    organization: str | None = Query(None, max_length=180),
    confidential: bool = Query(True),
    signature_entry_ids: str | None = Query(None, max_length=2400),
    sections: str | None = Query(None, max_length=600),
    packet_note: str | None = Query(None, max_length=1500),
    item_notes: str | None = Query(None, max_length=6000),
    include_notes: bool = Query(True),
    theme: str | None = Query("classic-dossier", max_length=40),
    brand_name: str | None = Query(None, max_length=120),
    department_label: str | None = Query(None, max_length=120),
    reviewer_name: str | None = Query(None, max_length=120),
    review_cycle_label: str | None = Query(None, max_length=120),
    current_user: dict = Depends(get_current_user),
):
    require_feature(current_user, "export_pdf")
    parsed_start, parsed_end = _parse_period(start_date, end_date)
    packet = build_platform_packet(
        current_user=current_user,
        start_date=parsed_start,
        end_date=parsed_end,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
        signature_entry_ids=parse_csv(signature_entry_ids, max_items=8),
        sections=parse_sections(sections),
        packet_note=packet_note,
        item_notes=parse_item_notes(item_notes),
        include_notes=include_notes,
        theme=theme,
        brand_name=brand_name,
        department_label=department_label,
        reviewer_name=reviewer_name,
        review_cycle_label=review_cycle_label,
    )
    pdf_bytes = build_platform_packet_pdf(packet)
    filename = make_platform_packet_filename(packet)
    record_packet_export(
        user_id=str(current_user["_id"]),
        packet=packet,
        filename=filename,
        pdf_bytes=pdf_bytes,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
