from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

FREE_ENTRY_LIMIT = 5
FREE_IMPACT_RECEIPT_LIMIT = 1

PLAN_FEATURES: dict[str, dict[str, Any]] = {
    "free": {
        "max_entries": FREE_ENTRY_LIMIT,
        "max_impact_receipts": FREE_IMPACT_RECEIPT_LIMIT,
        "advanced_reports": False,
        "performance_review_builder": False,
        "promotion_packet": False,
        "integrations": False,
        "advanced_public_analytics": False,
        "export_pdf": False,
    },
    "pro": {
        "max_entries": None,
        "max_impact_receipts": None,
        "advanced_reports": True,
        "performance_review_builder": True,
        "promotion_packet": True,
        "integrations": True,
        "advanced_public_analytics": True,
        "export_pdf": True,
    },
}


def normalize_plan(plan: str | None) -> str:
    """Return a supported plan name, defaulting unknown values to free."""
    normalized = (plan or "free").strip().lower()
    return normalized if normalized in PLAN_FEATURES else "free"


def get_plan_for_user(user: dict) -> str:
    """Return the normalized billing plan for a user document."""
    return normalize_plan(user.get("plan"))


def get_entitlements_for_user(user: dict) -> dict[str, Any]:
    """Return a copy of the entitlement map for the user's current plan."""
    return dict(PLAN_FEATURES[get_plan_for_user(user)])


def require_feature(user: dict, feature_name: str) -> None:
    """Raise 403 when a user's plan does not include a feature."""
    entitlements = get_entitlements_for_user(user)
    if entitlements.get(feature_name):
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "pro_feature_required",
            "message": "This feature requires BragStack Pro.",
            "feature": feature_name,
            "plan": get_plan_for_user(user),
        },
    )


def enforce_usage_limit(
    *,
    user: dict,
    entitlement_name: str,
    current_count: int,
    resource_name: str,
) -> None:
    """Raise 403 when a capped plan has reached a resource limit."""
    entitlements = get_entitlements_for_user(user)
    limit = entitlements.get(entitlement_name)

    if limit is None or current_count < limit:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "plan_limit_reached",
            "message": (
                f"Your {get_plan_for_user(user).title()} plan includes "
                f"{limit} {resource_name}. Upgrade to BragStack Pro for unlimited access."
            ),
            "resource": resource_name,
            "limit": limit,
            "current": current_count,
            "plan": get_plan_for_user(user),
        },
    )
