from fastapi import APIRouter, status, Depends, HTTPException
from app.core.dependencies import get_db
from app.models.subject import Subject
from app.models.question import Question
from app.models.user import User
from app.models.exam_bundle import ExamBundle
from app.utils.constant.globals import UserRole
from app.schemas.exam_bundle import *
from app.api.endpoints.user.functions import get_current_active_user
from sqlalchemy.orm import Session 
from typing import List
from sqlalchemy import func, select
from uuid import UUID

router = APIRouter(prefix="/exam_bundle", tags=['Exam Bundle'])

@router.post(
    "/create",
    response_model=ExamBundleSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_exam_bundle(
    exam_bundle: ExamBundleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admins can create exam bundles"
        )

    # Validate subject combinations
    for subject_id in exam_bundle.subject_combinations:
        db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not db_subject:
            raise HTTPException(
                status_code=400, detail=f"Subject with id {subject_id} not found"
            )

    # Fetch questions for each subject, limit the number of questions.
    selected_questions = []
    for subject_id in exam_bundle.subject_combinations:
        #  use a subquery to get random questions for each subject
        sub_query = (
            select(Question.id)
            .filter(Question.subject_id == subject_id)
            .order_by(func.random())
            .limit(exam_bundle.questions_per_subject)
            .alias("sub_query")
        )
        # Use the subquery
        questions = db.query(Question).filter(Question.id.in_(sub_query)).all()
        if len(questions) < exam_bundle.questions_per_subject:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough questions available for subject {subject_id}",
            )
        selected_questions.extend(questions)

    db_exam_bundle = ExamBundle(
        name=exam_bundle.name,
        time_in_mins=exam_bundle.time_in_mins,
        is_active=exam_bundle.is_active,
        subject_combinations=exam_bundle.subject_combinations,
        uploaded_by_id=current_user.id,
    )
    db.add(db_exam_bundle)
    db.commit()

    # Associate the selected questions with the exam bundle
    for question in selected_questions:
        db_exam_bundle.questions.append(question)  # type: ignore

    db.commit()
    db.refresh(db_exam_bundle)
    return db_exam_bundle


@router.get("/all", response_model=List[ExamBundleSchema])
def read_exam_bundles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    exam_bundles = db.query(ExamBundle).offset(skip).limit(limit).all()
    return exam_bundles


@router.get("/{exam_bundle_id}", response_model=ExamBundleSchema)
def read_exam_bundle(exam_bundle_id: UUID, db: Session = Depends(get_db)):
    db_exam_bundle = (
        db.query(ExamBundle).filter(ExamBundle.id == exam_bundle_id).first()
    )
    if not db_exam_bundle:
        raise HTTPException(status_code=404, detail="Exam Bundle not found")
    return db_exam_bundle


@router.put("/update/{exam_bundle_id}", response_model=ExamBundleSchema)
def update_exam_bundle(
    exam_bundle_id: UUID,
    exam_bundle: ExamBundleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_exam_bundle = db.query(ExamBundle).filter(ExamBundle.id == exam_bundle_id).first()
    if not db_exam_bundle:
        raise HTTPException(status_code=404, detail="Exam Bundle not found")

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admins can update exam bundles"
        )

    db_exam_bundle.name = exam_bundle.name
    db_exam_bundle.time_in_mins = exam_bundle.time_in_mins
    db_exam_bundle.is_active = exam_bundle.is_active
    db_exam_bundle.subject_combinations = exam_bundle.subject_combinations

    # Validate subject combinations
    for subject_id in exam_bundle.subject_combinations:
        db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not db_subject:
            raise HTTPException(
                status_code=400, detail=f"Subject with id {subject_id} not found"
            )

    # Clear existing questions
    db_exam_bundle.questions = []

    # Fetch new set of questions
    selected_questions = []
    for subject_id in exam_bundle.subject_combinations:
        sub_query = (
            select(Question.id)
            .filter(Question.subject_id == subject_id)
            .order_by(func.random())
            .limit(exam_bundle.questions_per_subject)
            .alias("sub_query")
        )
        questions = db.query(Question).filter(Question.id.in_(sub_query)).all()
        if len(questions) < exam_bundle.questions_per_subject:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough questions available for subject {subject_id}",
            )
        selected_questions.extend(questions)

    # Associate the selected questions with the exam bundle
    for question in selected_questions:
        db_exam_bundle.questions.append(question)  # type: ignore

    db.commit()
    db.refresh(db_exam_bundle)
    return db_exam_bundle


@router.delete("/delete/{exam_bundle_id}", response_model=ExamBundleSchema)
def delete_exam_bundle(
    exam_bundle_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_exam_bundle = db.query(ExamBundle).filter(ExamBundle.id == exam_bundle_id).first()
    if not db_exam_bundle:
        raise HTTPException(status_code=404, detail="Exam Bundle not found")

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admins can delete exam bundles"
        )

    db.delete(db_exam_bundle)
    db.commit()
    return db_exam_bundle
