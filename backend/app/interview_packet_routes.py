from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.database import impact_receipts_collection
from app.performance_packet_routes import (
    _build_packet,
    _clean_string,
    _entries_for_period,
    _entry_work_date,
    _has_quantified_result,
    _parse_period,
    _percentage,
)
from app.plans import require_feature


router = APIRouter(prefix="/packets", tags=["packets"])
MAX_INTERVIEW_STORIES = 8
DEFAULT_INTERVIEW_STORIES = 5


def _parse_selected_ids(value: str | None) -> list[str]:
    if not value:
        return []

    selected: list[str] = []
    for item in value.split(","):
        entry_id = item.strip()
        if entry_id and entry_id not in selected:
            selected.append(entry_id)

    if len(selected) > MAX_INTERVIEW_STORIES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Select no more than {MAX_INTERVIEW_STORIES} accomplishments for an interview packet.",
        )
    return selected


def _story_prompt(story: dict[str, Any]) -> list[str]:
    prompts = [f"Walk me through {story['title']}."]
    if not story.get("contribution"):
        prompts.append("What was your specific contribution or responsibility?")
    if not story.get("result"):
        prompts.append("What changed because of your work?")
    elif not _has_quantified_result(story.get("result", "")):
        prompts.append("Is there a truthful number, count, amount, time change, or quality measure you can add?")
    if not story.get("skills"):
        prompts.append("Which capabilities did this example demonstrate?")
    return prompts[:4]


def _build_interview_packet(
    *,
    current_user: dict,
    start_date: date | None,
    end_date: date | None,
    career_area: str | None,
    role_title: str | None,
    organization: str | None,
    confidential: bool,
    selected_entry_ids: list[str],
    target_role: str | None,
    target_organization: str | None,
    include_evidence_references: bool,
) -> dict:
    require_feature(current_user, "interview_packet")

    base = _build_packet(
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
    )["packet"]

    user_id = str(current_user["_id"])
    entries = _entries_for_period(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    entries_by_id = {str(entry["_id"]): entry for entry in entries}

    receipts = list(impact_receipts_collection.find({"user_id": user_id}))
    receipts_by_source = {
        str(receipt.get("source_entry_id")): receipt
        for receipt in receipts
        if receipt.get("source_entry_id")
    }

    if selected_entry_ids:
        selected_ids = [entry_id for entry_id in selected_entry_ids if entry_id in entries_by_id]
    else:
        selected_ids = [
            item.get("entry_id")
            for item in base.get("signature_accomplishments", [])[:DEFAULT_INTERVIEW_STORIES]
            if item.get("entry_id") in entries_by_id
        ]

    if not selected_ids and entries:
        selected_ids = [str(entry["_id"]) for entry in entries[:DEFAULT_INTERVIEW_STORIES]]

    categories: Counter[str] = Counter()
    skills: Counter[str] = Counter()
    stories: list[dict[str, Any]] = []

    for entry_id in selected_ids:
        entry = entries_by_id[entry_id]
        receipt = receipts_by_source.get(entry_id)
        work_date = _entry_work_date(entry)
        contribution = _clean_string(receipt.get("contribution")) if receipt else ""
        result = _clean_string(
            receipt.get("result") if receipt else entry.get("impact")
        )
        skill_values = (
            receipt.get("skills", [])
            if receipt and receipt.get("skills")
            else entry.get("tags", [])
        )
        clean_skills = [_clean_string(value) for value in skill_values if _clean_string(value)]
        evidence = receipt.get("evidence", []) if receipt else []
        confirmations = receipt.get("confirmations", []) if receipt else []
        verified = any(item.get("status") == "confirmed" for item in confirmations)
        category = _clean_string(entry.get("category"), "Accomplishment")
        categories[category] += 1
        skills.update(clean_skills)

        evidence_details = []
        if include_evidence_references:
            evidence_details = [
                {
                    "title": _clean_string(item.get("title"), "Evidence item"),
                    "type": _clean_string(item.get("evidence_type"), "other"),
                    "reference": _clean_string(item.get("reference")),
                }
                for item in evidence
            ]

        story = {
            "entry_id": entry_id,
            "entry_date": work_date.isoformat() if work_date else None,
            "title": _clean_string(entry.get("title"), "Documented accomplishment"),
            "category": category,
            "contribution": contribution,
            "result": result,
            "skills": clean_skills,
            "has_receipt": receipt is not None,
            "evidence_count": len(evidence),
            "evidence": evidence_details,
            "verified": verified,
            "proof_status": (
                "Verified"
                if verified
                else "Evidence-backed"
                if evidence
                else "Documented"
            ),
        }
        story["prep_prompts"] = _story_prompt(story)
        stories.append(story)

    receipts_count = sum(1 for story in stories if story["has_receipt"])
    evidence_count = sum(story["evidence_count"] for story in stories)
    verified_count = sum(1 for story in stories if story["verified"])
    quantified_count = sum(1 for story in stories if _has_quantified_result(story["result"]))
    stories_with_evidence = sum(1 for story in stories if story["evidence_count"] > 0)

    scorecard = {
        "accomplishments": len(stories),
        "impact_receipts": receipts_count,
        "evidence_items": evidence_count,
        "skills_demonstrated": len(skills),
        "receipt_coverage_percent": _percentage(receipts_count, len(stories)),
        "quantified_result_coverage_percent": _percentage(quantified_count, len(stories)),
        "verification_coverage_percent": _percentage(verified_count, len(stories)),
        "evidence_coverage_percent": _percentage(stories_with_evidence, len(stories)),
        "evidence_depth": round(evidence_count / receipts_count, 1) if receipts_count else 0,
        "confirmed_assertions": verified_count,
    }

    target_role_value = _clean_string(target_role)
    target_org_value = _clean_string(target_organization)
    target_text = " at ".join(value for value in [target_role_value, target_org_value] if value)
    subject_name = base.get("subject", {}).get("name") or "This candidate"

    summary_parts = [
        f"{subject_name} selected {len(stories)} documented accomplishment"
        f"{'s' if len(stories) != 1 else ''} for interview preparation."
    ]
    if target_text:
        summary_parts.append(f"The packet is framed for conversations related to {target_text}.")
    if quantified_count:
        summary_parts.append(
            f"{quantified_count} selected stor{'ies' if quantified_count != 1 else 'y'} include a measurable result."
        )
    summary_parts.append(
        "Story prompts are based only on documented fields; missing context is surfaced as a preparation question rather than invented."
    )

    interview_summary = " ".join(summary_parts)
    skill_details = [
        {"skill": skill, "count": count}
        for skill, count in skills.most_common(12)
    ]

    base.update(
        {
            "kind": "interview",
            "title": "Interview Packet",
            "target": {
                "role": target_role_value,
                "organization": target_org_value,
            },
            "scorecard": scorecard,
            "signature_accomplishments": stories,
            "interview_stories": stories,
            "measurable_results": [
                story for story in stories if _has_quantified_result(story.get("result", ""))
            ],
            "skill_details": skill_details,
            "impact_analytics": {
                "top_skills": dict(skills.most_common(8)),
                "categories": dict(categories.most_common(8)),
            },
            "receipt_records": [],
            "evidence_index": [],
            "contribution_records": [],
            "review_summary": interview_summary,
            "interview_summary": interview_summary,
            "interview_preferences": {
                "include_evidence_references": include_evidence_references,
                "selected_entry_ids": selected_ids,
            },
        }
    )

    return {"packet": base}


@router.get("/interview")
def get_interview_packet(
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
    """Build a career-neutral interview packet from user-selected accomplishments."""

    parsed_start, parsed_end = _parse_period(start_date, end_date)
    return _build_interview_packet(
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
    )
