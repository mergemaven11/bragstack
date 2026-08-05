from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.auth import get_current_user
from app.database import (
    entries_collection,
    impact_receipts_collection,
)
from app.models import (
    ImpactReceiptFromEntryCreate,
    ImpactReceiptResponse,
)


router = APIRouter(
    prefix="/impact-receipts",
    tags=["impact-receipts"],
)


def clean_string_list(values: list[str]) -> list[str]:
    """Trim values, remove blanks, and prevent duplicates."""

    cleaned_values = []
    seen_values = set()

    for value in values:
        cleaned_value = value.strip()

        if cleaned_value and cleaned_value not in seen_values:
            cleaned_values.append(cleaned_value)
            seen_values.add(cleaned_value)

    return cleaned_values


def build_trust_signals(evidence: list[dict]) -> list[str]:
    """Build honest trust signals for a newly created receipt."""

    trust_signals = ["self-documented"]

    if evidence:
        trust_signals.append("evidence-linked")

    return trust_signals


def serialize_impact_receipt(receipt: dict) -> dict:
    """Convert a MongoDB Impact Receipt into an API response."""

    return {
        "id": str(receipt["_id"]),
        "source_entry_id": receipt["source_entry_id"],
        "accomplishment": receipt["accomplishment"],
        "contribution": receipt["contribution"],
        "result": receipt["result"],
        "evidence": receipt.get("evidence", []),
        "skills": receipt.get("skills", []),
        "credit": receipt.get("credit", []),
        "confirmations": receipt.get("confirmations", []),
        "trust_signals": receipt.get(
            "trust_signals",
            ["self-documented"],
        ),
        "is_public": receipt.get("is_public", False),
        "schema_version": receipt.get("schema_version", 1),
        "created_at": receipt["created_at"],
        "updated_at": receipt["updated_at"],
    }


@router.post(
    "/from-entry/{entry_id}",
    response_model=ImpactReceiptResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_impact_receipt_from_entry(
    entry_id: str,
    payload: ImpactReceiptFromEntryCreate,
    current_user: dict = Depends(get_current_user),
):
    """Convert an owned brag entry into an Impact Receipt."""

    if not ObjectId.is_valid(entry_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid entry ID",
        )

    user_id = str(current_user["_id"])

    entry = entries_collection.find_one(
        {
            "_id": ObjectId(entry_id),
            "user_id": user_id,
        }
    )

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found",
        )

    existing_receipt = impact_receipts_collection.find_one(
        {
            "user_id": user_id,
            "source_entry_id": entry_id,
        }
    )

    if existing_receipt is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "impact_receipt_already_exists",
                "message": (
                    "This brag entry already has an Impact Receipt."
                ),
                "receipt_id": str(existing_receipt["_id"]),
            },
        )

    accomplishment = str(
        entry.get("title", "")
    ).strip()

    contribution = (
        payload.contribution.strip()
        if payload.contribution
        else str(entry.get("action", "")).strip()
    )

    result = (
        payload.result.strip()
        if payload.result
        else str(entry.get("impact", "")).strip()
    )

    if not accomplishment:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The source entry must have a title.",
        )

    if not contribution:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The source entry must have an action or a custom "
                "contribution."
            ),
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The source entry must have an impact or a custom result."
            ),
        )

    evidence = [
        evidence_item.model_dump()
        for evidence_item in payload.evidence
    ]

    credit = [
        credit_item.model_dump()
        for credit_item in payload.credit
    ]

    skills = clean_string_list(
        payload.skills or entry.get("tags", [])
    )

    now = datetime.now(timezone.utc)

    receipt_document = {
        "user_id": user_id,
        "source_entry_id": entry_id,
        "accomplishment": accomplishment,
        "contribution": contribution,
        "result": result,
        "evidence": evidence,
        "skills": skills,
        "credit": credit,
        "confirmations": [],
        "trust_signals": build_trust_signals(evidence),
        "is_public": payload.is_public,
        "schema_version": 1,
        "created_at": now,
        "updated_at": now,
    }

    result = impact_receipts_collection.insert_one(
        receipt_document
    )

    created_receipt = impact_receipts_collection.find_one(
        {"_id": result.inserted_id}
    )

    return serialize_impact_receipt(created_receipt)

@router.get("")
def list_impact_receipts(
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """List Impact Receipts owned by the authenticated user."""

    user_id = str(current_user["_id"])

    query = {
        "user_id": user_id,
    }

    total_receipts = (
        impact_receipts_collection.count_documents(query)
    )

    cursor = (
        impact_receipts_collection
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    receipts = [
        serialize_impact_receipt(receipt)
        for receipt in cursor
    ]

    return {
        "total_receipts": total_receipts,
        "returned_receipts": len(receipts),
        "limit": limit,
        "skip": skip,
        "has_more": skip + limit < total_receipts,
        "receipts": receipts,
    }