from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth import get_current_user
from app.database import entries_collection, impact_receipts_collection
from app.models import (
    ImpactReceiptFromEntryCreate,
    ImpactReceiptResponse,
    ImpactReceiptUpdate,
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


def build_trust_signals(
    evidence: list[dict],
    confirmations: list[dict] | None = None,
) -> list[str]:
    """Build trust signals from evidence and confirmed third-party checks."""

    trust_signals = ["self-documented"]

    if evidence:
        trust_signals.append("evidence-linked")

    for confirmation in confirmations or []:
        if confirmation.get("status") != "confirmed":
            continue

        confirmation_type = confirmation.get("confirmation_type")

        if confirmation_type == "collaborator":
            trust_signals.append("collaborator-confirmed")
        elif confirmation_type == "stakeholder":
            trust_signals.append("stakeholder-verified")
        elif confirmation_type == "organization":
            trust_signals.append("organization-issued")

    return list(dict.fromkeys(trust_signals))


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
                "message": "This brag entry already has an Impact Receipt.",
                "receipt_id": str(existing_receipt["_id"]),
            },
        )

    accomplishment = str(entry.get("title", "")).strip()

    contribution = (
        payload.contribution.strip()
        if payload.contribution
        else str(entry.get("action", "")).strip()
    )

    result_text = (
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

    if not result_text:
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
        "result": result_text,
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

    insert_result = impact_receipts_collection.insert_one(receipt_document)

    created_receipt = impact_receipts_collection.find_one(
        {"_id": insert_result.inserted_id}
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
    query = {"user_id": user_id}

    total_receipts = impact_receipts_collection.count_documents(query)

    cursor = (
        impact_receipts_collection
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    receipts = [serialize_impact_receipt(receipt) for receipt in cursor]

    return {
        "total_receipts": total_receipts,
        "returned_receipts": len(receipts),
        "limit": limit,
        "skip": skip,
        "has_more": skip + limit < total_receipts,
        "receipts": receipts,
    }


@router.patch(
    "/{receipt_id}",
    response_model=ImpactReceiptResponse,
)
def update_impact_receipt(
    receipt_id: str,
    payload: ImpactReceiptUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update owner-editable Impact Receipt fields, including visibility."""

    if not ObjectId.is_valid(receipt_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Impact Receipt ID",
        )

    user_id = str(current_user["_id"])
    query = {
        "_id": ObjectId(receipt_id),
        "user_id": user_id,
    }

    existing_receipt = impact_receipts_collection.find_one(query)

    if existing_receipt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Impact Receipt not found",
        )

    raw_updates = payload.model_dump(exclude_unset=True)
    updates = {}

    for field_name in ("accomplishment", "contribution", "result"):
        if field_name not in raw_updates:
            continue

        value = raw_updates[field_name]
        if value is None:
            continue

        cleaned_value = value.strip()
        if not cleaned_value:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"{field_name} cannot be blank",
            )

        updates[field_name] = cleaned_value

    if "skills" in raw_updates and raw_updates["skills"] is not None:
        updates["skills"] = clean_string_list(raw_updates["skills"])

    if "evidence" in raw_updates and raw_updates["evidence"] is not None:
        updates["evidence"] = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in payload.evidence or []
        ]

    if "credit" in raw_updates and raw_updates["credit"] is not None:
        updates["credit"] = [
            item.model_dump() if hasattr(item, "model_dump") else item
            for item in payload.credit or []
        ]

    if "is_public" in raw_updates and raw_updates["is_public"] is not None:
        updates["is_public"] = raw_updates["is_public"]

    evidence = updates.get("evidence", existing_receipt.get("evidence", []))
    confirmations = existing_receipt.get("confirmations", [])
    updates["trust_signals"] = build_trust_signals(evidence, confirmations)
    updates["updated_at"] = datetime.now(timezone.utc)

    impact_receipts_collection.update_one(query, {"$set": updates})

    updated_receipt = impact_receipts_collection.find_one(query)
    return serialize_impact_receipt(updated_receipt)
