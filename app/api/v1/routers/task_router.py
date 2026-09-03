"""
app/api/v1/routers/task_router.py — Task management endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.role_permission import Permission, Role, RolePermission, UserRole
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/projects", tags=["Tasks"])
task_router = router


def require_permission(permission_name: str):
    """
    FastAPI dependency that verifies the current user has the required permission
    by querying through user_role and role_permission junction tables without
    hardcoding any role names.
    """
    clean_perm = permission_name.strip()

    async def dependency(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        result = await db.execute(
            select(Permission.perm_desc)
            .join(RolePermission, RolePermission.perm_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == current_user.id,
                func.trim(Permission.perm_desc) == clean_perm,
            )
        )
        granted = {p.strip() for p in result.scalars().all() if p is not None}
        if clean_perm not in granted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires permission: {clean_perm}.",
            )
        return current_user

    return dependency


@router.post(
    "/{project_id}/tasks",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/{project_id}/tasks/",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_task(
    project_id: UUID,
    payload: TaskCreate,
    current_user: User = Depends(require_permission("assign_task")),
    db: AsyncSession = Depends(get_db),
):
    """Create a new task in a project. Protected: Requires 'assign_task' permission."""
    return await TaskService.create_task(
        project_id=project_id,
        data=payload,
        current_user=current_user,
        db=db,
    )


@router.get(
    "/{project_id}/tasks",
    response_model=List[TaskOut],
)
@router.get(
    "/{project_id}/tasks/",
    response_model=List[TaskOut],
    include_in_schema=False,
)
async def get_all_tasks(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch all tasks for a project. Protected: Any authenticated user."""
    _ = current_user
    return await TaskService.get_all_tasks(
        project_id=project_id,
        db=db,
    )


@router.get(
    "/{project_id}/tasks/{task_id}",
    response_model=TaskOut,
)
@router.get(
    "/{project_id}/tasks/{task_id}/",
    response_model=TaskOut,
    include_in_schema=False,
)
async def get_task_by_id(
    project_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch a single task by ID. Protected: Any authenticated user."""
    _ = current_user
    return await TaskService.get_task_by_id(
        project_id=project_id,
        task_id=task_id,
        db=db,
    )


@router.patch(
    "/{project_id}/tasks/{task_id}",
    response_model=TaskOut,
)
@router.patch(
    "/{project_id}/tasks/{task_id}/",
    response_model=TaskOut,
    include_in_schema=False,
)
async def update_task(
    project_id: UUID,
    task_id: UUID,
    payload: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an existing task in a project.
    Allowed if user has 'update_task' permission, is admin/hr, OR is the assignee of the task.
    """
    is_privileged = (current_user.role in ("admin", "hr"))

    if not is_privileged:
        perm_res = await db.execute(
            select(Permission.perm_desc)
            .join(RolePermission, RolePermission.perm_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == current_user.id,
                func.trim(Permission.perm_desc) == "update_task",
            )
        )
        if perm_res.scalar_one_or_none() is not None:
            is_privileged = True

    if not is_privileged:
        from app.models.task import Task
        task_res = await db.execute(
            select(Task).where(
                Task.task_id == task_id,
                Task.project_id == project_id,
            )
        )
        task = task_res.scalar_one_or_none()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with id={task_id} not found in project {project_id}.",
            )
        if task.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You do not have permission to update this task.",
            )

    return await TaskService.update_task(
        project_id=project_id,
        task_id=task_id,
        data=payload,
        db=db,
        current_user=current_user,
    )
