"""
app/schemas/__init__.py — Package exports for Pydantic schemas.
"""
from app.schemas.user import UserCreate, EmployeeCreate, UserLogin, UserOut, Token
from app.schemas.candidate import (
    CandidateCreate, CandidateUpdate, CandidateStatusUpdate, CandidateOut
)
from app.schemas.interview import InterviewCreate, InterviewOut
from app.schemas.notification import NotificationCreate, NotificationOut, NotificationUpdate
from app.schemas.project import ProjectCreate, ProjectOut, ProjectListOut

__all__ = [
    "UserCreate",
    "EmployeeCreate",
    "UserLogin",
    "UserOut",
    "Token",
    "CandidateCreate",
    "CandidateUpdate",
    "CandidateStatusUpdate",
    "CandidateOut",
    "InterviewCreate",
    "InterviewOut",
    "NotificationCreate",
    "NotificationOut",
    "NotificationUpdate",
    "ProjectCreate",
    "ProjectOut",
    "ProjectListOut",
]
