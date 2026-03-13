from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional

class Company(BaseModel):
    id: int
    name: str
    url: str
    value: str = "medium"
    cadence_days: int = 7
    status: str = "active"
    reason: str = ""
    notes: str = ""
    last_checked: Optional[datetime] = None
    last_applied: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CompanyCreate(BaseModel):
    name: str
    url: str
    value: Optional[str] = None
    cadence_days: Optional[int] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    value: Optional[str] = None
    cadence_days: Optional[int] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None

class ApplyNote(BaseModel):
    note: str

    