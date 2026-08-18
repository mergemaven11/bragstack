from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query

from app.database import (
    entries_collection,
    impact_receipts_collection,
    users_collection,
)


router = APIRouter(prefix="/public", tags=["public"])


def normalize_slug(slug: str) -> str:
    """Normalize a public profile slug for lookup."""
    return slug.strip().lower()


def parse_datetime(value):
    """Convert MongoDB datetime or ISO datetime text into UTC datetime."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc)
        except ValueError:
            return None

    return None


def parse_work_date(entry: dict) -> date | None:
    """Prefer entry_date and fall back to created_at for older records."""
    entry_date = entry.get("entry_date")

    if isinstance(entry_date, str) and entry_date.strip():
        try:
            return date.fromisoformat(entry_date.strip()[:10])
        except ValueError:
            pass

    created_at = parse_datetime(entry.get("created_at"))
    return created_at.date() if created_at else None


def serialize_entry(entry: dict) -> dict:
    """Convert a MongoDB brag entry into a safe public response."""

    return {
        "id": str(entry["_id"]),
        "title": entry.get("title", ""),
        "description": entry.get("description", ""),
        "category": entry.get("category", ""),
        "entry_type": entry.get("entry_type", ""),
        "entry_date": entry.get("entry_date", ""),
        "situation": entry.get("situation", ""),
        "action": entry.get("action", ""),
        "impact": entry.get("impact", ""),
        "lesson": entry.get("lesson", ""),
        "tags": entry.get("tags", []),
        "resume_bullet": entry.get("resume_bullet", ""),
        "is_public": entry.get("is_public", False),
        "created_at": entry.get("created_at"),
        "updated_at": entry.get("updated_at"),
    }


def serialize_public_profile(user: dict) -> dict:
    """Return profile fields that are safe for public display."""

    return {
        "name": user.get("name", ""),
        "public_slug": user.get("public_slug", ""),
        "headline": user.get("headline", ""),
        "bio": user.get("bio", ""),
        "location": user.get("location", ""),
        "github_url": user.get("github_url", ""),
        "portfolio_url": user.get("portfolio_url", ""),
        "resume_url": user.get("resume_url", ""),
    }


def serialize_public_impact_receipt(receipt: dict) -> dict:
    """Return only receipt fields that are safe for public presentation."""

    public_evidence = [
        {
            "evidence_type": item.get("evidence_type", "other"),
            "title": item.get("title", ""),
            "reference": item.get("reference"),
            "description": item.get("description"),
        }
        for item in receipt.get("evidence", [])
        if item.get("is_public", False)
    ]

    confirmed_count = sum(
        1
        for confirmation in receipt.get("confirmations", [])
        if confirmation.get("status") == "confirmed"
    )

    return {
        "id": str(receipt["_id"]),
        "source_entry_id": receipt.get("source_entry_id", ""),
        "accomplishment": receipt.get("accomplishment", ""),
        "contribution": receipt.get("contribution", ""),
        "result": receipt.get("result", ""),
        "skills": receipt.get("skills", []),
        "evidence": public_evidence,
        "trust_signals": receipt.get("trust_signals", ["self-documented"]),
        "confirmed_count": confirmed_count,
        "created_at": receipt.get("created_at"),
        "updated_at": receipt.get("updated_at"),
    }


def get_user_by_public_slug(slug: str) -> dict:
    """Find a user by their public slug."""
    normalized_slug = normalize_slug(slug)

    user = users_collection.find_one(
        {
            "$or": [
                {"public_slug": normalized_slug},
                {"slug": normalized_slug},
                {"username": normalized_slug},
            ]
        }
    )

    if user is None:
        raise HTTPException(status_code=404, detail="Public profile not found")

    return user


def get_public_entry_query(slug: str) -> dict:
    """Build the base public-entry query for a slug."""
    user = get_user_by_public_slug(slug)

    return {
        "user_id": str(user["_id"]),
        "is_public": True,
    }


def get_monthly_activity(query: dict) -> list[dict]:
    """Return accomplishment counts for the current month and five prior months."""
    today = datetime.now(timezone.utc).date()
    months = []

    for offset in range(5, -1, -1):
        year = today.year
        month = today.month - offset

        while month <= 0:
            month += 12
            year -= 1

        months.append(
            {
                "key": f"{year:04d}-{month:02d}",
                "label": datetime(year, month, 1).strftime("%b"),
                "count": 0,
            }
        )

    month_lookup = {item["key"]: item for item in months}

    for entry in entries_collection.find(query):
        work_date = parse_work_date(entry)
        if work_date is None:
            continue

        key = f"{work_date.year:04d}-{work_date.month:02d}"
        if key in month_lookup:
            month_lookup[key]["count"] += 1

    return months


@router.get("/brag/{slug}")
def get_public_brag_entries_by_slug(
    slug: str,
    limit: int = Query(default=6, ge=1, le=50),
    skip: int = Query(default=0, ge=0),
):
    """Return paginated public brag entries for a user's Proof Profile."""
    query = get_public_entry_query(slug)
    total_entries = entries_collection.count_documents(query)
    cursor = (
        entries_collection.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    entries = [serialize_entry(entry) for entry in cursor]

    return {
        "slug": normalize_slug(slug),
        "total_entries": total_entries,
        "limit": limit,
        "skip": skip,
        "returned_entries": len(entries),
        "has_more": skip + limit < total_entries,
        "activity_last_6_months": get_monthly_activity(query),
        "entries": entries,
        "message": (
            "No public entries yet."
            if total_entries == 0
            else "Public proof entries loaded successfully."
        ),
    }


@router.get("/brag/{slug}/profile")
def get_public_profile_by_slug(slug: str):
    """Return the owner information for a public BragStack."""

    user = get_user_by_public_slug(slug)

    return {
        "profile": serialize_public_profile(user),
    }


@router.get("/brag/{slug}/impact-receipts")
def get_public_impact_receipts_by_slug(slug: str):
    """Return public Impact Receipts without leaking private evidence."""

    user = get_user_by_public_slug(slug)
    query = {
        "user_id": str(user["_id"]),
        "is_public": True,
    }

    receipts = [
        serialize_public_impact_receipt(receipt)
        for receipt in impact_receipts_collection.find(query).sort("created_at", -1)
    ]

    return {
        "slug": normalize_slug(slug),
        "total_receipts": len(receipts),
        "receipts": receipts,
        "message": (
            "No public Impact Receipts yet."
            if not receipts
            else "Public Impact Receipts loaded successfully."
        ),
    }


@router.get("/brag/{slug}/reports/weekly")
def get_public_weekly_report_by_slug(slug: str):
    """Generate a weekly public report for a specific user's public profile."""
    query = get_public_entry_query(slug)

    today = datetime.now(timezone.utc).date()
    week_start = today - timedelta(days=6)
    entries = []

    for entry in entries_collection.find(query):
        work_date = parse_work_date(entry)

        if work_date is not None and week_start <= work_date <= today:
            entries.append(entry)

    entries.sort(
        key=lambda entry: parse_work_date(entry) or date.min,
        reverse=True,
    )

    categories = {}
    tags = {}
    resume_bullets = []

    for entry in entries:
        category = entry.get("category", "Uncategorized")
        categories[category] = categories.get(category, 0) + 1

        for tag in entry.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1

        if entry.get("resume_bullet"):
            resume_bullets.append(entry["resume_bullet"])

    sorted_tags = dict(sorted(tags.items(), key=lambda item: item[1], reverse=True))
    sorted_categories = dict(
        sorted(categories.items(), key=lambda item: item[1], reverse=True)
    )

    return {
        "slug": normalize_slug(slug),
        "period": "last_7_days",
        "date_basis": "entry_date",
        "total_entries": len(entries),
        "categories": sorted_categories,
        "top_tags": sorted_tags,
        "resume_bullets": resume_bullets,
        "message": (
            "No public entries found for this week."
            if not entries
            else "Public weekly report generated successfully."
        ),
    }


@router.get("/brag/{slug}/tags/summary")
def get_public_tags_summary_by_slug(slug: str):
    """Generate a public tag summary for a specific user's public profile."""
    query = get_public_entry_query(slug)

    entries = entries_collection.find(query)
    tag_counts = {}

    for entry in entries:
        for tag in entry.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    sorted_tag_counts = dict(
        sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
    )

    return {
        "slug": normalize_slug(slug),
        "total_unique_tags": len(sorted_tag_counts),
        "tags": sorted_tag_counts,
        "message": (
            "No public tags found yet."
            if not sorted_tag_counts
            else "Public tag summary generated successfully."
        ),
    }


@router.get("/brag/{slug}/categories/summary")
def get_public_categories_summary_by_slug(slug: str):
    """Generate a public category summary for a specific user's public profile."""
    query = get_public_entry_query(slug)

    entries = entries_collection.find(query)
    category_counts = {}

    for entry in entries:
        category = entry.get("category", "Uncategorized")
        category_counts[category] = category_counts.get(category, 0) + 1

    sorted_category_counts = dict(
        sorted(category_counts.items(), key=lambda item: item[1], reverse=True)
    )

    return {
        "slug": normalize_slug(slug),
        "total_unique_categories": len(sorted_category_counts),
        "categories": sorted_category_counts,
        "message": (
            "No public categories found yet."
            if not sorted_category_counts
            else "Public category summary generated successfully."
        ),
    }
