from fastapi import FastAPI
from models import Bookmark
from typing import List
from datetime import datetime, timezone, timedelta
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "VisitFlow running"}

app = FastAPI()

bookmarks: List[Bookmark] = []

@app.post("/bookmarks")
def add_bookmark(bookmark: Bookmark):
    bookmarks.append(bookmark)
    return {"message": "Bookmark added", "bookmark": bookmark}

@app.get("/bookmarks")
def list_bookmarks():
    return bookmarks

@app.get("/bookmarks/overdue/view")
def view_overdue(request: Request):
    overdue_items = [b for b in bookmarks if is_overdue(b)]
    return templates.TemplateResponse(
        "overdue.html",
        {"request": request, "overdue": overdue_items}
    )

@app.get("/bookmarks/view")
def view_bookmarks(request: Request):
    return templates.TemplateResponse(
        "bookmarks.html",
        {"request": request, "bookmarks": bookmarks}
    )

@app.post("/bookmarks/{bookmark_id}/visit")
def mark_visited(bookmark_id: int):
    for b in bookmarks:
        if b.id == bookmark_id:
            b.last_visited = datetime.now(timezone.utc)
            return {"message": "Marked as visited", "bookmark": b}
    return {"error": "Bookmark not found"}

def is_overdue(bookmark: Bookmark) -> bool:
    if bookmark.last_visited is None:
        return True

    now = datetime.now(timezone.utc)

    if bookmark.cadence == "daily":
        return now - bookmark.last_visited > timedelta(days=1)
    if bookmark.cadence == "weekly":
        return now - bookmark.last_visited > timedelta(weeks=1)
    if bookmark.cadence == "monthly":
        return now - bookmark.last_visited > timedelta(days=30)

    return False


@app.get("/bookmarks/overdue")
def list_overdue():
    overdue_items = [b for b in bookmarks if is_overdue(b)]
    return overdue_items

