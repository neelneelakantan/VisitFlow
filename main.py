from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from routes_api import router as api_router
from routes_pages import router as pages_router
from datetime import datetime

from templates_engine import templates
from store import VISIT_STORE

app = FastAPI()

# Clean separation between API and UI
app.include_router(api_router, prefix="/api")
app.include_router(pages_router)

@app.get("/")
def read_root():
    return {"status": "VisitFlow running"}


@app.get("/api/visits")
def list_visits():
    return [
        {
            "visit_id": v.visit_id,
            "timestamp": v.timestamp,
            "summary": v.structured_summary.get("key_points", []),
            "sentiment": v.insights.get("sentiment_energy", {}).get("sentiment"),
            "energy": v.insights.get("sentiment_energy", {}).get("energy")
        }
        for v in VISIT_STORE
    ]

@app.get("/api/visit/{visit_id}")
def get_visit(visit_id: str):
    for v in VISIT_STORE:
        if v.visit_id == visit_id:
            return v
    return {"error": "Visit not found"}


