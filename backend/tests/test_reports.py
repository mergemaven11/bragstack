from datetime import datetime, timedelta, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.reports_routes as reports_routes
from app.main import app


client = TestClient(app)


@pytest.fixture
def report_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_reports_test"]

    entries = mock_db["entries"]
    receipts = mock_db["impact_receipts"]
    user = {
        "_id": ObjectId(),
        "name": "Report User",
        "email": "report@example.com",
    }

    monkeypatch.setattr(reports_routes, "entries_collection", entries)
    monkeypatch.setattr(reports_routes, "impact_receipts_collection", receipts)
    app.dependency_overrides[reports_routes.get_current_user] = lambda: user

    yield user, entries, receipts

    app.dependency_overrides.clear()


def test_weekly_report_uses_entry_date_and_combines_receipts(report_context):
    user, entries, receipts = report_context
    today = datetime.now(timezone.utc).date()
    recent_date = (today - timedelta(days=2)).isoformat()
    old_date = (today - timedelta(days=20)).isoformat()

    recent = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Recent production recovery",
            "category": "Operations",
            "entry_type": "Current Job",
            "entry_date": recent_date,
            "tags": ["Docker", "Troubleshooting"],
            "impact": "Reduced repeat incidents by 35%.",
            "resume_bullet": "Resolved a recurring production incident.",
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
        }
    )

    entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Older work",
            "category": "Learning",
            "entry_type": "Personal Development",
            "entry_date": old_date,
            "tags": ["Python"],
            "impact": "Completed a course.",
            "resume_bullet": "Completed advanced Python training.",
            "is_public": False,
            "created_at": datetime.now(timezone.utc),
        }
    )

    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(recent.inserted_id),
            "accomplishment": "Recent production recovery",
            "contribution": "Diagnosed the failure.",
            "result": "Reduced repeat incidents by 35%.",
            "evidence": [
                {
                    "title": "INC-42",
                    "evidence_type": "support-incident",
                    "is_public": False,
                }
            ],
            "skills": ["Docker", "Incident Leadership"],
            "credit": [],
            "confirmations": [
                {
                    "name": "Manager",
                    "confirmation_type": "stakeholder",
                    "status": "confirmed",
                }
            ],
            "trust_signals": ["self-documented", "stakeholder-verified"],
            "is_public": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    response = client.get("/reports/weekly")

    assert response.status_code == 200
    data = response.json()

    assert data["period"]["key"] == "weekly"
    assert data["period"]["date_basis"] == "entry_date"
    assert data["totals"]["entries"] == 1
    assert data["totals"]["impact_receipts"] == 1
    assert data["totals"]["evidence_items"] == 1
    assert data["totals"]["confirmed_assertions"] == 1
    assert data["totals"]["quantified_results"] == 1
    assert data["categories"] == {"Operations": 1}
    assert data["top_skills"] == {"Docker": 1, "Incident Leadership": 1}
    assert len(data["highlights"]) == 1


def test_all_time_report_includes_all_owned_entries(report_context):
    user, entries, _ = report_context

    entries.insert_many(
        [
            {
                "user_id": str(user["_id"]),
                "title": "One",
                "category": "Engineering",
                "entry_type": "Current Job",
                "entry_date": "2026-01-01",
                "tags": ["Python"],
                "impact": "Shipped one improvement.",
                "resume_bullet": "Shipped one improvement.",
            },
            {
                "user_id": str(user["_id"]),
                "title": "Two",
                "category": "Engineering",
                "entry_type": "Side Project",
                "entry_date": "2026-07-01",
                "tags": ["React"],
                "impact": "Shipped another improvement.",
                "resume_bullet": "Shipped another improvement.",
            },
            {
                "user_id": str(ObjectId()),
                "title": "Other user's work",
                "category": "Other",
                "entry_type": "Current Job",
                "entry_date": "2026-07-01",
                "tags": ["Secret"],
                "impact": "Should not appear.",
                "resume_bullet": "Should not appear.",
            },
        ]
    )

    response = client.get("/reports/all-time")

    assert response.status_code == 200
    data = response.json()

    assert data["period"]["key"] == "all-time"
    assert data["totals"]["entries"] == 2
    assert data["categories"] == {"Engineering": 2}


def test_custom_report_validates_dates_and_filters_period(report_context):
    user, entries, _ = report_context

    entries.insert_many(
        [
            {
                "user_id": str(user["_id"]),
                "title": "June work",
                "category": "Support",
                "entry_type": "Current Job",
                "entry_date": "2026-06-15",
                "tags": [],
                "impact": "Helped a customer.",
                "resume_bullet": "Helped a customer.",
            },
            {
                "user_id": str(user["_id"]),
                "title": "July work",
                "category": "Support",
                "entry_type": "Current Job",
                "entry_date": "2026-07-15",
                "tags": [],
                "impact": "Helped another customer.",
                "resume_bullet": "Helped another customer.",
            },
        ]
    )

    response = client.get(
        "/reports/custom?start_date=2026-07-01&end_date=2026-07-31"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["totals"]["entries"] == 1
    assert data["highlights"][0]["title"] == "July work"

    invalid = client.get(
        "/reports/custom?start_date=2026-08-01&end_date=2026-07-01"
    )
    assert invalid.status_code == 422


def test_performance_packet_requires_pro_entitlement(report_context):
    user, _, _ = report_context
    user["plan"] = "free"

    response = client.get("/reports/performance-packet")

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["code"] == "paid_feature_required"
    assert detail["feature"] == "performance_review_builder"


def test_performance_packet_builds_transparent_scorecard(report_context):
    user, entries, receipts = report_context
    user["plan"] = "pro"
    user["headline"] = "Community Programs Coordinator"

    first = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Expanded workshop access",
            "category": "Community Impact",
            "entry_type": "Current Job",
            "entry_date": "2026-07-10",
            "tags": ["Facilitation", "Program Planning"],
            "impact": "Increased monthly attendance by 40%.",
            "resume_bullet": "Expanded access to recurring community workshops.",
        }
    )
    second = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": "Improved volunteer onboarding",
            "category": "Operations",
            "entry_type": "Current Job",
            "entry_date": "2026-07-18",
            "tags": ["Training"],
            "impact": "Standardized onboarding materials.",
            "resume_bullet": "Standardized volunteer onboarding.",
        }
    )

    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(first.inserted_id),
            "accomplishment": "Expanded workshop access",
            "contribution": "Redesigned scheduling and outreach.",
            "result": "Increased monthly attendance by 40%.",
            "evidence": [
                {"title": "Attendance report", "is_public": False},
                {"title": "Program calendar", "is_public": False},
            ],
            "skills": ["Facilitation", "Program Planning"],
            "confirmations": [
                {
                    "name": "Program Director",
                    "confirmation_type": "supervisor",
                    "status": "confirmed",
                }
            ],
            "trust_signals": ["supervisor-verified"],
        }
    )
    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(second.inserted_id),
            "accomplishment": "Improved volunteer onboarding",
            "contribution": "Created a repeatable onboarding guide.",
            "result": "Standardized onboarding materials.",
            "evidence": [],
            "skills": ["Training"],
            "confirmations": [],
            "trust_signals": [],
        }
    )

    response = client.get(
        "/reports/performance-packet?start_date=2026-07-01&end_date=2026-07-31"
    )

    assert response.status_code == 200
    packet = response.json()["packet"]
    scorecard = packet["scorecard"]

    assert packet["subject"]["role"] == "Community Programs Coordinator"
    assert packet["period"]["start_date"] == "2026-07-01"
    assert scorecard["accomplishments"] == 2
    assert scorecard["impact_receipts"] == 2
    assert scorecard["evidence_items"] == 2
    assert scorecard["receipt_coverage_percent"] == 100
    assert scorecard["quantified_result_coverage_percent"] == 50
    assert scorecard["verification_coverage_percent"] == 50
    assert scorecard["evidence_coverage_percent"] == 50
    assert scorecard["evidence_depth"] == 1.0
    assert packet["signature_accomplishments"][0]["title"] == "Expanded workshop access"
