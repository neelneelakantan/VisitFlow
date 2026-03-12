from fastapi import FastAPI
from datetime import datetime, timezone, timedelta
from fastapi.templating import Jinja2Templates
from fastapi import Request
from routes_api import router as api_router
from routes_pages import router as pages_router

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.include_router(api_router)
app.include_router(pages_router)

#print(app.routes)

@app.get("/")
def read_root():
    return {"status": "VisitFlow running"}



