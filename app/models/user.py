"""
app/models/user.py — SQLAlchemy ORM User model mapped to Supabase's auth.users table.

App-level profile fields (full_name, phone, location, job_title, bio, avatar) and the
app role are stored in Supabase's raw_user_meta_data / raw_app_meta_data JSONB columns.
The password lives in auth.users.encrypted_password (bcrypt).
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, index=True)
    encrypted_password = Column(String(255), nullable=True)
    raw_user_meta_data = Column(JSONB, nullable=True)
    raw_app_meta_data = Column(JSONB, nullable=True)
    banned_until = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True
    )

    @property
    def hashed_password(self) -> Optional[str]:
        return self.encrypted_password

    @property
    def full_name(self) -> Optional[str]:
        return (self.raw_user_meta_data or {}).get("full_name")

    @property
    def phone(self) -> Optional[str]:
        return (self.raw_user_meta_data or {}).get("phone")

    @property
    def location(self) -> Optional[str]:
        return (self.raw_user_meta_data or {}).get("location")

    @property
    def job_title(self) -> Optional[str]:
        return (self.raw_user_meta_data or {}).get("job_title")

    @property
    def bio(self) -> Optional[str]:
        return (self.raw_user_meta_data or {}).get("bio")

    @property
    def avatar(self) -> Optional[str]:
        return (self.raw_user_meta_data or {}).get("avatar")

    @property
    def role(self) -> str:
        return (self.raw_app_meta_data or {}).get("role") or "candidate"

    @property
    def is_active(self) -> bool:
        return self.deleted_at is None and self.banned_until is None
