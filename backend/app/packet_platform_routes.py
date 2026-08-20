from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query

from app.auth import get_current_user
from app.database import impact_receipts_collection
from app.packet_platform import (
    apply_packet_platform,
    parse_csv,
    parse_item_notes,
    parse_sections,
)
from app.performance_packet_routes import (
    _build_packet,
    _clean_string,
    _entries_for_period,
    _entry_work_date,
    _parse_period,
)

router = APIRouter(prefix="/packets", tags=["packets"])


def _signature_candidates(*, current_user: dict, start_date: date | None, end_date: date | None) -> list[dict[str, Any]]:
    user_id = str(current_user["_id"])
    entries = _entries_for_period(user_id=user_id, start_date=start_date, end_date=end_date)
    receipts = list(impact_receipts_collection.find({"user_id": user_id}))
    receipts_by_source = {
        str(item.get("source_entry_id")): item
        for item in receipts
        if item.get("source_entry_id")
    }
    candidates: list[dict[str, Any]] = []
    for entry in entries:
        entry_id = str(entry["_id"])
        receipt = receipts_by_source.get(entry_id)
        work_date = _entry_work_date(entry)
        result = _clean_string(receipt.get("result") if receipt else entry.get("impact"))
        skills = receipt.get("skills", []) if receipt and receipt.get("skills") else entry.get("tags", [])
        confirmations = receipt.get("confirmations", []) if receipt else []
        candidates.append(
            {
                "entry_id": entry_id,
                "receipt_id": str(receipt.get("_id")) if receipt else None,
                "entry_date": work_date.isoformat() if work_date else None,
                "title": _clean_string(entry.get("title"), "Untitled accomplishment"),
                "category": _clean_string(entry.get("category"), "Uncategorized"),
                "result": result,
                "skills": [_clean_string(value) for value in skills if _clean_string(value)],
                "has_receipt": receipt is not None,
                "trust_signals": [
                    _clean_string(value)
                    for value in (receipt.get("trust_signals", []) if receipt else [])
                    if _clean_string(value)
                ],
                "evidence_count": len(receipt.get("evidence", [])) if receipt else 0,
                "verified": any(item.get("status") == "confirmed" for item in confirmations),
            }
        )
    candidates.sort(key=lambda item: item.get("entry_date") or "", reverse=True)
    return candidates


def build_platform_packet(
    *,
    current_user: dict,
    start_date: date | None,
    end_date: date | None,
    career_area: str | None = None,
    role_title: str | None = None,
    organization: str | None = None,
    confidential: bool = True,
    signature_entry_ids: list[str] | None = None,
    sections: list[str] | None = None,
    packet_note: str | None = None,
    item_notes: dict[str, str] | None = None,
    include_notes: bool = True,
    theme: str | None = None,
    brand_name: str | None = None,
    department_label: str | None = None,
    reviewer_name: str | None = None,
    review_cycle_label: str | None = None,
) -> dict:
    packet = _build_packet(
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
    )["packet"]
    candidates = _signature_candidates(
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
    )
    return apply_packet_platform(
        packet,
        signature_entry_ids=signature_entry_ids,
        signature_candidates=candidates,
        sections=sections,
        packet_note=packet_note,
        item_notes=item_notes,
        include_notes=include_notes,
        theme=theme,
        brand_name=brand_name,
        department_label=department_label,
        reviewer_name=reviewer_name,
        review_cycle_label=review_cycle_label,
    )


@router.get("/performance-review-v12")
def get_performance_review_packet_v12(
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
    parsed_start, parsed_end = _parse_period(start_date, end_date)
    return {
        "packet": build_platform_packet(
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
    }
