from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
from fastapi import Form
from models import Company
from store import store
from templates_engine import templates

router = APIRouter()
@router.get("/", response_class=HTMLResponse)
def list_companies_page(
    request: Request,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20
):
    today = datetime.now(timezone.utc)
    companies = store.list_companies()

    # --- Search filter ---
    if q:
        q_lower = q.lower()
        companies = [
            c for c in companies
            if q_lower in c.name.lower()
            or q_lower in (c.url or "").lower()
            or q_lower in (c.notes or "").lower()
            or q_lower in c.value.lower()
        ]

    # --- Enrichment + overdue logic ---
    enriched = []
    for company in companies:
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

    # --- Sorting ---
    value_order = {"high": 0, "medium": 1, "low": 2}
    enriched.sort(
        key=lambda x: (
            not x["overdue"],
            value_order[x["company"].value]
        )
    )

    # --- Pagination ---
    total = len(enriched)
    total_pages = max(1, (total + page_size - 1) // page_size)

    # clamp page to valid range
    page = max(1, min(page, total_pages))

    start = (page - 1) * page_size
    end = start + page_size
    paged = enriched[start:end]

    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "companies": paged,
            "q": q or "",
            "page": page,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages
        }
    )


@router.get("/company/new", response_class=HTMLResponse)
def new_company_form(request: Request):
    return templates.TemplateResponse("new_company.html", {"request": request})

@router.post("/company/new")
def create_company_form(name: str = Form(...), url: str = Form(...),
                        value: str = Form("medium"), cadence_days: int = Form(7)):
    company = Company(
        id=0,
        name=name,
        url=url,
        value=value,
        cadence_days=cadence_days,
    )
    store.add_company(company)
    return RedirectResponse("/", status_code=303)

@router.get("/company/{company_id}", response_class=HTMLResponse)
def company_detail_page(request: Request, company_id: int):
    company = store.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return templates.TemplateResponse(
        "detail.html",
        {
            "request": request,
            "company": company
        }
    )


@router.post("/company/{company_id}/visit")
async def visit_now(company_id: int):
    store.mark_visited(company_id)
    return RedirectResponse(f"/company/{company_id}", status_code=303)


@router.post("/company/{company_id}/apply")
async def apply_now(company_id: int):
    store.mark_applied(company_id)
    return RedirectResponse(f"/company/{company_id}", status_code=303)


@router.get("/api-explorer", response_class=HTMLResponse)
def api_explorer(request: Request):
    return templates.TemplateResponse("api.html", {"request": request})


