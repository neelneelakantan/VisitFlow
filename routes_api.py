from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone

from models import Company, CompanyCreate, CompanyUpdate, ApplyNote
from store import store

from pydantic import BaseModel
from pipeline import build_visit_record
from models import VisitRecord
from store import VISIT_STORE
from templates_engine import templates
from models import FreeNote
from typing import Optional

from store import load_freenotes, save_freenotes
from store import add_freenote

router = APIRouter()


# -----------------------------
# LIST COMPANIES
# -----------------------------
@router.get("/companies")
def list_companies():
    return store.list_companies()


# -----------------------------
# CREATE COMPANY
# -----------------------------
@router.post("/companies")
def create_company(payload: CompanyCreate):
    company = Company(
        id=0,  # will be set by store.add_company
        name=payload.name,
        url=payload.url,
        value=payload.value or "medium",
        cadence_days=payload.cadence_days or 7,
        frequency =  payload.frequency or "weekly",
        specific_date = payload.specific_date,
        status=payload.status or "active",
        reason=payload.reason or "",
        notes=payload.notes or "",
        created_at=datetime.now(timezone.utc),
    )
    return store.add_company(company)


# -----------------------------
# GET COMPANY
# -----------------------------
@router.get("/companies/{company_id}")
def get_company(company_id: int):
    company = store.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


# -----------------------------
# UPDATE COMPANY
# -----------------------------
@router.put("/companies/{company_id}")
def update_company(company_id: int, payload: CompanyUpdate):
    company = store.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(company, field, value)

    company.updated_at = datetime.now(timezone.utc)
    return company


# -----------------------------
# VISIT COMPANY
# -----------------------------
@router.post("/companies/{company_id}/visit")
def visit_company(company_id: int):
    company = store.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    company.last_checked = datetime.now(timezone.utc)
    company.updated_at = datetime.now(timezone.utc)
    return company


# -----------------------------
# APPLY COMPANY (with note)
# -----------------------------
@router.post("/companies/{company_id}/apply")
def apply_company(company_id: int, payload: ApplyNote):
    company = store.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {payload.note}"

    company.notes = (company.notes + "\n" + entry).strip()
    company.updated_at = datetime.now(timezone.utc)
    return company


# -----------------------------
# OVERDUE COMPANIES
# -----------------------------

from datetime import datetime, timezone
from utils import compute_next_check

@router.get("/companies/overdue")
def get_overdue_companies():
    today = datetime.now(timezone.utc).date()
    overdue = []

    for company in store.list_companies():
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

@router.post("/visit", response_model=VisitRecord)
def process_visit(input: VisitInput):
    """
    Accept raw notes from the user and run them through
    the full VisitFlow transformation pipeline.
    """
    record = build_visit_record(input.notes)
    VISIT_STORE.append(record)
    return record


# router internally prefixes with /api so no need to prefix again.
@router.post("/freenotes")
def create_freenote(text: str, template_type: Optional[str] = None):
    return add_freenote(text, template_type)


@router.get("/freenotes")
def list_freenotes():
    notes = load_freenotes()
    return sorted(notes, key=lambda n: n["timestamp"], reverse=True)


