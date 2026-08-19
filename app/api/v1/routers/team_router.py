"""
app/api/v1/routers/team_router.py — Team CRUD + project-team endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.role_permission import Permission, Role, RolePermission, UserRole
from app.models.user import User
from app.schemas.team import (
    ProjectTeamAssign,
    ProjectTeamsOut,
    TeamCreate,
    TeamWithMembersOut,
)
from app.services.team_service import TeamService

team_router = APIRouter(prefix="/teams", tags=["Teams"])
project_team_router = APIRouter(prefix="/projects", tags=["Project Teams"])


def require_permission(permission_name: str):
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        result = await db.execute(
            select(Permission.perm_desc)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == current_user.id,
                Permission.perm_desc == permission_name,
            )
        )
        granted = {p for p in result.scalars().all() if p is not None}
        if permission_name not in granted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires permission: {permission_name}.",
            )
        return current_user

    return dependency


@team_router.post("", response_model=TeamWithMembersOut, status_code=status.HTTP_201_CREATED)
async def create_team(
    payload: TeamCreate,
    current_user: User = Depends(require_permission("create_team")),
    db: AsyncSession = Depends(get_db),
):
    return await TeamService.create_team(payload, current_user, db)


@team_router.get("", response_model=List[TeamWithMembersOut])
async def list_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TeamService.get_all_teams(db)


@team_router.get("/{team_id}", response_model=TeamWithMembersOut)
async def get_team(
    team_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TeamService.get_team_by_id(team_id, db)


@project_team_router.post("/{project_id}/teams", response_model=ProjectTeamsOut, status_code=status.HTTP_201_CREATED)
async def assign_team_to_project(
    project_id: UUID,
    payload: ProjectTeamAssign,
    current_user: User = Depends(require_permission("create_project")),
    db: AsyncSession = Depends(get_db),
):
    return await TeamService.assign_team_to_project(project_id, payload.team_id, db)


@project_team_router.get("/{project_id}/teams", response_model=List[TeamWithMembersOut])
async def list_project_teams(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await TeamService.get_teams_by_project(project_id, db)