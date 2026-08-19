from datetime import datetime, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.interview_packet_routes as interview_routes
import app.performance_packet_routes as packet_routes
from app.main import app


client = TestClient(app)


@pytest.fixture
def interview_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_interview_packet_test"]
    entries = mock_db["entries"]
    receipts = mock_db["impact_receipts"]

    monkeypatch.setattr(packet_routes, "entries_collection", entries)
    monkeypatch.setattr(packet_routes, "impact_receipts_collection", receipts)
    monkeypatch.setattr(interview_routes, "impact_receipts_collection", receipts)

    yield entries, receipts
    app.dependency_overrides.clear()


def _seed_education_case(entries, receipts, user):
    first = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Improved family conference participation",
            "category": "Family Engagement",
            "entry_type": "Current Job",
            "entry_date": "2026-02-14",
            "tags": ["Communication", "Family Engagement"],
            "impact": "Increased conference participation by 24% across the grade level.",
            "created_at": datetime.now(timezone.utc),
        }
    )
    second = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Created peer reading routine",
            "category": "Instruction",
            "entry_type": "Current Job",
            "entry_date": "2026-04-09",
            "tags": ["Instruction", "Student Support"],
            "impact": "Built a repeatable peer reading routine for small-group practice.",
            "created_at": datetime.now(timezone.utc),
        }
    )
    third = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Coordinated spring learning showcase",
            "category": "Program Coordination",
            "entry_type": "Current Job",
            "entry_date": "2026-05-22",
            "tags": ["Coordination", "Communication"],
            "impact": "Hosted a school-wide learning showcase for 180 attendees.",
            "created_at": datetime.now(timezone.utc),
        }
    )

    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(first.inserted_id),
            "accomplishment": "Improved family conference participation",
            "contribution": "Redesigned reminder messaging and coordinated multilingual outreach.",
            "result": "Increased conference participation by 24% across the grade level.",
            "evidence": [
                {
                    "title": "Conference attendance summary",
                    "evidence_type": "documentation",
                    "reference": "https://example.org/private-attendance-summary",
                    "description": "Attendance comparison for the review period.",
                    "is_public": False,
                }
            ],
            "skills": ["Communication", "Family Engagement"],
            "credit": [],
            "confirmations": [
                {
                    "name": "Assistant Principal",
                    "role": "School Leader",
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

    return str(first.inserted_id), str(second.inserted_id), str(third.inserted_id)


def test_free_user_cannot_build_interview_packet(interview_context):
    user = {
        "_id": ObjectId(),
        "name": "Free Member",
        "email": "free@example.com",
        "plan": "free",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user

    response = client.get("/packets/interview")

    assert response.status_code == 403
    assert response.json()["detail"]["feature"] == "interview_packet"


def test_interview_packet_uses_only_selected_stories_and_hides_evidence_by_default(interview_context):
    entries, receipts = interview_context
    user = {
        "_id": ObjectId(),
        "name": "Avery Brooks",
        "email": "avery@example.com",
        "headline": "Elementary Educator",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user
    first_id, second_id, third_id = _seed_education_case(entries, receipts, user)

    response = client.get(
        "/packets/interview",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "career_area": "Education",
            "role_title": "Elementary Educator",
            "target_role": "Instructional Coach",
            "target_organization": "Community School District",
            "selected_entry_ids": f"{first_id},{third_id}",
        },
    )

    assert response.status_code == 200
    packet = response.json()["packet"]
    assert packet["kind"] == "interview"
    assert packet["title"] == "Interview Packet"
    assert packet["target"]["role"] == "Instructional Coach"
    assert packet["scorecard"]["accomplishments"] == 2
    assert [story["entry_id"] for story in packet["interview_stories"]] == [first_id, third_id]
    assert second_id not in packet["interview_preferences"]["selected_entry_ids"]
    assert packet["interview_stories"][0]["evidence_count"] == 1
    assert packet["interview_stories"][0]["evidence"] == []
    assert packet["evidence_index"] == []
    assert packet["receipt_records"] == []
    assert "Instructional Coach" in packet["interview_summary"]


def test_interview_packet_can_explicitly_export_evidence_references(interview_context):
    entries, receipts = interview_context
    user = {
        "_id": ObjectId(),
        "name": "Avery Brooks",
        "email": "avery@example.com",
        "headline": "Elementary Educator",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user
    first_id, _, _ = _seed_education_case(entries, receipts, user)

    response = client.get(
        "/packets/interview",
        params={
            "selected_entry_ids": first_id,
            "include_evidence_references": "true",
        },
    )

    assert response.status_code == 200
    evidence = response.json()["packet"]["interview_stories"][0]["evidence"]
    assert evidence[0]["reference"] == "https://example.org/private-attendance-summary"


def test_interview_packet_pdf_download_is_real_and_named_for_interview(interview_context):
    entries, receipts = interview_context
    user = {
        "_id": ObjectId(),
        "name": "Avery Brooks",
        "email": "avery@example.com",
        "headline": "Elementary Educator",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user
    first_id, _, third_id = _seed_education_case(entries, receipts, user)

    response = client.get(
        "/packets/interview.pdf",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "selected_entry_ids": f"{first_id},{third_id}",
            "target_role": "Instructional Coach",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 4000
    assert "Avery-Brooks-interview-packet-2026-01-01-to-2026-06-30.pdf" in response.headers["content-disposition"]
