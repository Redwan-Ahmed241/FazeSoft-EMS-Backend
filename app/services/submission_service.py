"""
app/services/submission_service.py — Business logic for task submissions.
"""
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_permission import Permission, Role, RolePermission, UserRole
from app.models.submission import TaskSubmission
from app.models.task import Task
from app.models.user import User
from app.schemas.submission import SubmissionCreate, SubmissionOut


class SubmissionService:
    @staticmethod
    async def create_submission(
        task_id: UUID,
        payload: SubmissionCreate,
        current_user: User,
        db: AsyncSession,
    ) -> SubmissionOut:
        """
        Creates a task submission record.
        submitted_by is auto-set to current_user.id.
        Task status stays In Progress — do NOT change it.
        Protected: authenticated user who is assigned_to that task only.
        """
        task = await db.get(Task, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id={task_id} not found.",
            )

        if task.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Only the assigned user can submit work for this task.",
            )

        submission = TaskSubmission(
            task_id=task_id,
            submitted_by=current_user.id,
            commit_link=payload.commit_link,
            notes=payload.notes,
        )
        db.add(submission)
        await db.commit()
        await db.refresh(submission)

        submitter_name = current_user.full_name or (
            current_user.email.split("@")[0] if current_user.email else None
        )

        return SubmissionOut(
            submission_id=submission.submission_id,
            task_id=submission.task_id,
            submitted_by=submission.submitted_by,
            submitted_by_name=submitter_name,
            commit_link=submission.commit_link,
            notes=submission.notes,
            submitted_at=submission.submitted_at,
            created_at=submission.created_at,
        )

    @staticmethod
    async def get_submissions_by_task(
        task_id: UUID,
        current_user: User,
        db: AsyncSession,
    ) -> List[SubmissionOut]:
        """
        Returns all submissions for a task.
        Protected: Tier 1 + Tier 2 only (check assign_task permission or admin/hr role).
        """
        task = await db.get(Task, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id={task_id} not found.",
            )

        # Check Tier 1 (admin/hr) or Tier 2 (assign_task permission)
        is_authorized = False
        user_role = (current_user.role or "").lower()
        if any(r in user_role for r in ["admin", "hr", "cto", "head_of_operations"]):
            is_authorized = True

        if not is_authorized:
            # Check permissions
            perm_res = await db.execute(
                select(Permission.perm_desc)
                .join(RolePermission, RolePermission.perm_id == Permission.id)
                .join(Role, Role.id == RolePermission.role_id)
                .join(UserRole, UserRole.role_id == Role.id)
                .where(
                    UserRole.user_id == current_user.id,
                    func.trim(Permission.perm_desc) == "assign_task",
                )
            )
            if perm_res.scalar_one_or_none() is not None:
                is_authorized = True

        if not is_authorized:
            # Check role table entries
            role_res = await db.execute(
                select(Role.name, Role.role_desc)
                .join(UserRole, UserRole.role_id == Role.id)
                .where(UserRole.user_id == current_user.id)
            )
            for r_name, r_desc in role_res.all():
                combo = f"{r_name or ''} {r_desc or ''}".lower()
                if any(k in combo for k in ["admin", "hr", "cto", "head"]):
                    is_authorized = True
                    break

        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Requires Tier 1 (admin/hr) or Tier 2 (assign_task permission).",
            )

        stmt = (
            select(TaskSubmission, User)
            .outerjoin(User, User.id == TaskSubmission.submitted_by)
            .where(TaskSubmission.task_id == task_id)
            .order_by(TaskSubmission.submitted_at.desc())
        )
        result = await db.execute(stmt)

        submissions: List[SubmissionOut] = []
        for sub, u in result.all():
            submitter_name = None
            if u:
                submitter_name = u.full_name or (
                    u.email.split("@")[0] if u.email else None
                )
            submissions.append(
                SubmissionOut(
                    submission_id=sub.submission_id,
                    task_id=sub.task_id,
                    submitted_by=sub.submitted_by,
                    submitted_by_name=submitter_name,
                    commit_link=sub.commit_link,
                    notes=sub.notes,
                    submitted_at=sub.submitted_at,
                    created_at=sub.created_at,
                )
            )

        return submissions
