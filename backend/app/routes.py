from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.database import entries_collection
from app.models import BragEntryCreate


router = APIRouter(prefix="/entries", tags=["entries"])


def generate_resume_bullet(entry: BragEntryCreate) -> str:
    """Generate a polished resume bullet from a brag entry.

    Args:
        entry: The brag entry submitted by the user.

    Returns:
        A resume-style bullet describing the work and impact.
    """
    tags = ", ".join(entry.tags) if entry.tags else entry.category

    return (
        f"Troubleshot {entry.category.lower()} work involving {tags}. "
        f"Actions taken: {entry.action}. "
        f"Impact: {entry.impact}."
    )


def serialize_entry(entry: dict) -> dict:
    """Convert a MongoDB document into a JSON-safe response.

    Args:
        entry: MongoDB entry document.

    Returns:
        JSON-safe dictionary.
    """
    entry["id"] = str(entry["_id"])
    del entry["_id"]
    return entry


@router.post("")
def create_entry(entry: BragEntryCreate):
    """Create a new brag entry."""
    document = entry.model_dump()
    document["resume_bullet"] = generate_resume_bullet(entry)
    document["created_at"] = datetime.now(timezone.utc)
    document["user_id"] = "demo-user"

    result = entries_collection.insert_one(document)

    created_entry = entries_collection.find_one({"_id": result.inserted_id})

    return serialize_entry(created_entry)

@router.get("")
def list_entries():
    """List all brag entries."""
    entries = []

    for entry in entries_collection.find({"user_id": "demo-user"}).sort("created_at", -1):
        entries.append(serialize_entry(entry))

    return {"entries": entries}

# Reports

@router.get("/reports/weekly")
def get_weekly_report():
    """Generate a weekly report from recent brag entries.

    Returns:
        Summary of brag entries created in the last 7 days.
    """
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    entries = list(
        entries_collection.find(
            {
                "user_id": "demo-user",
                "created_at": {"$gte": seven_days_ago},
            }
        ).sort("created_at", -1)
    )

    total_entries = len(entries)
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

    return {
        "period": "last_7_days",
        "total_entries": total_entries,
        "categories": categories,
        "top_tags": tags,
        "resume_bullets": resume_bullets,
        "message": (
            "No entries yet this week. Add a brag entry to start tracking your wins."
            if total_entries == 0
            else "Weekly report generated successfully."
        ),
    }

@router.get("/tags/summary")
def get_tags_summary():
    """Generate a summary of all skill tags across brag entries.

    Returns:
        Dictionary containing tag names and their usage counts.
    """
    entries = entries_collection.find({"user_id": "demo-user"})

    tag_counts = {}

    for entry in entries:
        for tag in entry.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    sorted_tag_counts = dict(
        sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
    )

    return {
        "total_unique_tags": len(sorted_tag_counts),
        "tags": sorted_tag_counts,
        "message": (
            "No tags found yet. Add entries with skill tags to build your skill summary."
            if not sorted_tag_counts
            else "Tag summary generated successfully."
        ),
    }


@router.get("/categories/summary")
def get_categories_summary():
    """Generate a summary of all categories across brag entries.

    Returns:
        Dictionary containing category names and their usage counts.
    """
    entries = entries_collection.find({"user_id": "demo-user"})

    category_counts = {}

    for entry in entries:
        category = entry.get("category", "Uncategorized")
        category_counts[category] = category_counts.get(category, 0) + 1

    sorted_category_counts = dict(
        sorted(category_counts.items(), key=lambda item: item[1], reverse=True)
    )

    return {
        "total_unique_categories": len(sorted_category_counts),
        "categories": sorted_category_counts,
        "message": (
            "No categories found yet. Add entries to build your category summary."
            if not sorted_category_counts
            else "Category summary generated successfully."
        ),
    }

@router.get("/{entry_id}")
def get_entry(entry_id: str):
    """Get a single brag entry by ID."""
    if not ObjectId.is_valid(entry_id):
        raise HTTPException(status_code=400, detail="Invalid entry ID")

    entry = entries_collection.find_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": "demo-user",
        }
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return serialize_entry(entry)



@router.delete("/{entry_id}")
def delete_entry(entry_id: str):
    """Delete a brag entry by ID."""
    if not ObjectId.is_valid(entry_id):
        raise HTTPException(status_code=400, detail="Invalid entry ID")

    result = entries_collection.delete_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": "demo-user",
        }
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {"message": "Entry deleted"}

@router.put("/{entry_id}")
def update_entry(entry_id: str, entry: BragEntryCreate):
    """Update a brag entry by ID.

    Args:
        entry_id: MongoDB ObjectId for the brag entry.
        entry: Updated brag entry payload.

    Returns:
        Updated brag entry document.
    """
    if not ObjectId.is_valid(entry_id):
        raise HTTPException(status_code=400, detail="Invalid entry ID")

    updated_document = entry.model_dump()
    updated_document["resume_bullet"] = generate_resume_bullet(entry)
    updated_document["updated_at"] = datetime.now(timezone.utc)

    result = entries_collection.update_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": "demo-user",
        },
        {"$set": updated_document},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")

    updated_entry = entries_collection.find_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": "demo-user",
        }
    )

    return serialize_entry(updated_entry)

