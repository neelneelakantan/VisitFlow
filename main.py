from fastapi import FastAPI
from routes_api import router as api_router
from routes_pages import router as pages_router

# Enforce local-only execution for MVP 1.0
import os
import sys

ALLOWED_HOST = "127.0.0.1"

def enforce_local_only():
    # If VISITFLOW_HOST is set, validate it
    env_host = os.environ.get("VISITFLOW_HOST")
    if env_host and env_host != ALLOWED_HOST:
        print(f"ERROR: VisitFlow can only run on {ALLOWED_HOST}.")
        sys.exit(1)

    # If uvicorn is started with a different host, block it
    cli_host = None
    for arg in sys.argv:
        if arg.startswith("--host"):
            parts = arg.split("=", 1)
            if len(parts) == 2:
                cli_host = parts[1].strip()

    if cli_host and cli_host != ALLOWED_HOST:
        print(f"ERROR: VisitFlow can only run on {ALLOWED_HOST}.")
        sys.exit(1)

enforce_local_only()

app = FastAPI()

# Clean separation between API and UI
app.include_router(api_router, prefix="/api")
app.include_router(pages_router)

@app.get("/status")
def read_root():
    return {"status": "VisitFlow running"}



