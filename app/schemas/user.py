from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.utils.constant.globals import UserRole
from uuid import UUID

class UserBase(BaseModel):
	email: str
	admin_no: str | None = None

class UserCreate(UserBase):
	password: str
	first_name: str | None = None
	last_name: str | None = None
	profile_picture: str | None = None

class UserLogin(UserBase):
	password: str

class User(UserBase):
	id: UUID
	profile_picture: Optional[str]
	first_name: Optional[str]
	last_name: Optional[str]
	is_active: bool
	role: UserRole
	created_at: datetime
	updated_at: datetime
	
	model_config = {'from_attributes': True}

class UserUpdate(BaseModel):
	profile_picture: Optional[str]
	first_name: str | None = None
	last_name: str | None = None
	is_active: bool | None = None
	role: UserRole = None

class UserSchema(UserBase):
	id: UUID
	profile_picture: Optional[str]
	role: UserRole
	is_left: bool

	model_config = {'from_attributes': True}

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserCounts(BaseModel):
	total_students: int
	total_teachers: int
	total_admins: int
	total_users: int
	total_exams: int
	total_questions: int
	total_subjects: int
	total_classes: int