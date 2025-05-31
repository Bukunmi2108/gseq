from sqlalchemy import Column, String, Enum, LargeBinary, ForeignKey, Text, JSON
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
    options = Column(JSON, nullable=False)
    answer = Column(String, nullable=False)

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
