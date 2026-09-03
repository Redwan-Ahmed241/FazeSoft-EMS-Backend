"""
app/models/task.py — SQLAlchemy ORM Task model.
"""
import enum
import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class TaskStatus(str, enum.Enum):
    Todo = "Todo"
    InProgress = "In Progress"
    Done = "Done"


class TaskPriority(str, enum.Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"


class Task(Base):
    __tablename__ = "task"
    __mapper_args__ = {"eager_defaults": True}

    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        SAEnum(
            TaskStatus,
            name="task_status",
            create_constraint=True,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=TaskStatus.Todo,
        server_default="Todo",
        nullable=False,
    )
    priority = Column(
        SAEnum(
            TaskPriority,
            name="task_priority",
            create_constraint=True,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=TaskPriority.Medium,
        server_default="Medium",
        nullable=False,
    )
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("project.project_id", ondelete="CASCADE"),
        nullable=False,
    )
    assigned_to = Column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    assigned_by = Column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    deadline = Column(Date, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
