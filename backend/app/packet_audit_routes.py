from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.auth import get_current_user
from app.database import packet_export_audit_collection
from app.packet_audit import serialize_export
from app.plans import require_feature

router = APIRouter(prefix="/packets", tags=["packets"])


@router.get("/export-history")
def get_packet_export_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    require_feature(current_user, "export_pdf")
    items = list(
        packet_export_audit_collection.find({"user_id": str(current_user["_id"])})
        .sort("generated_at", -1)
        .limit(limit)
    )
    return {"exports": [serialize_export(item) for item in items]}
