"""
app/models/interview.py — SQLAlchemy ORM Interview model.
"""
from sqlalchemy import Column, String, Integer, DateTime, func

from app.core.database import Base


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_name = Column(String(255), nullable=False)
    candidate_email = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    date = Column(String(50), nullable=False)
    time = Column(String(50), nullable=False)
    duration = Column(String(50), nullable=False)
    type = Column(String(100), nullable=False)
    interviewer = Column(String(255), nullable=False)
    meeting_link = Column(String(500), nullable=True)
    avatar = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
