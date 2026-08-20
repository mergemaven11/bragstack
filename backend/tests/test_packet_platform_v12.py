from __future__ import annotations

from datetime import datetime, timedelta, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.certification_packet_routes as certification_routes
import app.interview_packet_routes as interview_routes
import app.packet_audit as packet_audit
import app.packet_audit_routes as packet_audit_routes
import app.packet_platform_routes as platform_routes
import app.packet_share_routes as share_routes
import app.performance_packet_routes as performance_routes
from app.main import app


client = TestClient(app)


@pytest.fixture
def platform_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    db = mock_client["bragstack_packet_platform_test"]
    entries = db["entries"]
    receipts = db["impact_receipts"]
    users = db["users"]
    audits = db["packet_export_audit"]
    shares = db["packet_shares"]

    monkeypatch.setattr(performance_routes, "entries_collection", entries)
    monkeypatch.setattr(performance_routes, "impact_receipts_collection", receipts)
    monkeypatch.setattr(platform_routes, "impact_receipts_collection", receipts)
    monkeypatch.setattr(interview_routes, "impact_receipts_collection", receipts)
    monkeypatch.setattr(share_routes, "packet_shares_collection", shares)
    monkeypatch.setattr(share_routes, "users_collection", users)
    monkeypatch.setattr(packet_audit, "packet_export_audit_collection", audits)
    monkeypatch.setattr(packet_audit_routes, "packet_export_audit_collection", audits)

    user = {
        "_id": ObjectId(),
        "name": "Morgan Lee",
        "email": "morgan@example.com",
        "headline": "Community Operations Lead",
        "location": "Atlanta, Georgia",
        "plan": "pro",
    }
    users.insert_one(dict(user))
    app.dependency_overrides[performance_routes.get_current_user] = lambda: user
    app.dependency_overrides[platform_routes.get_current_user] = lambda: user
    app.dependency_overrides[share_routes.get_current_user] = lambda: user

    yield {
        "entries": entries,
        "receipts": receipts,
        "users": users,
        "audits": audits,
        "shares": shares,
        "user": user,
    }

    app.dependency_overrides.clear()


def _seed_three_careers(context):
    entries = context["entries"]
    receipts = context["receipts"]
    user = context["user"]
    user_id = str(user["_id"])

    fixtures = [
        {
            "title": "Reduced client intake wait time",
            "category": "Operations",
            "date": "2026-02-10",
            "result": "Reduced average intake wait time by 22 minutes.",
            "skills": ["Scheduling", "Process Improvement"],
            "confirmation": {"name": "Avery", "role": "Program Client", "confirmation_type": "client", "status": "confirmed"},
            "evidence": [{"title": "Intake timing report", "evidence_type": "documentation", "reference": "PRIVATE-INTAKE-22", "description": "Before and after timing", "is_public": False}],
        },
        {
            "title": "Built peer onboarding guide",
            "category": "Training",
            "date": "2026-03-15",
            "result": "Prepared 14 new team members across 3 shifts.",
            "skills": ["Training", "Communication"],
            "confirmation": {"name": "Sam", "role": "Peer Lead", "confirmation_type": "peer", "status": "confirmed"},
            "evidence": [{"title": "Onboarding guide", "evidence_type": "documentation", "reference": "GUIDE-14", "description": "Training artifact", "is_public": False}],
        },
        {
            "title": "Improved customer follow-up quality",
            "category": "Service",
            "date": "2026-04-20",
            "result": "Raised follow-up completion to 96%.",
            "skills": ["Customer Service", "Quality"],
            "confirmation": {"name": "Customer survey", "role": "Feedback", "confirmation_type": "customer", "status": "confirmed"},
            "evidence": [{"title": "Customer feedback summary", "evidence_type": "customer-feedback", "reference": "FEEDBACK-96", "description": "Customer response summary", "is_public": False}],
        },
    ]

    ids = []
    for fixture in fixtures:
        inserted = entries.insert_one(
            {
                "user_id": user_id,
                "title": fixture["title"],
                "category": fixture["category"],
                "entry_type": "Current Job",
                "entry_date": fixture["date"],
                "tags": fixture["skills"],
                "impact": fixture["result"],
                "resume_bullet": fixture["title"],
                "created_at": datetime.now(timezone.utc),
            }
        )
        entry_id = str(inserted.inserted_id)
        ids.append(entry_id)
        receipts.insert_one(
            {
                "user_id": user_id,
                "source_entry_id": entry_id,
                "accomplishment": fixture["title"],
                "contribution": f"Owned the work behind {fixture['title'].lower()}.",
                "result": fixture["result"],
                "evidence": fixture["evidence"],
                "skills": fixture["skills"],
                "credit": [],
                "confirmations": [fixture["confirmation"]],
                "trust_signals": ["self-documented", "evidence-linked"],
                "is_public": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        )
    return ids


def test_v12_pinning_sections_notes_branding_and_recognition(platform_context):
    ids = _seed_three_careers(platform_context)

    response = client.get(
        "/packets/performance-review-v12",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "career_area": "Operations",
            "organization": "Neighborhood Services",
            "signature_entry_ids": f"{ids[2]},{ids[0]}",
            "sections": "signature-accomplishments,contribution-recognition,review-summary",
            "packet_note": "Scope changed mid-cycle; prioritize service quality and sustainable operations.",
            "item_notes": '{"%s":"Use this example to discuss customer trust."}' % ids[2],
            "include_notes": "true",
            "theme": "modern-minimal",
            "brand_name": "Neighborhood Services",
            "department_label": "Community Operations",
            "reviewer_name": "Annual Review Committee",
            "review_cycle_label": "2026 Midyear Review",
        },
    )

    assert response.status_code == 200
    packet = response.json()["packet"]
    assert packet["scorecard"]["accomplishments"] == 3
    assert [item["entry_id"] for item in packet["signature_accomplishments"]] == [ids[2], ids[0]]
    assert packet["render_config"]["sections"] == [
        "signature-accomplishments",
        "contribution-recognition",
        "review-summary",
    ]
    assert packet["render_config"]["theme"] == "modern-minimal"
    assert packet["annotations"]["packet_note"].startswith("Scope changed")
    assert packet["annotations"]["item_notes"][ids[2]].startswith("Use this example")
    assert packet["branding"]["brand_name"] == "Neighborhood Services"
    assert packet["branding"]["reviewer_name"] == "Annual Review Committee"

    labels = {
        recognition["label"]
        for record in packet["receipt_records"]
        for recognition in record.get("recognition", [])
    }
    assert {"Client confirmed", "Peer recognized", "Customer feedback attached"} <= labels


def test_explicit_empty_sections_make_two_page_packet_and_audit_metadata(platform_context):
    _seed_three_careers(platform_context)

    for theme in ["classic-dossier", "modern-minimal", "executive-report"]:
        response = client.get(
            "/packets/performance-review-v12.pdf",
            params={"sections": "__none__", "theme": theme},
        )
        assert response.status_code == 200
        assert response.content.startswith(b"%PDF")

    audits = list(platform_context["audits"].find({}))
    assert len(audits) == 3
    assert {item["theme"] for item in audits} == {
        "classic-dossier",
        "modern-minimal",
        "executive-report",
    }
    for item in audits:
        assert item["page_count"] == 2
        assert item["packet_kind"] == "performance-review"
        assert "pdf" not in item
        assert "packet" not in item
        assert "evidence" not in item
        assert "body" not in item

    history = client.get("/packets/export-history")
    assert history.status_code == 200
    assert len(history.json()["exports"]) == 3


def test_private_share_access_code_evidence_controls_revocation_and_expiry(platform_context):
    ids = _seed_three_careers(platform_context)
    future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    created = client.post(
        "/packets/shares",
        json={
            "career_area": "Operations",
            "signature_entry_ids": [ids[0]],
            "sections": ["signature-accomplishments"],
            "packet_note": "Private internal note that must not leak.",
            "include_notes": False,
            "expires_at": future,
            "access_code": "2468-secure",
            "allow_download": False,
            "include_evidence": False,
        },
    )
    assert created.status_code == 200
    share = created.json()["share"]
    token = share["token"]
    stored = platform_context["shares"].find_one({"_id": ObjectId(share["id"])})
    assert stored is not None
    assert "token" not in stored
    assert stored["token_hash"] != token
    assert stored["access_code_hash"] != "2468-secure"
    assert stored["include_evidence"] is False
    assert stored["include_notes"] is False

    assert client.get(f"/shared/packets/{token}").status_code == 401
    view = client.get(f"/shared/packets/{token}", params={"code": "2468-secure"})
    assert view.status_code == 200
    assert "PRIVATE-INTAKE-22" not in view.text
    assert "Private internal note" not in view.text
    assert view.headers["cache-control"] == "private, no-store"
    assert "noindex" in view.headers["x-robots-tag"]

    blocked_download = client.get(
        f"/shared/packets/{token}/download.pdf",
        params={"code": "2468-secure"},
    )
    assert blocked_download.status_code == 403

    revoked = client.delete(f"/packets/shares/{share['id']}")
    assert revoked.status_code == 200
    assert client.get(f"/shared/packets/{token}", params={"code": "2468-secure"}).status_code == 404

    expiring = client.post(
        "/packets/shares",
        json={
            "signature_entry_ids": [ids[1]],
            "sections": [],
            "expires_at": future,
        },
    )
    assert expiring.status_code == 200
    expiring_share = expiring.json()["share"]
    platform_context["shares"].update_one(
        {"_id": ObjectId(expiring_share["id"])},
        {"$set": {"expires_at": datetime.now(timezone.utc) - timedelta(seconds=1)}},
    )
    assert client.get(f"/shared/packets/{expiring_share['token']}").status_code == 404


def test_private_share_can_explicitly_enable_pdf_and_audits_shared_export(platform_context):
    ids = _seed_three_careers(platform_context)
    created = client.post(
        "/packets/shares",
        json={
            "signature_entry_ids": [ids[0]],
            "sections": [],
            "allow_download": True,
            "include_evidence": False,
            "include_notes": False,
        },
    )
    assert created.status_code == 200
    token = created.json()["share"]["token"]
    pdf = client.get(f"/shared/packets/{token}/download.pdf")
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")
    audit = platform_context["audits"].find_one({"packet_kind": "shared-performance-review"})
    assert audit is not None
    assert audit["page_count"] == 2


def test_verified_recognition_is_exposed_in_interview_and_certification_packets(platform_context):
    ids = _seed_three_careers(platform_context)
    user = platform_context["user"]
    app.dependency_overrides[interview_routes.get_current_user] = lambda: user
    app.dependency_overrides[certification_routes.get_current_user] = lambda: user

    interview = client.get(
        "/packets/interview",
        params={"selected_entry_ids": ",".join(ids)},
    )
    assert interview.status_code == 200
    interview_labels = {
        recognition["label"]
        for story in interview.json()["packet"]["interview_stories"]
        for recognition in story.get("recognition", [])
    }
    assert {"Client confirmed", "Peer recognized", "Customer feedback attached"} <= interview_labels

    certification = client.get(
        "/packets/certification",
        params={"credential_name": "Community Service Quality Credential"},
    )
    assert certification.status_code == 200
    certification_labels = set(certification.json()["packet"]["verified_recognition"])
    assert {"Client confirmed", "Peer recognized", "Customer feedback attached"} <= certification_labels
