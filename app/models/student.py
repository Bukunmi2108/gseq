from sqlalchemy import Column, ForeignKey, String, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.utils.constant.globals import UserRole
from .user import User
from app.core.base import Base

class Student(User):
    __tablename__ = "students"
    id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    admin_no = Column(String, unique=True, index=True, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    student_class_id = Column(UUID(as_uuid=True), ForeignKey("student_classes.id"), nullable=True)

    student_class = relationship("StudentClass", back_populates="students")

    __mapper_args__ = {
        "polymorphic_identity": UserRole.STUDENT.value,
    }  # Set the role

metadata = Base.metadata
