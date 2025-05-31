from pydantic import BaseModel
from datetime import timedelta
from app.schemas.question import QuestionSchema
from typing import List


class ExamBundleBase(BaseModel):
    name: str
    time_in_mins: timedelta
    is_active: bool
    subject_combinations: dict


class ExamBundleCreate(ExamBundleBase):
    uploaded_by_id: int
    questions_per_subject: int = 5  # Added questions_per_subject


class ExamBundleSchema(ExamBundleBase):
    id: int
    no_of_participants: int
    uploaded_by_id: int
    questions: List[QuestionSchema]  # Added questions to the schema

    model_config = {'from_attributes': True}
