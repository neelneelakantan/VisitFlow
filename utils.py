from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

def compute_next_check(company):
    """Return the next date this company should be checked."""
    freq = company.frequency
    last = company.last_checked or company.created_at

    # Normalize to datetime
    if isinstance(last, str):
        last = datetime.fromisoformat(last)

    if freq == "none":
        return None

    if freq == "daily":
        return last + timedelta(days=1)

    if freq == "weekly":
        # cadence_days still supported
        return last + timedelta(days=company.cadence_days)

    if freq == "monthly":
        return last + relativedelta(months=1)

    if freq == "custom":
        return last + timedelta(days=company.cadence_days)

    if freq == "specific_date":
        if company.specific_date:
            return datetime.fromisoformat(company.specific_date)
        return None

    return None

