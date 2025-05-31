from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID

class PracticeSessionAnswerBase(BaseModel):
    question_id: UUID
    selected_answer: Any

class PracticeSessionAnswerCreateSchema(PracticeSessionAnswerBase):
    pass

class PracticeSessionAnswerSchema(PracticeSessionAnswerBase):
    id: UUID
    # practice_session_id: UUID # Usually not needed if nested in PracticeSessionSchema
    is_correct: Optional[bool] = None
    marks_awarded: Optional[float] = None
    correct_answer: Optional[Any] = None # For review, populated from Question.answer

    model_config = {'from_attributes': True}
