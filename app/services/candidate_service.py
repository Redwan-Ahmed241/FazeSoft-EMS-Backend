"""
app/services/candidate_service.py — Business logic for candidate operations.
"""
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.candidate import Candidate, CandidateStatus
from app.models.user import User
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateStatusUpdate


class CandidateService:
    @staticmethod
    async def list_candidates(db: AsyncSession, current_user: User) -> List[Candidate]:
        if current_user.role in ("hr", "admin"):
            result = await db.execute(
                select(Candidate).order_by(Candidate.applied_date.desc(), Candidate.id.desc())
            )
            return list(result.scalars().all())
        else:
            result = await db.execute(
                select(Candidate).where(Candidate.email == current_user.email)
            )
            return list(result.scalars().all())

    @staticmethod
    async def create_candidate(db: AsyncSession, payload: CandidateCreate, current_user: User) -> Candidate:
        if current_user.role not in ("hr", "admin") and payload.email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Candidates can only create their own records.",
            )

        try:
            status_enum = CandidateStatus(payload.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{payload.status}'. Must be one of: {[s.value for s in CandidateStatus]}",
            )

        candidate = Candidate(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            position=payload.position,
            ai_score=payload.ai_score,
            experience=payload.experience,
            skills=payload.skills,
            education=payload.education or [],
            certifications=payload.certifications or [],
            status=status_enum,
            avatar=payload.avatar,
            applied_date=payload.applied_date,
            match_reasons=payload.match_reasons or [],
        )
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)
        return candidate

    @staticmethod
    async def get_candidate(db: AsyncSession, candidate_id: int, current_user: User) -> Candidate:
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()

        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with id={candidate_id} not found.",
            )

        if current_user.role not in ("hr", "admin") and candidate.email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only view your own candidate profile.",
            )
        return candidate

    @staticmethod
    async def update_candidate(
        db: AsyncSession, candidate_id: int, payload: CandidateUpdate, current_user: User
    ) -> Candidate:
        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()

        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with id={candidate_id} not found.",
            )

        if current_user.role not in ("hr", "admin") and candidate.email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only update your own candidate profile.",
            )

        update_data = payload.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(candidate, field, value)

        await db.commit()
        await db.refresh(candidate)
        return candidate

    @staticmethod
    async def update_candidate_status(
        db: AsyncSession, candidate_id: int, payload: CandidateStatusUpdate, current_user: User
    ) -> Candidate:
        if current_user.role not in ("hr", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only HR users can update pipeline statuses.",
            )

        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()

        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with id={candidate_id} not found.",
            )

        try:
            candidate.status = CandidateStatus(payload.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid status '{payload.status}'. Must be one of: {[s.value for s in CandidateStatus]}",
            )

        await db.commit()
        await db.refresh(candidate)
        return candidate

    @staticmethod
    async def delete_candidate(db: AsyncSession, candidate_id: int, current_user: User) -> None:
        if current_user.role not in ("hr", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only HR users can delete candidates.",
            )

        result = await db.execute(select(Candidate).where(Candidate.id == candidate_id))
        candidate = result.scalar_one_or_none()

        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate with id={candidate_id} not found.",
            )

        await db.delete(candidate)
        await db.commit()
