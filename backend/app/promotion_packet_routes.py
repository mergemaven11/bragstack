from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.auth import get_current_user
from app.performance_packet_routes import _build_packet, _parse_period
from app.plans import require_feature


router = APIRouter(prefix="/packets", tags=["packets"])


def _promotion_summary(packet: dict, target_role: str, target_level: str) -> str:
    subject = packet.get("subject", {})
    scorecard = packet.get("scorecard", {})
    name = subject.get("name") or "This professional"
    target = " / ".join(value for value in [target_role, target_level] if value)

    parts = [
        f"{name} has documented {scorecard.get('accomplishments', 0)} accomplishment"
        f"{'s' if scorecard.get('accomplishments', 0) != 1 else ''} for this review period."
    ]

    if target:
        parts.append(
            f"This packet organizes the evidence for a progression conversation toward {target}."
        )
    else:
        parts.append(
            "This packet organizes the evidence for a promotion or increased-scope conversation."
        )

    if scorecard.get("impact_receipts"):
        parts.append(
            f"The record includes {scorecard['impact_receipts']} structured Impact Receipt"
            f"{'s' if scorecard['impact_receipts'] != 1 else ''}, "
            f"{scorecard.get('evidence_items', 0)} supporting evidence item"
            f"{'s' if scorecard.get('evidence_items', 0) != 1 else ''}, and "
            f"{scorecard.get('confirmed_assertions', 0)} confirmed assertion"
            f"{'s' if scorecard.get('confirmed_assertions', 0) != 1 else ''}."
        )

    parts.append(
        "BragStack does not assign promotion readiness or make an employment decision; "
        "the packet presents the documented case and the underlying proof."
    )
    return " ".join(parts)


def _strengthening_actions(scorecard: dict) -> list[dict]:
    actions: list[dict] = []

    if scorecard.get("receipt_coverage_percent", 0) < 75:
        actions.append(
            {
                "area": "Structured proof",
                "action": "Convert more high-value accomplishments into Impact Receipts.",
                "why": "Promotion cases are easier to review when contribution, result, skills, and evidence are structured consistently.",
            }
        )

    if scorecard.get("quantified_result_coverage_percent", 0) < 60:
        actions.append(
            {
                "area": "Measurable impact",
                "action": "Add numbers, counts, percentages, time saved, quality changes, or other measurable outcomes where they are genuinely known.",
                "why": "Concrete outcomes make scope and impact easier to evaluate without inventing a score.",
            }
        )

    if scorecard.get("evidence_coverage_percent", 0) < 70:
        actions.append(
            {
                "area": "Supporting evidence",
                "action": "Attach artifacts, feedback, documents, certificates, links, or other proof to the strongest receipts.",
                "why": "Evidence gives reviewers a traceable basis for the promotion case.",
            }
        )

    if scorecard.get("verification_coverage_percent", 0) < 50:
        actions.append(
            {
                "area": "Recognition",
                "action": "Request confirmation or recognition on a few of the most important accomplishments when appropriate.",
                "why": "A small number of independent confirmations can strengthen credibility without turning BragStack into surveillance.",
            }
        )

    if not actions:
        actions.append(
            {
                "area": "Case quality",
                "action": "The evidence foundation is strong. Focus the conversation on increased scope, sustained impact, and the responsibilities expected in the target role or level.",
                "why": "Strong documentation is most useful when it is connected to the actual progression expectations of the organization or profession.",
            }
        )

    return actions


def _build_promotion_packet(
    *,
    current_user: dict,
    start_date,
    end_date,
    career_area: str | None,
    role_title: str | None,
    organization: str | None,
    confidential: bool,
    target_role: str | None,
    target_level: str | None,
) -> dict:
    require_feature(current_user, "promotion_packet")

    packet = _build_packet(
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
    )["packet"]

    target_role_value = (target_role or "").strip()
    target_level_value = (target_level or "").strip()
    scorecard = packet.get("scorecard", {})

    verified_records = [
        record for record in packet.get("contribution_records", []) if record.get("verified")
    ]

    packet.update(
        {
            "kind": "promotion",
            "title": "Promotion Packet",
            "target": {
                "role": target_role_value,
                "level": target_level_value,
            },
            "promotion_summary": _promotion_summary(
                packet,
                target_role_value,
                target_level_value,
            ),
            "promotion_case": {
                "demonstrated_impact": packet.get("signature_accomplishments", []),
                "measurable_impact": packet.get("measurable_results", []),
                "scope_and_ownership": packet.get("contribution_records", []),
                "growth_and_capabilities": packet.get("skill_details", []),
                "verified_recognition": verified_records,
                "strengthening_actions": _strengthening_actions(scorecard),
            },
            "review_summary": _promotion_summary(
                packet,
                target_role_value,
                target_level_value,
            ),
        }
    )

    return {"packet": packet}


@router.get("/promotion")
def get_promotion_packet(
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    career_area: str | None = Query(None, max_length=120),
    role_title: str | None = Query(None, max_length=160),
    organization: str | None = Query(None, max_length=180),
    confidential: bool = Query(True),
    target_role: str | None = Query(None, max_length=160),
    target_level: str | None = Query(None, max_length=120),
    current_user: dict = Depends(get_current_user),
):
    """Build a career-neutral, evidence-backed promotion packet."""

    parsed_start, parsed_end = _parse_period(start_date, end_date)
    return _build_promotion_packet(
        current_user=current_user,
        start_date=parsed_start,
        end_date=parsed_end,
        career_area=career_area,
        role_title=role_title,
        organization=organization,
        confidential=confidential,
        target_role=target_role,
        target_level=target_level,
    )
