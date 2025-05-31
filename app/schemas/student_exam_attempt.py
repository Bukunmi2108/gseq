from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.student_exam_attempt import ExamAttemptStatus # Import enum
from .student_answer import StudentAnswerSchema

class StudentExamAttemptBase(BaseModel):
    exam_bundle_id: UUID
    # student_id is implicit from authenticated user or path

class StudentExamAttemptCreate(StudentExamAttemptBase):
    # start_time will be set by server
    pass # student_id will be taken from current_user, exam_bundle_id from path

class StudentExamAttemptSchema(StudentExamAttemptBase):
    id: UUID
    student_id: UUID
    start_time: datetime
    submission_time: Optional[datetime] = None
    score: Optional[float] = None
    status: ExamAttemptStatus
    answers: List[StudentAnswerSchema] = []

    model_config = {'from_attributes': True, 'use_enum_values': True}
