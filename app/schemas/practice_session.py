from pydantic import BaseModel, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime

from app.models.practice_session import PracticeSessionStatus # Enum
from app.utils.constant.globals import QuestionType # Enum
from .practice_session_answer import PracticeSessionAnswerSchema

class PracticeSessionCreateSchema(BaseModel):
    subject_id: Optional[UUID] = None
    question_type: Optional[QuestionType] = None
    year: Optional[int] = None

class PracticeSessionBase(BaseModel):
    filter_subject_id: Optional[UUID] = None
    filter_question_type: Optional[QuestionType] = None
    filter_year: Optional[int] = None

class PracticeSessionSchema(PracticeSessionBase):
    id: UUID
    student_id: UUID
    start_time: datetime
    submission_time: Optional[datetime] = None
    score: Optional[float] = None
    status: PracticeSessionStatus
    question_ids: List[UUID]
    answers: List[PracticeSessionAnswerSchema] = []

    model_config = {'from_attributes': True, 'use_enum_values': True}
