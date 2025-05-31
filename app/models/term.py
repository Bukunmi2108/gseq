from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.base import Base
from app.utils.constant.globals import AcademicTerm
from .common import CommonModel


class Term(CommonModel):
    __tablename__ = "terms"

    name = Column(Enum(AcademicTerm), default=AcademicTerm.FIRST, nullable=False, unique=True)  
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)

    # Add the relationship
    session = relationship("Session", back_populates="terms")

    def __repr__(self):
        return f"{self.name}"


metadata = Base.metadata
