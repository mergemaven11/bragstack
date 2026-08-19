from datetime import datetime, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.performance_packet_routes as packet_routes
from app.main import app


client = TestClient(app)


@pytest.fixture
def packet_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_packet_test"]
    entries = mock_db["entries"]
    receipts = mock_db["impact_receipts"]

    monkeypatch.setattr(packet_routes, "entries_collection", entries)
    monkeypatch.setattr(packet_routes, "impact_receipts_collection", receipts)

    yield entries, receipts

    app.dependency_overrides.clear()


def test_free_user_cannot_generate_performance_packet(packet_context):
    user = {
        "_id": ObjectId(),
        "name": "Free Member",
        "email": "free@example.com",
        "plan": "free",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user

    response = client.get("/packets/performance-review")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "paid_feature_required"
    assert response.json()["detail"]["feature"] == "performance_review_builder"


def test_pro_packet_is_career_neutral_and_contains_full_dossier_data(packet_context):
    entries, receipts = packet_context
    user = {
        "_id": ObjectId(),
        "name": "Jordan Ellis",
        "email": "jordan@example.com",
        "headline": "Community Programs Coordinator",
        "location": "Columbus, Ohio",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user

    first_entry = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Expanded after-school family participation",
            "category": "Community Engagement",
            "entry_type": "Current Job",
            "entry_date": "2026-03-12",
            "tags": ["Program Coordination", "Family Engagement"],
            "impact": "Increased family participation by 28% across 4 sites.",
            "resume_bullet": "Expanded family participation across community programs.",
            "created_at": datetime.now(timezone.utc),
        }
    )
    second_entry = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Created volunteer onboarding workshop",
            "category": "Training",
            "entry_type": "Current Job",
            "entry_date": "2026-05-20",
            "tags": ["Training", "Communication"],
            "impact": "Prepared 18 volunteers for summer programming.",
            "resume_bullet": "Designed a volunteer onboarding workshop.",
            "created_at": datetime.now(timezone.utc),
        }
    )

    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(first_entry.inserted_id),
            "accomplishment": "Expanded after-school family participation",
            "contribution": "Coordinated outreach, translated materials, and redesigned registration follow-up.",
            "result": "Increased family participation by 28% across 4 sites.",
            "evidence": [
                {
                    "title": "Spring participation report",
                    "evidence_type": "documentation",
                    "reference": "SPRING-2026",
                    "description": "Attendance comparison for participating sites.",
                    "is_public": False,
                },
                {
                    "title": "Family feedback summary",
                    "evidence_type": "customer-feedback",
                    "reference": "Feedback survey",
                    "description": "Compiled caregiver comments.",
                    "is_public": False,
                },
            ],
            "skills": ["Program Coordination", "Family Engagement", "Communication"],
            "credit": [
                {
                    "name": "Outreach Team",
                    "contribution": "Supported multilingual family outreach.",
                }
            ],
            "confirmations": [
                {
                    "name": "Program Director",
                    "role": "Director",
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
            "source_entry_id": str(second_entry.inserted_id),
            "accomplishment": "Created volunteer onboarding workshop",
            "contribution": "Designed the workshop, materials, and facilitation plan.",
            "result": "Prepared 18 volunteers for summer programming.",
            "evidence": [],
            "skills": ["Training", "Communication"],
            "credit": [],
            "confirmations": [],
            "trust_signals": ["self-documented"],
            "is_public": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    response = client.get(
        "/packets/performance-review",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "career_area": "Nonprofit",
            "role_title": "Community Programs Coordinator",
            "organization": "Neighborhood Learning Collaborative",
            "confidential": "true",
        },
    )

    assert response.status_code == 200
    packet = response.json()["packet"]

    assert packet["subject"]["name"] == "Jordan Ellis"
    assert packet["subject"]["role"] == "Community Programs Coordinator"
    assert packet["context"]["career_area"] == "Nonprofit"
    assert packet["context"]["organization"] == "Neighborhood Learning Collaborative"
    assert packet["confidential"] is True

    assert packet["scorecard"]["accomplishments"] == 2
    assert packet["scorecard"]["impact_receipts"] == 2
    assert packet["scorecard"]["evidence_items"] == 2
    assert packet["scorecard"]["receipt_coverage_percent"] == 100
    assert packet["scorecard"]["quantified_result_coverage_percent"] == 100
    assert packet["scorecard"]["evidence_coverage_percent"] == 50
    assert packet["scorecard"]["verification_coverage_percent"] == 50
    assert packet["scorecard"]["evidence_depth"] == 1.0

    assert packet["impact_analytics"]["activity_by_month"] == {
        "2026-03": 1,
        "2026-05": 1,
    }
    assert packet["impact_analytics"]["categories"] == {
        "Community Engagement": 1,
        "Training": 1,
    }
    assert packet["impact_analytics"]["top_skills"]["Communication"] == 2

    assert len(packet["signature_accomplishments"]) == 2
    assert packet["measurable_results"][0]["metric_display"] in {"28%", "18"}
    assert len(packet["contribution_records"]) == 2
    assert len(packet["receipt_records"]) == 2
    assert len(packet["evidence_index"]) == 2
    assert packet["receipt_records"][0]["reference"].startswith("BS-2026-")
    assert "Community Programs Coordinator" not in packet["review_summary"] or packet["review_summary"]
    assert "documented 2 accomplishments" in packet["review_summary"]


def test_packet_period_validation_and_filtering(packet_context):
    entries, _ = packet_context
    user = {
        "_id": ObjectId(),
        "name": "Review User",
        "email": "review@example.com",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user

    entries.insert_many(
        [
            {
                "user_id": str(user["_id"]),
                "title": "Spring work",
                "category": "Service",
                "entry_type": "Current Job",
                "entry_date": "2026-04-10",
                "tags": ["Service"],
                "impact": "Completed spring milestone.",
            },
            {
                "user_id": str(user["_id"]),
                "title": "Summer work",
                "category": "Service",
                "entry_type": "Current Job",
                "entry_date": "2026-07-10",
                "tags": ["Service"],
                "impact": "Completed summer milestone.",
            },
        ]
    )

    response = client.get(
        "/packets/performance-review?start_date=2026-07-01&end_date=2026-07-31"
    )
    assert response.status_code == 200
    packet = response.json()["packet"]
    assert packet["scorecard"]["accomplishments"] == 1
    assert packet["signature_accomplishments"][0]["title"] == "Summer work"

    missing_end = client.get("/packets/performance-review?start_date=2026-07-01")
    assert missing_end.status_code == 422

    reversed_period = client.get(
        "/packets/performance-review?start_date=2026-08-01&end_date=2026-07-01"
    )
    assert reversed_period.status_code == 422
