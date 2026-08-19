"""
app/models/role_permission.py — SQLAlchemy ORM models for the RBAC system.

Tables: role, permission, role_permission, user_role
"""
import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Role(Base):
    __tablename__ = "role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_desc = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    permissions = relationship(
        "Permission",
        secondary="role_permission",
        back_populates="roles",
    )


class Permission(Base):
    __tablename__ = "permission"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    perm_desc = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)

    roles = relationship(
        "Role",
        secondary="role_permission",
        back_populates="permissions",
    )


class RolePermission(Base):
    __tablename__ = "role_permission"

    role_id = Column(
        UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id = Column(
        UUID(as_uuid=True), ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True
    )


class UserRole(Base):
    __tablename__ = "user_role"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("auth.users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id = Column(
        UUID(as_uuid=True), ForeignKey("role.id", ondelete="CASCADE"), primary_key=True
    )
