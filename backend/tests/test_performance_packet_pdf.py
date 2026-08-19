from datetime import datetime, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.performance_packet_routes as packet_routes
from app.main import app


client = TestClient(app)


@pytest.fixture
def pdf_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_packet_pdf_test"]
    entries = mock_db["entries"]
    receipts = mock_db["impact_receipts"]

    monkeypatch.setattr(packet_routes, "entries_collection", entries)
    monkeypatch.setattr(packet_routes, "impact_receipts_collection", receipts)

    yield entries, receipts

    app.dependency_overrides.clear()


def _seed_packet(entries, receipts, user):
    entry = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Expanded family participation",
            "category": "Community Engagement",
            "entry_type": "Current Job",
            "entry_date": "2026-03-12",
            "tags": ["Program Coordination", "Family Engagement"],
            "impact": "Increased family participation by 28% across 4 sites.",
            "resume_bullet": "Expanded family participation across community programs.",
            "created_at": datetime.now(timezone.utc),
        }
    )
    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(entry.inserted_id),
            "accomplishment": "Expanded family participation",
            "contribution": "Coordinated outreach and redesigned registration follow-up.",
            "result": "Increased family participation by 28% across 4 sites.",
            "evidence": [
                {
                    "title": "Spring participation dashboard",
                    "evidence_type": "documentation",
                    "reference": "https://example.com/evidence/spring-2026",
                    "description": "Attendance comparison for participating sites.",
                    "is_public": False,
                }
            ],
            "skills": ["Program Coordination", "Family Engagement"],
            "credit": [],
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


def test_free_user_cannot_export_pdf(pdf_context):
    user = {
        "_id": ObjectId(),
        "name": "Free Member",
        "email": "free@example.com",
        "plan": "free",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user

    response = client.get("/packets/performance-review.pdf")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "paid_feature_required"
    assert response.json()["detail"]["feature"] == "export_pdf"


def test_pro_user_downloads_real_pdf_with_expected_filename(pdf_context):
    entries, receipts = pdf_context
    user = {
        "_id": ObjectId(),
        "name": "Jordan Ellis",
        "email": "jordan@example.com",
        "headline": "Community Programs Coordinator",
        "location": "Columbus, Ohio",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user
    _seed_packet(entries, receipts, user)

    response = client.get(
        "/packets/performance-review.pdf",
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
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.headers["cache-control"] == "private, no-store"
    assert "Jordan-Ellis-performance-review-2026-01-01-to-2026-06-30.pdf" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 5000


def test_pdf_export_handles_long_evidence_index(pdf_context):
    entries, receipts = pdf_context
    user = {
        "_id": ObjectId(),
        "name": "Morgan Reyes",
        "email": "morgan@example.com",
        "headline": "Operations Supervisor",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user

    entry = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Improved shift handoff quality",
            "category": "Operations",
            "entry_type": "Current Job",
            "entry_date": "2026-06-10",
            "tags": ["Operations", "Coaching", "Quality"],
            "impact": "Reduced repeat handoff issues by 21% across 3 shifts.",
            "created_at": datetime.now(timezone.utc),
        }
    )

    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(entry.inserted_id),
            "accomplishment": "Improved shift handoff quality",
            "contribution": "Built a shared handoff checklist and coached team leads.",
            "result": "Reduced repeat handoff issues by 21% across 3 shifts.",
            "evidence": [
                {
                    "title": f"Handoff quality record {index}",
                    "evidence_type": "documentation",
                    "reference": f"OPS-{index:03d}",
                    "description": "Quality review evidence.",
                    "is_public": False,
                }
                for index in range(1, 31)
            ],
            "skills": ["Operations", "Coaching", "Quality"],
            "credit": [],
            "confirmations": [],
            "trust_signals": ["evidence-linked"],
            "is_public": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    response = client.get("/packets/performance-review.pdf")

    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 8000
