from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from app.core.dependencies import get_db
from app.models.subject import Subject
from app.models.user import User
from app.utils.constant.globals import UserRole
from app.schemas.subject import *
from app.api.endpoints.user.functions import get_current_active_user
from sqlalchemy.orm import Session 
from typing import List

router = APIRouter(prefix="/subject", tags=['Subjects'])

@router.post("/create", response_model=SubjectSchema, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject: SubjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admins can create subjects"
        )
    db_subject = Subject(name=subject.name)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


@router.get("/all", response_model=List[SubjectSchema])
def read_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    subjects = db.query(Subject).offset(skip).limit(limit).all()
    return subjects


@router.get("/{subject_id}", response_model=SubjectSchema)
def read_subject(subject_id: int, db: Session = Depends(get_db)):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_subject



@router.put("/update/{subject_id}", response_model=SubjectSchema)
def update_subject(
    subject_id: int, subject: SubjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admins can update subjects"
        )
    db_subject.name = subject.name
    db.commit()
    db.refresh(db_subject)
    return db_subject



@router.delete("/delete/{subject_id}", response_model=SubjectSchema)
def delete_subject(
    subject_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only admins can delete subjects"
        )
    db.delete(db_subject)
    db.commit()
    return db_subject
