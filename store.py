from models import Company
from datetime import datetime, timezone
import json
from pathlib import Path

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
VISIT_STORE = []


FREENOTES_FILE = Path("data/freenotes.json")

def load_freenotes():
    if not FREENOTES_FILE.exists():
        return []
    return json.loads(FREENOTES_FILE.read_text())

def save_freenotes(notes):
    FREENOTES_FILE.write_text(json.dumps(notes, indent=2))


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

