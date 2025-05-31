from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from app.core.dependencies import get_db
from app.models.student import Student
from app.models.user import User
from app.schemas.student import StudentSchema, StudentCreate
from app.api.endpoints.user.functions import get_current_active_user, get_password_hash
from app.utils.constant.globals import UserRole # Added UserRole
from sqlalchemy.orm import Session 
import uuid # Ensure uuid is imported if student_id type hint uses it directly
from typing import List



router = APIRouter(prefix="/student", tags=['Students'])


@router.post("/create", response_model=StudentSchema, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create student accounts."
        )

    db_user_email = db.query(User).filter(User.email == student.email).first()
    if db_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    db_user_admin_no = db.query(Student).filter(Student.admin_no == student.admin_no).first()
    if db_user_admin_no:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Admin number already registered"
        )

    hashed_password = get_password_hash(student.password)
    db_student = Student(
        email=student.email,
        password=hashed_password, # This should set User.password
        first_name=student.first_name,
        last_name=student.last_name,
        admin_no=student.admin_no, # Added admin_no
        role=UserRole.STUDENT # Added role
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return db_student


@router.put("/{student_id}", response_model=StudentSchema)
def update_student(
    student_id: uuid.UUID, student: StudentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    db_student = db.query(Student).filter(Student.id == student_id).first()
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    # Admin can update any student, student can only update their own profile.
    # This endpoint is for student self-update or admin update.
    # The original logic only allowed self-update.
    # For now, let's keep it as self-update or admin update.
    if current_user.role != UserRole.ADMIN and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this student account.")

    # Check for email collision if email is being changed
    if student.email != db_student.email:
        existing_email_user = db.query(User).filter(User.email == student.email).first()
        if existing_email_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered by another user.")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    # Admin can delete any student. Student cannot delete their own account via this.
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can delete student accounts.")

    # Consider what happens to related data (exam attempts etc) - cascade deletes should handle if set up.
    db.delete(db_student)
    db.commit()
    return db_student