from pydantic import BaseModel
import uuid

class SubjectBase(BaseModel):
    name: str


class SubjectCreate(SubjectBase):
    pass


class SubjectSchema(SubjectBase):
    id: uuid.UUID
    created_at: str
    updated_at: str

    model_config = {'from_attributes': True}
    