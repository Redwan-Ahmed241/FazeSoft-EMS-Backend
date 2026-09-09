"""
app/api/v1/routers/email_router.py — Candidate email sending endpoint.
"""
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_optional_current_user
from app.models.user import User
from app.schemas.email import EmailSendRequest, EmailSendResponse
from app.services.email_service import EmailService

router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
)


@router.post("/send", response_model=EmailSendResponse, status_code=status.HTTP_200_OK)
@router.post("/send/", response_model=EmailSendResponse, status_code=status.HTTP_200_OK, include_in_schema=False)
async def send_candidate_email(
    payload: EmailSendRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Send an email to a candidate (Interview Invite, Offer Letter, Follow Up, or Rejection).
    Delivers via backend SMTP server or Resend API if configured, or returns
    an unconfigured status prompting the frontend client to provide seamless Gmail/Outlook/mailto fallbacks.
    """
    return await EmailService.send_candidate_email(payload)
