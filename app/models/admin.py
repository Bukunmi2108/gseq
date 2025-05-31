from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.utils.constant.globals import UserRole
from .user import User

class Admin(User):
	__tablename__ = "admins"
	id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True) 

	__mapper_args__ = {
			"polymorphic_identity": UserRole.ADMIN.value,
	}  # Set the role
