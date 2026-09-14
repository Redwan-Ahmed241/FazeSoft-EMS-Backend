"""
app/main.py — FastAPI application entry point for HireMate backend.

Run with:
    uvicorn app.main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    force=True,
)

from app.core.config import settings
from app.api.v1 import api_v1_router
from app.api.v1.routers import (
    auth_router,
    candidate_router,
    client_router,
    email_router,
    interview_router,
    note_router,
    notification_router,
    resume_router,
    project_router,
    team_router,
    project_team_router,
)
from app.api.v1.routers.task_router import task_router
from app.api.v1.routers.submission_router import submission_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for the HireMate HR Management Dashboard",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────────────────────
#  CORS
# ─────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + [settings.FRONTEND_URL],
    allow_origin_regex=r"^https?://([a-zA-Z0-9-]+\.)*(fazesoft\.com|vercel\.app)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
#  Routers Registration
#  Registers routers under /api/v1 and legacy /api paths
# ─────────────────────────────────────────────────────────────

# v1 routes (/api/v1/auth, /api/v1/candidates, /api/v1/teams, etc.)
app.include_router(api_v1_router, prefix="/api")
app.include_router(team_router, prefix="/api/v1")
app.include_router(project_team_router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1")
app.include_router(submission_router, prefix="/api/v1")

# Backward compatibility routes (/api/auth, /api/candidates, /api/teams, etc.)
app.include_router(auth_router, prefix="/api")
app.include_router(team_router, prefix="/api")
app.include_router(project_team_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(submission_router, prefix="/api")
app.include_router(candidate_router, prefix="/api")
app.include_router(client_router, prefix="/api")
app.include_router(email_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(note_router, prefix="/api")
app.include_router(notification_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(project_router, prefix="/api")


# ─────────────────────────────────────────────────────────────
#  Health Check
# ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "HireMate API is running 🚀"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}


