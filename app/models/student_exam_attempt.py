from sqlalchemy import Column, ForeignKey, DateTime, Enum as SAEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.core.base import Base
from app.models.common import CommonModel

class ExamAttemptStatus(enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed" # Answers submitted by student
    GRADED = "graded"       # Auto-grading complete, score available

class StudentExamAttempt(CommonModel):
    __tablename__ = "student_exam_attempts"

    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exam_bundle_id = Column(UUID(as_uuid=True), ForeignKey("exam_bundles.id", ondelete="CASCADE"), nullable=False)

    start_time = Column(DateTime(timezone=True), nullable=False)
    submission_time = Column(DateTime(timezone=True), nullable=True) # Time when answers were submitted

    score = Column(Float, nullable=True) # Overall score, can be percentage or raw score
    status = Column(SAEnum(ExamAttemptStatus), nullable=False, default=ExamAttemptStatus.IN_PROGRESS)

    # Relationships
    student = relationship("User", back_populates="exam_attempts")
    exam_bundle = relationship("ExamBundle", back_populates="attempts")
    answers = relationship("StudentAnswer", back_populates="attempt", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<StudentExamAttempt id={self.id} student_id={self.student_id} exam_bundle_id={self.exam_bundle_id} status='{self.status.value}'>"
