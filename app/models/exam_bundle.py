from sqlalchemy import Column, String, Enum, Integer, LargeBinary, ForeignKey, Table, Interval, Boolean, JSON
from sqlalchemy.orm import relationship
from enum import Enum as PythonEnum
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import Base
from .common import CommonModel
from .associations import exam_bundle_student_classes_association


class ExamBundle(CommonModel):
    __tablename__ = "exam_bundles"

    name = Column(String, nullable=False)
    time_in_mins = Column(Interval, nullable=False) 
    is_active = Column(Boolean, default=True, nullable=False)
    no_of_participants = Column(Integer, default=0, nullable=False)
    subject_combinations = Column(JSON, nullable=False)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    uploaded_by = relationship("User", back_populates="exam_bundles")
    questions = relationship("Question", secondary="exam_bundle_questions", back_populates="exam_bundles")
    student_classes = relationship(
        "StudentClass",
        secondary=exam_bundle_student_classes_association,
        back_populates="exam_bundles"
    )
    attempts = relationship("StudentExamAttempt", back_populates="exam_bundle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.name}"


# Association table for ExamBundle and Question (Many-to-Many)
exam_bundle_questions = Table(
    "exam_bundle_questions",
    Base.metadata,
    Column("exam_bundle_id", ForeignKey("exam_bundles.id"), primary_key=True),
    Column("question_id", ForeignKey("questions.id"), primary_key=True),
)


metadata = Base.metadata


