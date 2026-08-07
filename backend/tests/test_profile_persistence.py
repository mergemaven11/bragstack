from datetime import datetime, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.auth_routes as auth_routes
import app.public_slug_routes as public_slug_routes
from app.main import app


client = TestClient(app)


@pytest.fixture
def profile_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_profile_test"]
    users = mock_db["users"]
    entries = mock_db["entries"]
    receipts = mock_db["impact_receipts"]

    user = {
        "_id": ObjectId(),
        "name": "Original Name",
        "email": "profile@example.com",
        "public_slug": "profile-user-123",
        "hashed_password": "unused",
        "created_at": datetime.now(timezone.utc),
    }
    users.insert_one(user.copy())

    monkeypatch.setattr(auth_routes, "users_collection", users)
    monkeypatch.setattr(public_slug_routes, "users_collection", users)
    monkeypatch.setattr(public_slug_routes, "entries_collection", entries)
    monkeypatch.setattr(public_slug_routes, "impact_receipts_collection", receipts)

    app.dependency_overrides[auth_routes.get_current_user] = lambda: users.find_one(
        {"_id": user["_id"]}
    )

    yield user, users

    app.dependency_overrides.clear()


def test_profile_update_persists_and_is_visible_publicly(profile_context):
    user, users = profile_context

    payload = {
        "name": "Updated Name",
        "headline": "Platform support engineer",
        "bio": "I turn technical work into measurable customer impact.",
        "location": "Atlanta, Georgia",
        "github_url": "https://github.com/example",
        "portfolio_url": "https://example.com",
        "resume_url": "https://example.com/resume",
    }

    response = client.patch("/auth/me/profile", json=payload)

    assert response.status_code == 200
    assert response.json()["headline"] == payload["headline"]

    stored_user = users.find_one({"_id": user["_id"]})
    assert stored_user["name"] == "Updated Name"
    assert stored_user["bio"] == payload["bio"]
    assert stored_user["resume_url"] == payload["resume_url"]

    public_response = client.get(f"/public/brag/{user['public_slug']}/profile")

    assert public_response.status_code == 200
    profile = public_response.json()["profile"]
    assert profile["name"] == "Updated Name"
    assert profile["headline"] == payload["headline"]
    assert profile["bio"] == payload["bio"]
    assert profile["location"] == payload["location"]
    assert profile["github_url"] == payload["github_url"]


def test_profile_update_rejects_non_http_links(profile_context):
    response = client.patch(
        "/auth/me/profile",
        json={
            "name": "Updated Name",
            "headline": "",
            "bio": "",
            "location": "",
            "github_url": "github.com/example",
            "portfolio_url": "",
            "resume_url": "",
        },
    )

    assert response.status_code == 422
