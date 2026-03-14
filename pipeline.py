
from models import VisitRecord
from datetime import datetime


# -----------------------------
# 1. INGEST
# -----------------------------
def ingest_notes(raw_text: str) -> VisitRecord:
    """Create a VisitRecord with raw notes and timestamp."""
    return VisitRecord(
        raw_notes=raw_text,
        timestamp=datetime.utcnow()
    )


# -----------------------------
# 2. NORMALIZE
# -----------------------------
def normalize_text(text: str) -> str:
    """Clean and normalize user input."""
    # Minimal placeholder logic
    cleaned = text.strip()
    cleaned = " ".join(cleaned.split())  # collapse whitespace
    return cleaned


# -----------------------------
# 3. EXTRACT STRUCTURE
# -----------------------------
def extract_structure(normalized: str) -> dict:
    """Extract themes, bullets, key points."""
    # Placeholder structure
    return {
        "themes": [],
        "key_points": [],
        "actions": []
    }


# -----------------------------
# 4. GENERATE INSIGHTS
# -----------------------------
def generate_insights(structured: dict) -> dict:
    """
    Generate simple insights based on structure:
    - observations: what happened
    - patterns: signals across key points or actions
    """
    observations = []
    patterns = []

    # Observation: if there are actions, user is moving forward
    if structured.get("actions"):
        observations.append("You identified at least one concrete action.")

    # Observation: if progress theme appears
    if "progress" in structured.get("themes", []):
        observations.append("You made progress today.")

    # Observation: if recruiter theme appears
    if "recruiter" in structured.get("themes", []):
        observations.append("You are engaging with recruiters.")

    # Pattern: if multiple key points mention the same topic
    key_points = structured.get("key_points", [])
    if len(key_points) > 1:
        patterns.append("You are tracking multiple threads in this visit.")

    return {
        "observations": observations,
        "patterns": patterns
    }


# -----------------------------
# 5. RECOMMEND NEXT STEPS
# -----------------------------
def generate_next_steps(structured: dict, insights: dict) -> list:
    """Suggest actionable next steps."""
    return [
        "Reflect on the key points.",
        "Identify one concrete action for tomorrow."
    ]


# -----------------------------
# 6. PACKAGE RESPONSE
# -----------------------------
def build_visit_record(raw_text: str) -> VisitRecord:
    """Full pipeline: ingest → normalize → extract → insights → next steps."""
    record = ingest_notes(raw_text)

    record.normalized_notes = normalize_text(record.raw_notes)
    record.structured_summary = extract_structure(record.normalized_notes)
    record.insights = generate_insights(record.structured_summary)
    # Add sentiment/energy detection
    record.insights["sentiment_energy"] = detect_sentiment_energy(record.normalized_notes)
    record.narrative = generate_narrative(record)

    record.recommended_next_steps = generate_next_steps(
        record.structured_summary,
        record.insights
    )

    return record


##### build sentiment light weight logic, can be swapped in future.  
def detect_sentiment_energy(text: str) -> dict:
    """
    Lightweight heuristic-based sentiment and energy detection.
    This is intentionally simple for MVP and can be replaced later.
    """
    lowered = text.lower()

    positive_words = ["good", "great", "excited", "progress", "confident"]
    negative_words = ["stuck", "worried", "bad", "frustrated", "tired"]
    high_energy_words = ["excited", "ready", "moving", "momentum"]
    low_energy_words = ["tired", "drained", "slow", "overwhelmed"]

    sentiment = "neutral"
    energy = "medium"

    if any(w in lowered for w in positive_words):
        sentiment = "positive"
    elif any(w in lowered for w in negative_words):
        sentiment = "negative"

    if any(w in lowered for w in high_energy_words):
        energy = "high"
    elif any(w in lowered for w in low_energy_words):
        energy = "low"

    return {
        "sentiment": sentiment,
        "energy": energy
    }


def extract_structure(normalized: str) -> dict:
    """
    Lightweight structure extraction:
    - key points: split into sentences
    - actions: detect verbs like 'call', 'email', 'apply', 'follow up'
    - themes: detect categories like recruiter, interview, progress, blockers
    """
    text = normalized.lower()

    # Sentence-level key points
    key_points = [s.strip() for s in normalized.split('.') if s.strip()]

    # Simple action detection
    action_verbs = ["call", "email", "apply", "follow up", "schedule", "prepare"]
    actions = [kp for kp in key_points if any(v in kp.lower() for v in action_verbs)]

    # Simple theme detection
    themes = []
    if "recruiter" in text:
        themes.append("recruiter")
    if "interview" in text:
        themes.append("interview")
    if "progress" in text:
        themes.append("progress")
    if "stuck" in text or "blocked" in text:
        themes.append("blocker")

    return {
        "themes": themes,
        "key_points": key_points,
        "actions": actions
    }


def generate_narrative(record: VisitRecord) -> str:
    """
    Adaptive narrative engine: warm, supportive, contextual, and lightly tactical.
    """
    parts = []

    visit_type = detect_visit_type(record.structured_summary)
    se = record.insights.get("sentiment_energy", {})
    sentiment = se.get("sentiment", "neutral")
    energy = se.get("energy", "medium")

    # --- Visit-type adaptive opening ---
    if visit_type == "interview":
        parts.append("You focused deeply today — interview days require presence, not volume.")
        parts.append("Your attention was exactly where it needed to be.")
    elif visit_type == "networking":
        parts.append("You expanded your surface area today — these connections compound over time.")
    elif visit_type == "followup":
        parts.append("You kept your loops tight today — that consistency is one of your strengths.")
    elif visit_type == "learning":
        parts.append("You invested in your learning today — that builds long-term leverage.")
    elif visit_type == "progress":
        parts.append("You’re building steady forward motion — keep leaning into what’s working.")
    elif visit_type == "blocker":
        parts.append("Even when things stall, you’re staying engaged — that’s real resilience.")
    else:
        # general
        if sentiment == "positive":
            parts.append("You showed good momentum today.")
        elif sentiment == "negative":
            parts.append("Today carried some weight, but you still showed up.")
        else:
            parts.append("You took the time to reflect today — that consistency matters.")

    # --- Energy calibration ---
    if energy == "high":
        parts.append("Your energy feels focused and engaged.")
    elif energy == "low":
        parts.append("Your energy feels a bit low — that’s completely normal. What matters is you stayed intentional.")

    # --- Key points ---
    key_points = record.structured_summary.get("key_points", [])
    if key_points:
        parts.append("Here’s what stood out from your notes:")
        for kp in key_points:
            parts.append(f"- {kp}")

    # --- Observations ---
    observations = record.insights.get("observations", [])
    if observations:
        parts.append("A few things worth acknowledging:")
        for obs in observations:
            parts.append(f"- {obs}")

    # --- Patterns ---
    patterns = record.insights.get("patterns", [])
    if patterns:
        parts.append("There are some patterns emerging:")
        for p in patterns:
            parts.append(f"- {p}")

    # --- Myth-busting nudges ---
    if visit_type == "interview":
        parts.append("You don’t need to chase early-application windows — your value isn’t tied to timing.")
        parts.append("Interview days are for clarity, not volume.")

    micro = generate_micro_insights(record.structured_summary, record.insights)
    if micro:
        parts.append("A few subtle patterns worth noticing:")
        for m in micro:
            parts.append(f"- {m}")

    trends = detect_emotional_trends(record.structured_summary, record.insights)
    if trends:
        parts.append("A few emotional signals worth noticing:")
        for t in trends:
            parts.append(f"- {t}")
    
    # --- Next steps ---
    next_steps = record.recommended_next_steps
    if next_steps:
        parts.append("A couple of simple next steps to keep your momentum steady:")
        for step in next_steps:
            parts.append(f"- {step}")

    # --- Closing ---
    parts.append("You’re navigating this with clarity and discipline — keep going at a human pace.")

    return "\n".join(parts)


def detect_visit_type(structured: dict) -> str:
    """
    Infer visit type based on themes and key phrases.
    """
    themes = structured.get("themes", [])
    text = " ".join(structured.get("key_points", [])).lower()

    if "interview" in themes or "prep" in text or "ta screen" in text:
        return "interview"

    if "recruiter" in themes or "network" in text or "webinar" in text or "event" in text:
        return "networking"

    if "follow" in text or "follow-up" in text or "follow up" in text:
        return "followup"

    if "learning" in text or "course" in text or "keywords" in text or "research" in text:
        return "learning"

    if "progress" in themes:
        return "progress"

    if "blocked" in themes or "stalled" in text or "no response" in text or "rejected" in text:
        return "blocker"

    return "general"


def generate_micro_insights(structured: dict, insights: dict) -> list:
    """
    Lightweight micro-insights engine.
    Surfaces small, meaningful patterns that help the user stay intentional.
    """
    micro = []
    themes = structured.get("themes", [])
    actions = structured.get("actions", [])
    key_points = structured.get("key_points", [])
    sentiment = insights.get("sentiment_energy", {}).get("sentiment")
    energy = insights.get("sentiment_energy", {}).get("energy")

    text = " ".join(key_points).lower()

    # Follow-up rhythm
    if any("follow" in kp.lower() for kp in key_points):
        micro.append("Your follow-up rhythm is consistent — that’s one of your quiet strengths.")

    # Learning streak
    if any(word in text for word in ["learning", "course", "review", "keywords"]):
        micro.append("Your learning cadence is picking up — that compounds over time.")

    # Networking cluster
    if any(word in text for word in ["connected", "reached out", "network", "webinar", "event"]):
        micro.append("You expanded your surface area — these relationships build optionality.")

    # Emotional cadence
    if sentiment == "positive" and energy == "low":
        micro.append("You made progress even on a low-energy day — that’s real discipline.")

    # Blocker awareness
    if any(word in text for word in ["stalled", "no response", "paused", "rejected"]):
        micro.append("A few threads are quiet right now — that’s normal in an asymmetric process.")

    return micro


def detect_emotional_trends(structured: dict, insights: dict) -> list:
    """
    Lightweight emotional trend awareness based on the shape of the current visit.
    No history required — uses density, tone, and cognitive load to infer trends.
    """
    trends = []

    key_points = structured.get("key_points", [])
    actions = structured.get("actions", [])
    patterns = insights.get("patterns", [])
    sentiment = insights.get("sentiment_energy", {}).get("sentiment")
    energy = insights.get("sentiment_energy", {}).get("energy")

    # Cognitive load: many key points
    if len(key_points) >= 3:
        trends.append("You’re carrying several threads today — pacing yourself will help.")

    # Execution mode: multiple actions
    if len(actions) >= 2:
        trends.append("You’re in an execution phase — good moment to convert clarity into action.")

    # Emotional resilience: positive sentiment + low energy
    if sentiment == "positive" and energy == "low":
        trends.append("You made progress even on a low-energy day — that’s real discipline.")

    # Reflective mode: neutral sentiment + multiple observations
    if sentiment == "neutral" and len(patterns) >= 1:
        trends.append("You’re in a reflective mode today — this often leads to clarity.")

    # Focused clarity: high energy + few threads
    if energy == "high" and len(key_points) <= 2:
        trends.append("Your focus feels sharp today — you’re in a clarity phase.")

    return trends

