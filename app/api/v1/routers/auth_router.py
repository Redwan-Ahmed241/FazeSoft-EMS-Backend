"""
app/api/v1/routers/auth_router.py — Signup, Login, Employee Creation, and Me endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token, EmployeeCreate
from app.services.auth_service import AuthService

from typing import List

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and return a JWT token."""
    return await AuthService.signup(db, payload)


@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user credentials and return a JWT token."""
    return await AuthService.login(db, payload)


@router.post("/create-employee", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    """Create an employee login account."""
    return await AuthService.create_employee(db, payload)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return UserOut.model_validate(current_user)


@router.get("/users", response_model=List[UserOut])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all registered users (for team member assignment)."""
    return await AuthService.get_all_users(db)
