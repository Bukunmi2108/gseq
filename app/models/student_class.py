from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from app.core.base import Base
from .common import CommonModel
from .associations import exam_bundle_student_classes_association

class StudentClass(CommonModel):
	__tablename__ = "student_classes"

	name = Column(String)

	students = relationship("Student", back_populates="student_class")
	teachers = relationship(
        "Teacher",
        secondary="teacher_student_class_association", # Reference the association table
        back_populates="classes_held"
    )
	exam_bundles = relationship(
        "ExamBundle",
        secondary=exam_bundle_student_classes_association,
        back_populates="student_classes"
    )
	
	def __repr__(self):
		return f"{self.name}"
	
metadata = Base.metadata

