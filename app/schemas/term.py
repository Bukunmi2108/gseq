from pydantic import BaseModel
from app.utils.constant.globals import AcademicTerm

class TermBase(BaseModel):
    name: AcademicTerm


class TermCreate(TermBase):
    session_id: int


class TermSchema(TermBase):
    id: int
    session_id: int

    model_config = {'from_attributes': True}
