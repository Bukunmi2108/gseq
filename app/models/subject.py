from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.base import Base
from .common import CommonModel


class Subject(CommonModel):
    __tablename__ = "subjects"

    name = Column(String, nullable=False, unique=True)  
    teachers = relationship(
        "Teacher", secondary="teacher_subject_association", back_populates="subjects_taught"
    )
    questions = relationship("Question", back_populates="subject")


    def __repr__(self):
        return f"{self.name}"


metadata = Base.metadata
