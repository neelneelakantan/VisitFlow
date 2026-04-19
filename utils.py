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
        if not company.specific_date:
            return None

        # Parse the milestone date and ensure timezone-aware
        milestone_date = datetime.fromisoformat(company.specific_date)
        if milestone_date.tzinfo is None:
            milestone_date = milestone_date.replace(tzinfo=timezone.utc)

        today = datetime.now(timezone.utc)
        last_visit = company.last_checked

        # Before the milestone → upcoming / due today
        if today.date() <= milestone_date.date():
            return milestone_date

        # After the milestone:
        # If no visit after the milestone → overdue
        if last_visit is None or last_visit < milestone_date:
            return milestone_date

        # If visited after the milestone → clear overdue
        return None

    return None

