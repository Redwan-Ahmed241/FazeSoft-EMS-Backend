"""
app/models/project.py — SQLAlchemy ORM Project model.
"""
import enum
import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, Enum as SAEnum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    Planned = "Planned"
    InProgress = "In Progress"


class Project(Base):
    __tablename__ = "project"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(255), nullable=False)
    project_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        SAEnum(
            ProjectStatus,
            name="project_status",
            create_constraint=True,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )
    manager_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"), nullable=False)
    client_id = Column(UUID(as_uuid=True), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )