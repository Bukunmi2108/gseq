from sqlalchemy import Column, String, Enum, Integer, LargeBinary, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum as PythonEnum

from app.core.base import Base
from app.utils.constant.globals import UserRole
from app.models.associations import book_user_likes_association
from .common import CommonModel



class Book(CommonModel):
    __tablename__ = "books"

    name = Column(String, nullable=False)
    uploaded_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    cover_image = Column(LargeBinary, nullable=True)
    pdf = Column(LargeBinary, nullable=True)
    likes = relationship("User", secondary=book_user_likes_association, back_populates="liked_books")
    views = Column(Integer, default=0, nullable=False)

    # Relationships
    uploaded_by = relationship("User", back_populates="uploaded_books")

    def __repr__(self):
        return f"{self.name}"

metadata = Base.metadata
