from datetime import datetime, timezone
from uuid import uuid4

import mongomock
import pytest
from fastapi.testclient import TestClient

import app.public_slug_routes as public_slug_routes
import app.routes as routes
from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def use_mock_database(monkeypatch):
    """Use an in-memory MongoDB replacement for public route tests."""
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_test"]

    mock_entries_collection = mock_db["entries"]
    mock_users_collection = mock_db["users"]

    monkeypatch.setattr(routes, "entries_collection", mock_entries_collection)
    monkeypatch.setattr(public_slug_routes, "entries_collection", mock_entries_collection)
    monkeypatch.setattr(public_slug_routes, "users_collection", mock_users_collection)

    yield


def test_root_returns_health_message():
    """Verify the API root route returns the health check message."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "BragStack API is running"}


def test_public_brag_route_returns_public_payload():
    """Verify the public brag route returns a public entries response."""
    response = client.get("/public/brag")

    assert response.status_code == 200

    data = response.json()

    assert "total_entries" in data
    assert "entries" in data
    assert "message" in data
    assert isinstance(data["entries"], list)


def test_public_brag_slug_route_returns_only_that_users_public_entries():
    """Verify slug public brag route only returns public entries for that user."""
    slug = f"test-user-{uuid4().hex[:8]}"

    user_result = public_slug_routes.users_collection.insert_one(
        {
            "name": "Test User",
            "email": f"{slug}@example.com",
            "public_slug": slug,
            "hashed_password": "unused",
            "created_at": datetime.now(timezone.utc),
        }
    )

    other_user_result = public_slug_routes.users_collection.insert_one(
        {
            "name": "Other User",
            "email": f"other-{slug}@example.com",
            "public_slug": f"other-{slug}",
            "hashed_password": "unused",
            "created_at": datetime.now(timezone.utc),
        }
    )

    public_slug_routes.entries_collection.insert_many(
        [
            {
                "user_id": str(user_result.inserted_id),
                "title": "Visible win",
                "description": "This should show up.",
                "category": "Support",
                "tags": ["docker", "customer"],
                "resume_bullet": "Resolved a customer Docker issue.",
                "is_public": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "user_id": str(user_result.inserted_id),
                "title": "Private win",
                "description": "This should not show up.",
                "category": "Private",
                "tags": ["secret"],
                "resume_bullet": "",
                "is_public": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "user_id": str(other_user_result.inserted_id),
                "title": "Other user win",
                "description": "This should not show up.",
                "category": "Other",
                "tags": ["other"],
                "resume_bullet": "",
                "is_public": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]
    )

    response = client.get(f"/public/brag/{slug}")

    assert response.status_code == 200

    data = response.json()

    assert data["slug"] == slug
    assert data["total_entries"] == 1
    assert data["entries"][0]["title"] == "Visible win"


def test_public_weekly_report_slug_route_returns_summary():
    """Verify slug public weekly report returns summary data for that user."""
    slug = f"weekly-user-{uuid4().hex[:8]}"

    user_result = public_slug_routes.users_collection.insert_one(
        {
            "name": "Weekly User",
            "email": f"{slug}@example.com",
            "public_slug": slug,
            "hashed_password": "unused",
            "created_at": datetime.now(timezone.utc),
        }
    )

    public_slug_routes.entries_collection.insert_one(
        {
            "user_id": str(user_result.inserted_id),
            "title": "Weekly win",
            "description": "This should appear in weekly summary.",
            "category": "Engineering",
            "tags": ["python", "api"],
            "resume_bullet": "Built a public API endpoint.",
            "is_public": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    response = client.get(f"/public/brag/{slug}/reports/weekly")

    assert response.status_code == 200

    data = response.json()

    assert data["slug"] == slug
    assert data["period"] == "last_7_days"
    assert data["total_entries"] == 1
    assert data["categories"] == {"Engineering": 1}
    assert data["top_tags"] == {"python": 1, "api": 1}
    assert data["resume_bullets"] == ["Built a public API endpoint."]


def test_public_tags_summary_slug_route_returns_tags():
    """Verify slug public tags summary returns tag counts for that user."""
    slug = f"tags-user-{uuid4().hex[:8]}"

    user_result = public_slug_routes.users_collection.insert_one(
        {
            "name": "Tags User",
            "email": f"{slug}@example.com",
            "public_slug": slug,
            "hashed_password": "unused",
            "created_at": datetime.now(timezone.utc),
        }
    )

    public_slug_routes.entries_collection.insert_many(
        [
            {
                "user_id": str(user_result.inserted_id),
                "title": "Tag win one",
                "description": "First tag win.",
                "category": "Support",
                "tags": ["docker", "api"],
                "resume_bullet": "",
                "is_public": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
            {
                "user_id": str(user_result.inserted_id),
                "title": "Tag win two",
                "description": "Second tag win.",
                "category": "Support",
                "tags": ["docker"],
                "resume_bullet": "",
                "is_public": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ]
    )

    response = client.get(f"/public/brag/{slug}/tags/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["slug"] == slug
    assert data["total_unique_tags"] == 2
    assert data["tags"] == {"docker": 2, "api": 1}


def test_public_brag_slug_route_returns_404_for_missing_profile():
    """Verify unknown public profile slugs return 404."""
    response = client.get("/public/brag/profile-that-does-not-exist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Public profile not found"