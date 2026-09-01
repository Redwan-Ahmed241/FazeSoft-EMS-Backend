"""
app/services/auth_service.py — Business logic for authentication & user management.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.role_permission import Role, UserRole
from app.schemas.user import UserCreate, UserLogin, UserOut, Token, EmployeeCreate
from app.core.auth import get_password_hash, verify_password, create_access_token


async def _resolve_rbac_role(db: AsyncSession, user_id) -> str:
    """Look up the user's role from the user_role → role tables."""
    result = await db.execute(
        select(Role.role_desc)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    )
    role = result.scalars().first()
    return (role or "candidate").lower()


def _user_out(user: User, role: str) -> UserOut:
    """Build a UserOut with the RBAC-resolved role."""
    data = UserOut.model_validate(user)
    data.role = role
    return data


class AuthService:
    @staticmethod
    async def signup(db: AsyncSession, payload: UserCreate) -> Token:
        result = await db.execute(select(User).where(User.email == payload.email))
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        user = User(
            email=payload.email,
            encrypted_password=get_password_hash(payload.password),
            raw_user_meta_data={"full_name": payload.full_name},
            raw_app_meta_data={"role": "candidate"},
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        role = await _resolve_rbac_role(db, user.id)
        token = create_access_token(data={"sub": str(user.id)})
        return Token(access_token=token, user=_user_out(user, role))

    @staticmethod
    async def login(db: AsyncSession, payload: UserLogin) -> Token:
        result = await db.execute(select(User).where(User.email == payload.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated.",
            )

        role = await _resolve_rbac_role(db, user.id)
        token = create_access_token(data={"sub": str(user.id)})
        return Token(access_token=token, user=_user_out(user, role))

    @staticmethod
    async def create_employee(db: AsyncSession, payload: EmployeeCreate) -> UserOut:
        result = await db.execute(select(User).where(User.email == payload.email))
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        user = User(
            email=payload.email,
            encrypted_password=get_password_hash(payload.password),
            raw_user_meta_data={
                "full_name": payload.full_name,
                "job_title": payload.job_title,
            },
            raw_app_meta_data={"role": "employee"},
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        role = await _resolve_rbac_role(db, user.id)
        return _user_out(user, role)

    @staticmethod
    async def get_all_users(db: AsyncSession) -> list[UserOut]:
        result = await db.execute(
            select(User)
            .where(User.deleted_at.is_(None), User.banned_until.is_(None))
            .order_by(User.created_at.desc())
        )
        users = result.scalars().all()
        out = []
        for u in users:
            role = await _resolve_rbac_role(db, u.id)
            out.append(_user_out(u, role))
        return out

    @staticmethod
    async def get_me(db: AsyncSession, user: User) -> UserOut:
        role = await _resolve_rbac_role(db, user.id)
        return _user_out(user, role)
