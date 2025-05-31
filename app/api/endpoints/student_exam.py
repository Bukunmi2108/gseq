from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel # Added for StartExamAttemptResponse

from app.core.dependencies import get_db
from app.models.user import User
from app.models.exam_bundle import ExamBundle
from app.models.student_class import StudentClass
from app.models.student import Student
from app.models.question import Question
from app.models.student_exam_attempt import StudentExamAttempt, ExamAttemptStatus
from app.models.student_answer import StudentAnswer # Added
from app.schemas.exam_bundle import ExamBundleSchema
from app.schemas.question import QuestionSchema
from app.schemas.student_exam_attempt import StudentExamAttemptSchema
from app.schemas.student_answer import StudentAnswerCreate # Added
from app.api.endpoints.user.functions import get_current_active_user
from app.utils.constant.globals import UserRole

router = APIRouter(prefix="/student", tags=["Student Exams"])

@router.get("/available_exams", response_model=List[ExamBundleSchema])
def list_available_exams_for_student(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Ensure the user is a student. Assuming UserRole.USER is the student role as per User model polymorphic_identity.
    # Or if there's a specific UserRole.STUDENT. Let's use UserRole.USER for now based on User model.
    # The plan mentioned "STUDENT", let's check UserRole definition.
    # Re-checking User model: polymorphic_identity='student' for Student model, UserRole.USER for base User.
    # The Student model inherits User. So a Student user will have current_user.id which is a User ID.
    # The role check should be against the role defined for students.
    # If Student model sets a specific role like UserRole.STUDENT, use that. If not, UserRole.USER might be it.
    # The plan mentions `current_user.role != "STUDENT"`. This implies UserRole.STUDENT enum value.
    if current_user.role != UserRole.STUDENT: # Assuming UserRole.STUDENT exists and is the correct role for students
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access available exams."
        )

    # We need the Student specific profile to get student_class_id
    student_profile = db.query(Student).filter(Student.id == current_user.id).first()
    if not student_profile or not student_profile.student_class_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile or class assignment not found."
        )

    available_exams = (
        db.query(ExamBundle)
        .join(ExamBundle.student_classes)
        .filter(StudentClass.id == student_profile.student_class_id, ExamBundle.is_active == True)
        .all()
    )
    return available_exams

# Define the custom response model for start_exam_attempt
class StartExamAttemptResponse(BaseModel): # Need to import BaseModel from pydantic
    attempt: StudentExamAttemptSchema
    questions: List[QuestionSchema]


@router.post("/exam_attempts/{exam_bundle_id}/start", response_model=StartExamAttemptResponse)
def start_exam_attempt(
    exam_bundle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can start an exam attempt."
        )

    db_exam_bundle = db.query(ExamBundle).filter(ExamBundle.id == exam_bundle_id, ExamBundle.is_active == True).first()
    if not db_exam_bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active exam bundle not found."
        )

    student_profile = db.query(Student).filter(Student.id == current_user.id).first()
    if not student_profile or not student_profile.student_class_id:
        # This case might be redundant if list_available_exams already filters, but good for direct access.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Student class not found or student profile incomplete.")

    is_eligible = False
    for s_class in db_exam_bundle.student_classes:
        if s_class.id == student_profile.student_class_id:
            is_eligible = True
            break
    if not is_eligible:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not eligible for this exam.")

    existing_active_attempt = (
        db.query(StudentExamAttempt)
        .filter(
            StudentExamAttempt.student_id == current_user.id,
            StudentExamAttempt.exam_bundle_id == exam_bundle_id,
            StudentExamAttempt.status == ExamAttemptStatus.IN_PROGRESS,
        )
        .first()
    )
    if existing_active_attempt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active attempt for this exam.",
        )

    new_attempt = StudentExamAttempt(
        student_id=current_user.id,
        exam_bundle_id=exam_bundle_id,
        start_time=datetime.now(timezone.utc),
        status=ExamAttemptStatus.IN_PROGRESS
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    # QuestionSchema already excludes 'answer' field, so direct validation is fine.
    questions_for_exam = [QuestionSchema.model_validate(q) for q in db_exam_bundle.questions]

    attempt_schema = StudentExamAttemptSchema.model_validate(new_attempt)

    return StartExamAttemptResponse(attempt=attempt_schema, questions=questions_for_exam)


@router.get("/exam_attempts", response_model=List[StudentExamAttemptSchema])
def list_student_exam_attempts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their exam attempts."
        )

    attempts = db.query(StudentExamAttempt).filter(StudentExamAttempt.student_id == current_user.id).order_by(StudentExamAttempt.start_time.desc()).all()
    # For each attempt, Pydantic will serialize it.
    # StudentExamAttemptSchema has answers: List[StudentAnswerSchema].
    # StudentAnswerSchema now has correct_answer field.
    # The StudentAnswer model has @property correct_answer.
    # So, this should work directly.
    return attempts


@router.get("/exam_attempts/{attempt_id}/result", response_model=StudentExamAttemptSchema)
def get_student_exam_attempt_result(
    attempt_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can view their exam results."
        )

    db_attempt = db.query(StudentExamAttempt).filter(
        StudentExamAttempt.id == attempt_id,
        StudentExamAttempt.student_id == current_user.id
    ).options(
        # Eager load answers and their related questions to ensure `correct_answer` property can be accessed
        # without further queries if the session were to close before Pydantic serialization.
        # This depends on how Pydantic interacts with lazy-loaded properties.
        # For safety, especially if properties access related models that might be lazy-loaded:
        # from sqlalchemy.orm import joinedload
        # .options(joinedload(StudentExamAttempt.answers).joinedload(StudentAnswer.question))
        # However, Pydantic's from_attributes usually handles this by accessing properties during serialization.
        # Let's assume it works first, and optimize with joinedload if performance/lazyloading becomes an issue.
    ).first()

    if not db_attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam attempt not found or does not belong to the current user."
        )

    if db_attempt.status == ExamAttemptStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This exam attempt is still in progress. Submit answers to view results."
        )

    return db_attempt


@router.post("/exam_attempts/{attempt_id}/submit", response_model=StudentExamAttemptSchema)
def submit_exam_answers(
    attempt_id: UUID,
    answers_submission: List[StudentAnswerCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can submit answers."
        )

    # Fetch the student's exam attempt
    db_attempt = db.query(StudentExamAttempt).filter(
        StudentExamAttempt.id == attempt_id,
        StudentExamAttempt.student_id == current_user.id
    ).first()

    if not db_attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam attempt not found or does not belong to the current user."
        )

    if db_attempt.status != ExamAttemptStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This exam attempt is already {db_attempt.status.value} and cannot be submitted to."
        )

    total_score_achieved = 0.0

    # Fetch all question IDs part of the original exam bundle to validate submitted question_ids
    # Ensure exam_bundle relationship is loaded if it's lazy by default.
    # Accessing db_attempt.exam_bundle might trigger a lazy load if session is still active.
    if not db_attempt.exam_bundle: # Should not happen if FK is set and data is consistent
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Exam bundle details missing for the attempt.")

    exam_bundle_question_ids = {str(q.id) for q in db_attempt.exam_bundle.questions}
    processed_question_ids = set()

    for answer_data in answers_submission:
        str_question_id = str(answer_data.question_id)
        if str_question_id not in exam_bundle_question_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Question ID {answer_data.question_id} is not part of this exam bundle."
            )
        if str_question_id in processed_question_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate answer submitted for question ID {answer_data.question_id}."
            )
        processed_question_ids.add(str_question_id)

        db_question = db.query(Question).filter(Question.id == answer_data.question_id).first()
        if not db_question:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question with id {answer_data.question_id} not found.")

        is_correct = False
        marks_awarded = 0.0

        if str(answer_data.selected_answer) == str(db_question.answer):
            is_correct = True
            marks_awarded = 1.0

        total_score_achieved += marks_awarded

        student_answer = StudentAnswer(
            student_exam_attempt_id=db_attempt.id,
            question_id=answer_data.question_id,
            selected_answer=str(answer_data.selected_answer),
            is_correct=is_correct,
            marks_awarded=marks_awarded
        )
        db.add(student_answer)

    db_attempt.score = total_score_achieved
    db_attempt.status = ExamAttemptStatus.GRADED
    db_attempt.submission_time = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_attempt)

    return db_attempt
