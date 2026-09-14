"""
app/models/submission.py — SQLAlchemy ORM TaskSubmission model.
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

from app.core.database import Base


class TaskSubmission(Base):
    __tablename__ = "task_submission"
    __mapper_args__ = {"eager_defaults": True}

    submission_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("task.task_id", ondelete="CASCADE"),
        nullable=False,
    )
    submitted_by = Column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    commit_link = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    submitted_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
