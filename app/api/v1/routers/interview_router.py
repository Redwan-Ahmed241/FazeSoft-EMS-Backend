"""
app/api/v1/routers/interview_router.py — Full CRUD endpoints for interview schedules with RBAC.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.interview import InterviewCreate, InterviewOut
from app.services.interview_service import InterviewService

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/", response_model=List[InterviewOut])
async def list_interviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List interviews."""
    return await InterviewService.list_interviews(db, current_user)


@router.post("/", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
async def create_interview(
    payload: InterviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new interview schedule (HR only)."""
    return await InterviewService.create_interview(db, payload, current_user)


@router.get("/{interview_id}", response_model=InterviewOut)
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch an interview by ID with permission checks."""
    return await InterviewService.get_interview(db, interview_id, current_user)


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_interview(
    interview_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Permanently cancel/delete an interview schedule (HR only)."""
    await InterviewService.delete_interview(db, interview_id, current_user)
