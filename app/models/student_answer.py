from sqlalchemy import Column, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, Any # Added Optional, Any

from app.core.base import Base
from app.models.common import CommonModel
# from app.models.question import Question # Not strictly needed if relationship is just "Question" string

class StudentAnswer(CommonModel):
    __tablename__ = "student_answers"

    student_exam_attempt_id = Column(UUID(as_uuid=True), ForeignKey("student_exam_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)

    selected_answer = Column(Text, nullable=True) # Stores the student's answer (e.g., 'A', 'True', or text for fill-in-the-blanks)
    is_correct = Column(Boolean, nullable=True) # Null if not graded, True/False after grading
    marks_awarded = Column(Float, nullable=True, default=0.0)

    # Relationships
    attempt = relationship("StudentExamAttempt", back_populates="answers")
    question = relationship("Question") # No back_populates needed here to avoid cluttering Question model unless desired

    @property
    def correct_answer(self) -> Optional[Any]:
        if self.question:
            return self.question.answer
        return None

    def __repr__(self):
        return f"<StudentAnswer attempt_id={self.student_exam_attempt_id} question_id={self.question_id} is_correct={self.is_correct}>"
