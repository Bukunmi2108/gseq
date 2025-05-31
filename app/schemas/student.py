from app.schemas.user import UserBase, UserSchema
from typing import Optional
from uuid import UUID

class StudentBase(UserBase):
  pass

class StudentCreate(StudentBase):
  profile_picture: Optional[str]
  password: str
    
class StudentSchema(UserSchema):
  admin_no: str | None = None
  
  model_config = {'from_attributes': True}
    