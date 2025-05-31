from fastapi import APIRouter, status, Depends, HTTPException
from app.core.dependencies import get_db
from app.models.subject import Subject
from app.models.question import Question
from app.models.user import User
from app.models.exam_bundle import ExamBundle
from app.models.student_class import StudentClass
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
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins or teachers can create exam bundles"
        )

    selected_questions = []
    for subject_id, num_questions in exam_bundle.subject_combinations.items():
        db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not db_subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Subject with id {subject_id} not found"
            )

        # Fetch questions for each subject
        questions_query = (
            select(Question.id)
            .filter(Question.subject_id == subject_id)
            .order_by(func.random())
            .limit(num_questions)
        )
        # Execute the query to get question IDs
        question_ids = db.execute(questions_query).scalars().all()

        if len(question_ids) < num_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough questions available for subject {db_subject.name} (requested {num_questions}, found {len(question_ids)})",
            )

        # Fetch actual Question objects
        questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
        selected_questions.extend(questions)

    db_exam_bundle = ExamBundle(
        name=exam_bundle.name,
        time_in_mins=exam_bundle.time_in_mins,
        is_active=exam_bundle.is_active,
        subject_combinations=exam_bundle.subject_combinations, # This now holds Dict[UUID, int]
        uploaded_by_id=current_user.id,
    )
    db.add(db_exam_bundle)

    # Associate the selected questions with the exam bundle
    for question in selected_questions:
        db_exam_bundle.questions.append(question)

    # Associate student classes
    if exam_bundle.class_ids:
        for class_id in exam_bundle.class_ids:
            student_class = db.query(StudentClass).filter(StudentClass.id == class_id).first()
            if not student_class:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"StudentClass with id {class_id} not found"
                )
            db_exam_bundle.student_classes.append(student_class)

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam Bundle not found")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam Bundle not found")

    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins or teachers can update exam bundles"
        )

    # Update basic fields
    db_exam_bundle.name = exam_bundle.name
    db_exam_bundle.time_in_mins = exam_bundle.time_in_mins
    db_exam_bundle.is_active = exam_bundle.is_active
    db_exam_bundle.subject_combinations = exam_bundle.subject_combinations

    # Clear existing associations for questions and student classes
    db_exam_bundle.questions = []
    db_exam_bundle.student_classes = []
    # It might be better to commit here if there's a chance of failure below,
    # but often it's fine to commit once at the end. For now, one commit at the end.

    selected_questions = []
    for subject_id, num_questions in exam_bundle.subject_combinations.items():
        db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
        if not db_subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Subject with id {subject_id} not found"
            )

        questions_query = (
            select(Question.id)
            .filter(Question.subject_id == subject_id)
            .order_by(func.random())
            .limit(num_questions)
        )
        question_ids = db.execute(questions_query).scalars().all()

        if len(question_ids) < num_questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough questions available for subject {db_subject.name} (requested {num_questions}, found {len(question_ids)})",
            )

        questions = db.query(Question).filter(Question.id.in_(question_ids)).all()
        selected_questions.extend(questions)

    # Associate the new selected questions with the exam bundle
    for question in selected_questions:
        db_exam_bundle.questions.append(question)

    # Fetch and add new student classes
    if exam_bundle.class_ids:
        for class_id in exam_bundle.class_ids:
            student_class = db.query(StudentClass).filter(StudentClass.id == class_id).first()
            if not student_class:
                # db.rollback() # Rollback if a class is not found, if previous parts were committed.
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"StudentClass with id {class_id} not found during update"
                )
            db_exam_bundle.student_classes.append(student_class)

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam Bundle not found")

    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins or teachers can delete exam bundles"
        )

    db.delete(db_exam_bundle)
    db.commit()
    return db_exam_bundle
