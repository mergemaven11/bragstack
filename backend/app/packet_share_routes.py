from __future__ import annotations

import hashlib
import io
import secrets
from datetime import datetime, timezone
from html import escape
from typing import Any

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.auth import get_current_user, hash_password, verify_password
from app.database import packet_shares_collection, users_collection
from app.packet_audit import record_packet_export
from app.packet_platform import OPTIONAL_SECTIONS, apply_packet_platform, sanitize_shared_packet
from app.packet_platform_pdf import build_platform_packet_pdf, make_platform_packet_filename
from app.packet_platform_routes import _signature_candidates
from app.performance_packet_routes import _build_packet, _parse_period
from app.plans import require_feature

router = APIRouter(tags=["packet-sharing"])


class PacketShareCreate(BaseModel):
    start_date: str | None = None
    end_date: str | None = None
    career_area: str = Field(default="", max_length=120)
    role_title: str = Field(default="", max_length=160)
    organization: str = Field(default="", max_length=180)
    confidential: bool = True
    signature_entry_ids: list[str] = Field(default_factory=list, max_length=8)
    sections: list[str] = Field(default_factory=lambda: list(OPTIONAL_SECTIONS), max_length=len(OPTIONAL_SECTIONS))
    packet_note: str = Field(default="", max_length=1500)
    item_notes: dict[str, str] = Field(default_factory=dict)
    include_notes: bool = False
    theme: str = Field(default="classic-dossier", max_length=40)
    brand_name: str = Field(default="", max_length=120)
    department_label: str = Field(default="", max_length=120)
    reviewer_name: str = Field(default="", max_length=120)
    review_cycle_label: str = Field(default="", max_length=120)
    expires_at: datetime | None = None
    access_code: str | None = Field(default=None, min_length=4, max_length=64)
    allow_download: bool = False
    include_evidence: bool = False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _serialize_share(item: dict[str, Any]) -> dict[str, Any]:
    def iso(value):
        return value.isoformat() if hasattr(value, "isoformat") else value

    return {
        "id": str(item.get("_id")),
        "created_at": iso(item.get("created_at")),
        "expires_at": iso(item.get("expires_at")),
        "revoked_at": iso(item.get("revoked_at")),
        "revoked": bool(item.get("revoked")),
        "allow_download": bool(item.get("allow_download")),
        "include_evidence": bool(item.get("include_evidence")),
        "include_notes": bool(item.get("include_notes")),
        "requires_access_code": bool(item.get("access_code_hash")),
        "review_period": {
            "start_date": item.get("options", {}).get("start_date"),
            "end_date": item.get("options", {}).get("end_date"),
        },
    }


def _validate_share(item: dict[str, Any] | None, access_code: str | None) -> dict[str, Any]:
    if not item or item.get("revoked"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared packet not found")
    expires_at = _aware(item.get("expires_at"))
    if expires_at and expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared packet not found")
    code_hash = item.get("access_code_hash")
    if code_hash and (not access_code or not verify_password(access_code, code_hash)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access code required")
    return item


def _build_shared_packet(item: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    owner_id = item.get("user_id")
    if not ObjectId.is_valid(owner_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared packet not found")
    owner = users_collection.find_one({"_id": ObjectId(owner_id)})
    if not owner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared packet not found")

    options = item.get("options") or {}
    parsed_start, parsed_end = _parse_period(options.get("start_date"), options.get("end_date"))
    packet = _build_packet(
        current_user=owner,
        start_date=parsed_start,
        end_date=parsed_end,
        career_area=options.get("career_area"),
        role_title=options.get("role_title"),
        organization=options.get("organization"),
        confidential=bool(options.get("confidential", True)),
    )["packet"]
    selected_sections = options["sections"] if "sections" in options else list(OPTIONAL_SECTIONS)
    packet = apply_packet_platform(
        packet,
        signature_entry_ids=options.get("signature_entry_ids") or [],
        signature_candidates=_signature_candidates(current_user=owner, start_date=parsed_start, end_date=parsed_end),
        sections=selected_sections,
        packet_note=options.get("packet_note"),
        item_notes=options.get("item_notes") or {},
        include_notes=bool(item.get("include_notes")),
        theme=options.get("theme"),
        brand_name=options.get("brand_name"),
        department_label=options.get("department_label"),
        reviewer_name=options.get("reviewer_name"),
        review_cycle_label=options.get("review_cycle_label"),
    )
    packet = sanitize_shared_packet(
        packet,
        include_evidence=bool(item.get("include_evidence")),
        include_notes=bool(item.get("include_notes")),
    )
    packet["shared_view"] = True
    return owner, packet


def _shared_html(packet: dict[str, Any], *, allow_download: bool, token: str, access_code: str | None) -> str:
    subject = packet.get("subject", {})
    branding = packet.get("branding", {})
    score = packet.get("scorecard", {})
    signatures = packet.get("signature_accomplishments", []) or []
    theme = packet.get("render_config", {}).get("theme") or "classic-dossier"
    download = ""
    if allow_download:
        code_param = f"?code={escape(access_code or '')}" if access_code else ""
        download = f'<a class="download" rel="nofollow" href="/shared/packets/{escape(token)}/download.pdf{code_param}">Download PDF</a>'
    accomplishments = "".join(
        f'<article><small>{escape(str(item.get("category") or "Accomplishment"))}</small><h3>{escape(str(item.get("title") or ""))}</h3><p>{escape(str(item.get("result") or ""))}</p></article>'
        for item in signatures[:8]
    ) or "<p>No signature accomplishments were included.</p>"
    note = ""
    annotations = packet.get("annotations", {})
    if annotations.get("include_in_export") and annotations.get("packet_note"):
        note = f'<aside><strong>User-authored context</strong><p>{escape(str(annotations["packet_note"]))}</p></aside>'
    sharing_notice = f'<p class="notice">{escape(str(packet.get("sharing_notice")))}</p>' if packet.get("sharing_notice") else ""
    return f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta name='robots' content='noindex,nofollow'><meta name='referrer' content='no-referrer'><title>{escape(str(packet.get('title') or 'BragStack Packet'))}</title><style>
body{{margin:0;background:#eef0f1;color:#172126;font-family:Inter,system-ui,-apple-system,sans-serif}}main{{max-width:850px;margin:32px auto;background:#fff;padding:52px;box-shadow:0 18px 60px #0001}}header{{border-bottom:3px solid #173f43;padding-bottom:26px}}.brand{{font-size:12px;letter-spacing:.13em;font-weight:800;color:#1f5559}}h1{{font-family:Georgia,serif;font-size:42px;margin:20px 0 4px}}h2{{font-weight:500;color:#667176;margin:0}}.meta{{margin-top:18px;color:#667176}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:28px 0}}.stats div{{border:1px solid #dde1df;padding:16px;text-align:center}}.stats strong{{display:block;font-family:Georgia,serif;font-size:24px;color:#173f43}}section{{margin-top:34px}}article{{border-top:1px solid #e5e7e6;padding:18px 0}}article small{{color:#1f5559;font-weight:700;text-transform:uppercase}}article h3{{margin:5px 0;font-family:Georgia,serif;font-size:21px}}article p,aside p{{color:#5d686e;line-height:1.55}}aside,.notice{{background:#f5f3ee;padding:14px 16px;border-left:3px solid #b68b4c}}.download{{display:inline-block;margin-top:20px;padding:11px 15px;border-radius:8px;background:#173f43;color:white;text-decoration:none;font-weight:700}}footer{{margin-top:44px;padding-top:16px;border-top:1px solid #ddd;color:#788086;font-size:12px}}@media(max-width:700px){{main{{margin:0;padding:28px 20px}}.stats{{grid-template-columns:repeat(2,1fr)}}h1{{font-size:34px}}}}
</style></head><body data-theme='{escape(theme)}'><main><header><div class='brand'>{escape(str(branding.get('brand_name') or 'BRAGSTACK'))} · CAREER EVIDENCE</div><h1>{escape(str(subject.get('name') or 'BragStack Member'))}</h1><h2>{escape(str(subject.get('role') or 'Professional'))}</h2><div class='meta'>{escape(str(packet.get('period',{}).get('label') or 'All recorded work'))}</div>{download}</header><div class='stats'><div><strong>{score.get('accomplishments',0)}</strong>Accomplishments</div><div><strong>{score.get('impact_receipts',0)}</strong>Impact Receipts</div><div><strong>{score.get('evidence_items',0)}</strong>Evidence items</div><div><strong>{score.get('skills_demonstrated',0)}</strong>Skills</div></div>{sharing_notice}{note}<section><h2>Signature accomplishments</h2>{accomplishments}</section><footer>BragStack · Private packet share · This share is independent of any public Proof Profile.</footer></main></body></html>"""


@router.post("/packets/shares")
def create_packet_share(payload: PacketShareCreate, current_user: dict = Depends(get_current_user)):
    require_feature(current_user, "performance_review_builder")
    parsed_start, parsed_end = _parse_period(payload.start_date, payload.end_date)
    now = datetime.now(timezone.utc)
    expires_at = _aware(payload.expires_at)
    if expires_at and expires_at <= now:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="expires_at must be in the future")

    token = secrets.token_urlsafe(32)
    options = payload.model_dump(exclude={"expires_at", "access_code", "allow_download", "include_evidence", "include_notes"})
    options["start_date"] = parsed_start.isoformat() if parsed_start else None
    options["end_date"] = parsed_end.isoformat() if parsed_end else None
    options["sections"] = [section for section in OPTIONAL_SECTIONS if section in payload.sections]
    options["signature_entry_ids"] = payload.signature_entry_ids[:8]

    result = packet_shares_collection.insert_one(
        {
            "user_id": str(current_user["_id"]),
            "token_hash": _token_hash(token),
            "options": options,
            "created_at": now,
            "expires_at": expires_at,
            "access_code_hash": hash_password(payload.access_code) if payload.access_code else None,
            "allow_download": payload.allow_download,
            "include_evidence": payload.include_evidence,
            "include_notes": payload.include_notes,
            "revoked": False,
            "revoked_at": None,
        }
    )
    return {
        "share": {
            "id": str(result.inserted_id),
            "token": token,
            "path": f"/shared/packets/{token}",
            "expires_at": expires_at.isoformat() if expires_at else None,
            "allow_download": payload.allow_download,
            "include_evidence": payload.include_evidence,
            "include_notes": payload.include_notes,
            "requires_access_code": bool(payload.access_code),
        }
    }


@router.get("/packets/shares")
def list_packet_shares(current_user: dict = Depends(get_current_user)):
    require_feature(current_user, "performance_review_builder")
    items = list(packet_shares_collection.find({"user_id": str(current_user["_id"])}).sort("created_at", -1).limit(50))
    return {"shares": [_serialize_share(item) for item in items]}


@router.delete("/packets/shares/{share_id}")
def revoke_packet_share(share_id: str, current_user: dict = Depends(get_current_user)):
    if not ObjectId.is_valid(share_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    result = packet_shares_collection.update_one(
        {"_id": ObjectId(share_id), "user_id": str(current_user["_id"])},
        {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc)}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    return {"revoked": True}


@router.get("/shared/packets/{token}", response_class=HTMLResponse)
def view_shared_packet(token: str, code: str | None = Query(None, max_length=64)):
    item = _validate_share(packet_shares_collection.find_one({"token_hash": _token_hash(token)}), code)
    _, packet = _build_shared_packet(item)
    return HTMLResponse(
        _shared_html(packet, allow_download=bool(item.get("allow_download")), token=token, access_code=code),
        headers={
            "Cache-Control": "private, no-store",
            "Referrer-Policy": "no-referrer",
            "X-Robots-Tag": "noindex, nofollow",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/shared/packets/{token}/download.pdf")
def download_shared_packet(token: str, code: str | None = Query(None, max_length=64)):
    item = _validate_share(packet_shares_collection.find_one({"token_hash": _token_hash(token)}), code)
    if not item.get("allow_download"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Download is disabled for this share")
    owner, packet = _build_shared_packet(item)
    pdf_bytes = build_platform_packet_pdf(packet)
    filename = make_platform_packet_filename(packet)
    audit_packet = dict(packet)
    audit_packet["kind"] = "shared-performance-review"
    record_packet_export(user_id=str(owner["_id"]), packet=audit_packet, filename=filename, pdf_bytes=pdf_bytes)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, no-store",
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
        },
    )
