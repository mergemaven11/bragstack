from __future__ import annotations

import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.packet_audit import record_packet_export
from app.performance_packet_routes import _parse_period
from app.plans import require_feature
from app.promotion_packet_pdf import build_promotion_packet_pdf, make_promotion_packet_filename
from app.promotion_packet_routes import _build_promotion_packet


router = APIRouter(prefix="/packets", tags=["packets"])


@router.get("/promotion.pdf")
def download_promotion_packet_pdf(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    career_area: str | None = Query(None, max_length=120),
    role_title: str | None = Query(None, max_length=160),
    organization: str | None = Query(None, max_length=180),
    confidential: bool = Query(True),
    target_role: str | None = Query(None, max_length=160),
    target_level: str | None = Query(None, max_length=120),
    current_user: dict = Depends(get_current_user),
):
    """Generate a downloadable PDF promotion packet for eligible plans."""

    require_feature(current_user, "export_pdf")
    parsed_start, parsed_end = _parse_period(start_date, end_date)
    packet = _build_promotion_packet(
        current_user=current_user,
        start_date=parsed_start,
        end_date=parsed_end,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
        target_role=target_role,
        target_level=target_level,
    )["packet"]

    pdf_bytes = build_promotion_packet_pdf(packet)
    filename = make_promotion_packet_filename(packet)
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
