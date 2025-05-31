from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from app.core.dependencies import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentSchema, StudentCreate
from app.api.endpoints.user.functions import get_current_active_user
from app.api.endpoints.user.functions import get_password_hash
from sqlalchemy.orm import Session 
import uuid
from typing import List



router = APIRouter(prefix="/student", tags=['Students'])


@router.post("/create", response_model=StudentSchema, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_user = db.query(Student).filter(Student.admin_no == student.admin_no).first()
    if db_user:
        raise HTTPException(
            status_code=400, detail="Admin number already registered"
        )
    hashed_password = get_password_hash(student.password)
    db_student = Student(
        email=student.email,
        password=hashed_password,
        first_name=student.first_name,
        last_name=student.last_name,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.get("/all", response_model=List[StudentSchema])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.get("/{student_id}", response_model=StudentSchema)
def read_student(student_id: uuid.UUID, db: Session = Depends(get_db)):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student


@router.put("/{student_id}", response_model=StudentSchema)
def update_student(
    student_id: uuid.UUID, student: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_student.email = student.email
    db_student.first_name = student.first_name
    db_student.last_name = student.last_name
    if student.password:
        db_student.password = get_password_hash(student.password)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.delete("/delete/{student_id}", response_model=StudentSchema)
def delete_student(
    student_id: uuid.UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")

    if current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(db_student)
    db.commit()
    return db_student