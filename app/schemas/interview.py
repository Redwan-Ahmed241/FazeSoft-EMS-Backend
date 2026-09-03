"""
app/schemas/interview.py — Pydantic schemas for Interview.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class InterviewCreate(BaseModel):
    candidate_name: str = Field(min_length=1)
    candidate_email: EmailStr
    position: str = Field(min_length=1)
    date: str = Field(min_length=1)
    time: str = Field(min_length=1)
    duration: str = Field(min_length=1)
    type: str = Field(min_length=1)
    interviewer: str = Field(min_length=1)
    meeting_link: Optional[str] = None
    avatar: Optional[str] = None


class InterviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_name: str
    candidate_email: str
    position: str
    date: str
    time: str
    duration: str
    type: str
    interviewer: str
    meeting_link: Optional[str] = None
    avatar: Optional[str] = None
    created_at: datetime
