from models import Company
from datetime import datetime, timezone

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
