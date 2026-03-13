from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone

from models import Company, CompanyCreate, CompanyUpdate, ApplyNote
from store import store

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
@router.get("/companies/overdue")
def get_overdue_companies():
    today = datetime.now(timezone.utc)
    overdue = []

    for company in store.list_companies():
        if company.status != "active":
            continue

        if company.last_checked is None:
            overdue.append(company)
            continue

        days = (today - company.last_checked).days
        if days >= company.cadence_days:
            overdue.append(company)

    return overdue
