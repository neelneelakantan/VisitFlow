from fastapi import APIRouter, HTTPException
from models import Company, CompanyCreate, CompanyUpdate, ApplyNote
from store import companies, add_company
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone

router = APIRouter()

@router.get("/companies")
def list_companies():
    return list(companies.values())

@router.post("/companies")
def create_company(payload: CompanyCreate):
    company = Company(
        id=len(companies) + 1,
        name=payload.name,
        url=payload.url,
        value=payload.value or "medium",
        cadence_days=payload.cadence_days or 7,
        status=payload.status or "active",
        reason=payload.reason or "",
        notes=payload.notes or ""
    )
    return add_company(company)

@router.get("/companies/{company_id}")
def get_company(company_id: int):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")
    return companies[company_id]

@router.put("/companies/{company_id}")
def update_company(company_id: int, payload: CompanyUpdate):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")

    company = companies[company_id]
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(company, field, value)

    company.updated_at = datetime.now(timezone.utc)
    return company

@router.post("/companies/{company_id}/visit")
def visit_company(company_id: int):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")

    company = companies[company_id]
    company.last_checked = datetime.now(timezone.utc)
    company.updated_at = datetime.now(timezone.utc)
    return company

@router.post("/companies/{company_id}/apply")
def apply_company(company_id: int, payload: ApplyNote):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")

    company = companies[company_id]
    timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {payload.note}"

    company.notes = (company.notes + "\n" + entry).strip()
    company.updated_at = datetime.now(timezone.utc)
    return company


@router.post("/companies/{company_id}/visit")
def visit_company(company_id: int):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")

    company = companies[company_id]
    company.last_checked = datetime.now(timezone.utc)
    company.updated_at = datetime.now(timezone.utc)

    return company

@router.post("/companies/{company_id}/apply")
def apply_company(company_id: int, payload: ApplyNote):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")

    company = companies[company_id]

    timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {payload.note}"

    company.notes = (company.notes + "\n" + entry).strip()
    company.updated_at = datetime.now(timezone.utc)

    return company

@router.get("/companies/overdue")
def get_overdue_companies():
    today = datetime.now(timezone.utc)
    overdue = []

    for company in companies.values():
        if company.status != "active":
            continue

        if company.last_checked is None:
            overdue.append(company)
            continue

        days = (today - company.last_checked).days
        if days >= company.cadence_days:
            overdue.append(company)

    return overdue

@router.get("/companies/{company_id}/visit")
def visit_company(company_id: int):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")

    company = companies[company_id]
    company.last_checked = datetime.now(timezone.utc)
    company.updated_at = datetime.now(timezone.utc)

    return RedirectResponse(url="/", status_code=303)

@router.get("/companies/{company_id}/apply")
def apply_company(company_id: int, note: str = ""):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")

    company = companies[company_id]

    timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    print(timestamp)
    entry = f"[{timestamp}] {note}"

    company.notes = (company.notes + "\n" + entry).strip()
    company.updated_at = datetime.now(timezone.utc)

    return RedirectResponse(url=f"/company/{company_id}", status_code=303)


