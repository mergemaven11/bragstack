import pytest

from app.packet_platform import normalize_recognition, recognition_label


@pytest.mark.parametrize(
    ("career_context", "confirmation", "expected"),
    [
        (
            "Creative / independent professional",
            {"name": "Studio Client", "role": "Client", "confirmation_type": "client", "status": "confirmed"},
            "Client confirmed",
        ),
        (
            "Education / supervised practice",
            {"name": "Faculty Mentor", "role": "Instructor", "confirmation_type": "instructor", "status": "confirmed"},
            "Instructor confirmed",
        ),
        (
            "Skilled trades / crew collaboration",
            {"name": "Crew Partner", "role": "Journeyperson", "confirmation_type": "peer", "status": "confirmed"},
            "Peer recognized",
        ),
        (
            "Customer service",
            {"name": "Customer Feedback", "role": "Customer", "confirmation_type": "customer", "status": "confirmed"},
            "Customer feedback attached",
        ),
    ],
)
def test_verified_recognition_labels_are_career_neutral(career_context, confirmation, expected):
    recognition = normalize_recognition([confirmation], [])
    assert career_context
    assert recognition[0]["label"] == expected
    assert recognition[0]["status"] == "confirmed"


def test_legacy_manager_and_stakeholder_types_remain_backward_compatible():
    assert recognition_label("manager", "Manager") == "Supervisor confirmed"
    assert recognition_label("stakeholder", "Program Director") == "Stakeholder confirmed"


def test_pending_confirmation_never_becomes_verified_recognition():
    recognition = normalize_recognition(
        [{"name": "Peer", "role": "Colleague", "confirmation_type": "peer", "status": "pending"}],
        [],
    )
    assert recognition == []


def test_organization_issued_trust_signal_is_recognition_without_inventing_a_person():
    recognition = normalize_recognition([], ["organization-issued"])
    assert recognition == [
        {
            "label": "Organization-issued",
            "name": "",
            "role": "",
            "source_type": "trust-signal",
            "status": "confirmed",
        }
    ]
