from __future__ import annotations

import re
from collections import Counter
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.database import entries_collection, impact_receipts_collection


router = APIRouter(prefix="/reports", tags=["reports"])


def _parse_date_value(value) -> date | None:
    """Convert an entry date or timestamp into a calendar date."""

    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None

        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return None

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc).date()

    return None


def _entry_work_date(entry: dict) -> date | None:
    """Prefer the user-entered work date, then fall back to creation time."""

    return _parse_date_value(entry.get("entry_date")) or _parse_date_value(
        entry.get("created_at")
    )


def _sorted_counts(counter: Counter) -> dict[str, int]:
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0].lower())))


def _has_quantified_result(value: str) -> bool:
    """Return True when a result contains a numeric signal."""

    return bool(re.search(r"\d", value or ""))


def _entries_in_period(
    user_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[dict]:
    entries = list(entries_collection.find({"user_id": user_id}))

    if start_date is None and end_date is None:
        return entries

    selected = []

    for entry in entries:
        work_date = _entry_work_date(entry)
        if work_date is None:
            continue

        if start_date is not None and work_date < start_date:
            continue

        if end_date is not None and work_date > end_date:
            continue

        selected.append(entry)

    return selected


def _build_report(
    *,
    user_id: str,
    period_key: str,
    period_label: str,
    start_date: date | None = None,
    end_date: date | None = None,
) -> dict:
    entries = _entries_in_period(user_id, start_date, end_date)
    entry_ids = {str(entry["_id"]) for entry in entries}

    receipt_query = {"user_id": user_id}
    receipts = list(impact_receipts_collection.find(receipt_query))

    if start_date is not None or end_date is not None:
        receipts = [
            receipt
            for receipt in receipts
            if receipt.get("source_entry_id") in entry_ids
        ]

    receipts_by_source = {
        receipt.get("source_entry_id"): receipt
        for receipt in receipts
        if receipt.get("source_entry_id")
    }

    categories = Counter()
    entry_types = Counter()
    skills = Counter()
    trust_signals = Counter()

    resume_bullets = []
    highlights = []

    for entry in entries:
        entry_id = str(entry["_id"])
        receipt = receipts_by_source.get(entry_id)

        category = str(entry.get("category") or "Uncategorized").strip()
        categories[category] += 1

        entry_type = str(entry.get("entry_type") or "Unspecified").strip()
        entry_types[entry_type] += 1

        skill_values = (
            receipt.get("skills", [])
            if receipt is not None
            else entry.get("tags", [])
        )

        for skill in skill_values:
            cleaned_skill = str(skill).strip()
            if cleaned_skill:
                skills[cleaned_skill] += 1

        resume_bullet = str(entry.get("resume_bullet") or "").strip()
        if resume_bullet:
            resume_bullets.append(resume_bullet)

        result_text = (
            str(receipt.get("result") or "").strip()
            if receipt is not None
            else str(entry.get("impact") or "").strip()
        )

        work_date = _entry_work_date(entry)
        highlights.append(
            {
                "entry_id": entry_id,
                "receipt_id": str(receipt["_id"]) if receipt else None,
                "entry_date": work_date.isoformat() if work_date else None,
                "title": str(entry.get("title") or "Untitled accomplishment"),
                "category": category,
                "result": result_text,
                "skills": [str(value) for value in skill_values if str(value).strip()],
                "has_receipt": receipt is not None,
                "is_public": bool(
                    receipt.get("is_public", False)
                    if receipt is not None
                    else entry.get("is_public", False)
                ),
                "trust_signals": (
                    receipt.get("trust_signals", []) if receipt is not None else []
                ),
            }
        )

    highlights.sort(
        key=lambda item: item.get("entry_date") or "",
        reverse=True,
    )

    evidence_items = 0
    public_evidence_items = 0
    confirmed_receipts = 0
    confirmed_assertions = 0
    quantified_results = 0

    for receipt in receipts:
        evidence = receipt.get("evidence", [])
        evidence_items += len(evidence)
        public_evidence_items += sum(
            1 for item in evidence if item.get("is_public", False)
        )

        confirmations = receipt.get("confirmations", [])
        receipt_confirmed = False

        for confirmation in confirmations:
            if confirmation.get("status") == "confirmed":
                confirmed_assertions += 1
                receipt_confirmed = True

        if receipt_confirmed:
            confirmed_receipts += 1

        for signal in receipt.get("trust_signals", []):
            cleaned_signal = str(signal).strip()
            if cleaned_signal:
                trust_signals[cleaned_signal] += 1

        if _has_quantified_result(str(receipt.get("result") or "")):
            quantified_results += 1

    summary_parts = [
        f"{len(entries)} accomplishment{'s' if len(entries) != 1 else ''}",
        f"{len(receipts)} Impact Receipt{'s' if len(receipts) != 1 else ''}",
    ]

    if evidence_items:
        summary_parts.append(
            f"{evidence_items} evidence item{'s' if evidence_items != 1 else ''}"
        )

    if confirmed_assertions:
        summary_parts.append(
            f"{confirmed_assertions} confirmed contribution"
            f"{'s' if confirmed_assertions != 1 else ''}"
        )

    summary = (
        f"{period_label}: " + ", ".join(summary_parts) + "."
        if entries or receipts
        else f"{period_label}: no accomplishments recorded for this period yet."
    )

    return {
        "period": {
            "key": period_key,
            "label": period_label,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "date_basis": "entry_date",
        },
        "summary": summary,
        "totals": {
            "entries": len(entries),
            "impact_receipts": len(receipts),
            "public_entries": sum(
                1 for entry in entries if entry.get("is_public", False)
            ),
            "public_receipts": sum(
                1 for receipt in receipts if receipt.get("is_public", False)
            ),
            "evidence_items": evidence_items,
            "public_evidence_items": public_evidence_items,
            "confirmed_receipts": confirmed_receipts,
            "confirmed_assertions": confirmed_assertions,
            "quantified_results": quantified_results,
        },
        "categories": _sorted_counts(categories),
        "entry_types": _sorted_counts(entry_types),
        "top_skills": _sorted_counts(skills),
        "trust_signals": _sorted_counts(trust_signals),
        "highlights": highlights[:20],
        "resume_bullets": resume_bullets[:25],
    }


@router.get("/weekly")
def get_weekly_report(current_user: dict = Depends(get_current_user)):
    """Return a seven-calendar-day career report based on entry_date."""

    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=6)

    return _build_report(
        user_id=str(current_user["_id"]),
        period_key="weekly",
        period_label="Last 7 days",
        start_date=start_date,
        end_date=today,
    )


@router.get("/all-time")
def get_all_time_report(current_user: dict = Depends(get_current_user)):
    """Return an all-time career summary across entries and Impact Receipts."""

    return _build_report(
        user_id=str(current_user["_id"]),
        period_key="all-time",
        period_label="All-time career summary",
    )


@router.get("/summary")
def get_summary_report(current_user: dict = Depends(get_current_user)):
    """Alias for the all-time career summary."""

    return get_all_time_report(current_user)


@router.get("/custom")
def get_custom_report(
    start_date: str = Query(..., description="Inclusive YYYY-MM-DD start date"),
    end_date: str = Query(..., description="Inclusive YYYY-MM-DD end date"),
    current_user: dict = Depends(get_current_user),
):
    """Return a career report for a custom inclusive work-date range."""

    try:
        parsed_start = date.fromisoformat(start_date)
        parsed_end = date.fromisoformat(end_date)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date and end_date must use YYYY-MM-DD format",
        ) from exc

    if parsed_end < parsed_start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be on or after start_date",
        )

    return _build_report(
        user_id=str(current_user["_id"]),
        period_key="custom",
        period_label=f"{parsed_start.isoformat()} through {parsed_end.isoformat()}",
        start_date=parsed_start,
        end_date=parsed_end,
    )
