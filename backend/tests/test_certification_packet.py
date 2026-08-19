from datetime import datetime, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.performance_packet_routes as packet_routes
from app.main import app


client = TestClient(app)


@pytest.fixture
def certification_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_certification_packet_test"]
    entries = mock_db["entries"]
    receipts = mock_db["impact_receipts"]

    monkeypatch.setattr(packet_routes, "entries_collection", entries)
    monkeypatch.setattr(packet_routes, "impact_receipts_collection", receipts)

    yield entries, receipts
    app.dependency_overrides.clear()


def _seed_cosmetology_case(entries, receipts, user):
    cases = [
        (
            "Completed state sanitation renewal",
            "Licensure",
            "2026-02-12",
            "Completed the required sanitation refresher before renewal.",
            "Met the annual sanitation education requirement.",
            "license",
            "State cosmetology license copy",
            "GA-COS-RENEWAL",
            [],
            [],
        ),
        (
            "Completed advanced color continuing education",
            "Continuing Education",
            "2026-04-18",
            "Completed an 8-hour advanced color course and documented the techniques practiced.",
            "Completed 8 hours of continuing education.",
            "continuing education",
            "Advanced Color CE certificate",
            "CE-8HR-2026",
            [{"name": "Course Instructor", "role": "Educator", "confirmation_type": "stakeholder", "status": "confirmed"}],
            ["evidence-linked"],
        ),
        (
            "Completed infection-control certification",
            "Safety",
            "2026-06-03",
            "Completed the provider's infection-control certification program.",
            "Earned the provider-issued infection-control certificate.",
            "certificate",
            "Infection Control Certificate",
            "CERT-IC-2026",
            [],
            ["organization-issued", "evidence-linked"],
        ),
    ]

    for title, category, entry_date, contribution, result, evidence_type, evidence_title, reference, confirmations, trust_signals in cases:
        entry = entries.insert_one(
            {
                "user_id": str(user["_id"]),
                "title": title,
                "category": category,
                "entry_type": "Current Job",
                "entry_date": entry_date,
                "tags": ["Client Safety", "Professional Standards"],
                "impact": result,
                "created_at": datetime.now(timezone.utc),
            }
        )
        receipts.insert_one(
            {
                "user_id": str(user["_id"]),
                "source_entry_id": str(entry.inserted_id),
                "accomplishment": title,
                "contribution": contribution,
                "result": result,
                "evidence": [
                    {
                        "title": evidence_title,
                        "evidence_type": evidence_type,
                        "reference": reference,
                        "description": "Credential-supporting record for the current review period.",
                        "is_public": False,
                    }
                ],
                "skills": ["Client Safety", "Professional Standards"],
                "credit": [],
                "confirmations": confirmations,
                "trust_signals": trust_signals,
                "is_public": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        )


def test_free_user_cannot_build_certification_packet(certification_context):
    user = {
        "_id": ObjectId(),
        "name": "Free Member",
        "email": "free@example.com",
        "plan": "free",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user

    response = client.get("/packets/certification")

    assert response.status_code == 403
    assert response.json()["detail"]["feature"] == "certification_packet"


def test_certification_packet_distinguishes_evidence_statuses(certification_context):
    entries, receipts = certification_context
    user = {
        "_id": ObjectId(),
        "name": "Avery Brooks",
        "email": "avery@example.com",
        "headline": "Licensed Cosmetologist",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user
    _seed_cosmetology_case(entries, receipts, user)

    response = client.get(
        "/packets/certification",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "career_area": "Beauty / Cosmetology",
            "role_title": "Licensed Cosmetologist",
            "organization": "Independent Studio",
            "credential_name": "Cosmetology License Renewal",
            "issuing_body": "State Licensing Board",
            "review_type": "License Renewal",
            "requirement_notes": "Document continuing education, sanitation training, and current credential evidence.",
        },
    )

    assert response.status_code == 200
    packet = response.json()["packet"]
    assert packet["kind"] == "certification"
    assert packet["credential_review"]["credential_name"] == "Cosmetology License Renewal"
    assert packet["credential_review"]["issuing_body"] == "State Licensing Board"
    assert packet["credential_evidence_summary"] == {
        "credential_items": 3,
        "supporting_items": 3,
        "self_added": 1,
        "confirmed": 1,
        "organization_issued": 1,
    }
    statuses = {item["evidence_status"] for item in packet["credential_evidence"]}
    assert statuses == {"Self-added", "Confirmed", "Organization-issued"}
    assert all(item["is_credential_evidence"] for item in packet["credential_evidence"])
    assert "self-added evidence is not presented as independently verified" in packet["review_summary"].lower()
    assert len(packet["competency_records"]) >= 1
    assert len(packet["experience_records"]) == 3


def test_pro_user_downloads_certification_pdf(certification_context):
    entries, receipts = certification_context
    user = {
        "_id": ObjectId(),
        "name": "Avery Brooks",
        "email": "avery@example.com",
        "headline": "Licensed Cosmetologist",
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user
    _seed_cosmetology_case(entries, receipts, user)

    response = client.get(
        "/packets/certification.pdf",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "credential_name": "Cosmetology License Renewal",
            "issuing_body": "State Licensing Board",
            "review_type": "License Renewal",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 5000
    assert "Avery-Brooks-Cosmetology-License-Renewal-2026-01-01-to-2026-06-30.pdf" in response.headers["content-disposition"]
