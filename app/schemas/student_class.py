from pydantic import BaseModel
from uuid import UUID

class StudentClassBase(BaseModel):
    name: str

class StudentClassCreate(StudentClassBase):
    pass

class StudentClassSchema(StudentClassBase):
    id: UUID

    model_config = {'from_attributes': True}
