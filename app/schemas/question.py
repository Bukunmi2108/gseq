from pydantic import BaseModel
from app.utils.constant.globals import QuestionType
from uuid import UUID
from typing import Optional

class QuestionBase(BaseModel):
    type: QuestionType
    question_text: str
    options: dict
    answer: str
    year: Optional[int] = None


class QuestionCreate(QuestionBase):
    subject_id: UUID


class QuestionSchema(QuestionBase):
    id: UUID
    subject_id: UUID

    model_config = {'from_attributes': True}