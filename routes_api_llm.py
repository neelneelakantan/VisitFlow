# routes_api_llm.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

from fastapi.responses import JSONResponse
import store
from llm_client import LLMError, ask_gemini
import markdown
from store import load_insight_cache, save_insight_cache

router = APIRouter()
@router.get("/llm/weekly-insight")

def weekly_insight(start_date: str, end_date: str, force: bool = False):
    cache_key = f"{start_date}:{end_date}"
    cache = load_insight_cache()

    # Return cached result if available
    if not force and cache_key in cache:
        return {"insight_html": cache[cache_key]}

    # Otherwise compute insight

    """
    Generate an LLM insight over a date range.
    Dates must be ISO strings: YYYY-MM-DD.
    """

    try:
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    # Load Daily3 entries between dates
    entries = store.load_daily3_between(start, end)

    if not entries:
        return {"insight": "No entries found in this date range."}

    prompt = f"""
Analyze these Daily3 entries between {start_date} and {end_date}:

{entries}

Return ONLY the following, in 2–3 short bullet points each:

- 2 patterns you notice (max 20 words each)
- 1 thing to continue (max 20 words)
- 1 thing to adjust next week (max 20 words)
= if notes are present, also return 1 insight from the notes (max 20 words)

NO reflection paragraphs.
NO motivational tone.
NO storytelling.
NO filler.
Be concise, factual, and neutral.
"""

    try:
        result = ask_gemini(prompt)
        #return {"ok": True, "text": text}

    except LLMError as e:
        return JSONResponse(
            status_code=200,
            content={"ok": False, "error_code": e.code, "message": e.message}
        )

    html = markdown.markdown(result)
 
    # Save/overwrite to cache
    cache[cache_key] = html
    save_insight_cache(cache)

    return {"insight_html": html}
