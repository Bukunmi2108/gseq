from sqlalchemy import Column, ForeignKey, String, Date, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.utils.constant.globals import UserRole
from .user import User
from app.core.base import Base


# Define the association table for the many-to-many relationship between Teacher and StudentClass
teacher_student_class_association = Table(
    "teacher_student_class_association",
    Base.metadata,  # Use the same metadata
    Column("teacher_id", ForeignKey("teachers.id"), primary_key=True),
    Column("student_class_id", ForeignKey("student_classes.id"), primary_key=True),
)

# Define the association table for the many-to-many relationship between Teacher and Subject
teacher_subject_association = Table(
    "teacher_subject_association",
    Base.metadata,  # Use the same metadata
    Column("teacher_id", ForeignKey("teachers.id"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id"), primary_key=True),
)


class Teacher(User):
    __tablename__ = "teachers"
    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True) 

    classes_held = relationship(
        "StudentClass",
        secondary="teacher_student_class_association",
        back_populates="teachers",
    )
    subjects_taught = relationship(
        "Subject", secondary="teacher_subject_association", back_populates="teachers"
    )

    __mapper_args__ = {
        "polymorphic_identity": UserRole.TEACHER.value,
    } 

metadata = Base.metadata
