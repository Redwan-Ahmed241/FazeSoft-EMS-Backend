"""
app/api/v1/routers/project_router.py — Project endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, require_role_and_permission
from app.core.database import get_db
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectOut, ProjectListOut, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    dependencies=[Depends(get_current_user)],
)

require_project_creator = require_role_and_permission("admin", "create_project")


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(require_project_creator),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project. Restricted to Admin users with create_project permission."""
    return await ProjectService.create_project(db, payload, current_user)


@router.get("/", response_model=List[ProjectListOut])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return a lightweight list of all projects."""
    projects = await ProjectService.get_all_projects(db)
    return [ProjectListOut.model_validate(p) for p in projects]


@router.put("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    current_user: User = Depends(require_project_creator),
    db: AsyncSession = Depends(get_db),
):
    """Update editable project fields."""
    return await ProjectService.update_project(db, project_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(require_project_creator),
    db: AsyncSession = Depends(get_db),
):
    """Delete a project (also removes its project-team links)."""
    await ProjectService.delete_project(db, project_id)
    return None


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch a single project by ID."""
    return await ProjectService.get_project_by_id(db, project_id)