from fastapi import FastAPI
from routes_api import router as api_router
from routes_pages import router as pages_router

# VisitFlow is designed to run on 127.0.0.1 in MVP 1.0.
# OS and browser warnings provide sufficient protection if bound to other interfaces.

app = FastAPI()

# Clean separation between API and UI
app.include_router(api_router, prefix="/api")
app.include_router(pages_router)

@app.get("/status")
def read_root():
    return {"status": "VisitFlow running"}



