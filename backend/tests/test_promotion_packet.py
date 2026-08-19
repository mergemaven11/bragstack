from datetime import datetime, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.performance_packet_routes as packet_routes
from app.main import app


client = TestClient(app)


@pytest.fixture
def promotion_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_promotion_packet_test"]
    entries = mock_db["entries"]
    receipts = mock_db["impact_receipts"]

    monkeypatch.setattr(packet_routes, "entries_collection", entries)
    monkeypatch.setattr(packet_routes, "impact_receipts_collection", receipts)

    yield entries, receipts
    app.dependency_overrides.clear()


def _seed_operations_case(entries, receipts, user):
    first = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Improved shift handoff quality",
            "category": "Operations",
            "entry_type": "Current Job",
            "entry_date": "2026-03-18",
            "tags": ["Coaching", "Quality", "Operations"],
            "impact": "Reduced repeat handoff issues by 21% across 3 shifts.",
            "created_at": datetime.now(timezone.utc),
        }
    )
    second = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Expanded lead training coverage",
            "category": "People Development",
            "entry_type": "Current Job",
            "entry_date": "2026-05-10",
            "tags": ["Training", "Coaching", "Leadership"],
            "impact": "Prepared 12 team leads to run the updated handoff process.",
            "created_at": datetime.now(timezone.utc),
        }
    )

    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(first.inserted_id),
            "accomplishment": "Improved shift handoff quality",
            "contribution": "Designed the checklist, piloted it with leads, and coached each shift on the new standard.",
            "result": "Reduced repeat handoff issues by 21% across 3 shifts.",
            "evidence": [
                {
                    "title": "Quality review summary",
                    "evidence_type": "documentation",
                    "reference": "OPS-Q2-2026",
                    "description": "Before-and-after handoff quality review.",
                    "is_public": False,
                }
            ],
            "skills": ["Coaching", "Quality", "Operations"],
            "credit": [],
            "confirmations": [
                {
                    "name": "Regional Operations Manager",
                    "role": "Regional Manager",
                    "confirmation_type": "stakeholder",
                    "status": "confirmed",
                }
            ],
            "trust_signals": ["evidence-linked", "stakeholder-verified"],
            "is_public": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(second.inserted_id),
            "accomplishment": "Expanded lead training coverage",
            "contribution": "Built a short training session and coached team leads through live shift handoffs.",
            "result": "Prepared 12 team leads to run the updated handoff process.",
            "evidence": [],
            "skills": ["Training", "Coaching", "Leadership"],
            "credit": [],
            "confirmations": [],
            "trust_signals": ["self-documented"],
            "is_public": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )


def test_free_user_cannot_build_promotion_packet(promotion_context):
    user = {
        "_id": ObjectId(),
        "name": "Free Member",
        "email": "free@example.com",
        "plan": "free",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user

    response = client.get("/packets/promotion")

    assert response.status_code == 403
    assert response.json()["detail"]["feature"] == "promotion_packet"


def test_pro_promotion_packet_is_evidence_backed_and_career_neutral(promotion_context):
    entries, receipts = promotion_context
    user = {
        "_id": ObjectId(),
        "name": "Morgan Reyes",
        "email": "morgan@example.com",
        "headline": "Operations Supervisor",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user
    _seed_operations_case(entries, receipts, user)

    response = client.get(
        "/packets/promotion",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "career_area": "Operations",
            "role_title": "Operations Supervisor",
            "organization": "Regional Fulfillment Center",
            "target_role": "Senior Operations Manager",
            "target_level": "Next-level leadership",
        },
    )

    assert response.status_code == 200
    packet = response.json()["packet"]
    assert packet["kind"] == "promotion"
    assert packet["title"] == "Promotion Packet"
    assert packet["target"]["role"] == "Senior Operations Manager"
    assert packet["target"]["level"] == "Next-level leadership"
    assert packet["scorecard"]["accomplishments"] == 2
    assert len(packet["promotion_case"]["demonstrated_impact"]) == 2
    assert len(packet["promotion_case"]["scope_and_ownership"]) == 2
    assert len(packet["promotion_case"]["verified_recognition"]) == 1
    assert packet["promotion_case"]["strengthening_actions"]
    assert "does not assign promotion readiness" in packet["promotion_summary"]
    assert "Senior Operations Manager" in packet["promotion_summary"]


def test_pro_user_downloads_dedicated_promotion_pdf(promotion_context):
    entries, receipts = promotion_context
    user = {
        "_id": ObjectId(),
        "name": "Morgan Reyes",
        "email": "morgan@example.com",
        "headline": "Operations Supervisor",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user
    _seed_operations_case(entries, receipts, user)

    response = client.get(
        "/packets/promotion.pdf",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "career_area": "Operations",
            "target_role": "Senior Operations Manager",
            "target_level": "Next-level leadership",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 5000
    assert "Morgan-Reyes-promotion-packet-2026-01-01-to-2026-06-30.pdf" in response.headers["content-disposition"]
