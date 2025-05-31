from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from app.core.dependencies import get_db
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.teacher import TeacherSchema, TeacherCreate
from app.api.endpoints.user.functions import get_current_active_user, get_password_hash
from app.utils.constant.globals import UserRole # Added UserRole
from sqlalchemy.orm import Session 
from typing import List
import uuid



router = APIRouter(prefix="/teacher", tags=['Teachers'])

@router.post("/create", response_model=TeacherSchema, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create teacher accounts."
        )

    db_user = db.query(User).filter(User.email == teacher.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = get_password_hash(teacher.password)
    db_teacher = Teacher(
        email=teacher.email,
        password=hashed_password, # This should set User.password
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        role=UserRole.TEACHER # Added role
    )
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.get("/all", response_model=List[TeacherSchema])
def read_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = db.query(Teacher).offset(skip).limit(limit).all()
    return teachers


@router.get("/{teacher_id}", response_model=TeacherSchema)
def read_teacher(teacher_id: uuid.UUID, db: Session = Depends(get_db)):
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return db_teacher


@router.put("/update/{teacher_id}", response_model=TeacherSchema)
def update_teacher(
    teacher_id: uuid.UUID, teacher: TeacherCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    if current_user.role != UserRole.ADMIN and current_user.id != teacher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this teacher account.")

    if teacher.email != db_teacher.email:
        existing_email_user = db.query(User).filter(User.email == teacher.email).first()
        if existing_email_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered by another user.")

    db_teacher.email = teacher.email
    db_teacher.first_name = teacher.first_name
    db_teacher.last_name = teacher.last_name
    if teacher.password:
        db_teacher.password = get_password_hash(teacher.password)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


@router.delete("/delete/{teacher_id}", response_model=TeacherSchema)
def delete_teacher(
    teacher_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete teacher accounts.")

    db.delete(db_teacher)
    db.commit()
    return db_teacher
