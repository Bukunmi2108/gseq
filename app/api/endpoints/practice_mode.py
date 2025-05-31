import random
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any # Dict, Any might not be strictly needed here but good for flexibility
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel # For StartPracticeSessionResponse

from app.core.dependencies import get_db
from app.models.user import User
from app.models.question import Question
from app.models.practice_session import PracticeSession, PracticeSessionStatus
from app.models.practice_session_answer import PracticeSessionAnswer # Added
from app.schemas.practice_session import PracticeSessionCreateSchema, PracticeSessionSchema
from app.schemas.practice_session_answer import PracticeSessionAnswerCreateSchema # Added
from app.schemas.question import QuestionSchema
from app.api.endpoints.user.functions import get_current_active_user
from app.utils.constant.globals import UserRole, QuestionType

router = APIRouter(prefix="/student/practice", tags=["Student Practice Mode"])

# Define a response model for starting a session, including questions
class StartPracticeSessionResponse(BaseModel):
    session: PracticeSessionSchema
    questions: List[QuestionSchema]


@router.post("/sessions/start", response_model=StartPracticeSessionResponse)
def start_practice_session(
    practice_options: PracticeSessionCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can start a practice session."
        )

    query = db.query(Question)
    if practice_options.subject_id:
        query = query.filter(Question.subject_id == practice_options.subject_id)
    if practice_options.question_type:
        query = query.filter(Question.type == practice_options.question_type)
    if practice_options.year:
        query = query.filter(Question.year == practice_options.year)

    available_questions = query.all()

    if not available_questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No questions found matching your criteria. Try broadening your filters."
        )

    num_questions_to_select = min(len(available_questions), 60)
    selected_questions = random.sample(available_questions, num_questions_to_select)

    selected_question_ids = [q.id for q in selected_questions]

    new_session = PracticeSession(
        student_id=current_user.id,
        start_time=datetime.now(timezone.utc),
        status=PracticeSessionStatus.IN_PROGRESS,
        filter_subject_id=practice_options.subject_id,
        filter_question_type=practice_options.question_type,
        filter_year=practice_options.year,
        question_ids=selected_question_ids
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    response_questions = [QuestionSchema.model_validate(q) for q in selected_questions]
    response_session = PracticeSessionSchema.model_validate(new_session)

    return StartPracticeSessionResponse(session=response_session, questions=response_questions)


@router.post("/sessions/{session_id}/submit", response_model=PracticeSessionSchema)
def submit_practice_session_answers(
    session_id: UUID,
    answers_submission: List[PracticeSessionAnswerCreateSchema],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can submit practice session answers."
        )

    db_session_attempt = db.query(PracticeSession).filter(
        PracticeSession.id == session_id,
        PracticeSession.student_id == current_user.id
    ).first()

    if not db_session_attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found or does not belong to the current user."
        )

    if db_session_attempt.status != PracticeSessionStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This practice session is already {db_session_attempt.status.value}."
        )

    total_score_achieved = 0.0

    practice_session_question_ids_str = {str(qid) for qid in db_session_attempt.question_ids}
    processed_question_ids_payload = set()

    for answer_data in answers_submission:
        str_answer_question_id = str(answer_data.question_id)
        if str_answer_question_id not in practice_session_question_ids_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question ID {answer_data.question_id} was not part of this practice session."
            )
        if str_answer_question_id in processed_question_ids_payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate answer submitted for question ID {answer_data.question_id}."
            )
        processed_question_ids_payload.add(str_answer_question_id)

        db_question = db.query(Question).filter(Question.id == answer_data.question_id).first()
        if not db_question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question with id {answer_data.question_id} not found.")

        is_correct = False
        marks_awarded = 0.0

        if str(answer_data.selected_answer) == str(db_question.answer):
            is_correct = True
            marks_awarded = 1.0

        total_score_achieved += marks_awarded

        practice_answer = PracticeSessionAnswer(
            practice_session_id=db_session_attempt.id,
            question_id=answer_data.question_id,
            selected_answer=str(answer_data.selected_answer),
            is_correct=is_correct,
            marks_awarded=marks_awarded
        )
        db.add(practice_answer)

    db_session_attempt.score = total_score_achieved
    db_session_attempt.status = PracticeSessionStatus.COMPLETED
    db_session_attempt.submission_time = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_session_attempt)

    return db_session_attempt


@router.get("/sessions", response_model=List[PracticeSessionSchema])
def list_student_practice_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their practice sessions."
        )

    sessions = db.query(PracticeSession).filter(PracticeSession.student_id == current_user.id).order_by(PracticeSession.start_time.desc()).all()
    return sessions


@router.get("/sessions/{session_id}/result", response_model=PracticeSessionSchema)
def get_student_practice_session_result(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their practice session results."
        )

    db_practice_session = db.query(PracticeSession).filter(
        PracticeSession.id == session_id,
        PracticeSession.student_id == current_user.id
    ).first()

    if not db_practice_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice session not found or does not belong to the current user."
        )

    if db_practice_session.status == PracticeSessionStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This practice session is still in progress. Submit answers to view results."
        )

    return db_practice_session
