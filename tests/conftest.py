import pytest
from typing import Generator, Any
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic.config import Config
from alembic import command

from app.main import app # Assuming app.main.app is your FastAPI instance
from app.core.database import Base, get_db
from app.core.settings import settings
from app.models.user import User
from app.models.subject import Subject
from app.models.student_class import StudentClass
from app.models.question import Question
from app.utils.constant.globals import UserRole, QuestionType
from app.api.endpoints.user.auth import create_access_token # For creating tokens

# Use a separate test database
TEST_DATABASE_URL = settings.DATABASE_URL + "_test"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    # Run alembic migrations
    alembic_cfg = Config("alembic.ini") # Ensure alembic.ini is at the root
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
    yield
    # Optionally, downgrade to base after tests
    # command.downgrade(alembic_cfg, "base")


@pytest.fixture(scope="function")
def db() -> Generator[Session, Any, None]:
    Base.metadata.create_all(bind=engine) # Create tables for each test function
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine) # Drop tables after each test function

@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, Any, None]:
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    del app.dependency_overrides[get_db] # Clean up

# --- Test Data Fixtures ---
@pytest.fixture(scope="function")
def test_admin_user(db: Session) -> User:
    admin = User(
        email="admin@example.com",
        password="adminpassword", # In a real scenario, hash this
        role=UserRole.ADMIN,
        first_name="Admin",
        last_name="User"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def test_teacher_user(db: Session) -> User:
    teacher = User(
        email="teacher@example.com",
        password="teacherpassword",
        role=UserRole.TEACHER,
        first_name="Teacher",
        last_name="User"
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher

@pytest.fixture(scope="function")
def test_student_user(db: Session) -> User:
    student = User(
        email="student@example.com",
        password="studentpassword",
        role=UserRole.USER, # Assuming USER is student role
        first_name="Student",
        last_name="User"
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@pytest.fixture(scope="function")
def admin_auth_headers(test_admin_user: User) -> dict:
    access_token = create_access_token(data={"sub": str(test_admin_user.id)})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def teacher_auth_headers(test_teacher_user: User) -> dict:
    access_token = create_access_token(data={"sub": str(test_teacher_user.id)})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def student_auth_headers(test_student_user: User) -> dict:
    access_token = create_access_token(data={"sub": str(test_student_user.id)})
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture(scope="function")
def test_subject1(db: Session) -> Subject:
    subject = Subject(name="Math")
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@pytest.fixture(scope="function")
def test_subject2(db: Session) -> Subject:
    subject = Subject(name="Science")
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@pytest.fixture(scope="function")
def test_class1(db: Session) -> StudentClass:
    s_class = StudentClass(name="Class 10A")
    db.add(s_class)
    db.commit()
    db.refresh(s_class)
    return s_class

@pytest.fixture(scope="function")
def test_class2(db: Session) -> StudentClass:
    s_class = StudentClass(name="Class 11B")
    db.add(s_class)
    db.commit()
    db.refresh(s_class)
    return s_class

@pytest.fixture(scope="function")
def test_questions_s1(db: Session, test_subject1: Subject) -> list[Question]:
    questions = []
    for i in range(10): # Create 10 questions for subject 1
        q = Question(
            subject_id=test_subject1.id,
            question_text=f"Math Question {i+1}",
            options={"A": "1", "B": "2", "C": "3", "D": "4"},
            answer="A",
            type=QuestionType.SCHOOL,
        )
        questions.append(q)
    db.add_all(questions)
    db.commit()
    for q in questions:
      db.refresh(q)
    return questions

@pytest.fixture(scope="function")
def test_questions_s2(db: Session, test_subject2: Subject) -> list[Question]:
    questions = []
    for i in range(7): # Create 7 questions for subject 2
        q = Question(
            subject_id=test_subject2.id,
            question_text=f"Science Question {i+1}",
            options={"A": "True", "B": "False"},
            answer="True",
            type=QuestionType.SCHOOL,
        )
        questions.append(q)
    db.add_all(questions)
    db.commit()
    for q in questions:
      db.refresh(q)
    return questions
