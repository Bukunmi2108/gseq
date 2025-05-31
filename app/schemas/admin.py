from app.schemas.user import UserBase, UserSchema

class AdminBase(UserBase):
    pass

class AdminCreate(AdminBase):
    password: str

class AdminSchema(UserSchema):
    # Admin-specific fields, if any, would go here.
    # For now, it just inherits from UserSchema.
    class Config:
        orm_mode = True