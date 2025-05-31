import enum
from sqlalchemy import Column, ForeignKey, DateTime, Integer, Enum as SAEnum, Float, JSON, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import Base
from app.models.common import CommonModel
from app.utils.constant.globals import QuestionType

class PracticeSessionStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class PracticeSession(CommonModel):
    __tablename__ = "practice_sessions"

    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    start_time = Column(DateTime(timezone=True), nullable=False)
    submission_time = Column(DateTime(timezone=True), nullable=True)

    score = Column(Float, nullable=True)
    status = Column(SAEnum(PracticeSessionStatus), nullable=False, default=PracticeSessionStatus.IN_PROGRESS)

    filter_subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=True)
    filter_question_type = Column(SAEnum(QuestionType), nullable=True)
    filter_year = Column(Integer, nullable=True)

    question_ids = Column(JSON, nullable=False)

    # Relationships
    student = relationship("User", back_populates="practice_sessions")
    answers = relationship("PracticeSessionAnswer", back_populates="practice_session", cascade="all, delete-orphan")

    # subject = relationship("Subject", foreign_keys=[filter_subject_id]) # Deferred specific setup

    def __repr__(self):
        return f"<PracticeSession id={self.id} student_id={self.student_id} status='{self.status.value}'>"
