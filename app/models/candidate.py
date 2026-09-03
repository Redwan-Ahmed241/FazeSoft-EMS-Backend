"""
app/models/candidate.py — SQLAlchemy ORM Candidate model.
"""
import enum
from datetime import date
from sqlalchemy import Column, String, Integer, DateTime, Date, Enum as SAEnum, JSON, func

from app.core.database import Base


class CandidateStatus(str, enum.Enum):
    Applied   = "Applied"
    Screened  = "Screened"
    Interview = "Interview"
    Offer     = "Offer"
    Hired     = "Hired"
    Approved  = "Approved"
    Rejected  = "Rejected"


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    position = Column(String(255), nullable=False)
    ai_score = Column(Integer, default=0, nullable=False)
    experience = Column(String(100), nullable=True)
    skills = Column(JSON, default=list, nullable=False)
    education = Column(JSON, default=list, nullable=True)
    certifications = Column(JSON, default=list, nullable=True)
    status = Column(
        SAEnum(CandidateStatus, name="candidate_status", create_constraint=True),
        default=CandidateStatus.Applied,
        nullable=False,
    )
    avatar = Column(String(500), nullable=True)
    applied_date = Column(Date, default=date.today, nullable=False)
    match_reasons = Column(JSON, default=list, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
