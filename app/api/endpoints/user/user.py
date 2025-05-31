# fastapi 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.dependencies import get_db, oauth2_scheme 
from app.schemas.user import User, UserCreate, UserUpdate, UserCounts
from app.api.endpoints.user import functions as user_functions
from app.models.user import User as Usermodel
from app.models.admin import Admin
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.exam_bundle import ExamBundle
from app.models.question import Question
from app.models.subject import Subject
from app.models.student_class import StudentClass
from uuid import UUID


router = APIRouter()


# @router.get('/')
# async def read_auth_page():
#     return {"msg": "Auth page Initialization done"}

# create new user 
@router.post('/', response_model=User)
async def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_functions.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = user_functions.create_new_user(db, user)
    return new_user

# get all user 
@router.get('/', response_model=list[User])
async def read_all_user( skip: int = 0, limit: int = 100,  db: Session = Depends(get_db)):
    return user_functions.read_all_user(db, skip, limit)


#=============================
@router.get("/count", response_model=UserCounts)
def get_user_counts(
    db: Session = Depends(get_db),
    current_admin_user: Admin = Depends(user_functions.get_current_admin_user)
):
    """
    Returns the total number of students, teachers, and admins.
    Requires admin privileges.
    """
    try:
        total_students = db.query(Student).count()
        total_teachers = db.query(Teacher).count()
        total_admins = db.query(Admin).count()
        total_users = db.query(Usermodel).count()
        total_exams = db.query(ExamBundle).count()
        total_questions = db.query(Question).count()
        total_subjects = db.query(Subject).count()
        total_classes = db.query(StudentClass).count()

        return UserCounts(
            total_students=total_students,
            total_teachers=total_teachers,
            total_admins=total_admins,
            total_users=total_users,
            total_exams=total_exams,
            total_questions=total_questions,
            total_subjects=total_subjects,
            total_classes=total_classes
        )
    except Exception as e:
        print(f"Error fetching user counts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching user counts."
        )
#=============================


# get current user 
@router.get('/me', response_model=User)
async def read_current_user(current_user: Annotated[User, Depends(user_functions.get_current_user)]):
    """
    Retrieves the current authenticated user's details.
    """
    return current_user

# get user by id 
@router.get('/{user_id}', response_model=User)
async def read_user_by_id( user_id: UUID, db: Session = Depends(get_db)):
    return user_functions.get_user_by_id(db, user_id)

@router.patch('/{user_id}', 
              response_model=User,
            #   dependencies=[Depends(RoleChecker(['admin']))]
              )
async def update_user( user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    print(f"Received data: {user.model_dump()}")
    return user_functions.update_user(db, user_id, user)


@router.delete('/{user_id}', 
            #    response_model=User,
            #    dependencies=[Depends(RoleChecker(['admin']))]
               )
async def delete_user( user_id: int, db: Session = Depends(get_db)):
    return user_functions.delete_user(db, user_id)


