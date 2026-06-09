from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import get_current_user
from app.database import entries_collection
from app.models import BragEntryCreate

router = APIRouter(prefix="/entries", tags=["entries"])


def get_user_id(current_user: dict) -> str:
    """Return the authenticated user's MongoDB ID as a string.

    Args:
        current_user: The authenticated user document from MongoDB.

    Returns:
        The authenticated user's ID as a string.
    """
    return str(current_user["_id"])


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
    """Convert a MongoDB entry document into a JSON-safe response.

    Args:
        entry: The MongoDB entry document.

    Returns:
        A JSON-safe dictionary with the MongoDB ObjectId converted to a string.
    """
    entry["id"] = str(entry["_id"])
    del entry["_id"]
    return entry


@router.post("")
def create_entry(
    entry: BragEntryCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new brag entry for the authenticated user.

    Args:
        entry: The brag entry payload from the request body.
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        The created brag entry.
    """
    now = datetime.now(timezone.utc)

    document = entry.model_dump()
    document["resume_bullet"] = generate_resume_bullet(entry)
    document["created_at"] = now
    document["updated_at"] = now
    document["user_id"] = get_user_id(current_user)

    result = entries_collection.insert_one(document)

    created_entry = entries_collection.find_one({"_id": result.inserted_id})

    return serialize_entry(created_entry)


@router.get("")
def list_entries(
    limit: int = Query(default=10, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """List brag entries owned by the authenticated user.

    Args:
        limit: The maximum number of entries to return.
        skip: The number of entries to skip for pagination.
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        A paginated list of brag entries owned by the authenticated user.
    """
    query = {"user_id": get_user_id(current_user)}

    total_entries = entries_collection.count_documents(query)

    cursor = (
        entries_collection.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    entries = [serialize_entry(entry) for entry in cursor]

    return {
        "total_entries": total_entries,
        "limit": limit,
        "skip": skip,
        "returned_entries": len(entries),
        "has_more": skip + limit < total_entries,
        "entries": entries,
    }


@router.get("/reports/weekly")
def get_weekly_report(current_user: dict = Depends(get_current_user)):
    """Generate a weekly report from the authenticated user's recent entries.

    Args:
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        A summary of brag entries created in the last 7 days.
    """
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    entries = list(
        entries_collection.find(
            {
                "user_id": get_user_id(current_user),
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
def get_tags_summary(current_user: dict = Depends(get_current_user)):
    """Generate a skill tag summary for the authenticated user.

    Args:
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        A dictionary containing tag names and their usage counts.
    """
    entries = entries_collection.find({"user_id": get_user_id(current_user)})

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
def get_categories_summary(current_user: dict = Depends(get_current_user)):
    """Generate a category summary for the authenticated user.

    Args:
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        A dictionary containing category names and their usage counts.
    """
    entries = entries_collection.find({"user_id": get_user_id(current_user)})

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


@router.get("/search")
def search_entries(
    query: str,
    current_user: dict = Depends(get_current_user),
):
    """Search the authenticated user's brag entries by keyword.

    Args:
        query: The search term used to find matching brag entries.
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        Matching brag entries owned by the authenticated user.
    """
    search_filter = {
        "user_id": get_user_id(current_user),
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"category": {"$regex": query, "$options": "i"}},
            {"situation": {"$regex": query, "$options": "i"}},
            {"action": {"$regex": query, "$options": "i"}},
            {"impact": {"$regex": query, "$options": "i"}},
            {"lesson": {"$regex": query, "$options": "i"}},
            {"tags": {"$regex": query, "$options": "i"}},
        ],
    }

    entries = [
        serialize_entry(entry)
        for entry in entries_collection.find(search_filter).sort("created_at", -1)
    ]

    return {
        "query": query,
        "total_results": len(entries),
        "entries": entries,
        "message": (
            "No matching entries found."
            if not entries
            else "Search completed successfully."
        ),
    }


@router.get("/{entry_id}")
def get_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get a single brag entry owned by the authenticated user.

    Args:
        entry_id: The MongoDB ObjectId for the brag entry.
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        The matching brag entry.

    Raises:
        HTTPException: If the entry ID is invalid or the entry is not found.
    """
    if not ObjectId.is_valid(entry_id):
        raise HTTPException(status_code=400, detail="Invalid entry ID")

    entry = entries_collection.find_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": get_user_id(current_user),
        }
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return serialize_entry(entry)


@router.put("/{entry_id}")
def update_entry(
    entry_id: str,
    entry: BragEntryCreate,
    current_user: dict = Depends(get_current_user),
):
    """Update a brag entry owned by the authenticated user.

    Args:
        entry_id: The MongoDB ObjectId for the brag entry.
        entry: The updated brag entry payload.
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        The updated brag entry document.

    Raises:
        HTTPException: If the entry ID is invalid or the entry is not found.
    """
    if not ObjectId.is_valid(entry_id):
        raise HTTPException(status_code=400, detail="Invalid entry ID")

    now = datetime.now(timezone.utc)

    updated_document = entry.model_dump()
    updated_document["resume_bullet"] = generate_resume_bullet(entry)
    updated_document["updated_at"] = now

    result = entries_collection.update_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": get_user_id(current_user),
        },
        {"$set": updated_document},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")

    updated_entry = entries_collection.find_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": get_user_id(current_user),
        }
    )

    return serialize_entry(updated_entry)


@router.delete("/{entry_id}")
def delete_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a brag entry owned by the authenticated user.

    Args:
        entry_id: The MongoDB ObjectId for the brag entry.
        current_user: The authenticated user injected by the auth dependency.

    Returns:
        A confirmation message after the entry is deleted.

    Raises:
        HTTPException: If the entry ID is invalid or the entry is not found.
    """
    if not ObjectId.is_valid(entry_id):
        raise HTTPException(status_code=400, detail="Invalid entry ID")

    result = entries_collection.delete_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": get_user_id(current_user),
        }
    )

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Entry not found")

    return {"message": "Entry deleted"}