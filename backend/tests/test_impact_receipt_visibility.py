from datetime import datetime, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.impact_receipt_routes as impact_receipt_routes
import app.public_slug_routes as public_slug_routes
from app.main import app


client = TestClient(app)


@pytest.fixture
def receipt_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_receipt_visibility_test"]

    users = mock_db["users"]
    entries = mock_db["entries"]
    receipts = mock_db["impact_receipts"]

    user = {
        "_id": ObjectId(),
        "name": "Receipt User",
        "email": "receipt@example.com",
        "public_slug": "receipt-user-123",
    }
    users.insert_one(user.copy())

    monkeypatch.setattr(impact_receipt_routes, "entries_collection", entries)
    monkeypatch.setattr(impact_receipt_routes, "impact_receipts_collection", receipts)
    monkeypatch.setattr(public_slug_routes, "users_collection", users)
    monkeypatch.setattr(public_slug_routes, "entries_collection", entries)
    monkeypatch.setattr(public_slug_routes, "impact_receipts_collection", receipts)

    app.dependency_overrides[impact_receipt_routes.get_current_user] = lambda: user

    yield user, receipts

    app.dependency_overrides.clear()


def test_owner_can_toggle_receipt_visibility(receipt_context):
    user, receipts = receipt_context
    now = datetime.now(timezone.utc)

    result = receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(ObjectId()),
            "accomplishment": "Reduced incident volume",
            "contribution": "Found the root cause.",
            "result": "Reduced repeat incidents by 25%.",
            "evidence": [],
            "skills": ["Troubleshooting"],
            "credit": [],
            "confirmations": [],
            "trust_signals": ["self-documented"],
            "is_public": False,
            "schema_version": 1,
            "created_at": now,
            "updated_at": now,
        }
    )

    response = client.patch(
        f"/impact-receipts/{result.inserted_id}",
        json={"is_public": True},
    )

    assert response.status_code == 200
    assert response.json()["is_public"] is True

    stored = receipts.find_one({"_id": result.inserted_id})
    assert stored["is_public"] is True
    assert stored["updated_at"] >= now


def test_public_receipts_hide_private_evidence(receipt_context):
    user, receipts = receipt_context
    now = datetime.now(timezone.utc)

    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(ObjectId()),
            "accomplishment": "Public receipt",
            "contribution": "Implemented the fix.",
            "result": "Improved reliability by 20%.",
            "evidence": [
                {
                    "evidence_type": "ticket",
                    "title": "Private ticket",
                    "reference": "SECRET-1",
                    "description": "Internal details",
                    "is_public": False,
                },
                {
                    "evidence_type": "project-link",
                    "title": "Public project",
                    "reference": "https://example.com/project",
                    "description": "Public proof",
                    "is_public": True,
                },
            ],
            "skills": ["Python"],
            "credit": [{"name": "Private Collaborator", "contribution": "Helped"}],
            "confirmations": [],
            "trust_signals": ["self-documented", "evidence-linked"],
            "is_public": True,
            "schema_version": 1,
            "created_at": now,
            "updated_at": now,
        }
    )

    response = client.get(f"/public/brag/{user['public_slug']}/impact-receipts")

    assert response.status_code == 200
    data = response.json()
    assert data["total_receipts"] == 1
    assert len(data["receipts"][0]["evidence"]) == 1
    assert data["receipts"][0]["evidence"][0]["title"] == "Public project"
    assert "credit" not in data["receipts"][0]
