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
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
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
            # A new project starts as "Planned"; it moves to "In Progress" once a
            # team is assigned to it (see TeamService.assign_team_to_project).
            status=ProjectStatus.Planned,
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
    async def update_project(
        db: AsyncSession,
        project_id: UUID,
        payload: ProjectUpdate,
    ) -> Project:
        result = await db.execute(
            select(Project).where(Project.project_id == project_id)
        )
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )

        updates = payload.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(project, field, value)
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
    async def delete_project(
        db: AsyncSession,
        project_id: UUID,
    ) -> None:
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )

        # Remove project-team links first (DB-level cascade is unreliable here).
        from app.models.team import ProjectTeam

        await db.execute(
            ProjectTeam.__table__.delete().where(ProjectTeam.project_id == project_id)
        )

        await db.delete(project)
        await db.commit()

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

    @staticmethod
    async def update_project(
        db: AsyncSession,
        project_id: UUID,
        payload: ProjectCreate,
        current_user: User,
    ) -> Project:
        project = await ProjectService.get_project_by_id(db, project_id)

        if payload.project_code != project.project_code:
            existing = await db.execute(
                select(Project).where(
                    Project.project_code == payload.project_code,
                    Project.project_id != project_id,
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Project with code '{payload.project_code}' already exists.",
                )
            project.project_code = payload.project_code

        project.project_name = payload.project_name
        project.description = payload.description
        project.status = ProjectService._resolve_status(payload)
        project.client_id = payload.client_id
        project.start_date = payload.start_date
        project.end_date = payload.end_date

        await db.commit()
        await db.refresh(project)
        return project