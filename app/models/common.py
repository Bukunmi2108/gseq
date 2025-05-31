from sqlalchemy import Column, Boolean, DateTime, func
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.core.base import Base


class CommonModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

