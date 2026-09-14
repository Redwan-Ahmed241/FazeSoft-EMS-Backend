"""
app/services/auth_service.py — Business logic for authentication & user management.
"""
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.user import User
from app.models.role_permission import Role, UserRole, Permission, RolePermission
from app.schemas.user import UserCreate, UserLogin, UserOut, Token, EmployeeCreate
from app.core.auth import get_password_hash, verify_password, create_access_token


async def _resolve_rbac_role(db: AsyncSession, user_id) -> tuple[str, Optional[str], Optional[str], list[str]]:
    """Look up the user's role and permissions from the user_role → role → permission tables."""
    result = await db.execute(
        select(Role.name, Role.role_desc)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    )
    row = result.first()

    perm_result = await db.execute(
        select(Permission.perm_desc)
        .join(RolePermission, RolePermission.perm_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    )
    permissions = [p.strip() for p in perm_result.scalars().all() if p is not None]

    if row:
        name, desc = row
        return (name or desc or "Candidate", name, desc, permissions)
    return ("Candidate", "Candidate", "Candidate", permissions)


def _user_out(user: User, role_info: tuple[str, Optional[str], Optional[str], list[str]]) -> UserOut:
    """Build a UserOut with the RBAC-resolved role and permissions."""
    role_str, role_name, role_desc, perms = role_info
    data = UserOut.model_validate(user)
    data.role = role_str
    data.role_name = role_name
    data.role_desc = role_desc
    data.permissions = perms
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
            raw_app_meta_data={},
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
            raw_app_meta_data={"role": "Intern"},
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
        if not users:
            return []

        user_ids = [u.id for u in users]

        # Bulk query roles for all users
        role_stmt = (
            select(UserRole.user_id, Role.name, Role.role_desc)
            .join(Role, Role.id == UserRole.role_id)
            .where(UserRole.user_id.in_(user_ids))
        )
        role_rows = (await db.execute(role_stmt)).all()
        user_roles = {r[0]: (r[1], r[2]) for r in role_rows}

        # Bulk query permissions for all users
        perm_stmt = (
            select(UserRole.user_id, Permission.perm_desc)
            .join(Role, Role.id == UserRole.role_id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .join(Permission, Permission.id == RolePermission.perm_id)
            .where(UserRole.user_id.in_(user_ids))
        )
        perm_rows = (await db.execute(perm_stmt)).all()
        user_perms: dict[UUID, list[str]] = {}
        for uid, pdesc in perm_rows:
            if pdesc:
                user_perms.setdefault(uid, []).append(pdesc.strip())

        out = []
        for u in users:
            role_data = user_roles.get(u.id)
            if role_data:
                r_name, r_desc = role_data
                role_str = r_name or r_desc or "Candidate"
            else:
                role_str, r_name, r_desc = "Candidate", "Candidate", "Candidate"
            perms = user_perms.get(u.id, [])
            out.append(_user_out(u, (role_str, r_name, r_desc, perms)))
        return out

    @staticmethod
    async def get_me(db: AsyncSession, user: User) -> UserOut:
        role = await _resolve_rbac_role(db, user.id)
        return _user_out(user, role)

    @staticmethod
    async def change_user_role(
        target_user_id: UUID,
        role_name: str,
        current_user: User,
        db: AsyncSession,
    ) -> UserOut:
        # Business rule 3: A user cannot change their own role
        if current_user.id == target_user_id or str(current_user.id) == str(target_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change your own role.",
            )

        # Fetch target user -> 404 if not found
        result = await db.execute(
            select(User).where(
                User.id == target_user_id,
                User.deleted_at.is_(None),
                User.banned_until.is_(None),
            )
        )
        target_user = result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found.",
            )

        # Check target is not CTO -> 403
        target_role_info = await _resolve_rbac_role(db, target_user.id)
        target_role_name = target_role_info[1]
        if target_role_name and target_role_name.strip().upper() == "CTO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change role of a CTO.",
            )

        # Fetch role by role_name -> 404 if not found
        clean_role_name = role_name.strip()
        role_result = await db.execute(
            select(Role).where(
                (Role.name == clean_role_name) | (Role.role_desc == clean_role_name)
            )
        )
        new_role = role_result.scalars().first()
        if not new_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{clean_role_name}' not found.",
            )

        # Delete existing row from user_role where user_id = target_user_id
        await db.execute(
            delete(UserRole).where(UserRole.user_id == target_user_id)
        )

        # Insert new row into user_role (user_id, role_id)
        new_user_role = UserRole(user_id=target_user_id, role_id=new_role.id)
        db.add(new_user_role)

        # Commit in single transaction
        await db.commit()
        await db.refresh(target_user)

        # Return updated UserOut
        updated_role_info = await _resolve_rbac_role(db, target_user.id)
        return _user_out(target_user, updated_role_info)
