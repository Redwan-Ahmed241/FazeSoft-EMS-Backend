"""
app/services/team_service.py — Business logic for teams, team members, and project-team links.
"""
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project
from app.models.team import Team, TeamMember, ProjectTeam
from app.models.user import User
from app.schemas.team import (
    ProjectTeamsOut,
    TeamCreate,
    TeamWithMembersOut,
)


class TeamService:
    @staticmethod
    async def create_team(
        data: TeamCreate,
        current_user: User,
        db: AsyncSession,
    ) -> TeamWithMembersOut:
        _ = current_user

        team = Team(team_name=data.team_name, description=data.description)
        db.add(team)
        await db.flush()

        try:
            for member in data.members:
                db.add(
                    TeamMember(
                        team_id=team.team_id,
                        user_id=member.user_id,
                        role=member.role,
                    )
                )
            await db.commit()
        except Exception:
            await db.rollback()
            raise

        return await TeamService.get_team_by_id(team.team_id, db)

    @staticmethod
    async def get_all_teams(db: AsyncSession) -> List[TeamWithMembersOut]:
        result = await db.execute(
            select(Team)
            .options(selectinload(Team.members))
            .order_by(Team.created_at.desc())
        )
        return [TeamWithMembersOut.model_validate(t) for t in result.scalars().all()]

    @staticmethod
    async def get_team_by_id(
        team_id: UUID,
        db: AsyncSession,
    ) -> TeamWithMembersOut:
        
        db.expire_all()
        result = await db.execute(
            select(Team)
            .options(selectinload(Team.members))
            .where(Team.team_id == team_id)
        )
        team = result.scalar_one_or_none()

        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with id={team_id} not found.",
            )

        await db.refresh(team, ["members"])
        for member in team.members:
            await db.refresh(member)

        return TeamWithMembersOut.model_validate(team)

    @staticmethod
    async def assign_team_to_project(
        project_id: UUID,
        team_id: UUID,
        db: AsyncSession,
    ) -> ProjectTeamsOut:
        team = await db.get(Team, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with id={team_id} not found.",
            )

        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )

        existing = await db.execute(
            select(ProjectTeam).where(
                ProjectTeam.project_id == project_id,
                ProjectTeam.team_id == team_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Team {team_id} is already assigned to project {project_id}.",
            )

        link = ProjectTeam(project_id=project_id, team_id=team_id)
        db.add(link)
        await db.commit()
        await db.refresh(link)
        return ProjectTeamsOut.model_validate(link)

    @staticmethod
    async def get_teams_by_project(
        project_id: UUID,
        db: AsyncSession,
    ) -> List[TeamWithMembersOut]:
        project = await db.get(Project, project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id={project_id} not found.",
            )

        result = await db.execute(
            select(ProjectTeam).where(ProjectTeam.project_id == project_id)
        )
        links = result.scalars().all()

        if not links:
            return []

        team_ids = [link.team_id for link in links]
        teams_result = await db.execute(
            select(Team)
            .options(selectinload(Team.members))
            .where(Team.team_id.in_(team_ids))
            .order_by(Team.created_at.desc())
        )
        return [TeamWithMembersOut.model_validate(t) for t in teams_result.scalars().all()]