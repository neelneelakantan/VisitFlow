
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel

from models import Company, CompanyCreate, CompanyUpdate, ApplyNote, VisitRecord
from pipeline import build_visit_record
import store
from store import load_freenotes, add_freenote, add_visit, instance, save_companies
from utils import compute_next_check


router = APIRouter()


# -----------------------------
# LIST COMPANIES
# -----------------------------
@router.get("/companies")
def list_companies():
    return instance.list_companies()


# -----------------------------
# CREATE COMPANY
# -----------------------------
@router.post("/companies")
def create_company(payload: CompanyCreate):
    company = Company(
        id=0,  # will be set by store.add_company
        name=payload.name,
        urls=payload.urls,
        value=payload.value or "medium",
        cadence_days=payload.cadence_days or 7,
        frequency =  payload.frequency or "weekly",
        specific_date = payload.specific_date,
        status=payload.status or "active",
        reason=payload.reason or "",
        notes=payload.notes or "",
        created_at=datetime.now(timezone.utc),
    )
    return instance.add_company(company)


# -----------------------------
# GET COMPANY
# -----------------------------
@router.get("/companies/{company_id}")
def get_company(company_id: int):
    company = instance.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


# -----------------------------
# VISIT COMPANY
# -----------------------------
@router.post("/companies/{company_id}/visit")
def visit_company(company_id: int):
    company = instance.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    # Update company metadata
    company.last_checked = datetime.now(timezone.utc)
    company.updated_at = datetime.now(timezone.utc)

    # Create a blank visit record
    record = VisitRecord(
        raw_notes="",
        normalized_notes=None,
        structured_summary=None,
        insights=None,
        recommended_next_steps=None,
        tags=None,
        confidence=None,
        narrative=None
    )

    add_visit(record, company_id)

    return company


# -----------------------------
# APPLY COMPANY (with note)
# -----------------------------
@router.post("/companies/{company_id}/apply")
def apply_company(company_id: int, payload: ApplyNote):
    company = instance.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {payload.note}"
    instance.mark_visited(company_id)

    company.notes = (company.notes + "\n" + entry).strip()
    company.updated_at = datetime.now(timezone.utc)
    save_companies(list(instance.companies.values()))
    return company


# -----------------------------
# OVERDUE COMPANIES
# -----------------------------


@router.get("/companies/overdue")
def get_overdue_companies():
    today = datetime.now(timezone.utc).date()
    overdue = []

    for company in instance.list_companies():
        if company.status != "active":
            continue

        next_check = compute_next_check(company)
        if next_check is None:
            continue

        if next_check.date() < today:
            overdue.append(company)

    return overdue


class VisitInput(BaseModel):
    notes: str


@router.post("/visit")
def create_visit(input: VisitInput, company_id: Optional[int] = None):
    record = build_visit_record(input.notes)
    return add_visit(record, company_id)


@router.get("/visits")
def list_visits():
    return [
        {
            "visit_id": v.visit_id,
            "timestamp": v.timestamp,
            "summary": v.structured_summary.get("key_points", []),
            "sentiment": v.insights.get("sentiment_energy", {}).get("sentiment"),
            "energy": v.insights.get("sentiment_energy", {}).get("energy")
        }
        for v in store.VISIT_STORE
    ]


@router.get("/visit/{visit_id}")
def get_visit(visit_id: str):
    for v in store.VISIT_STORE:
        if v.visit_id == visit_id:
            return v
    return {"error": "Visit not found"}



# router internally prefixes with /api so no need to prefix again.
@router.post("/freenotes")
def create_freenote(text: str, template_type: Optional[str] = None):
    return add_freenote(text, template_type)


@router.get("/freenotes")
def list_freenotes():
    notes = load_freenotes()
    return sorted(notes, key=lambda n: n["timestamp"], reverse=True)


