from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from store import companies
from datetime import datetime, timezone

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def list_companies_page(request: Request):
    today = datetime.now(timezone.utc)
    enriched = []

    for company in companies.values():
        # Determine overdue status
        if company.status != "active":
            overdue = False
        elif company.last_checked is None:
            overdue = True
        else:
            days = (today - company.last_checked).days
            overdue = days >= company.cadence_days

        enriched.append({
            "company": company,
            "overdue": overdue
        })

    # Sorting: overdue first, then by value tier
    value_order = {"high": 0, "medium": 1, "low": 2}

    enriched.sort(
        key=lambda x: (
            not x["overdue"],               # overdue first
            value_order[x["company"].value] # then by value
        )
    )

    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "companies": enriched
        }
    )


@router.get("/company/{company_id}", response_class=HTMLResponse)
def company_detail_page(request: Request, company_id: int):
    if company_id not in companies:
        raise HTTPException(status_code=404, detail="Company not found")

    return templates.TemplateResponse(
        "detail.html",
        {
            "request": request,
            "company": companies[company_id]
        }
    )

