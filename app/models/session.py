from sqlalchemy import Column, String, Date
from sqlalchemy.orm import relationship
from app.core.base import Base
from .common import CommonModel


class Session(CommonModel):
    __tablename__ = "sessions"

    name = Column(String, nullable=False, unique=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    terms = relationship("Term", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.name}"


metadata = Base.metadata
