from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID

class StudentAnswerBase(BaseModel):
    question_id: UUID
    selected_answer: Any # Flexible for different answer types (e.g. string, number, list of strings for multiple choice)

class StudentAnswerCreate(StudentAnswerBase):
    pass

class StudentAnswerSchema(StudentAnswerBase):
    id: UUID
    student_exam_attempt_id: UUID
    is_correct: Optional[bool] = None
    marks_awarded: Optional[float] = None
    # To show correct answer during review:
    correct_answer: Optional[Any] = None # This would be populated from Question.answer

    model_config = {'from_attributes': True}
