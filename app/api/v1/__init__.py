"""
app/api/v1/__init__.py — API v1 Router aggregator.
"""
from fastapi import APIRouter

from app.api.v1.routers import (
    auth_router,
    candidate_router,
    interview_router,
    notification_router,
    resume_router,
    project_router,
)

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(candidate_router)
api_v1_router.include_router(interview_router)
api_v1_router.include_router(notification_router)
api_v1_router.include_router(resume_router)
api_v1_router.include_router(project_router)
