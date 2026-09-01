"""
app/models/client.py — SQLAlchemy ORM Client model.
"""
import uuid
from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class Client(Base):
    __tablename__ = "client"

    client_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=False)
    address = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
