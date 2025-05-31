from sqlalchemy import Column, String, Enum, Boolean, LargeBinary, ForeignKey, Table
from sqlalchemy.orm import relationship
from enum import Enum as PythonEnum
from app.core.base import Base
from app.utils.constant.globals import UserRole
from app.models.associations import book_user_likes_association
from .common import CommonModel



class User(CommonModel):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False) 
    is_left = Column(Boolean, default=False, nullable=False)  # Made not nullable
    profile_picture = Column(LargeBinary, nullable=True)

    # Relationships
    uploaded_books = relationship("Book", back_populates="uploaded_by")
    exam_bundles = relationship("ExamBundle", back_populates="uploaded_by")
    liked_books = relationship(
        "Book", secondary=book_user_likes_association, back_populates="likes"
    )

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": role,
    }

metadata = Base.metadata