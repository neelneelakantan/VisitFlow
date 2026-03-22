from models import Company, VisitRecord
from datetime import datetime, timezone
import json
from pathlib import Path


# 1. Define file path FIRST
BASE_DIR = Path(__file__).resolve().parent
VISITS_FILE = BASE_DIR / "data" / "visits.json"
VISITS_FILE.parent.mkdir(exist_ok=True)


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

# 3. Initialize global store AFTER helpers exist
VISIT_STORE = load_visits()  

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
        self.data = {}
        self.next_id = 1

    def add_company(self, company: Company):
        company.id = self.next_id
        self.data[self.next_id] = company
        self.next_id += 1
        return company

    def get_company(self, company_id: int):
        return self.data.get(company_id)

    def list_companies(self):
        return list(self.data.values())

    def update_company(self, company_id: int, **fields):
        company = self.data[company_id]
        for key, value in fields.items():
            setattr(company, key, value)
        return company

    def mark_visited(self, company_id: int):
        company = self.data[company_id]
        company.last_checked = datetime.now(timezone.utc)
        return company

    def mark_applied(self, company_id: int):
        company = self.data[company_id]
        company.last_applied = datetime.now(timezone.utc)
        return company

# Global instance
store = Store()
# DO NOT reset VISIT_STORE here
#VISIT_STORE = []

store.FREENOTES_FILE = BASE_DIR / "data" / "freenotes.json"

def load_freenotes():
    if not store.FREENOTES_FILE.exists():
        return []
    return json.loads(store.FREENOTES_FILE.read_text())

def save_freenotes(notes):
    store.FREENOTES_FILE.write_text(json.dumps(notes, indent=2))


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

