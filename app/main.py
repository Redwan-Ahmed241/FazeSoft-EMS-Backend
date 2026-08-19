"""
app/main.py — FastAPI application entry point for HireMate backend.

Run with:
    uvicorn app.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import api_v1_router
from app.api.v1.routers import (
    auth_router,
    candidate_router,
    interview_router,
    notification_router,
    resume_router,
    project_router,
    team_router,
    project_team_router,
)

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

# Backward compatibility routes (/api/auth, /api/candidates, etc.)
app.include_router(auth_router, prefix="/api")
app.include_router(candidate_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
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
