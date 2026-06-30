from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException

from app.database import entries_collection, users_collection


router = APIRouter(prefix="/public", tags=["public"])


def normalize_slug(slug: str) -> str:
    """Normalize a public profile slug for lookup."""
    return slug.strip().lower()


def serialize_entry(entry: dict) -> dict:
    """Convert a MongoDB brag entry document into an API response dictionary."""
    return {
        "id": str(entry["_id"]),
        "title": entry.get("title", ""),
        "description": entry.get("description", ""),
        "category": entry.get("category", ""),
        "tags": entry.get("tags", []),
        "resume_bullet": entry.get("resume_bullet", ""),
        "is_public": entry.get("is_public", False),
        "created_at": entry.get("created_at"),
        "updated_at": entry.get("updated_at"),
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


@router.get("/brag/{slug}")
def get_public_brag_entries_by_slug(slug: str):
    """Return public brag entries for a specific user's public profile."""
    query = get_public_entry_query(slug)

    entries = [
        serialize_entry(entry)
        for entry in entries_collection.find(query).sort("created_at", -1)
    ]

    return {
        "slug": normalize_slug(slug),
        "total_entries": len(entries),
        "entries": entries,
        "message": (
            "No public entries yet."
            if not entries
            else "Public brag entries loaded successfully."
        ),
    }


@router.get("/brag/{slug}/reports/weekly")
def get_public_weekly_report_by_slug(slug: str):
    """Generate a weekly public report for a specific user's public profile."""
    query = get_public_entry_query(slug)

    week_start = datetime.now(timezone.utc) - timedelta(days=7)
    query["created_at"] = {"$gte": week_start.isoformat()}

    entries = list(entries_collection.find(query).sort("created_at", -1))

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