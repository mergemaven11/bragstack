from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from app.database import packet_export_audit_collection


def count_pdf_pages(pdf_bytes: bytes) -> int | None:
    if not pdf_bytes:
        return None
    count = len(re.findall(rb"/Type\s*/Page(?!s)\b", pdf_bytes))
    return count or None


def record_packet_export(
    *,
    user_id: str,
    packet: dict[str, Any],
    filename: str,
    pdf_bytes: bytes,
) -> None:
    """Store metadata only. Never store PDF bytes or evidence/body contents."""
    packet_export_audit_collection.insert_one(
        {
            "user_id": user_id,
            "packet_kind": packet.get("kind") or "unknown",
            "generated_at": datetime.now(timezone.utc),
            "review_period": {
                "start_date": packet.get("period", {}).get("start_date"),
                "end_date": packet.get("period", {}).get("end_date"),
                "label": packet.get("period", {}).get("label"),
            },
            "career_area": packet.get("context", {}).get("career_area") or "",
            "filename": filename,
            "page_count": count_pdf_pages(pdf_bytes),
            "theme": packet.get("render_config", {}).get("theme") or "classic-dossier",
        }
    )


def serialize_export(item: dict[str, Any]) -> dict[str, Any]:
    generated = item.get("generated_at")
    return {
        "id": str(item.get("_id")),
        "packet_kind": item.get("packet_kind"),
        "generated_at": generated.isoformat() if hasattr(generated, "isoformat") else generated,
        "review_period": item.get("review_period") or {},
        "career_area": item.get("career_area") or "",
        "filename": item.get("filename") or "",
        "page_count": item.get("page_count"),
        "theme": item.get("theme") or "classic-dossier",
    }
