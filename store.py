from models import Company, VisitRecord
from datetime import date, datetime, timezone, timedelta
import json
import re
from pathlib import Path
from typing import Optional


# 1. Define file path FIRST
BASE_DIR = Path(__file__).resolve().parent
VISITS_FILE = BASE_DIR / "data" / "visits.json"
VISITS_FILE.parent.mkdir(exist_ok=True)

COMPANIES_FILE = BASE_DIR / "data" / "companies.json"
COMPANIES_FILE.parent.mkdir(exist_ok=True)


# 2. Define load/save helpers
def load_visits():
    if not VISITS_FILE.exists():
        return []
    try:
        raw = json.loads(VISITS_FILE.read_text())
        visits = [VisitRecord.model_validate(v) for v in raw]
        return visits
    except Exception as e:
        print("Error loading visits:", e)
        return []
    

def save_visits(visits):
    data = [v.model_dump(mode="json") for v in visits]
    VISITS_FILE.write_text(json.dumps(data, indent=2))


def load_companies():
    """Load companies from disk into a list of Company models."""
    if not COMPANIES_FILE.exists():
        return []

    try:
        raw = json.loads(COMPANIES_FILE.read_text())
        companies = [Company.model_validate(c) for c in raw]

        return companies
    except Exception as e:
        print("Error loading companies:", e)
        return []


def save_companies(companies):
    """Persist list of Company models to disk."""
    data = [c.model_dump(mode="json") for c in companies]
    COMPANIES_FILE.write_text(json.dumps(data, indent=2))


# 3. Initialize global store AFTER helpers exist
VISIT_STORE = load_visits()  
COMPANY_STORE = load_companies()

# 4. add_visit helper
def add_visit(record: VisitRecord, company_id: Optional[int]):
    record.company_id = company_id
    VISIT_STORE.append(record)
    save_visits(VISIT_STORE)
    return record

def get_visit(visit_id: str):
    for v in VISIT_STORE:
        if v.visit_id == visit_id:
            return v
    return None


class Store:
    def __init__(self):
        # Load companies from disk
        self.companies = load_companies()

        # Convert list → dict keyed by company.id
        self.companies = {c.id: c for c in self.companies}

        if self.companies:
            # Option A: from keys
            self.next_id = max(self.companies.keys()) + 1
            # or Option B: from values
            # self.next_id = max(c.id for c in self.companies.values()) + 1
        else:
            self.next_id = 1
        # Compute next_id safely


    def add_company(self, company: Company):
        company.id = self.next_id
        self.companies[self.next_id] = company
        self.next_id += 1

        # Persist to disk
        save_companies(list(self.companies.values()))
        return company

    def purge_deleted_companies(self):
        self.companies = {
            cid: c for cid, c in self.companies.items()
            if c.status != "deleted"
        }
        save_companies(list(self.companies.values()))


    def get_company(self, company_id: int):
        return self.companies.get(company_id)
    

    def list_companies(self):
        return [c for c in self.companies.values() if c.status != "deleted"]

    def list_deleted_companies(self):
        return [c for c in self.companies.values() if c.status == "deleted"]


    def mark_visited(self, company_id: int):
        company = self.companies[company_id]
        company.last_checked = datetime.now(timezone.utc)

        save_companies(list(self.companies.values()))
        return company


    def mark_applied(self, company_id: int):
        company = self.companies[company_id]
        now = datetime.now(timezone.utc)

        company.last_applied = now
        company.updated_at = now

        save_companies(list(self.companies.values()))
        return company


# Global instance
instance = Store()
# DO NOT reset VISIT_STORE here
#VISIT_STORE = []

instance.FREENOTES_FILE = BASE_DIR / "data" / "freenotes.json"

def load_freenotes():
    if not instance.FREENOTES_FILE.exists():
        return []
    return json.loads(instance.FREENOTES_FILE.read_text())

def save_freenotes(notes):
    instance.FREENOTES_FILE.write_text(json.dumps(notes, indent=2))


def add_freenote(text, template_type=None):
    notes = load_freenotes()
    new_id = max([n["id"] for n in notes], default=0) + 1
    note = {
        "id": new_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text": text,
        "template_type": template_type
    }
    notes.append(note)
    save_freenotes(notes)
    return note

def get_freenote(note_id: int):
    notes = load_freenotes()
    for n in notes:
        if n["id"] == note_id:
            return n
    return None


def update_freenote(note_id: int, text: str):
    notes = load_freenotes()
    for n in notes:
        if n["id"] == note_id:
            n["text"] = text
            save_freenotes(notes)
            return n
    return None


def delete_freenote(note_id: int):
    notes = load_freenotes()
    notes = [n for n in notes if n["id"] != note_id]
    save_freenotes(notes)


DAILY3_FILE = BASE_DIR / "data" / "daily3.json"
DAILY3_FILE.parent.mkdir(exist_ok=True)


def load_daily3():
    if not DAILY3_FILE.exists():
        return {}

    text = DAILY3_FILE.read_text().strip()
    if not text:
        return {}  # empty file → treat as empty dict

    try:
        return json.loads(text)
    except Exception:
        return {}  # corrupted file → reset to empty


def save_daily3(data):
    DAILY3_FILE.write_text(json.dumps(data, indent=2))

def load_daily3_for_today():
    data = load_daily3()
    today = datetime.now().date().isoformat()
    return data.get(today)

def save_daily3_for_today(entry):
    data = load_daily3()
    today = datetime.now(timezone.utc).date().isoformat()
    data[today] = entry
    save_daily3(data)



def compute_weekly_metrics():
    today = datetime.now().date()
    week_start = today - timedelta(days=6)

    data = load_daily3()

    blocks_done = 0
    energy_values = []
    completion_values = []

    for date_str, entry in data.items():
        try:
            d = datetime.fromisoformat(date_str).date()
        except:
            continue

        if d < week_start or d > today:
            continue

        # Count blocks done
        for key in ["b1_result", "b2_result", "b3_result"]:
            if entry.get(key, "").strip().lower() == "done":
                blocks_done += 1

        # Energy trend
        if "energy" in entry:
            energy_values.append(entry["energy"])

        # Completion trend
        if "completion" in entry:
            try:
                completion_values.append(int(entry["completion"]))
            except:
                pass

    return {
        "blocks_done": blocks_done,
        "energy_values": energy_values,
        "completion_values": completion_values,
        "week_start": week_start.isoformat(),
        "week_end": today.isoformat(),
    }



def load_daily3_for_date(date_str: str):
    data = load_daily3()
    return data.get(date_str)


def save_daily3_for_date(date_str: str, entry: dict):
    data = load_daily3()
    data[date_str] = entry
    save_daily3(data)


HARVESTER_FILE = BASE_DIR / "data" / "harvester.json"
HARVESTER_FILE.parent.mkdir(exist_ok=True)

def load_harvester():
    data = load_json("harvester.json", default=[])
    normalized = []

    for item in data:
        if isinstance(item, str):
            normalized.append({
                "name": item,
                "source_url": None,
                "careers_url": None,
                "last_visited": None,
            })
        else:
            # ensure field exists
            if "last_visited" not in item:
                item["last_visited"] = None
            normalized.append(item)

    # --- SORTING: never visited → oldest → newest ---
    def sort_key(e):
        ts = e.get("last_visited")
        if not ts:
            return (0, datetime.min)  # never visited → top
        return (1, datetime.fromisoformat(ts))

    return sorted(normalized, key=sort_key)



def save_harvester(items: list[str]):
    items = sorted(items, key=lambda x: x.lower())
    HARVESTER_FILE.write_text(json.dumps(items, indent=2))


def mark_harvester_visited(name: str):
    data = load_harvester()
    now = datetime.now(timezone.utc).isoformat()

    for entry in data:
        if entry["name"] == name:
            entry["last_visited"] = now

    save_harvester(data)


INSIGHT_CACHE_PATH = Path("data/insight_cache.json")

def load_insight_cache():
    if INSIGHT_CACHE_PATH.exists():
        return json.loads(INSIGHT_CACHE_PATH.read_text())
    return {}

def save_insight_cache(cache):
    INSIGHT_CACHE_PATH.write_text(json.dumps(cache, indent=2))


def load_daily3_between(start: date, end: date):
    """
    Load Daily3 entries between two dates (inclusive).
    Returns a list of dicts.
    """
    results = []
    current = start

    while current <= end:
        iso = current.isoformat()
        entry = load_daily3_for_date(iso)
        if entry:
            results.append({
                "date": iso,
                "entry": entry
            })
        current += timedelta(days=1)

    return results


import json
import os
from urllib.parse import urlparse

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_json(filename, default):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# -----------------------------
# Harvester helpers
# -----------------------------

def load_harvester():
    data = load_json("harvester.json", default=[])
    normalized = []

    for item in data:
        if isinstance(item, str):
            normalized.append({
                "name": item,
                "source_url": None,
                "careers_url": None,
                "last_visited": None,
            })
        else:
            # ensure field exists
            if "last_visited" not in item:
                item["last_visited"] = None
            normalized.append(item)

    # --- SORTING: never visited → oldest → newest ---
    def sort_key(e):
        ts = e.get("last_visited")
        if not ts:
            return (0, datetime.min)  # never visited → top
        return (1, datetime.fromisoformat(ts))

    return sorted(normalized, key=sort_key)


def save_harvester(data):
    save_json("harvester.json", data)


def normalize_company_name(slug: str) -> str:
    """
    Normalize a Workday-style slug into a clean company name.
    Examples:
      Accurate_Careers → Accurate
      acme-careers → Acme
      AcmeCareers → Acme
    """
    # Remove trailing Careers (with optional _ or -)
    slug = re.sub(r"[_-]?Careers$", "", slug, flags=re.IGNORECASE)

    # Replace separators for readability
    slug = slug.replace("_", " ").replace("-", " ")

    return slug.title().strip()


def extract_company_from_url(url: str):
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    path_parts = [p for p in parsed.path.split("/") if p]

    # -----------------------------
    # Workable
    # -----------------------------
    if "workable.com" in domain and len(path_parts) >= 1:
        slug = path_parts[0]
        company = slug.replace("-", " ").title()
        careers_url = f"https://{domain}/{slug}/"
        return company, careers_url

    # -----------------------------
    # Lever
    # -----------------------------
    if "lever.co" in domain and len(path_parts) >= 1:
        slug = path_parts[0]
        company = slug.replace("-", " ").title()
        careers_url = f"https://{domain}/{slug}"
        return company, careers_url

    # -----------------------------
    # Greenhouse
    # -----------------------------
    if "greenhouse.io" in domain and len(path_parts) >= 1:
        slug = path_parts[0]  # first segment is the company
        company = slug.replace("-", " ").title()
        careers_url = f"https://{domain}/{slug}"
        #print(f"DEBUG: Greenhouse URL detected. domain='{domain}', path_parts={path_parts}")
        return company, careers_url

    # -----------------------------
    # SmartRecruiters
    # -----------------------------
    if "smartrecruiters.com" in domain and len(path_parts) >= 1:
        slug = path_parts[0]
        clean = re.sub(r"\d+$", "", slug)  # remove trailing digits
        company = clean.replace("-", " ").title()
        careers_url = f"https://{domain}/{slug}"
        return company, careers_url

    # -----------------------------
    # BambooHR
    # Example: https://acme.bamboohr.com/careers/123
    # -----------------------------
    if "bamboohr.com" in domain:
        sub = domain.split(".")[0]
        company = sub.replace("-", " ").title()
        careers_url = f"https://{domain}/careers"
        return company, careers_url

    # -----------------------------
    # Ashby
    # Example: https://jobs.ashbyhq.com/acme/123
    # -----------------------------
    if "ashbyhq.com" in domain and len(path_parts) >= 1:
        slug = path_parts[0]
        company = slug.replace("-", " ").title()
        careers_url = f"https://{domain}/{slug}"
        return company, careers_url

    # -----------------------------
    # JazzHR
    # Example: https://acme.applytojob.com/apply/123
    # -----------------------------
    if "applytojob.com" in domain:
        sub = domain.split(".")[0]
        company = sub.replace("-", " ").title()
        careers_url = f"https://{domain}"
        return company, careers_url

    # -----------------------------
    # Workday (correct extraction)
    # Example: https://acme.wd5.myworkdayjobs.com/en-US/AcmeCareers/job/...
    # -----------------------------
    if "myworkdayjobs.com" in domain:
        # domain example: workiva.wd503.myworkdayjobs.com
        host_parts = domain.split(".")
        company = host_parts[0]  # always the company name

        # careers URL is simply the base domain
        careers_url = f"https://{domain}"

        return company, careers_url


    # -----------------------------
    # Taleo (best effort)
    # Example: https://acme.taleo.net/careersection/...
    # -----------------------------
    if "taleo.net" in domain:
        sub = domain.split(".")[0]
        company = sub.replace("-", " ").title()
        careers_url = f"https://{domain}"
        return company, careers_url

    # -----------------------------
    # Indeed redirect URLs
    # Example: https://www.indeed.com/viewjob?jk=...
    # → cannot extract company reliably → fallback
    # -----------------------------
    if "indeed.com" in domain:
        company = "Indeed"
        careers_url = "https://indeed.com"
        return company, careers_url

    # -----------------------------
    # LinkedIn job URLs
    # Example: https://www.linkedin.com/jobs/view/123
    # → cannot extract company reliably → fallback
    # -----------------------------
    if "linkedin.com" in domain:
        company = "Linkedin"
        careers_url = "https://linkedin.com/jobs"
        return company, careers_url

    # -----------------------------
    # Fallback: domain-based extraction
    # -----------------------------
    company = domain.split(".")[0].replace("-", " ").title()
    careers_url = f"https://{domain}/careers"
    return company, careers_url



