from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import uuid

class Company(BaseModel):
    id: int
    name: str
    url: str
    value: str = "medium"

    # Old field (still supported)
    cadence_days: int = 7

    # New fields
    frequency: str = "weekly"   # default matches cadence_days=7
    specific_date: Optional[str] = None  # ISO date string like "2026-04-01"

    status: str = "active"
    reason: str = ""
    notes: str = ""
    last_checked: Optional[datetime] = None
    last_applied: Optional[datetime] = None
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
    frequency: Optional[str] = None
    specific_date: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    value: Optional[str] = None
    cadence_days: Optional[int] = None
    status: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    frequency: Optional[str] = None
    specific_date: Optional[str] = None


class ApplyNote(BaseModel):
    note: str


class VisitRecord(BaseModel):
    visit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    company_id: Optional[int] = None

    raw_notes: str
    normalized_notes: Optional[str] = None

    structured_summary: Optional[Dict[str, Any]] = None
    insights: Optional[Dict[str, Any]] = None
    recommended_next_steps: Optional[List[str]] = None

    tags: Optional[List[str]] = None
    confidence: Optional[float] = None
    narrative: Optional[str] = None


class FreeNote(BaseModel):
    id: int
    timestamp: str
    text: str
    template_type: Optional[str] = None


