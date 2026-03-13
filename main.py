from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from routes_api import router as api_router
from routes_pages import router as pages_router
from datetime import datetime

from templates_engine import templates

app = FastAPI()

# Clean separation between API and UI
app.include_router(api_router, prefix="/api")
app.include_router(pages_router)

@app.get("/")
def read_root():
    return {"status": "VisitFlow running"}

