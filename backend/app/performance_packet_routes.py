from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.database import entries_collection, impact_receipts_collection
from app.plans import require_feature


router = APIRouter(prefix="/packets", tags=["packets"])


def _parse_date_value(value: Any) -> date | None:
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
    return _parse_date_value(entry.get("entry_date")) or _parse_date_value(
        entry.get("created_at")
    )


def _percentage(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        return 0
    return round((numerator / denominator) * 100)


def _has_quantified_result(value: str) -> bool:
    return bool(re.search(r"\d", value or ""))


def _extract_metric_display(value: str) -> str | None:
    """Extract one displayable numeric token without inventing a metric."""

    text = (value or "").strip()
    if not text:
        return None

    patterns = [
        r"\$\s?\d[\d,]*(?:\.\d+)?(?:[KMBkmb])?",
        r"\d+(?:\.\d+)?\s?%",
        r"\d+(?:\.\d+)?\s?[xX]",
        r"\d[\d,]*(?:\.\d+)?\s?(?:hours?|hrs?|days?|weeks?|months?|years?)",
        r"\d[\d,]*(?:\.\d+)?\s?(?:people|clients?|customers?|students?|patients?|cases?|units?|projects?|teams?|sites?)",
        r"\d[\d,]*(?:\.\d+)?",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0).strip()

    return None


def _clean_string(value: Any, fallback: str = "") -> str:
    text = str(value or "").strip()
    return text or fallback


def _entries_for_period(
    *,
    user_id: str,
    start_date: date | None,
    end_date: date | None,
) -> list[dict]:
    entries = list(entries_collection.find({"user_id": user_id}))
    selected: list[dict] = []

    for entry in entries:
        work_date = _entry_work_date(entry)
        if start_date is not None and (work_date is None or work_date < start_date):
            continue
        if end_date is not None and (work_date is None or work_date > end_date):
            continue
        selected.append(entry)

    return selected


def _receipt_reference(receipt: dict, work_date: date | None) -> str:
    year = work_date.year if work_date else datetime.now(timezone.utc).year
    token = str(receipt.get("_id") or "000000")[-6:].upper()
    return f"BS-{year}-{token}"


def _build_review_narrative(
    *,
    subject_name: str,
    entries_count: int,
    receipts_count: int,
    evidence_count: int,
    confirmed_receipts: int,
    quantified_results: int,
    categories: Counter,
    skills: Counter,
) -> str:
    if entries_count == 0:
        return (
            f"{subject_name} has not yet documented accomplishments for this review "
            "period. Add work outcomes, evidence, and Impact Receipts to build a "
            "complete performance narrative."
        )

    category_names = [name for name, _ in categories.most_common(3)]
    skill_names = [name for name, _ in skills.most_common(4)]

    parts = [
        f"{subject_name} documented {entries_count} accomplishment"
        f"{'s' if entries_count != 1 else ''} during this review period."
    ]

    if category_names:
        parts.append(
            "The strongest concentration of documented work appears in "
            + ", ".join(category_names)
            + "."
        )

    proof_parts: list[str] = []
    if receipts_count:
        proof_parts.append(
            f"{receipts_count} structured Impact Receipt"
            f"{'s' if receipts_count != 1 else ''}"
        )
    if evidence_count:
        proof_parts.append(
            f"{evidence_count} supporting evidence item"
            f"{'s' if evidence_count != 1 else ''}"
        )
    if confirmed_receipts:
        proof_parts.append(
            f"{confirmed_receipts} verified contribution"
            f"{'s' if confirmed_receipts != 1 else ''}"
        )
    if quantified_results:
        proof_parts.append(
            f"{quantified_results} quantified result"
            f"{'s' if quantified_results != 1 else ''}"
        )

    if proof_parts:
        parts.append("The record includes " + ", ".join(proof_parts) + ".")

    if skill_names:
        parts.append(
            "Frequently demonstrated capabilities include "
            + ", ".join(skill_names)
            + "."
        )

    parts.append(
        "The packet is evidence-backed and intended to support review, growth, "
        "recognition, and advancement conversations with traceable examples."
    )

    return " ".join(parts)


def _build_packet(
    *,
    current_user: dict,
    start_date: date | None,
    end_date: date | None,
    career_area: str | None,
    role_title: str | None,
    organization: str | None,
    confidential: bool,
) -> dict:
    require_feature(current_user, "performance_review_builder")

    user_id = str(current_user["_id"])
    entries = _entries_for_period(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    entry_ids = {str(entry["_id"]) for entry in entries}

    receipts = list(impact_receipts_collection.find({"user_id": user_id}))
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

    categories: Counter[str] = Counter()
    skills: Counter[str] = Counter()
    trust_signals: Counter[str] = Counter()
    activity_by_month: Counter[str] = Counter()
    skill_dates: dict[str, list[date]] = defaultdict(list)

    highlights: list[dict] = []
    measurable_results: list[dict] = []

    for entry in entries:
        entry_id = str(entry["_id"])
        receipt = receipts_by_source.get(entry_id)
        work_date = _entry_work_date(entry)
        category = _clean_string(entry.get("category"), "Uncategorized")
        categories[category] += 1

        if work_date:
            activity_by_month[work_date.strftime("%Y-%m")] += 1

        skill_values = (
            receipt.get("skills", [])
            if receipt is not None and receipt.get("skills")
            else entry.get("tags", [])
        )

        clean_skills: list[str] = []
        for value in skill_values:
            skill = _clean_string(value)
            if not skill:
                continue
            clean_skills.append(skill)
            skills[skill] += 1
            if work_date:
                skill_dates[skill].append(work_date)

        result_text = _clean_string(
            receipt.get("result") if receipt is not None else entry.get("impact")
        )
        trust_values = receipt.get("trust_signals", []) if receipt is not None else []
        for signal in trust_values:
            cleaned_signal = _clean_string(signal)
            if cleaned_signal:
                trust_signals[cleaned_signal] += 1

        highlight = {
            "entry_id": entry_id,
            "receipt_id": str(receipt["_id"]) if receipt is not None else None,
            "entry_date": work_date.isoformat() if work_date else None,
            "title": _clean_string(entry.get("title"), "Untitled accomplishment"),
            "category": category,
            "result": result_text,
            "skills": clean_skills,
            "has_receipt": receipt is not None,
            "trust_signals": [_clean_string(value) for value in trust_values if _clean_string(value)],
            "evidence_count": len(receipt.get("evidence", [])) if receipt else 0,
            "verified": any(
                confirmation.get("status") == "confirmed"
                for confirmation in (receipt.get("confirmations", []) if receipt else [])
            ),
        }
        highlights.append(highlight)

        if _has_quantified_result(result_text):
            measurable_results.append(
                {
                    **highlight,
                    "metric_display": _extract_metric_display(result_text),
                }
            )

    highlights.sort(key=lambda item: item.get("entry_date") or "", reverse=True)
    measurable_results.sort(
        key=lambda item: (
            item.get("verified", False),
            item.get("evidence_count", 0),
            item.get("entry_date") or "",
        ),
        reverse=True,
    )

    signature_accomplishments = sorted(
        highlights,
        key=lambda item: (
            _has_quantified_result(item.get("result", "")),
            item.get("verified", False),
            item.get("evidence_count", 0),
            item.get("has_receipt", False),
            item.get("entry_date") or "",
        ),
        reverse=True,
    )[:8]

    evidence_items = 0
    receipts_with_evidence = 0
    confirmed_receipts = 0
    confirmed_assertions = 0
    quantified_receipts = 0
    receipt_records: list[dict] = []
    evidence_index: list[dict] = []
    contribution_records: list[dict] = []

    entries_by_id = {str(entry["_id"]): entry for entry in entries}

    for receipt in receipts:
        source_entry = entries_by_id.get(receipt.get("source_entry_id"), {})
        work_date = _entry_work_date(source_entry)
        evidence = receipt.get("evidence", []) or []
        confirmations = receipt.get("confirmations", []) or []
        confirmed = [
            confirmation
            for confirmation in confirmations
            if confirmation.get("status") == "confirmed"
        ]
        result_text = _clean_string(receipt.get("result"))
        reference = _receipt_reference(receipt, work_date)

        evidence_items += len(evidence)
        if evidence:
            receipts_with_evidence += 1
        if confirmed:
            confirmed_receipts += 1
            confirmed_assertions += len(confirmed)
        if _has_quantified_result(result_text):
            quantified_receipts += 1

        record = {
            "id": str(receipt.get("_id")),
            "reference": reference,
            "entry_date": work_date.isoformat() if work_date else None,
            "accomplishment": _clean_string(
                receipt.get("accomplishment"),
                _clean_string(source_entry.get("title"), "Documented accomplishment"),
            ),
            "contribution": _clean_string(receipt.get("contribution")),
            "result": result_text,
            "skills": [_clean_string(value) for value in receipt.get("skills", []) if _clean_string(value)],
            "evidence": [
                {
                    "title": _clean_string(item.get("title"), "Evidence item"),
                    "type": _clean_string(item.get("evidence_type"), "other"),
                    "reference": _clean_string(item.get("reference")),
                    "description": _clean_string(item.get("description")),
                    "is_public": bool(item.get("is_public", False)),
                }
                for item in evidence
            ],
            "confirmations": [
                {
                    "name": _clean_string(item.get("name"), "Confirmed contributor"),
                    "role": _clean_string(item.get("role")),
                    "type": _clean_string(item.get("confirmation_type")),
                    "status": _clean_string(item.get("status")),
                }
                for item in confirmations
            ],
            "credit": [
                {
                    "name": _clean_string(item.get("name")),
                    "contribution": _clean_string(item.get("contribution")),
                }
                for item in receipt.get("credit", [])
            ],
            "trust_signals": [
                _clean_string(value)
                for value in receipt.get("trust_signals", [])
                if _clean_string(value)
            ],
            "verified": bool(confirmed),
        }
        receipt_records.append(record)

        contribution_records.append(
            {
                "reference": reference,
                "entry_date": record["entry_date"],
                "accomplishment": record["accomplishment"],
                "contribution": record["contribution"],
                "result": record["result"],
                "verified": record["verified"],
                "confirmations": record["confirmations"],
                "credit": record["credit"],
                "evidence_count": len(record["evidence"]),
            }
        )

        for item in record["evidence"]:
            evidence_index.append(
                {
                    "receipt_reference": reference,
                    "accomplishment": record["accomplishment"],
                    **item,
                }
            )

    receipt_records.sort(key=lambda item: item.get("entry_date") or "", reverse=True)
    contribution_records.sort(
        key=lambda item: (
            item.get("verified", False),
            item.get("evidence_count", 0),
            item.get("entry_date") or "",
        ),
        reverse=True,
    )

    skill_details = []
    for skill, count in skills.most_common():
        dates = sorted(skill_dates.get(skill, []))
        skill_details.append(
            {
                "skill": skill,
                "count": count,
                "first_seen": dates[0].isoformat() if dates else None,
                "last_seen": dates[-1].isoformat() if dates else None,
            }
        )

    scorecard = {
        "accomplishments": len(entries),
        "impact_receipts": len(receipts),
        "evidence_items": evidence_items,
        "skills_demonstrated": len(skills),
        "receipt_coverage_percent": _percentage(len(receipts), len(entries)),
        "quantified_result_coverage_percent": _percentage(
            quantified_receipts, len(receipts)
        ),
        "verification_coverage_percent": _percentage(
            confirmed_receipts, len(receipts)
        ),
        "evidence_coverage_percent": _percentage(
            receipts_with_evidence, len(receipts)
        ),
        "evidence_depth": round(evidence_items / len(receipts), 1) if receipts else 0,
        "confirmed_assertions": confirmed_assertions,
    }

    subject_name = _clean_string(current_user.get("name"), "BragStack Member")
    subject_role = _clean_string(
        role_title,
        _clean_string(
            current_user.get("headline"),
            _clean_string(current_user.get("role_title"), "Professional"),
        ),
    )

    if start_date and end_date:
        period = {
            "key": "custom",
            "label": f"{start_date.isoformat()} through {end_date.isoformat()}",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "date_basis": "entry_date",
        }
    else:
        period = {
            "key": "all-time",
            "label": "All recorded work",
            "start_date": None,
            "end_date": None,
            "date_basis": "entry_date",
        }

    review_summary = _build_review_narrative(
        subject_name=subject_name,
        entries_count=len(entries),
        receipts_count=len(receipts),
        evidence_count=evidence_items,
        confirmed_receipts=confirmed_receipts,
        quantified_results=quantified_receipts,
        categories=categories,
        skills=skills,
    )

    talking_points = [
        {
            "title": item["title"],
            "result": item.get("result", ""),
            "category": item.get("category", ""),
        }
        for item in signature_accomplishments[:5]
    ]

    return {
        "packet": {
            "kind": "performance-review",
            "title": "Performance Review Packet",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "confidential": confidential,
            "context": {
                "career_area": _clean_string(career_area),
                "organization": _clean_string(organization),
            },
            "subject": {
                "name": subject_name,
                "role": subject_role,
                "location": _clean_string(current_user.get("location")),
            },
            "period": period,
            "scorecard": scorecard,
            "impact_analytics": {
                "categories": dict(categories.most_common()),
                "top_skills": dict(skills.most_common()),
                "trust_signals": dict(trust_signals.most_common()),
                "activity_by_month": dict(sorted(activity_by_month.items())),
            },
            "skill_details": skill_details[:20],
            "signature_accomplishments": signature_accomplishments,
            "measurable_results": measurable_results[:12],
            "contribution_records": contribution_records[:12],
            "receipt_records": receipt_records,
            "evidence_index": evidence_index,
            "review_summary": review_summary,
            "talking_points": talking_points,
        }
    }


def _parse_period(start_date: str | None, end_date: str | None) -> tuple[date | None, date | None]:
    if bool(start_date) != bool(end_date):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date and end_date must be provided together",
        )

    if not start_date or not end_date:
        return None, None

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

    return parsed_start, parsed_end


@router.get("/performance-review")
def get_performance_review_packet(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    career_area: str | None = Query(None, max_length=120),
    role_title: str | None = Query(None, max_length=160),
    organization: str | None = Query(None, max_length=180),
    confidential: bool = Query(True),
    current_user: dict = Depends(get_current_user),
):
    """Return all data required to render a complete paper-first review packet."""

    parsed_start, parsed_end = _parse_period(start_date, end_date)
    return _build_packet(
        current_user=current_user,
        start_date=parsed_start,
        end_date=parsed_end,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
    )
