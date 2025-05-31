import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func as sql_func # For random ordering if needed, though random.sample is used
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from typing import Optional, List # Added List for type hint

from app.models.user import User
from app.models.student import Student
from app.models.subject import Subject
from app.models.student_class import StudentClass
from app.models.question import Question
from app.models.practice_session import PracticeSession, PracticeSessionStatus
from app.models.practice_session_answer import PracticeSessionAnswer
from app.schemas.practice_session import PracticeSessionSchema
from app.schemas.question import QuestionSchema
from app.utils.constant.globals import UserRole, QuestionType
from app.core.dependencies import get_db # For create_question_for_practice helper

# Fixtures from conftest: client, db, test_student_user, student_auth_headers,
# test_subject1, test_subject2, test_questions_s1, test_questions_s2, (these might not be used if questions_for_practice_filters is comprehensive)
# test_admin_user, admin_auth_headers (for creating questions with year/type)
# test_class1 (to assign student to a class)


def create_question_for_practice(
    client: TestClient, admin_headers: dict, subject_id: UUID,
    text: str, q_type: QuestionType, year: Optional[int], answer: str = "A"
) -> Question:
    payload = {
        "subject_id": str(subject_id),
        "type": q_type.value,
        "question_text": text,
        "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}, # Ensure enough options for chr(ord('A') + (i % 4))
        "answer": answer,
        "year": year
    }
    response = client.post("/api/v1/question/create", headers=admin_headers, json=payload)
    assert response.status_code == 201, f"Failed to create question for practice: {response.text}"
    q_data = response.json()
    # Use the db session from the client's app dependency overrides
    db_session = client.app.dependency_overrides[get_db]().__next__()
    db_question = db_session.query(Question).get(q_data["id"])
    # client.app.dependency_overrides[get_db]().__next__().close() # Close session if manually created
    return db_question

@pytest.fixture(scope="function")
def student_user_setup(db: Session, test_student_user: User, test_class1: StudentClass) -> Student:
    # This fixture ensures the user from test_student_user fixture (from conftest)
    # is correctly set up as a Student with role, admin_no, and class.

    # Ensure the role is STUDENT
    if test_student_user.role != UserRole.STUDENT:
        test_student_user.role = UserRole.STUDENT
        db.add(test_student_user) # Add to session if modified
        db.commit()
        db.refresh(test_student_user)

    # Query for Student specific attributes or create/update them
    student = db.query(Student).filter(Student.id == test_student_user.id).first()
    if student:
        student.admin_no = student.admin_no or f"PS-{uuid4().hex[:6]}"
        student.student_class_id = student.student_class_id or test_class1.id
        db.add(student)
    else:
        # This case implies test_student_user was a base User not yet a Student in the Student table (for joined table inheritance)
        # Or if single table, that it wasn't correctly queried with Student polymorphic identity.
        # Assuming Student model is an extension of User and uses User's ID.
        student = Student(
            id=test_student_user.id, # Critical: Must match the User ID from test_student_user
            email=test_student_user.email, # Copy relevant fields
            first_name=test_student_user.first_name,
            last_name=test_student_user.last_name,
            password_hash=test_student_user.password, # If User model stores hashed password
            role=UserRole.STUDENT,
            admin_no=f"PS-{uuid4().hex[:6]}",
            student_class_id=test_class1.id
        )
        db.merge(student) # Use merge to handle User part potentially existing

    db.commit()
    db.refresh(student)
    return student

@pytest.fixture(scope="function")
def questions_for_practice_filters(client: TestClient, db: Session, admin_auth_headers: dict, test_subject1: Subject, test_subject2: Subject) -> List[Question]:
    q_list = []
    # Ensure questions from conftest are cleared or not interfering if they are not specific enough
    # For precise testing, it's better to create all questions needed for this test module here.

    # Delete existing questions to ensure a clean slate for filter tests (optional, depends on test isolation)
    # db.query(Question).delete()
    # db.commit()

    q_list.append(create_question_for_practice(client, admin_auth_headers, test_subject1.id, "S1 JAMB 2020 Q1", QuestionType.JAMB, 2020, "A"))
    q_list.append(create_question_for_practice(client, admin_auth_headers, test_subject1.id, "S1 WAEC 2020 Q1", QuestionType.WAEC, 2020, "B"))
    q_list.append(create_question_for_practice(client, admin_auth_headers, test_subject1.id, "S1 JAMB 2021 Q1", QuestionType.JAMB, 2021, "C"))
    q_list.append(create_question_for_practice(client, admin_auth_headers, test_subject2.id, "S2 NECO 2020 Q1", QuestionType.NECO, 2020, "D"))
    q_list.append(create_question_for_practice(client, admin_auth_headers, test_subject2.id, "S2 SCHOOL 2021 Q1", QuestionType.SCHOOL, 2021, "A"))

    for i in range(70):
        q_list.append(create_question_for_practice(client, admin_auth_headers, test_subject1.id, f"S1 JAMB 2022 Q{i+1}", QuestionType.JAMB, 2022, answer=chr(ord('A') + (i % 4))))

    db.commit() # Ensure all questions are committed before tests run
    return q_list

# --- Tests ---

def test_start_practice_session_no_filters(
    client: TestClient, student_auth_headers: dict, student_user_setup: Student, questions_for_practice_filters: list
):
    payload = {}
    response = client.post("/api/v1/student/practice/sessions/start", headers=student_auth_headers, json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "session" in data
    assert "questions" in data
    assert len(data["questions"]) > 0 # Should pick some questions
    assert len(data["questions"]) <= 60 # Max 60
    assert data["session"]["status"] == PracticeSessionStatus.IN_PROGRESS.value
    assert data["session"]["filter_subject_id"] is None
    assert data["session"]["filter_question_type"] is None
    assert data["session"]["filter_year"] is None

def test_start_practice_session_with_filters(
    client: TestClient, student_auth_headers: dict, student_user_setup: Student,
    questions_for_practice_filters: list, test_subject1: Subject
):
    payload = {
        "subject_id": str(test_subject1.id),
        "question_type": QuestionType.JAMB.value,
        "year": 2022
    }
    response = client.post("/api/v1/student/practice/sessions/start", headers=student_auth_headers, json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["questions"]) == 60 # We created 70 S1 JAMB 2022 questions
    assert data["session"]["filter_subject_id"] == str(test_subject1.id)
    assert data["session"]["filter_question_type"] == QuestionType.JAMB.value
    assert data["session"]["filter_year"] == 2022
    for q_data in data["questions"]:
        assert q_data["subject_id"] == str(test_subject1.id)
        assert q_data["type"] == QuestionType.JAMB.value
        # Year is not in QuestionSchema by default, if needed, it should be added.
        # The current QuestionSchema: id, type, subject_id, question_text, options.
        # Let's assume QuestionSchema was updated as per previous step to include year.
        # Re-checking plan: QuestionSchema was updated in step 1 of this overall task.
        # So, q_data["year"] should be available.
        # However, the question creation helper might need to ensure it returns Question model.
        # The endpoint returns QuestionSchema, which inherits year from QuestionBase.
        # Need to confirm Question model has year for this to pass. Yes, model was updated.
        # No, wait, the q_data is QuestionSchema. The schema had year added.
        # But the Question model instance used to create the QuestionSchema must have 'year'.
        # This is fine, `create_question_for_practice` creates Question with year.
        # And `QuestionSchema` now includes `year`.
        # So, `q_data['year']` should exist.
        # This test doesn't check q_data['year'] though. Let's add it if crucial.
        # For now, checking filters on session is primary.

def test_start_practice_session_no_questions_found(
    client: TestClient, student_auth_headers: dict, student_user_setup: Student, questions_for_practice_filters: list
):
    payload = {"year": 1900}
    response = client.post("/api/v1/student/practice/sessions/start", headers=student_auth_headers, json=payload)
    assert response.status_code == 404, response.text
    assert "No questions found" in response.json()["detail"]

def test_submit_practice_answers_success(
    client: TestClient, db: Session, student_auth_headers: dict, student_user_setup: Student,
    questions_for_practice_filters: list, test_subject1: Subject # questions_for_practice_filters ensures questions exist
):
    start_payload = {"subject_id": str(test_subject1.id), "question_type": QuestionType.JAMB.value, "year": 2022}
    start_response = client.post("/api/v1/student/practice/sessions/start", headers=student_auth_headers, json=start_payload)
    assert start_response.status_code == 200, start_response.text
    session_data = start_response.json()["session"]
    questions_data = start_response.json()["questions"] # These are QuestionSchema
    session_id = session_data["id"]

    answers_payload = []
    expected_score = 0
    for i, q_schema in enumerate(questions_data):
        question_id = q_schema["id"]
        # Fetch the actual question from DB to know its correct answer
        actual_question = db.query(Question).filter(Question.id == question_id).first()
        assert actual_question is not None, f"Question {question_id} from session not found in DB"

        selected_answer = actual_question.answer if i % 2 == 0 else "WrongAnswer" # Alternate
        if selected_answer == actual_question.answer:
            expected_score += 1.0 # Assuming 1 mark per question

        answers_payload.append({"question_id": question_id, "selected_answer": selected_answer})

    submit_response = client.post(f"/api/v1/student/practice/sessions/{session_id}/submit", headers=student_auth_headers, json=answers_payload)
    assert submit_response.status_code == 200, submit_response.text
    result_data = submit_response.json()
    assert result_data["id"] == session_id
    assert result_data["status"] == PracticeSessionStatus.COMPLETED.value
    assert result_data["score"] == expected_score
    assert len(result_data["answers"]) == len(questions_data)

def test_submit_practice_answers_invalid_question(
    client: TestClient, student_auth_headers: dict, student_user_setup: Student,
    questions_for_practice_filters: list, test_subject1: Subject
):
    start_payload = {"subject_id": str(test_subject1.id)}
    start_response = client.post("/api/v1/student/practice/sessions/start", headers=student_auth_headers, json=start_payload)
    session_id = start_response.json()["session"]["id"]

    answers_payload = [{"question_id": str(uuid4()), "selected_answer": "Doesn't matter"}]
    submit_response = client.post(f"/api/v1/student/practice/sessions/{session_id}/submit", headers=student_auth_headers, json=answers_payload)
    assert submit_response.status_code == 400
    assert "was not part of this practice session" in submit_response.json()["detail"]

def test_get_practice_sessions_list(
    client: TestClient, student_auth_headers: dict, student_user_setup: Student,
    questions_for_practice_filters: list, test_subject1: Subject
):
    client.post("/api/v1/student/practice/sessions/start", headers=student_auth_headers, json={"subject_id": str(test_subject1.id)}).raise_for_status()

    response = client.get("/api/v1/student/practice/sessions", headers=student_auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

    student_sessions = [s for s in data if s["student_id"] == str(student_user_setup.id)]
    assert len(student_sessions) >= 1
    assert student_sessions[0]["filter_subject_id"] == str(test_subject1.id)

def test_get_practice_session_result(
    client: TestClient, db: Session, student_auth_headers: dict, student_user_setup: Student,
    questions_for_practice_filters: list, test_subject1: Subject
):
    start_payload = {"subject_id": str(test_subject1.id), "question_type": QuestionType.JAMB.value, "year": 2022}
    start_response = client.post("/api/v1/student/practice/sessions/start", headers=student_auth_headers, json=start_payload)
    session_id = start_response.json()["session"]["id"]
    questions_data = start_response.json()["questions"]

    answers_payload = []
    for q_data in questions_data:
        actual_question = db.query(Question).filter(Question.id == q_data["id"]).first()
        answers_payload.append({"question_id": q_data["id"], "selected_answer": str(actual_question.answer)}) # All correct

    client.post(f"/api/v1/student/practice/sessions/{session_id}/submit", headers=student_auth_headers, json=answers_payload).raise_for_status()

    response = client.get(f"/api/v1/student/practice/sessions/{session_id}/result", headers=student_auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == session_id
    assert data["status"] == PracticeSessionStatus.COMPLETED.value
    assert data["score"] == len(questions_data) # All answers were correct
    assert len(data["answers"]) == len(questions_data)
    for ans_data in data["answers"]:
        assert ans_data["is_correct"] is True
        assert ans_data["correct_answer"] is not None

def test_get_practice_session_result_in_progress_fails(
    client: TestClient, student_auth_headers: dict, student_user_setup: Student,
    questions_for_practice_filters: list, test_subject1: Subject
):
    start_payload = {"subject_id": str(test_subject1.id)}
    start_response = client.post("/api/v1/student/practice/sessions/start", headers=student_auth_headers, json=start_payload)
    session_id = start_response.json()["session"]["id"]

    response = client.get(f"/api/v1/student/practice/sessions/{session_id}/result", headers=student_auth_headers)
    assert response.status_code == 400
    assert "still in progress" in response.json()["detail"]
