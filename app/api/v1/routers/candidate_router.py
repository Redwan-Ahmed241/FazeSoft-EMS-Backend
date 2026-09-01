"""
app/api/v1/routers/candidate_router.py — Full CRUD + status-update endpoints for candidates.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.candidate import CandidateCreate, CandidateUpdate, CandidateStatusUpdate, CandidateOut
from app.services.candidate_service import CandidateService

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=List[CandidateOut])
@router.get("/", response_model=List[CandidateOut], include_in_schema=False)
async def list_candidates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Return candidates. HR gets all. Candidates get only their own record."""
    return await CandidateService.list_candidates(db, current_user)


@router.post("", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=CandidateOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_candidate(
    payload: CandidateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new candidate record."""
    return await CandidateService.create_candidate(db, payload, current_user)


@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch a single candidate by ID with permission checks."""
    return await CandidateService.get_candidate(db, candidate_id, current_user)


@router.put("/{candidate_id}", response_model=CandidateOut)
async def update_candidate(
    candidate_id: int,
    payload: CandidateUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update candidate fields with permission checks."""
    return await CandidateService.update_candidate(db, candidate_id, payload, current_user)


@router.patch("/{candidate_id}/status", response_model=CandidateOut)
async def update_candidate_status(
    candidate_id: int,
    payload: CandidateStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update only the pipeline status of a candidate (restricted to HR)."""
    return await CandidateService.update_candidate_status(db, candidate_id, payload, current_user)


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Permanently delete a candidate record (restricted to HR)."""
    await CandidateService.delete_candidate(db, candidate_id, current_user)
