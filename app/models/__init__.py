"""
app/models/__init__.py — Package exports for SQLAlchemy models.
"""
from app.core.database import Base
from app.models.user import User
from app.models.candidate import Candidate, CandidateStatus
from app.models.client import Client
from app.models.interview import Interview
from app.models.notification import Notification
from app.models.project import Project, ProjectStatus
from app.models.role_permission import Role, Permission, RolePermission, UserRole
from app.models.team import Team, TeamMember, TeamMemberRole, ProjectTeam

__all__ = [
    "Base",
    "User",
    "Candidate",
    "CandidateStatus",
    "Client",
    "Interview",
    "Notification",
    "Project",
    "ProjectStatus",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "Team",
    "TeamMember",
    "TeamMemberRole",
    "ProjectTeam",
]

