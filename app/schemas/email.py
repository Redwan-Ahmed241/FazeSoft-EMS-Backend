"""
app/schemas/email.py — Pydantic schemas for sending emails.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class EmailSendRequest(BaseModel):
    to_email: EmailStr
    to_name: Optional[str] = None
    subject: str
    body: str
    is_html: bool = False
    is_interview: bool = False
    interview_date: Optional[str] = None
    interview_time: Optional[str] = None
    meeting_link: Optional[str] = None
    candidate_id: Optional[int] = None


class EmailSendResponse(BaseModel):
    success: bool
    status: str
    message: str
    provider: Optional[str] = None
    recipient: str
