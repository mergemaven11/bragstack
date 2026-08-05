from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class BragEntryCreate(BaseModel):
    """Request model for creating a brag entry."""

    title: str = Field(..., examples=["Debugged Docker networking issue"])
    category: str = Field(..., examples=["Docker"])
    entry_date: str = Field(..., examples=["2026-05-27"])
    entry_type: str = Field(..., examples=["Current Job"])
    situation: str = Field(..., examples=["Customer container could not connect to MongoDB."])
    action: str = Field(..., examples=["Checked logs, inspected networks, and verified Compose service names."])
    impact: str = Field(..., examples=["Found incorrect hostname and restored connectivity."])
    lesson: Optional[str] = Field(None, examples=["Docker Compose DNS uses service names."])
    tags: list[str] = Field(default_factory=list, examples=[["Docker", "Networking", "Compose"]])
    is_public: bool = Field(default=False, examples=[True])


class BragEntryResponse(BaseModel):
    """Response model for a brag entry."""

    id: str
    title: str
    category: str
    entry_date: str
    entry_type: str
    situation: str
    action: str
    impact: str
    lesson: Optional[str]
    tags: list[str]
    is_public: bool = False
    resume_bullet: str
    created_at: datetime


class BragEntryCreate(BaseModel):
    """Request model for creating a brag entry."""

    title: str = Field(
        ...,
        examples=["Debugged Docker networking issue"],
    )
    category: str = Field(
        ...,
        examples=["Docker"],
    )
    entry_date: str = Field(
        ...,
        examples=["2026-05-27"],
    )
    entry_type: str = Field(
        ...,
        examples=["Current Job"],
    )
    situation: str = Field(
        ...,
        examples=[
            "Customer container could not connect to MongoDB."
        ],
    )
    action: str = Field(
        ...,
        examples=[
            "Checked logs, inspected networks, and verified "
            "Compose service names."
        ],
    )
    impact: str = Field(
        ...,
        examples=[
            "Found the incorrect hostname and restored connectivity."
        ],
    )
    lesson: Optional[str] = Field(
        None,
        examples=["Docker Compose DNS uses service names."],
    )
    tags: list[str] = Field(
        default_factory=list,
        examples=[["Docker", "Networking", "Compose"]],
    )
    is_public: bool = Field(
        default=False,
        examples=[True],
    )


class BragEntryResponse(BaseModel):
    """Response model for a brag entry."""

    id: str
    title: str
    category: str
    entry_date: str
    entry_type: str
    situation: str
    action: str
    impact: str
    lesson: Optional[str]
    tags: list[str]
    is_public: bool = False
    resume_bullet: str
    created_at: datetime


EvidenceType = Literal[
    "support-incident",
    "pull-request",
    "ticket",
    "documentation",
    "customer-feedback",
    "project-link",
    "attachment",
    "other",
]

ConfirmationType = Literal[
    "collaborator",
    "stakeholder",
    "organization",
]

ConfirmationStatus = Literal[
    "pending",
    "confirmed",
    "declined",
    "revoked",
]

TrustSignal = Literal[
    "self-documented",
    "evidence-linked",
    "collaborator-confirmed",
    "stakeholder-verified",
    "organization-issued",
]


class ImpactEvidence(BaseModel):
    """One piece of evidence supporting an Impact Receipt."""

    evidence_type: EvidenceType = "other"

    title: str = Field(
        ...,
        min_length=1,
        max_length=120,
        examples=["Docker DNS incident INC-1042"],
    )

    reference: Optional[str] = Field(
        default=None,
        max_length=500,
        examples=["INC-1042"],
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        examples=[
            "Incident showing the original failure and resolution."
        ],
    )

    is_public: bool = Field(
        default=False,
        description=(
            "Evidence is private unless the owner explicitly "
            "makes it public."
        ),
    )


class ImpactCredit(BaseModel):
    """Credit for another person who contributed to the outcome."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["Jordan"],
    )

    contribution: str = Field(
        ...,
        min_length=1,
        max_length=300,
        examples=["Tested the networking fix before deployment."],
    )


class ImpactConfirmation(BaseModel):
    """Confirmation from a collaborator or stakeholder."""

    name: str
    role: Optional[str] = None
    confirmation_type: ConfirmationType
    status: ConfirmationStatus = "pending"
    requested_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None


class ImpactReceiptFromEntryCreate(BaseModel):
    """Request used to turn an existing brag entry into a receipt."""

    contribution: Optional[str] = Field(
        default=None,
        max_length=2000,
        description=(
            "The owner's specific contribution. Defaults to the "
            "source entry action."
        ),
    )

    result: Optional[str] = Field(
        default=None,
        max_length=2000,
        description=(
            "What changed because of the work. Defaults to the "
            "source entry impact."
        ),
    )

    evidence: list[ImpactEvidence] = Field(
        default_factory=list,
    )

    skills: list[str] = Field(
        default_factory=list,
        description=(
            "Skills demonstrated by this specific accomplishment."
        ),
    )

    credit: list[ImpactCredit] = Field(
        default_factory=list,
        description=(
            "Other contributors and the work they performed."
        ),
    )

    is_public: bool = False


class ImpactReceiptUpdate(BaseModel):
    """Owner-editable Impact Receipt fields."""

    accomplishment: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=300,
    )

    contribution: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=2000,
    )

    result: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=2000,
    )

    evidence: Optional[list[ImpactEvidence]] = None
    skills: Optional[list[str]] = None
    credit: Optional[list[ImpactCredit]] = None
    is_public: Optional[bool] = None


class ImpactReceiptResponse(BaseModel):
    """Complete Impact Receipt returned by the API."""

    id: str
    source_entry_id: str

    accomplishment: str
    contribution: str
    result: str

    evidence: list[ImpactEvidence]
    skills: list[str]
    credit: list[ImpactCredit]

    confirmations: list[ImpactConfirmation]
    trust_signals: list[TrustSignal]

    is_public: bool = False
    schema_version: int = 1

    created_at: datetime
    updated_at: datetime