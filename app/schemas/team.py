"""
app/schemas/team.py — Pydantic schemas for teams, team members, and project-team links.
"""
from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.team import TeamMemberRole


class TeamMemberInput(BaseModel):
    user_id: UUID
    role: TeamMemberRole


class TeamCreate(BaseModel):
    team_name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    members: List[TeamMemberInput] = Field(default_factory=list)


class TeamMemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    role: TeamMemberRole
    joined_at: datetime


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: UUID
    team_name: str
    description: str
    created_at: datetime
    updated_at: datetime


class TeamWithMembersOut(TeamOut):
    members: List[TeamMemberOut] = Field(default_factory=list)


class ProjectTeamAssign(BaseModel):
    team_id: UUID


class ProjectTeamsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    team_id: UUID
    assigned_at: datetime