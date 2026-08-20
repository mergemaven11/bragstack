from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query

from app.auth import get_current_user
from app.packet_platform import normalize_recognition
from app.performance_packet_routes import _build_packet, _clean_string, _parse_period
from app.plans import require_feature


router = APIRouter(prefix="/packets", tags=["packets"])

CREDENTIAL_EVIDENCE_TYPES = {
    "certificate", "certification", "credential", "license", "licensure",
    "continuing education", "continuing-education", "course completion",
    "course-completion", "training certificate", "training-certificate",
}


def _normalize_evidence_type(value: Any) -> str:
    return _clean_string(value, "other").strip().lower().replace("_", " ")


def _attach_recognition(packet: dict[str, Any]) -> None:
    by_reference = {}
    for receipt in packet.get("receipt_records", []) or []:
        recognition = normalize_recognition(receipt.get("confirmations"), receipt.get("trust_signals"))
        receipt["recognition"] = recognition
        receipt["verified"] = bool(recognition)
        by_reference[receipt.get("reference")] = recognition
    for contribution in packet.get("contribution_records", []) or []:
        contribution["recognition"] = normalize_recognition(contribution.get("confirmations"), []) or by_reference.get(contribution.get("reference"), [])
        contribution["verified"] = bool(contribution["recognition"])


def _evidence_status(receipt: dict[str, Any]) -> str:
    signals = {
        _clean_string(signal).strip().lower().replace("_", "-")
        for signal in receipt.get("trust_signals", [])
        if _clean_string(signal)
    }
    if "organization-issued" in signals:
        return "Organization-issued"
    if receipt.get("recognition") or receipt.get("verified"):
        return "Confirmed"
    return "Self-added"


def _build_certification_packet(
    *,
    current_user: dict,
    start_date: date | None,
    end_date: date | None,
    career_area: str | None,
    role_title: str | None,
    organization: str | None,
    confidential: bool,
    credential_name: str | None,
    issuing_body: str | None,
    review_type: str | None,
    requirement_notes: str | None,
) -> dict:
    require_feature(current_user, "certification_packet")

    packet = _build_packet(
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
    )["packet"]
    _attach_recognition(packet)

    receipts_by_reference = {
        item.get("reference"): item
        for item in packet.get("receipt_records", [])
        if item.get("reference")
    }

    credential_evidence: list[dict[str, Any]] = []
    supporting_evidence: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    recognition_counts: Counter[str] = Counter()

    for receipt in packet.get("receipt_records", []) or []:
        for recognition in receipt.get("recognition", []) or []:
            recognition_counts[recognition.get("label") or "Confirmed recognition"] += 1

    for item in packet.get("evidence_index", []):
        receipt = receipts_by_reference.get(item.get("receipt_reference"), {})
        evidence_status = _evidence_status(receipt)
        evidence_type = _normalize_evidence_type(item.get("type"))
        record = {
            **item,
            "evidence_status": evidence_status,
            "is_credential_evidence": evidence_type in CREDENTIAL_EVIDENCE_TYPES,
            "recognition": receipt.get("recognition", []),
        }
        status_counts[evidence_status] += 1
        supporting_evidence.append(record)
        if record["is_credential_evidence"]:
            credential_evidence.append(record)

    credential_name_value = _clean_string(credential_name)
    issuing_body_value = _clean_string(issuing_body)
    review_type_value = _clean_string(review_type, "Certification / Licensure Review")
    requirement_notes_value = _clean_string(requirement_notes)

    review_summary_parts = [
        f"This packet organizes {packet.get('scorecard', {}).get('accomplishments', 0)} documented accomplishment"
        f"{'s' if packet.get('scorecard', {}).get('accomplishments', 0) != 1 else ''} and "
        f"{len(supporting_evidence)} supporting evidence item"
        f"{'s' if len(supporting_evidence) != 1 else ''} for a {review_type_value.lower()}."
    ]
    if credential_name_value:
        review_summary_parts.append(f"The review target is {credential_name_value}.")
    if issuing_body_value:
        review_summary_parts.append(f"The named issuing or reviewing body is {issuing_body_value}.")
    review_summary_parts.append(
        "Evidence status reflects BragStack trust signals and Verified Recognition only: self-added evidence is not presented as independently verified."
    )

    packet.update(
        {
            "kind": "certification",
            "title": "Certification & Licensure Packet",
            "credential_review": {
                "credential_name": credential_name_value,
                "issuing_body": issuing_body_value,
                "review_type": review_type_value,
                "requirement_notes": requirement_notes_value,
            },
            "credential_evidence": credential_evidence,
            "supporting_evidence": supporting_evidence,
            "credential_evidence_summary": {
                "credential_items": len(credential_evidence),
                "supporting_items": len(supporting_evidence),
                "self_added": status_counts.get("Self-added", 0),
                "confirmed": status_counts.get("Confirmed", 0),
                "organization_issued": status_counts.get("Organization-issued", 0),
            },
            "verified_recognition": dict(recognition_counts.most_common()),
            "competency_records": packet.get("skill_details", []),
            "experience_records": packet.get("contribution_records", []),
            "review_summary": " ".join(review_summary_parts),
        }
    )

    return {"packet": packet}


@router.get("/certification")
def get_certification_packet(
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
    """Build a career-neutral certification and licensure evidence packet."""
    parsed_start, parsed_end = _parse_period(start_date, end_date)
    return _build_certification_packet(
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
    )
