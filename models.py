from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Bookmark(BaseModel):
    id: int
    url: str
    notes: Optional[str] = None
    cadence: str  # "daily", "weekly", "monthly"
    last_visited: Optional[datetime] = None

    