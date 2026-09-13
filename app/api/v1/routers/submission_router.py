"""
app/api/v1/routers/submission_router.py — Endpoints for task submissions.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.submission import SubmissionCreate, SubmissionOut
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/tasks", tags=["Submissions"])
submission_router = router


@router.post(
    "/{task_id}/submissions",
    response_model=SubmissionOut,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/{task_id}/submissions/",
    response_model=SubmissionOut,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_task_submission(
    task_id: UUID,
    payload: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new task submission.
    Protected: authenticated user who is assigned to that task only.
    Task status stays In Progress — does not change.
    """
    return await SubmissionService.create_submission(
        task_id=task_id,
        payload=payload,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/{task_id}/submissions",
    response_model=List[SubmissionOut],
)
@router.get(
    "/{task_id}/submissions/",
    response_model=List[SubmissionOut],
    include_in_schema=False,
)
async def get_task_submissions(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch all submissions for a task.
    Protected: Tier 1 + Tier 2 only (check assign_task permission or admin/hr role).
    """
    return await SubmissionService.get_submissions_by_task(
        task_id=task_id,
        current_user=current_user,
        db=db,
    )
