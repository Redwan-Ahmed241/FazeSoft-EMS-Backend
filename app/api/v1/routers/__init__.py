"""
app/api/v1/routers/__init__.py — Package exports for API v1 routers.
"""
from app.api.v1.routers.auth_router import router as auth_router
from app.api.v1.routers.candidate_router import router as candidate_router
from app.api.v1.routers.interview_router import router as interview_router
from app.api.v1.routers.notification_router import router as notification_router
from app.api.v1.routers.resume_router import router as resume_router
from app.api.v1.routers.project_router import router as project_router
from app.api.v1.routers.client_router import router as client_router
from app.api.v1.routers.team_router import team_router, project_team_router

__all__ = [
    "auth_router",
    "candidate_router",
    "client_router",
    "interview_router",
    "notification_router",
    "resume_router",
    "project_router",
    "team_router",
    "project_team_router",
]
