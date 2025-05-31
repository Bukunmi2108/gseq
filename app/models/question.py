from sqlalchemy import Column, String, Enum, LargeBinary, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship
from enum import Enum as PythonEnum
from sqlalchemy.dialects.postgresql import UUID
from app.core.base import Base
from app.utils.constant.globals import QuestionType
from .common import CommonModel



class Question(CommonModel):
    __tablename__ = "questions"

    type = Column(Enum(QuestionType), default=QuestionType.SCHOOL, nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    question_image = Column(LargeBinary, nullable=True)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False) # e.g., {"A": "Option 1", "B": "Option 2"}
    answer = Column(String, nullable=False) # e.g., "A" or the text of the correct option
    year = Column(Integer, nullable=True) # Added: The year the question pertains to

    # Relationships
    subject = relationship("Subject", back_populates="questions")
    exam_bundles = relationship(
        "ExamBundle", 
        secondary="exam_bundle_questions", # Reference the association table
        back_populates="questions"
    )
    
    def __repr__(self):
        return f"{self.question_text[:50]}..." if self.question_text else "No Question Text"  # improved repr

metadata = Base.metadata
