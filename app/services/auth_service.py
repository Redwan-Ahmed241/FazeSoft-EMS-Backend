"""
app/services/auth_service.py — Business logic for authentication & user management.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserOut, Token, EmployeeCreate
from app.core.auth import get_password_hash, verify_password, create_access_token


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

        token = create_access_token(data={"sub": str(user.id)})
        return Token(access_token=token, user=UserOut.model_validate(user))

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

        token = create_access_token(data={"sub": str(user.id)})
        return Token(access_token=token, user=UserOut.model_validate(user))

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

        return UserOut.model_validate(user)

    @staticmethod
    async def get_all_users(db: AsyncSession) -> list[UserOut]:
        result = await db.execute(
            select(User)
            .where(User.deleted_at.is_(None), User.banned_until.is_(None))
            .order_by(User.created_at.desc())
        )
        return [UserOut.model_validate(u) for u in result.scalars().all()]
