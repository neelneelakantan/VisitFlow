# followup_engine.py
import re
from datetime import datetime, timedelta, timezone

INTERVIEW_REGEX = re.compile(r"(interview|screen|loop|call|recruiter|hiring|talent)", re.IGNORECASE)
FOLLOWUP_REGEX = re.compile(r"(follow.?up|thank.?you|sent.?email)", re.IGNORECASE)

def detect_interviews(entries):
    interviews = []
    for e in entries:
        if INTERVIEW_REGEX.search(e["text"]):
            interviews.append(e)
    return interviews

def detect_followups(entries):
    followups = []
    for e in entries:
        if FOLLOWUP_REGEX.search(e["text"]):
            followups.append(e)
    return followups

def find_pending_followups(entries):
    interviews = detect_interviews(entries)
    followups = detect_followups(entries)

    pending = []

    for iv in interviews:
        company = iv["company"]
        iv_time = iv["timestamp"]

        # Find followups for same company after interview
        fups = [
            f for f in followups
            if f["company"] == company and f["timestamp"] > iv_time
        ]

        if not fups:
            # Check if >24 hours passed
            now = datetime.now(timezone.utc)
            if now - iv_time > timedelta(hours=24):
                pending.append(iv)

    return pending
