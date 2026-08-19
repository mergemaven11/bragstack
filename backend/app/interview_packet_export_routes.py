from __future__ import annotations

import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.auth import get_current_user
from app.interview_packet_pdf import build_interview_packet_pdf, make_interview_packet_filename
from app.interview_packet_routes import _build_interview_packet, _parse_selected_ids
from app.performance_packet_routes import _parse_period
from app.plans import require_feature


router = APIRouter(prefix="/packets", tags=["packets"])


@router.get("/interview.pdf")
def download_interview_packet_pdf(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    career_area: str | None = Query(None, max_length=120),
    role_title: str | None = Query(None, max_length=160),
    organization: str | None = Query(None, max_length=180),
    confidential: bool = Query(True),
    selected_entry_ids: str | None = Query(None, max_length=512),
    target_role: str | None = Query(None, max_length=160),
    target_organization: str | None = Query(None, max_length=180),
    include_evidence_references: bool = Query(False),
    current_user: dict = Depends(get_current_user),
):
    """Generate a downloadable evidence-backed interview packet PDF."""

    require_feature(current_user, "export_pdf")
    parsed_start, parsed_end = _parse_period(start_date, end_date)
    packet = _build_interview_packet(
        current_user=current_user,
        start_date=parsed_start,
        end_date=parsed_end,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
        selected_entry_ids=_parse_selected_ids(selected_entry_ids),
        target_role=target_role,
        target_organization=target_organization,
        include_evidence_references=include_evidence_references,
    )["packet"]

    pdf_bytes = build_interview_packet_pdf(packet)
    filename = make_interview_packet_filename(packet)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
