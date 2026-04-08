from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime, timezone, timedelta
from fastapi import Form
from models import Company, VisitRecord
import store
from store import load_freenotes, add_freenote, add_visit, instance, save_companies, get_visit, save_visits
from store import load_companies, load_visits, get_freenote, update_freenote, delete_freenote
from store import load_harvester, save_harvester, extract_company_from_url, load_json, save_json
from templates_engine import templates
from pipeline import build_visit_record
from utils import compute_next_check
from typing import Optional
import re


router = APIRouter()

@router.get("/")
def dashboard_page(request: Request):
    companies = instance.list_companies()
    today = datetime.now().date()

    total = len(companies)

    overdue = []
    due_today = []
    upcoming = []
    never_checked = []
    no_duedate = []

    for c in companies:
        next_check = compute_next_check(c)

        if next_check is None:
            no_duedate.append(c)
            continue

        next_date = next_check.date()

        ### need to build logic for secific as well
        if c.last_checked is None:
            never_checked.append(c)
        elif next_date < today:
            overdue.append(c)
        elif next_date == today:
            due_today.append(c)
        elif today < next_date <= today + timedelta(days=7):
            upcoming.append(c)

    weekly = store.compute_weekly_metrics()
    today_entry = store.load_daily3_for_date(today.isoformat())

    # --- Compute today's completion dynamically ---
    computed_completion = 0
    if today_entry:
        for key in ["b1_result", "b2_result", "b3_result"]:
            val = today_entry.get(key, "")
            if isinstance(val, str) and val.strip().lower() == "done":
                computed_completion += 1

    # TODO sort the upcoming to be on shortest

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total": total,
            "overdue": overdue,
            "due_today": due_today,
            "upcoming": upcoming,
            "no_duedate" : no_duedate,
            "never_checked": never_checked,
            "weekly": weekly,
            "today_entry": today_entry,
            "computed_completion": computed_completion,
        }
    )



@router.get("/companies", response_class=HTMLResponse)
def list_companies_page(
    request: Request,
    q: str | None = None,
    page: int = 1,
    page_size: int = 20
):
    today = datetime.now(timezone.utc).date()
    companies = instance.list_companies()

    # --- Search filter ---
    if q:
        q_lower = q.lower()
        companies = [
            c for c in companies
            if q_lower in c.name.lower()
            or any (q_lower in u.lower() for u in c.urls)
            or q_lower in (c.notes or "").lower()
            or q_lower in c.value.lower()
        ]

    # --- Enrichment + overdue logic ---
    enriched = []
    for company in companies:
        next_check = compute_next_check(company)

        if next_check is None:
            overdue = False
        else:
            overdue = next_check.date() < today

        enriched.append({
            "company": company,
            "overdue": overdue,
            "next_check": next_check,
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


@router.get("/companies/new", response_class=HTMLResponse)
def new_company_form(request: Request):
    return templates.TemplateResponse("new_company.html", {"request": request})


@router.get("/companies/deleted")
def deleted_companies(request: Request):
    companies = instance.list_deleted_companies()
    return templates.TemplateResponse(
        "company_deleted_list.html",
        {"request": request, "companies": companies}
    )

@router.post("/reload")
def reload_data():
    # Reload companies
    companies = load_companies()
    instance.companies = {c.id: c for c in companies}

    # Recompute next_id
    if instance.companies:
        instance.next_id = max(instance.companies.keys()) + 1
    else:
        instance.next_id = 1

    # Reload visits
    store.VISIT_STORE[:] = load_visits()

    # Reload freenotes
    # (no internal store, so nothing to update)

    return RedirectResponse("/", status_code=303)


@router.post("/companies/purge/")
def purge_deleted():
    instance.purge_deleted_companies()
    return RedirectResponse("/companies/deleted", status_code=303)


@router.post("/companies/new")
def create_company_form(
    name: str = Form(...),
    urls: str = Form(...),
    value: str = Form("medium"),
    cadence_days: int = Form(7),
    frequency: str = Form("weekly"),
    specific_date: str | None = Form(None),
):
    urls_list = [u.strip() for u in urls.splitlines() if u.strip()]

    company = Company(
        id=0,
        name=name,
        urls=urls_list,
        value=value,
        cadence_days=cadence_days,
        frequency=frequency,
        specific_date=specific_date,
        notes="",   # ensure no null ever written
    )
    instance.add_company(company)
    return RedirectResponse("/companies", status_code=303)


@router.get("/companies/harvester")
async def harvester_list(request: Request, q: str = ""):
    data = load_harvester()

    if q:
        items = [e for e in data if q.lower() in e["name"].lower()]
    else:
        items = data

    return templates.TemplateResponse(
        "harvester_list.html",
        {"request": request, "items": items, "q": q},
    )



@router.post("/companies/harvester/delete")
async def harvester_delete(request: Request):
    form = await request.form()
    name = form["name"]

    data = load_harvester()
    data = [e for e in data if e["name"] != name]
    save_harvester(data)

    return RedirectResponse("/companies/harvester", status_code=303)



@router.get("/companies/harvester/edit")
async def harvester_edit(request: Request, name: str):
    data = load_harvester()
    entry = next((e for e in data if e["name"] == name), None)
    print("DEBUG: name param =", name)
    print("DEBUG: harvester data =", load_harvester())
    return templates.TemplateResponse(
        "harvester_edit.html",
        {"request": request, "entry": entry},
    )


@router.post("/companies/harvester/edit")
async def harvester_edit_post(request: Request):
    form = await request.form()

    old_name = form["old_name"]
    source_url = form.get("source_url", "").strip() or None

    data = load_harvester()

    for entry in data:
        if entry["name"] == old_name:

            # If source URL changed, re-derive everything
            if source_url and source_url != entry["source_url"]:
                new_name, new_careers = extract_company_from_url(source_url)
                entry["name"] = new_name
                entry["source_url"] = source_url
                entry["careers_url"] = new_careers
            else:
                # No change → keep existing
                entry["source_url"] = source_url

    save_harvester(data)

    return RedirectResponse("/companies/harvester", status_code=303)



@router.get("/companies/harvest", response_class=HTMLResponse)
def harvest_form(request: Request):
    return templates.TemplateResponse(
        "harvest.html",
        {"request": request}
    )


@router.post("/companies/harvester/promote")
async def harvester_promote(request: Request):
    form = await request.form()
    name = form["name"]

    data = load_harvester()
    remaining = []
    promoted_entry = None

    for entry in data:
        if entry["name"] == name:
            promoted_entry = entry
        else:
            remaining.append(entry)

    save_harvester(remaining)

    # Promote to Companies (string only)
    companies = load_json("companies.json", default=[])
    if name not in companies:
        companies.append(name)
        save_json("companies.json", companies)

    return RedirectResponse("/companies/harvester", status_code=303)



@router.post("/companies/harvest")
async def companies_harvest(request: Request):
    form = await request.form()
    raw = form["raw"]

    lines = [line.strip() for line in raw.splitlines() if line.strip()]

    data = load_harvester()
    existing = {e["name"].lower() for e in data}

    added = []
    skipped = 0

    for line in lines:
        if line.startswith("http://") or line.startswith("https://"):
            name, careers_url = extract_company_from_url(line)
            source_url = line
        else:
            name = line
            careers_url = None
            source_url = None

        if name.lower() in existing:
            skipped += 1
            continue

        entry = {
            "name": name,
            "source_url": source_url,
            "careers_url": careers_url,
        }

        data.append(entry)
        existing.add(name.lower())
        added.append(entry)

    save_harvester(data)

    return templates.TemplateResponse(
        "harvest_result.html",
        {"request": request, "added": added, "skipped": skipped},
    )




@router.get("/companies/{company_id}/edit")
def edit_company_form(request: Request, company_id: int):
    company = instance.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return templates.TemplateResponse(
        "edit_company.html",
        {"request": request, "company": company}
    )

@router.post("/companies/{company_id}/edit")
def edit_company_submit(
    company_id: int,
    name: str = Form(...),
    urls: str = Form(...),
    value: str = Form(...),
    cadence_days: int = Form(...),
    frequency: str = Form(...),
    specific_date: str | None = Form(None),
    notes: str | None = Form(None),
):
    company = instance.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    urls_list = [u.strip() for u in urls.splitlines() if u.strip()]

    company.name = name
    company.urls = urls_list
    company.value = value
    company.cadence_days = cadence_days
    company.frequency = frequency
    company.specific_date = specific_date
    company.notes = notes or ""

    save_companies(list(instance.companies.values()))
    return RedirectResponse(f"/companies/{company_id}", status_code=303)

@router.get("/companies/{company_id}")
def company_detail(request: Request, company_id: int):
    company = instance.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.status == "deleted":
        return templates.TemplateResponse(
            "company_deleted.html",
            {"request": request, "company": company}
        )
    
    # Compute next check
    next_check = compute_next_check(company)

    # Compute status flags
    is_overdue = False
    is_due_today = False
    is_upcoming = False

    if next_check:
        now = datetime.now(timezone.utc)
        due = next_check

        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)

        if due < now:
            is_overdue = True
        elif due.date() == now.date():
            is_due_today = True
        else:
            is_upcoming = True

    # -----------------------------
    # REAL VISIT LOADING LOGIC
    # -----------------------------
    visits = [
        v for v in store.VISIT_STORE
        if v.company_id == company_id
    ]

    # Sort newest first
    visits.sort(key=lambda v: v.timestamp, reverse=True)

    # Enrich for UI (last 3 visits)
    enriched = []
    for v in visits[:3]:
        local_ts = v.timestamp.astimezone()
        ts_str = local_ts.strftime("%b %d, %Y %I:%M %p")

        sentiment = None
        energy = None
        if v.insights and "sentiment_energy" in v.insights:
            sentiment = v.insights["sentiment_energy"].get("sentiment")
            energy = v.insights["sentiment_energy"].get("energy")

        enriched.append({
            "id": v.visit_id,
            "timestamp": ts_str,
            "summary": v.structured_summary,
            "sentiment": sentiment,
            "energy": energy,
        })

    return templates.TemplateResponse(
        "detail.html",
        {
            "request": request,
            "company": company,
            "recent_visits": enriched,
            "has_visits": len(visits) > 0,
            "last_visit": enriched[0] if enriched else None,
            "next_check": next_check,
            "is_overdue": is_overdue,
            "is_due_today": is_due_today,
            "is_upcoming": is_upcoming,
        }
    )




@router.post("/companies/{company_id}/visit")
async def visit_now(company_id: int):
    company = instance.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    company.last_checked = datetime.now(timezone.utc)
    company.updated_at = datetime.now(timezone.utc)
    
    instance.mark_visited(company_id)

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

    return RedirectResponse(f"/companies/{company_id}", status_code=303)


@router.post("/companies/{company_id}/apply")
async def apply_now(company_id: int):
    company = instance.get_company(company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    # Update applied timestamp
    instance.mark_applied(company_id)

    # --- Option A: Auto‑add a simple note ---
    # TODO: Option B — allow user to enter a custom note before applying
    timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] Applied via UI"

    company.notes = (company.notes + "\n" + entry).strip()

    # Persist to disk
    save_companies(list(instance.companies.values()))

    return RedirectResponse(f"/companies/{company_id}", status_code=303)

@router.get("/company/{company_id}/delete")
def delete_company_confirm(request: Request, company_id: int):
    company = instance.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Find visits referencing this company
    visits = [v for v in store.VISIT_STORE if v.company_id == company_id]

    return templates.TemplateResponse(
        "company_delete_confirm.html",
        {
            "request": request,
            "company": company,
            "visits": visits
        }
    )

@router.post("/company/{company_id}/delete")
def delete_company_action(
    company_id: int,
    action: str = Form(...),
):
    company = instance.get_company(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Soft delete the company
    company.status = "deleted"
    save_companies(list(instance.companies.values()))

    # Redirect to company list
    return RedirectResponse("/companies", status_code=303)


@router.get("/api-explorer", response_class=HTMLResponse)
def api_explorer(request: Request):
    return templates.TemplateResponse("api.html", {"request": request})


@router.get("/test")
def test_page(request: Request):
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "title": "Test Page"}
    )


@router.get("/timeline")
def timeline(request: Request):
    visits = store.VISIT_STORE

    enriched = []
    for v in visits:
        # Convert timestamp to local timezone
        local_ts = v.timestamp.astimezone()

        # Format timestamp for readability
        ts_str = local_ts.strftime("%b %d, %Y %I:%M %p")

        # Company lookup
        company = None
        if v.company_id is not None:
            company = instance.get_company(v.company_id)

        # Notes preview
        preview = ""
        if v.raw_notes:
            preview = v.raw_notes[:80] + ("..." if len(v.raw_notes) > 80 else "")

        sentiment = None
        energy = None
        if v.insights and "sentiment_energy" in v.insights:
            sentiment = v.insights["sentiment_energy"].get("sentiment")
            energy = v.insights["sentiment_energy"].get("energy")

        enriched.append({
            "id": v.visit_id,
            "timestamp": ts_str,
            "company": company,
            "sentiment": sentiment,
            "energy": energy,
            "summary": v.structured_summary,
            "preview": preview,
        })

    return templates.TemplateResponse(
        "timeline.html",
        {"request": request, "visits": enriched}
    )



@router.get("/visit/{visit_id}")
def visit_detail(request: Request, visit_id: str):
    visit = get_visit(visit_id)

    company = None
    if visit.company_id is not None:
        company = instance.get_company(visit.company_id)

    return templates.TemplateResponse(
        "visit_detail.html",
        {
            "request": request,
            "visit": visit,
            "company": company
        }
    )


@router.get("/new")
def new_visit(request: Request, company_id: Optional[int] = None):
    company = None
    if company_id:
        company = instance.get_company(int(company_id))

    return templates.TemplateResponse(
        "new_visit.html",
        {
            "request": request,
            "company_id": company_id,
            "company": company
        }
    )


@router.post("/new")
def submit_visit(
    request: Request,
    notes: str = Form(...),
    company_id: str = Form(None)
):
    # Normalize company_id
    if company_id in (None, "", "None"):
        company_id_int = None
    else:
        company_id_int = int(company_id)

    # Run notes through the full pipeline
    record = build_visit_record(notes)

    # Save visit with company context
    add_visit(record, company_id_int)

    return RedirectResponse("/timeline", status_code=303)


@router.get("/freenotes")
def freenotes_list_page(request: Request):
    notes = load_freenotes()
    notes = sorted(notes, key=lambda n: n["timestamp"], reverse=True)
    return templates.TemplateResponse(
        "freenotes_list.html",
        {"request": request, "notes": notes}
    )

@router.get("/freenotes/new")
def freenotes_new_page(request: Request):
    return templates.TemplateResponse(
        "freenotes_new.html",
        {"request": request}
    )

@router.post("/freenotes/new")
def freenotes_new_submit(
    note: str = Form(...)
):
    add_freenote(note)
    return RedirectResponse("/freenotes", status_code=303)

@router.get("/freenotes/{note_id}")
def freenote_detail(request: Request, note_id: int):
    note = get_freenote(note_id)
    return templates.TemplateResponse(
        "freenote_detail.html",
        {"request": request, "note": note}
    )

 
@router.get("/visit/{visit_id}/edit")
def edit_visit_page(request: Request, visit_id: str):
    visit = get_visit(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    return templates.TemplateResponse(
        "edit_visit.html",
        {"request": request, "visit": visit}
    )

@router.post("/visit/{visit_id}/edit")
def edit_visit_submit(
    visit_id: str,
    notes: str = Form(...)
):
    visit = get_visit(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")

    # Update raw notes
    visit.raw_notes = notes

    # Re-run pipeline for updated fields
    updated = build_visit_record(notes)

    visit.normalized_notes = updated.normalized_notes
    visit.structured_summary = updated.structured_summary
    visit.insights = updated.insights
    visit.recommended_next_steps = updated.recommended_next_steps
    visit.narrative = updated.narrative

    save_visits(store.VISIT_STORE)
    return RedirectResponse(f"/visit/{visit_id}", status_code=303)


@router.post("/visit/{visit_id}/delete")
def delete_visit(visit_id: str):
    store.VISIT_STORE = [v for v in store.VISIT_STORE if v.visit_id != visit_id]
    save_visits(store.VISIT_STORE)
    return RedirectResponse("/timeline", status_code=303)

@router.get("/freenotes/{note_id}/edit")
def freenote_edit_form(request: Request, note_id: int):
    note = get_freenote(note_id)
    return templates.TemplateResponse(
        "freenote_edit.html",
        {"request": request, "note": note}
    )


@router.post("/freenotes/{note_id}/edit")
def freenote_edit_submit(note_id: int, text: str = Form(...)):
    update_freenote(note_id, text)
    return RedirectResponse(f"/freenotes/{note_id}", status_code=303)


@router.get("/freenotes/{note_id}/delete")
def freenote_delete(request: Request, note_id: int):
    delete_freenote(note_id)
    return RedirectResponse("/freenotes", status_code=303)


@router.get("/daily3")
def daily3_page(request: Request, date: str | None = None):
    if date is None:
        date = datetime.now().date().isoformat()


    current = datetime.fromisoformat(date)
    yesterday = (current - timedelta(days=1)).date().isoformat()
    tomorrow = (current + timedelta(days=1)).date().isoformat()

    entry = store.load_daily3_for_date(date)

    # compute completion dynamically
    computed_completion = 0
    if entry:
        for key in ["b1_result", "b2_result", "b3_result"]:
            val = entry.get(key, "")
            if isinstance(val, str) and val.strip().lower() == "done":
                computed_completion += 1

    return templates.TemplateResponse(
        "daily3.html",
        {
            "request": request,
            "entry": entry,
            "date": date,
            "yesterday": yesterday,
            "tomorrow": tomorrow,
            "computed_completion": computed_completion,
        }
    )


@router.post("/daily3")
def daily3_submit(
    request: Request,
    date: str = Form(...),
    b1_plan: str = Form(""),
    b1_result: str = Form("none"),
    b1_outcome: str = Form(""),
    b2_plan: str = Form(""),
    b2_result: str = Form("none"),
    b2_outcome: str = Form(""),
    b3_plan: str = Form(""),
    b3_result: str = Form("none"),
    b3_outcome: str = Form(""),
    completion: str = Form("0"),
    energy: str = Form("steady"),
    notes: str = Form("")
):
    entry = {
        "b1_plan": b1_plan,
        "b1_result": b1_result,
        "b1_outcome": b1_outcome,
        "b2_plan": b2_plan,
        "b2_result": b2_result,
        "b2_outcome": b2_outcome,
        "b3_plan": b3_plan,
        "b3_result": b3_result,
        "b3_outcome": b3_outcome,
        "energy": energy,
        "notes": notes,
    }

    store.save_daily3_for_date(date, entry)

    return RedirectResponse(f"/daily3?date={date}", status_code=303)



@router.get("/daily3/summary")
def daily3_dashboard(request: Request):
    today_entry = store.load_daily3_for_today()
    metrics = store.compute_weekly_metrics()

    # --- Compute today's completion dynamically ---
    computed_completion = 0
    if today_entry:
        for key in ["b1_result", "b2_result", "b3_result"]:
            val = today_entry.get(key, "")
            if isinstance(val, str) and val.strip().lower() == "done":
                computed_completion += 1

    return templates.TemplateResponse(
        "daily3_dashboard.html",
        {
            "request": request,
            "today_entry": today_entry,
            "metrics": metrics,
            "computed_completion": computed_completion,
        }
    )




