"""
app/api/v1/routers/auth_router.py — Signup, Login, Employee Creation, and Me endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from typing import List
from uuid import UUID
from sqlalchemy import select, func

from app.models.role_permission import Permission, Role, RolePermission, UserRole
from app.schemas.user import UserCreate, UserLogin, UserOut, Token, EmployeeCreate, RoleChangeRequest


def require_permission(permission_name: str):
    """FastAPI dependency that verifies the current user has the required permission."""
    clean_perm = permission_name.strip()

    async def dependency(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        result = await db.execute(
            select(Permission.perm_desc)
            .join(RolePermission, RolePermission.perm_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == current_user.id,
                func.trim(Permission.perm_desc) == clean_perm,
            )
        )
        granted = {p.strip() for p in result.scalars().all() if p is not None}
        if clean_perm not in granted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires permission: {clean_perm}.",
            )
        return current_user

    return dependency

from app.services.auth_service import AuthService

router = APIRouter(tags=["Authentication"])


@router.post("/auth/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and return a JWT token."""
    return await AuthService.signup(db, payload)


@router.post("/auth/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user credentials and return a JWT token."""
    return await AuthService.login(db, payload)


@router.post("/auth/create-employee", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_employee(payload: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    """Create an employee login account."""
    return await AuthService.create_employee(db, payload)


@router.get("/auth/me", response_model=UserOut)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the currently authenticated user."""
    return await AuthService.get_me(db, current_user)


@router.get("/auth/users", response_model=List[UserOut])
@router.get("/users", response_model=List[UserOut])
async def list_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all registered users (for team member assignment)."""
    return await AuthService.get_all_users(db)


@router.patch("/users/{user_id}/role", response_model=UserOut)
async def change_user_role_endpoint(
    user_id: UUID,
    payload: RoleChangeRequest,
    current_user: User = Depends(require_permission("change_role")),
    db: AsyncSession = Depends(get_db),
):
    """
    Change the role of a target user.
    Protected: current user must have 'change_role' permission.
    """
    return await AuthService.change_user_role(
        target_user_id=user_id,
        role_name=payload.role_name,
        current_user=current_user,
        db=db,
    )
