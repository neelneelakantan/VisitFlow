from models import Company, VisitRecord
from datetime import datetime, timezone
import json
from pathlib import Path


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
def add_visit(record: VisitRecord, company_id: int):
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
        companies = load_companies()

        # Convert list → dict keyed by company.id
        self.companies = {c.id: c for c in companies}

        # Compute next_id safely
        if companies:
            self.next_id = max(c.id for c in companies) + 1
        else:
            self.next_id = 1


    def add_company(self, company: Company):
        company.id = self.next_id
        self.companies[self.next_id] = company
        self.next_id += 1

        # Persist to disk
        save_companies(list(self.companies.values()))
        return company


    def get_company(self, company_id: int):
        return self.companies.get(company_id)
    

    def list_companies(self):
        return list(self.companies.values())


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

