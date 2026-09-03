"""
app/services/interview_service.py — Business logic for interview operations.
"""
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.interview import Interview
from app.models.user import User
from app.schemas.interview import InterviewCreate


class InterviewService:
    @staticmethod
    async def list_interviews(db: AsyncSession, current_user: User) -> List[Interview]:
        if current_user.role in ("hr", "admin"):
            result = await db.execute(select(Interview).order_by(Interview.date.asc()))
            return list(result.scalars().all())
        else:
            result = await db.execute(
                select(Interview)
                .where(Interview.candidate_email == current_user.email)
                .order_by(Interview.date.asc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def create_interview(db: AsyncSession, payload: InterviewCreate, current_user: User) -> Interview:
        if current_user.role not in ("hr", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only HR users can schedule interviews.",
            )

        interview = Interview(
            candidate_name=payload.candidate_name,
            candidate_email=payload.candidate_email,
            position=payload.position,
            date=payload.date,
            time=payload.time,
            duration=payload.duration,
            type=payload.type,
            interviewer=payload.interviewer,
            meeting_link=payload.meeting_link,
            avatar=payload.avatar,
        )
        db.add(interview)
        await db.commit()
        await db.refresh(interview)
        return interview

    @staticmethod
    async def get_interview(db: AsyncSession, interview_id: int, current_user: User) -> Interview:
        result = await db.execute(select(Interview).where(Interview.id == interview_id))
        interview = result.scalar_one_or_none()

        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview with id={interview_id} not found.",
            )

        if current_user.role not in ("hr", "admin") and interview.candidate_email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only view your own interviews.",
            )
        return interview

    @staticmethod
    async def delete_interview(db: AsyncSession, interview_id: int, current_user: User) -> None:
        if current_user.role not in ("hr", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only HR users can cancel interviews.",
            )

        result = await db.execute(select(Interview).where(Interview.id == interview_id))
        interview = result.scalar_one_or_none()

        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview with id={interview_id} not found.",
            )

        await db.delete(interview)
        await db.commit()
