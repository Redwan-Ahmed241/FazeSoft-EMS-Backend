"""
app/schemas/candidate.py — Pydantic schemas for Candidate.
"""
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CandidateCreate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    phone: Optional[str] = None
    position: str = Field(min_length=1)
    ai_score: int = Field(default=0, ge=0, le=100)
    experience: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    education: Optional[List[dict]] = Field(default_factory=list)
    certifications: Optional[List[str]] = Field(default_factory=list)
    status: str = Field(default="Applied")
    avatar: Optional[str] = None
    applied_date: Optional[date] = None
    match_reasons: Optional[List[str]] = Field(default_factory=list)


class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    ai_score: Optional[int] = Field(default=None, ge=0, le=100)
    experience: Optional[str] = None
    skills: Optional[List[str]] = None
    education: Optional[List[dict]] = None
    certifications: Optional[List[str]] = None
    avatar: Optional[str] = None
    match_reasons: Optional[List[str]] = None


class CandidateStatusUpdate(BaseModel):
    status: str = Field(description="One of: Applied, Screened, Interview, Offer, Hired, Approved, Rejected")


class CandidateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: Optional[str] = None
    position: str
    ai_score: int
    experience: Optional[str] = None
    skills: List[str] = []
    education: Optional[List[dict]] = []
    certifications: Optional[List[str]] = []
    status: str
    avatar: Optional[str] = None
    applied_date: date
    match_reasons: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime
