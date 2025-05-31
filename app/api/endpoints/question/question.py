from fastapi import APIRouter, status, Depends, HTTPException, Response
from app.core.dependencies import get_db
from app.models.subject import Subject
from app.models.question import Question
from app.models.user import User
from app.utils.constant.globals import UserRole
from app.schemas.question import *
from app.api.endpoints.user.functions import get_current_active_user
from sqlalchemy.orm import Session 
from typing import List
from uuid import UUID

router = APIRouter(prefix="/question", tags=['Question'])


@router.post("/create", response_model=QuestionSchema, status_code=status.HTTP_201_CREATED)
def create_question(
    question: QuestionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create questions"
        )
    db_subject = db.query(Subject).filter(Subject.id == question.subject_id).first()
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Subject not found"
        )  # Ensure subject exists

    db_question = Question(
        type=question.type,
        subject_id=question.subject_id,
        question_text=question.question_text,
        options=question.options,
        answer=question.answer,
        year=question.year
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@router.get("/all", response_model=List[QuestionSchema])
def read_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    questions = db.query(Question).offset(skip).limit(limit).all()
    return questions


@router.get("/{question_id}", response_model=QuestionSchema)
def read_question(question_id: UUID, db: Session = Depends(get_db)):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return db_question



@router.put("/update/{question_id}", response_model=QuestionSchema)
def update_question(
    question_id: UUID, question: QuestionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    if current_user.role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only Admins or Teachers can update questions"
        )

    db_subject = db.query(Subject).filter(Subject.id == question.subject_id).first()
    if not db_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Subject not found"
        )  # Ensure subject exists

    db_question.type = question.type
    db_question.subject_id = question.subject_id
    db_question.question_text = question.question_text
    db_question.options = question.options
    db_question.answer = question.answer
    db_question.year = question.year
    db.commit()
    db.refresh(db_question)
    return db_question



@router.delete("/delete/{question_id}", response_model=QuestionSchema)
def delete_question(
    question_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete questions"
        )
    db.delete(db_question)
    db.commit()
    return db_question


@router.get("/{question_id}/image")
def get_question_image(question_id: UUID, db: Session = Depends(get_db)):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    if not db_question.question_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found for this question")

    return Response(content=db_question.question_image, media_type="image/jpeg")