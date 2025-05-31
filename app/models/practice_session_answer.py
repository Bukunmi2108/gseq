from sqlalchemy import Column, ForeignKey, Text, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional, Any # Added for correct_answer property

from app.core.base import Base
from app.models.common import CommonModel

class PracticeSessionAnswer(CommonModel):
    __tablename__ = "practice_session_answers"

    practice_session_id = Column(UUID(as_uuid=True), ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False) # ondelete="CASCADE" removed

    selected_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    marks_awarded = Column(Float, nullable=True, default=0.0)

    # Relationships
    practice_session = relationship("PracticeSession", back_populates="answers")
    question = relationship("Question")

    @property
    def correct_answer(self) -> Optional[Any]:
        if self.question:
            return self.question.answer
        return None

    def __repr__(self):
        return f"<PracticeSessionAnswer session_id={self.practice_session_id} question_id={self.question_id} is_correct={self.is_correct}>"
