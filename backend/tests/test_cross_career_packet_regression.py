from datetime import datetime, timezone

import mongomock
import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

import app.performance_packet_routes as packet_routes
from app.main import app


client = TestClient(app)


CAREER_CASES = [
    {
        "id": "healthcare",
        "career_area": "Healthcare",
        "role": "Medical Assistant",
        "organization": "Community Health Clinic",
        "title": "Improved patient intake flow",
        "category": "Patient Experience",
        "result": "Reduced patient check-in delays by 18% across 240 visits.",
        "skills": ["Patient Communication", "Care Coordination", "Process Improvement"],
        "evidence": [],
        "confirmations": [],
        "expected_metric": "18%",
    },
    {
        "id": "education",
        "career_area": "Education",
        "role": "Elementary Teacher",
        "organization": "Riverside Elementary",
        "title": "Raised reading proficiency",
        "category": "Student Outcomes",
        "result": "Raised reading proficiency to 86% for 28 students by the spring benchmark.",
        "skills": ["Instruction", "Student Engagement", "Assessment"],
        "evidence": [
            {
                "title": "Spring reading benchmark summary",
                "evidence_type": "documentation",
                "reference": "READING-SPRING-2026",
                "description": "Class-level benchmark comparison.",
                "is_public": False,
            }
        ],
        "confirmations": [],
        "expected_metric": "86%",
    },
    {
        "id": "skilled-trades",
        "career_area": "Skilled Trades",
        "role": "Automotive Technician",
        "organization": "Northside Auto Service",
        "title": "Improved diagnostic turnaround",
        "category": "Quality & Service",
        "result": "Cut average diagnostic turnaround by 2.5 hours across 36 service calls.",
        "skills": ["Diagnostics", "Customer Service", "Quality Control"],
        "evidence": [
            {
                "title": "Service turnaround log",
                "evidence_type": "metric",
                "reference": "Q2-SERVICE-LOG",
                "description": "Before-and-after service timing summary.",
                "is_public": False,
            }
        ],
        "confirmations": [
            {
                "name": "Shop Manager",
                "role": "Service Manager",
                "confirmation_type": "supervisor",
                "status": "confirmed",
            }
        ],
        "expected_metric": "2.5 hours",
    },
    {
        "id": "sales",
        "career_area": "Sales",
        "role": "Customer Success Manager",
        "organization": "Regional Services Group",
        "title": "Protected at-risk renewals",
        "category": "Customer Retention",
        "result": "Renewed $185,000 in annual contracts and retained 94% of at-risk accounts.",
        "skills": ["Relationship Management", "Negotiation", "Customer Success"],
        "evidence": [
            {
                "title": "Renewal portfolio summary",
                "evidence_type": "metric",
                "reference": "FY26-RENEWALS",
                "description": "Annual renewal value and retention summary.",
                "is_public": False,
            }
        ],
        "confirmations": [
            {
                "name": "Regional Director",
                "role": "Customer Success Director",
                "confirmation_type": "stakeholder",
                "status": "confirmed",
            }
        ],
        "expected_metric": "$185,000",
    },
    {
        "id": "operations",
        "career_area": "Operations",
        "role": "Warehouse Lead",
        "organization": "Metro Fulfillment Center",
        "title": "Reduced damaged shipments",
        "category": "Quality",
        "result": "Reduced damaged shipments by 31% across 12,400 orders while maintaining daily throughput.",
        "skills": ["Quality Control", "Team Leadership", "Operations"],
        "evidence": [
            {
                "title": "Damage-rate dashboard export",
                "evidence_type": "metric",
                "reference": "OPS-Q2-DAMAGE",
                "description": "Shipment quality trend for the review period.",
                "is_public": False,
            }
        ],
        "confirmations": [
            {
                "name": "Operations Manager",
                "role": "Operations Manager",
                "confirmation_type": "supervisor",
                "status": "confirmed",
            }
        ],
        "expected_metric": "31%",
    },
    {
        "id": "creative",
        "career_area": "Creative",
        "role": "Independent Brand Designer",
        "organization": "Independent Practice",
        "title": "Expanded repeat client work",
        "category": "Client Impact",
        "result": "Delivered 14 client campaigns and increased repeat bookings by 22%.",
        "skills": ["Brand Design", "Client Communication", "Creative Direction"],
        "evidence": [
            {
                "title": "Project delivery tracker",
                "evidence_type": "project-artifact",
                "reference": "2026-CLIENT-TRACKER",
                "description": "Completed client engagements for the period.",
                "is_public": False,
            }
        ],
        "confirmations": [],
        "expected_metric": "22%",
    },
    {
        "id": "technology",
        "career_area": "Technology",
        "role": "Platform Engineer",
        "organization": "Cloud Services Team",
        "title": "Reduced deployment rollback impact",
        "category": "Reliability",
        "result": "Reduced deployment rollback rate from 8% to 3% and saved 6 hours per incident.",
        "skills": ["Reliability", "Automation", "Incident Response"],
        "evidence": [
            {
                "title": "Release reliability report",
                "evidence_type": "documentation",
                "reference": "REL-2026-Q2",
                "description": "Release and rollback trend report.",
                "is_public": False,
            }
        ],
        "confirmations": [
            {
                "name": "Engineering Manager",
                "role": "Engineering Manager",
                "confirmation_type": "supervisor",
                "status": "confirmed",
            }
        ],
        "expected_metric": "8%",
    },
]


@pytest.fixture
def cross_career_context(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["bragstack_cross_career_packet_test"]
    entries = mock_db["entries"]
    receipts = mock_db["impact_receipts"]

    monkeypatch.setattr(packet_routes, "entries_collection", entries)
    monkeypatch.setattr(packet_routes, "impact_receipts_collection", receipts)

    yield entries, receipts
    app.dependency_overrides.clear()


def _seed_case(entries, receipts, user, case):
    entry = entries.insert_one(
        {
            "user_id": str(user["_id"]),
            "title": case["title"],
            "category": case["category"],
            "entry_type": "Current Job",
            "entry_date": "2026-06-15",
            "tags": case["skills"],
            "impact": case["result"],
            "resume_bullet": case["result"],
            "created_at": datetime.now(timezone.utc),
        }
    )

    receipts.insert_one(
        {
            "user_id": str(user["_id"]),
            "source_entry_id": str(entry.inserted_id),
            "accomplishment": case["title"],
            "contribution": f"Led the documented work that produced this {case['category'].lower()} outcome.",
            "result": case["result"],
            "evidence": case["evidence"],
            "skills": case["skills"],
            "credit": [],
            "confirmations": case["confirmations"],
            "trust_signals": ["self-documented"]
            + (["evidence-linked"] if case["evidence"] else [])
            + (["stakeholder-verified"] if case["confirmations"] else []),
            "is_public": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )


@pytest.mark.parametrize("case", CAREER_CASES, ids=[case["id"] for case in CAREER_CASES])
def test_performance_packet_and_pdf_work_across_careers(cross_career_context, case):
    entries, receipts = cross_career_context
    user = {
        "_id": ObjectId(),
        "name": f"Regression {case['id'].title()}",
        "email": f"{case['id']}@example.com",
        "headline": case["role"],
        "plan": "pro",
    }
    app.dependency_overrides[packet_routes.get_current_user] = lambda: user
    _seed_case(entries, receipts, user, case)

    params = {
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "career_area": case["career_area"],
        "role_title": case["role"],
        "organization": case["organization"],
        "confidential": "true",
    }

    response = client.get("/packets/performance-review", params=params)
    assert response.status_code == 200

    packet = response.json()["packet"]
    assert packet["context"]["career_area"] == case["career_area"]
    assert packet["subject"]["role"] == case["role"]
    assert packet["context"]["organization"] == case["organization"]
    assert packet["scorecard"]["accomplishments"] == 1
    assert packet["scorecard"]["impact_receipts"] == 1
    assert packet["signature_accomplishments"][0]["title"] == case["title"]
    assert packet["measurable_results"][0]["metric_display"] == case["expected_metric"]
    assert packet["receipt_records"][0]["skills"] == case["skills"]

    if case["evidence"]:
        assert packet["scorecard"]["evidence_items"] == len(case["evidence"])
        assert packet["scorecard"]["evidence_coverage_percent"] == 100
    else:
        assert packet["scorecard"]["evidence_items"] == 0
        assert packet["scorecard"]["evidence_coverage_percent"] == 0
        assert packet["evidence_index"] == []

    if case["confirmations"]:
        assert packet["scorecard"]["verification_coverage_percent"] == 100
    else:
        assert packet["scorecard"]["verification_coverage_percent"] == 0

    # The universal packet contract should stay profession-neutral.
    serialized = response.text.lower()
    for profession_specific_key in (
        "pull_requests_completed",
        "patients_seen",
        "students_taught",
        "units_repaired",
        "deals_closed",
    ):
        assert profession_specific_key not in serialized

    pdf_response = client.get("/packets/performance-review.pdf", params=params)
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"].startswith("application/pdf")
    assert pdf_response.content.startswith(b"%PDF")
    assert len(pdf_response.content) > 5000


def test_cross_career_fixture_set_covers_required_result_shapes():
    combined_results = " ".join(case["result"] for case in CAREER_CASES)

    assert "%" in combined_results
    assert "$" in combined_results
    assert "hours" in combined_results
    assert "students" in combined_results or "visits" in combined_results
    assert "orders" in combined_results or "service calls" in combined_results
    assert any(term in combined_results.lower() for term in ("quality", "damaged", "proficiency"))
