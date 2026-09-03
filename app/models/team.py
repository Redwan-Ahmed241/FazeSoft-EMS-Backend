"""
app/models/team.py — SQLAlchemy ORM models for teams, team members, and project-team links.
"""
import enum
import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class TeamMemberRole(str, enum.Enum):
    front_end = "front_end"
    back_end = "back_end"


class Team(Base):
    __tablename__ = "teams"

    team_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    members = relationship(
        "TeamMember",
        back_populates="team",
        cascade="all, delete-orphan",
    )


class TeamMember(Base):
    __tablename__ = "team_member"

    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.team_id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role = Column(
        SAEnum(TeamMemberRole, name="team_member_role", create_constraint=True),
        nullable=False,
    )
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    team = relationship("Team", back_populates="members")


class ProjectTeam(Base):
    __tablename__ = "project_teams"

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("project.project_id", ondelete="CASCADE"),
        primary_key=True,
    )
    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.team_id", ondelete="CASCADE"),
        primary_key=True,
    )
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)