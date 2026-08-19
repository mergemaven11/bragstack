from __future__ import annotations

import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.certification_packet_pdf import build_certification_packet_pdf, make_certification_packet_filename
from app.certification_packet_routes import _build_certification_packet
from app.performance_packet_routes import _parse_period
from app.plans import require_feature


router = APIRouter(prefix="/packets", tags=["packets"])


@router.get("/certification.pdf")
def download_certification_packet_pdf(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    career_area: str | None = Query(None, max_length=120),
    role_title: str | None = Query(None, max_length=160),
    organization: str | None = Query(None, max_length=180),
    confidential: bool = Query(True),
    credential_name: str | None = Query(None, max_length=180),
    issuing_body: str | None = Query(None, max_length=180),
    review_type: str | None = Query(None, max_length=120),
    requirement_notes: str | None = Query(None, max_length=1200),
    current_user: dict = Depends(get_current_user),
):
    """Generate a downloadable certification and licensure evidence packet PDF."""

    require_feature(current_user, "export_pdf")
    parsed_start, parsed_end = _parse_period(start_date, end_date)
    packet = _build_certification_packet(
        current_user=current_user,
        start_date=parsed_start,
        end_date=parsed_end,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
        credential_name=credential_name,
        issuing_body=issuing_body,
        review_type=review_type,
        requirement_notes=requirement_notes,
    )["packet"]

    pdf_bytes = build_certification_packet_pdf(packet)
    filename = make_certification_packet_filename(packet)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
