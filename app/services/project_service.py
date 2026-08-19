"""
app/services/project_service.py — Business logic for project operations.
"""
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.schemas.project import ProjectCreate


class ProjectService:
    @staticmethod
    def _resolve_status(payload: ProjectCreate) -> ProjectStatus:
        """Auto-set status: 'In Progress' when all fields are filled, else 'Planned'."""
        required_fields = [
            payload.project_name,
            payload.project_code,
            payload.description,
            payload.client_id,
            payload.start_date,
            payload.end_date,
        ]
        if all(field is not None for field in required_fields):
            return ProjectStatus.InProgress
        return ProjectStatus.Planned

    @staticmethod
    async def create_project(
        db: AsyncSession,
        payload: ProjectCreate,
        current_user: User,
    ) -> Project:
        existing = await db.execute(
            select(Project).where(Project.project_code == payload.project_code)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Project with code '{payload.project_code}' already exists.",
            )

        project = Project(
            project_name=payload.project_name,
            project_code=payload.project_code,
            description=payload.description,
            status=ProjectService._resolve_status(payload),
            manager_id=current_user.id,
            client_id=payload.client_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def get_all_projects(db: AsyncSession) -> List[Project]:
        result = await db.execute(
            select(Project).order_by(Project.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_project_by_id(db: AsyncSession, project_id: UUID) -> Project:
        result = await db.execute(
            select(Project).where(Project.project_id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )
        return project