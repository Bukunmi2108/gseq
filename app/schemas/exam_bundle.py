from pydantic import BaseModel
from datetime import timedelta
from typing import List, Dict
from uuid import UUID
from app.schemas.question import QuestionSchema
from app.schemas.student_class import StudentClassSchema


class ExamBundleBase(BaseModel):
    name: str
    time_in_mins: timedelta
    is_active: bool
    subject_combinations: Dict[UUID, int]


class ExamBundleCreate(ExamBundleBase):
    uploaded_by_id: UUID
    class_ids: List[UUID]


class ExamBundleSchema(ExamBundleBase):
    id: UUID
    no_of_participants: int
    uploaded_by_id: UUID
    questions: List[QuestionSchema]
    student_classes: List[StudentClassSchema] = []

    model_config = {'from_attributes': True}
