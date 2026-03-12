from models import Company

companies = {}
next_id = 1

def add_company(company: Company):
    global next_id

    # Assign ID here
    company.id = next_id

    companies[next_id] = company
    next_id += 1

    return company
