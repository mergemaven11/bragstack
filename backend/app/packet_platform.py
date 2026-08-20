from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

OPTIONAL_SECTIONS = (
    "impact-analytics",
    "signature-accomplishments",
    "measurable-results",
    "skills-growth",
    "contribution-recognition",
    "impact-receipts",
    "evidence-index",
    "review-summary",
)

PACKET_THEMES = (
    "classic-dossier",
    "modern-minimal",
    "executive-report",
)


def _clean(value: Any, limit: int | None = None) -> str:
    text = str(value or "").strip()
    return text[:limit] if limit else text


def parse_csv(value: str | None, *, max_items: int = 50) -> list[str]:
    if not value:
        return []
    result: list[str] = []
    for raw in value.split(","):
        item = raw.strip()
        if item and item not in result:
            result.append(item)
        if len(result) >= max_items:
            break
    return result


def parse_sections(value: str | None) -> list[str]:
    requested = parse_csv(value, max_items=len(OPTIONAL_SECTIONS))
    if not requested:
        return list(OPTIONAL_SECTIONS)
    return [section for section in OPTIONAL_SECTIONS if section in requested]


def parse_item_notes(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    try:
        payload = json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}

    result: dict[str, str] = {}
    for key, note in list(payload.items())[:20]:
        clean_key = _clean(key, 120)
        clean_note = _clean(note, 800)
        if clean_key and clean_note:
            result[clean_key] = clean_note
    return result


def recognition_label(confirmation_type: str | None, role: str | None = None) -> str:
    kind = _clean(confirmation_type).lower().replace("_", "-")
    role_text = _clean(role).lower()

    if kind in {"manager", "supervisor"} or "supervisor" in role_text or "manager" in role_text:
        return "Supervisor confirmed"
    if kind in {"client", "customer-client"}:
        return "Client confirmed"
    if kind in {"peer", "coworker", "colleague"}:
        return "Peer recognized"
    if kind in {"customer", "customer-feedback", "feedback"}:
        return "Customer feedback attached"
    if kind in {"instructor", "teacher", "faculty", "preceptor"}:
        return "Instructor confirmed"
    if kind in {"organization", "organization-issued", "org-issued", "issuer"}:
        return "Organization-issued"
    if kind in {"stakeholder", "reviewer"}:
        return "Stakeholder confirmed"
    return "Confirmed recognition"


def normalize_recognition(confirmations: list[dict] | None, trust_signals: list[str] | None = None) -> list[dict]:
    recognition: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for item in confirmations or []:
        if _clean(item.get("status")).lower() != "confirmed":
            continue
        label = recognition_label(item.get("type") or item.get("confirmation_type"), item.get("role"))
        name = _clean(item.get("name"), 120)
        role = _clean(item.get("role"), 120)
        key = (label, name, role)
        if key in seen:
            continue
        seen.add(key)
        recognition.append(
            {
                "label": label,
                "name": name,
                "role": role,
                "source_type": _clean(item.get("type") or item.get("confirmation_type"), 80),
                "status": "confirmed",
            }
        )

    normalized_signals = {_clean(value).lower().replace("_", "-") for value in trust_signals or []}
    if normalized_signals.intersection({"organization-issued", "org-issued", "issuer-confirmed"}):
        key = ("Organization-issued", "", "")
        if key not in seen:
            recognition.append(
                {
                    "label": "Organization-issued",
                    "name": "",
                    "role": "",
                    "source_type": "trust-signal",
                    "status": "confirmed",
                }
            )
    return recognition


def _add_recognition(packet: dict[str, Any]) -> None:
    for record in packet.get("receipt_records", []) or []:
        record["recognition"] = normalize_recognition(
            record.get("confirmations"), record.get("trust_signals")
        )

    by_reference = {
        record.get("reference"): record.get("recognition", [])
        for record in packet.get("receipt_records", []) or []
    }
    for record in packet.get("contribution_records", []) or []:
        recognition = normalize_recognition(record.get("confirmations"), [])
        record["recognition"] = recognition or by_reference.get(record.get("reference"), [])


def apply_packet_platform(
    packet: dict[str, Any],
    *,
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
) -> dict[str, Any]:
    result = deepcopy(packet)
    selected_sections = sections or list(OPTIONAL_SECTIONS)
    selected_sections = [key for key in OPTIONAL_SECTIONS if key in selected_sections]
    theme_name = theme if theme in PACKET_THEMES else "classic-dossier"

    requested_ids = [value for value in (signature_entry_ids or []) if value]
    if requested_ids:
        all_items = {
            str(item.get("entry_id")): item
            for item in (result.get("signature_accomplishments", []) or [])
            if item.get("entry_id")
        }
        # The base packet only keeps its top 8 signature records. Pull any other
        # requested entry from measurable results if it is present there.
        for item in result.get("measurable_results", []) or []:
            if item.get("entry_id"):
                all_items.setdefault(str(item["entry_id"]), item)
        ordered = [all_items[entry_id] for entry_id in requested_ids if entry_id in all_items]
        result["signature_accomplishments"] = ordered
        result["talking_points"] = [
            {
                "title": item.get("title", ""),
                "result": item.get("result", ""),
                "category": item.get("category", ""),
            }
            for item in ordered[:5]
        ]

    safe_item_notes = {
        _clean(key, 120): _clean(value, 800)
        for key, value in (item_notes or {}).items()
        if _clean(key) and _clean(value)
    }
    result["render_config"] = {
        "sections": selected_sections,
        "theme": theme_name,
        "signature_entry_ids": requested_ids,
    }
    result["annotations"] = {
        "include_in_export": bool(include_notes),
        "packet_note": _clean(packet_note, 1500),
        "item_notes": safe_item_notes,
        "authorship": "User-authored context · not verified evidence",
    }
    result["branding"] = {
        "brand_name": _clean(brand_name, 120),
        "department_label": _clean(department_label, 120),
        "reviewer_name": _clean(reviewer_name, 120),
        "review_cycle_label": _clean(review_cycle_label, 120),
        "provenance": "BragStack · Career Evidence System",
    }
    _add_recognition(result)
    return result


def sanitize_shared_packet(packet: dict[str, Any], *, include_evidence: bool, include_notes: bool) -> dict[str, Any]:
    result = deepcopy(packet)
    if not include_evidence:
        result["evidence_index"] = []
        for record in result.get("receipt_records", []) or []:
            record["evidence"] = []
        result["sharing_notice"] = "Evidence references were excluded from this shared packet."
    if not include_notes:
        result["annotations"] = {
            "include_in_export": False,
            "packet_note": "",
            "item_notes": {},
            "authorship": "User-authored context · not verified evidence",
        }
    return result
