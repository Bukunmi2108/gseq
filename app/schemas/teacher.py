from app.schemas.user import UserBase, UserSchema

class TeacherBase(UserBase):
    pass

class TeacherCreate(TeacherBase):
    password: str
    
class TeacherSchema(UserSchema):
    pass
    model_config = {'from_attributes': True}