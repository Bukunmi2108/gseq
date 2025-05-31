import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from app.models.user import User
from app.models.student import Student
from app.models.subject import Subject
from app.models.student_class import StudentClass
from app.models.question import Question
from app.models.exam_bundle import ExamBundle
from app.models.student_exam_attempt import StudentExamAttempt, ExamAttemptStatus
from app.models.student_answer import StudentAnswer
from app.schemas.student_exam_attempt import StudentExamAttemptSchema # For type hints
from app.schemas.question import QuestionSchema # For type hints
from app.utils.constant.globals import UserRole # For creating users with specific roles

# Fixtures needed from conftest:
# client, db, test_admin_user, test_teacher_user, test_student_user,
# admin_auth_headers, teacher_auth_headers, student_auth_headers,
# test_subject1, test_subject2, test_class1, test_class2,
# test_questions_s1, test_questions_s2

# Helper function to create an exam bundle for tests
def create_exam_bundle_for_test(
    client: TestClient,
    db: Session,
    admin_headers: dict,
    name: str,
    subject_question_counts: dict, # {subject_id: count}
    class_ids: list[UUID],
    uploaded_by_id: UUID
) -> ExamBundle:
    payload = {
        "name": name,
        "time_in_mins": "PT60M", # 60 minutes
        "is_active": True,
        "subject_combinations": {str(k): v for k, v in subject_question_counts.items()},
        "class_ids": [str(cid) for cid in class_ids],
        "uploaded_by_id": str(uploaded_by_id)
    }
    response = client.post("/api/v1/exam_bundle/create", headers=admin_headers, json=payload)
    assert response.status_code == 201, f"Failed to create exam bundle for test: {response.text}"
    bundle_data = response.json()
    bundle = db.query(ExamBundle).filter(ExamBundle.id == bundle_data["id"]).first()
    assert bundle is not None
    return bundle

@pytest.fixture(scope="function")
def student_user_in_class1(db: Session, test_student_user: User, test_class1: StudentClass) -> Student:
    # test_student_user from conftest.py should ideally be a User with UserRole.STUDENT
    # The Student model is a joined table inheritance from User.
    # We fetch the User instance, then ensure it's treated as a Student and update its specific fields.

    # Ensure the user role is STUDENT for this context
    if test_student_user.role != UserRole.STUDENT:
        test_student_user.role = UserRole.STUDENT
        # If test_student_user is from a fixture that already committed it as non-STUDENT,
        # this change might not reflect if not committed back.
        # However, User model uses polymorphic_on=role, so this is critical.
        # Let's assume test_student_user fixture from conftest.py creates user with UserRole.USER or UserRole.STUDENT.
        # If UserRole.USER is student, then this is fine. If UserRole.STUDENT is distinct, it must be set.
        # The plan uses UserRole.STUDENT in endpoints, so let's align.

    db.commit() # Commit role change if any
    db.refresh(test_student_user)

    # Query for the Student specific model instance using the User ID.
    student_profile = db.query(Student).filter(Student.id == test_student_user.id).first()

    if not student_profile:
        # This implies that the test_student_user from conftest.py was just a User,
        # and no corresponding Student record was created (e.g. if Student is a separate table linked by user_id).
        # Given current model setup (Student inherits User), this path means test_student_user was not found as Student.
        # This could happen if the role was not set to STUDENT, and polymorphic loading didn't cast it.
        # Or if Student specific data (like admin_no) is required for the Student instance to be valid.
        # For this test setup, we'll assume if not found, we need to create it.
        # However, this is risky as 'id' must match.
        # A better way: ensure test_student_user fixture creates the User with role STUDENT.
        # And that Student model has an entry for this user ID.
        # For now, let's assume the test_student_user fixture creates a User that *can* be a Student.
        # And we ensure the student-specific attributes here.
        # The polymorphic setup means querying Student should find the User if role matches.
        # If role was UserRole.USER and Student expects UserRole.STUDENT, it won't be found.
        # This fixture will now assume test_student_user is a User whose role is set to STUDENT.
        # And it will ensure the Student specific attributes are set.
        # The Student model requires admin_no.
        # If the Student record doesn't exist despite User existing and role being STUDENT,
        # it might be because Student specific data was never added.
        # Let's try to update or create Student attributes.
        # This part is tricky due to SQLAlchemy's polymorphic identity.
        # Simplest: Assume Student entry exists if User with role STUDENT exists.
        test_student_user.admin_no = test_student_user.admin_no or f"ADM-{uuid4()}"
        test_student_user.student_class_id = test_class1.id
        db.merge(test_student_user) # Merge to update or insert Student specific data if User already exists.
                                    # This is not quite right for joined table.
                                    # For joined table, you'd create Student(id=user.id, ...).
                                    # For single table, you update user attributes. User.role is key.
                                    # Let's assume polymorphic setup where User is queried and Student fields are updated.
        student_profile = db.query(Student).filter(Student.id == test_student_user.id).first()
        if not student_profile : # If still not found, something is wrong with fixture assumptions
             # Fallback: create a new Student if all else fails (less ideal for linking to test_student_user auth)
             # This path should ideally not be hit if test_student_user is correctly configured.
             student_profile = Student(id=test_student_user.id, email=test_student_user.email, first_name="Test",last_name="Student", role=UserRole.STUDENT, admin_no=f"ADM-{uuid4()}", student_class_id=test_class1.id, password="testpassword")
             db.add(student_profile)


    student_profile.student_class_id = test_class1.id
    if not student_profile.admin_no: # Ensure admin_no is set
        student_profile.admin_no = f"ADM-{uuid4()}"
    db.commit()
    db.refresh(student_profile)
    return student_profile

@pytest.fixture(scope="function")
def exam_bundle_for_class1(
    client: TestClient, db: Session, admin_auth_headers: dict, test_admin_user: User,
    test_subject1: Subject, test_questions_s1: list[Question], test_class1: StudentClass
) -> ExamBundle:
    return create_exam_bundle_for_test(
        client, db, admin_auth_headers, "Class 1 Exam",
        {test_subject1.id: 5}, [test_class1.id], test_admin_user.id
    )

@pytest.fixture(scope="function")
def another_exam_bundle_for_class1(
    client: TestClient, db: Session, admin_auth_headers: dict, test_admin_user: User,
    test_subject2: Subject, test_questions_s2: list[Question], test_class1: StudentClass
) -> ExamBundle:
    return create_exam_bundle_for_test(
        client, db, admin_auth_headers, "Class 1 Science Exam",
        {test_subject2.id: 3}, [test_class1.id], test_admin_user.id
    )

# --- Tests ---

def test_list_available_exams_for_student(
    client: TestClient, db: Session, student_auth_headers: dict,
    student_user_in_class1: Student,
    exam_bundle_for_class1: ExamBundle,
):
    response = client.get("/api/v1/student/available_exams", headers=student_auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    found = any(item["id"] == str(exam_bundle_for_class1.id) for item in data)
    assert found, "Exam bundle for student's class not found in available exams."

def test_list_available_exams_not_student_fails(
    client: TestClient, teacher_auth_headers: dict
):
    response = client.get("/api/v1/student/available_exams", headers=teacher_auth_headers)
    assert response.status_code == 403

def test_start_exam_attempt_success(
    client: TestClient, db: Session, student_auth_headers: dict,
    student_user_in_class1: Student, exam_bundle_for_class1: ExamBundle
):
    response = client.post(f"/api/v1/student/exam_attempts/{exam_bundle_for_class1.id}/start", headers=student_auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()

    assert "attempt" in data
    assert "questions" in data

    attempt_data = data["attempt"]
    assert attempt_data["exam_bundle_id"] == str(exam_bundle_for_class1.id)
    assert attempt_data["student_id"] == str(student_user_in_class1.id)
    assert attempt_data["status"] == ExamAttemptStatus.IN_PROGRESS.value
    assert "id" in attempt_data
    attempt_id = attempt_data["id"]

    questions_data = data["questions"]
    assert len(questions_data) == 5
    for q_data in questions_data:
        assert "answer" not in q_data

    db_attempt = db.query(StudentExamAttempt).filter(StudentExamAttempt.id == attempt_id).first()
    assert db_attempt is not None
    assert db_attempt.status == ExamAttemptStatus.IN_PROGRESS

def test_start_exam_attempt_already_in_progress(
    client: TestClient, student_auth_headers: dict, exam_bundle_for_class1: ExamBundle
):
    client.post(f"/api/v1/student/exam_attempts/{exam_bundle_for_class1.id}/start", headers=student_auth_headers)
    response = client.post(f"/api/v1/student/exam_attempts/{exam_bundle_for_class1.id}/start", headers=student_auth_headers)
    assert response.status_code == 400, response.text
    assert "already have an active attempt" in response.json()["detail"]

def test_start_exam_attempt_not_eligible(
    client: TestClient, db: Session, student_auth_headers: dict,
    test_subject1: Subject, test_questions_s1: list[Question],
    test_class2: StudentClass, admin_auth_headers: dict, test_admin_user: User,
    student_user_in_class1: Student # Student is in class1
):
    bundle_for_class2 = create_exam_bundle_for_test(
       client, db, admin_auth_headers, "Class 2 Exam",
       {test_subject1.id: 1}, [test_class2.id], test_admin_user.id
    )
    response = client.post(f"/api/v1/student/exam_attempts/{bundle_for_class2.id}/start", headers=student_auth_headers)
    assert response.status_code == 403
    assert "not eligible for this exam" in response.json()["detail"]

def test_submit_exam_answers_success(
    client: TestClient, db: Session, student_auth_headers: dict,
    student_user_in_class1: Student, exam_bundle_for_class1: ExamBundle
):
    start_response = client.post(f"/api/v1/student/exam_attempts/{exam_bundle_for_class1.id}/start", headers=student_auth_headers)
    attempt_id = start_response.json()["attempt"]["id"]
    questions = start_response.json()["questions"]

    answers_payload = []
    expected_score = 0
    for i, q_data in enumerate(questions):
        question_id = q_data["id"]
        actual_question = db.query(Question).filter(Question.id == question_id).first()
        selected = actual_question.answer if i == 0 else "Wrong Answer" # Correct for 1st, wrong for others
        if str(selected) == str(actual_question.answer): # Ensure comparison is consistent (e.g. string vs string)
            expected_score += 1

        answers_payload.append({
            "question_id": question_id,
            "selected_answer": selected
        })

    submit_response = client.post(f"/api/v1/student/exam_attempts/{attempt_id}/submit", headers=student_auth_headers, json=answers_payload)
    assert submit_response.status_code == 200, submit_response.text
    data = submit_response.json()
    assert data["id"] == attempt_id
    assert data["status"] == ExamAttemptStatus.GRADED.value
    assert data["score"] == expected_score
    assert data["submission_time"] is not None

    db_attempt = db.query(StudentExamAttempt).filter(StudentExamAttempt.id == attempt_id).first()
    assert db_attempt.status == ExamAttemptStatus.GRADED
    assert db_attempt.score == expected_score
    assert len(db_attempt.answers) == len(questions)
    first_answer_in_db = db.query(StudentAnswer).filter(StudentAnswer.student_exam_attempt_id == attempt_id, StudentAnswer.question_id == questions[0]["id"]).first()
    assert first_answer_in_db is not None
    assert first_answer_in_db.is_correct is True

def test_submit_exam_answers_attempt_not_in_progress(
    client: TestClient, db: Session, student_auth_headers: dict, student_user_in_class1: Student, exam_bundle_for_class1: ExamBundle
):
    start_response = client.post(f"/api/v1/student/exam_attempts/{exam_bundle_for_class1.id}/start", headers=student_auth_headers)
    attempt_id = start_response.json()["attempt"]["id"]
    questions = start_response.json()["questions"]

    answers_payload = [{"question_id": questions[0]["id"], "selected_answer": "A"}]
    client.post(f"/api/v1/student/exam_attempts/{attempt_id}/submit", headers=student_auth_headers, json=answers_payload)

    response = client.post(f"/api/v1/student/exam_attempts/{attempt_id}/submit", headers=student_auth_headers, json=answers_payload)
    assert response.status_code == 400, response.text
    assert "already GRADED" in response.json()["detail"]

def test_submit_exam_answers_invalid_question_id(
    client: TestClient, student_auth_headers: dict, exam_bundle_for_class1: ExamBundle
):
    start_response = client.post(f"/api/v1/student/exam_attempts/{exam_bundle_for_class1.id}/start", headers=student_auth_headers)
    attempt_id = start_response.json()["attempt"]["id"]

    invalid_question_id = str(uuid4())
    answers_payload = [{"question_id": invalid_question_id, "selected_answer": "A"}]

    response = client.post(f"/api/v1/student/exam_attempts/{attempt_id}/submit", headers=student_auth_headers, json=answers_payload)
    assert response.status_code == 400
    assert f"Question ID {invalid_question_id} is not part of this exam bundle" in response.json()["detail"]

def test_get_student_exam_attempts_list(
    client: TestClient, db: Session, student_auth_headers: dict,
    student_user_in_class1: Student, exam_bundle_for_class1: ExamBundle,
    another_exam_bundle_for_class1: ExamBundle
):
    client.post(f"/api/v1/student/exam_attempts/{exam_bundle_for_class1.id}/start", headers=student_auth_headers).raise_for_status()
    client.post(f"/api/v1/student/exam_attempts/{another_exam_bundle_for_class1.id}/start", headers=student_auth_headers).raise_for_status()

    response = client.get("/api/v1/student/exam_attempts", headers=student_auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

    # Filter for attempts made by this specific student to avoid issues with other tests' data
    student_specific_attempts = [att for att in data if att["student_id"] == str(student_user_in_class1.id)]
    assert len(student_specific_attempts) >= 2

    bundle1_found = any(item["exam_bundle_id"] == str(exam_bundle_for_class1.id) for item in student_specific_attempts)
    bundle2_found = any(item["exam_bundle_id"] == str(another_exam_bundle_for_class1.id) for item in student_specific_attempts)
    assert bundle1_found and bundle2_found

def test_get_student_exam_attempt_result_success(
    client: TestClient, db: Session, student_auth_headers: dict,
    student_user_in_class1: Student, exam_bundle_for_class1: ExamBundle
):
    start_response = client.post(f"/api/v1/student/exam_attempts/{exam_bundle_for_class1.id}/start", headers=student_auth_headers)
    attempt_id = start_response.json()["attempt"]["id"]
    questions_in_exam = start_response.json()["questions"]

    answers_payload = []
    for q_data in questions_in_exam:
        actual_question = db.query(Question).filter(Question.id == q_data["id"]).first()
        answers_payload.append({"question_id": q_data["id"], "selected_answer": str(actual_question.answer)})

    client.post(f"/api/v1/student/exam_attempts/{attempt_id}/submit", headers=student_auth_headers, json=answers_payload)

    response = client.get(f"/api/v1/student/exam_attempts/{attempt_id}/result", headers=student_auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == attempt_id
    assert data["status"] == ExamAttemptStatus.GRADED.value
    assert data["score"] == len(questions_in_exam)
    assert len(data["answers"]) == len(questions_in_exam)

    for ans_data in data["answers"]:
        assert "question_id" in ans_data
        assert "selected_answer" in ans_data
        assert ans_data["is_correct"] is True
        assert "correct_answer" in ans_data
        assert ans_data["correct_answer"] is not None

def test_get_student_exam_attempt_result_in_progress(
    client: TestClient, student_auth_headers: dict, exam_bundle_for_class1: ExamBundle
):
    start_response = client.post(f"/api/v1/student/exam_attempts/{exam_bundle_for_class1.id}/start", headers=student_auth_headers)
    attempt_id = start_response.json()["attempt"]["id"]

    response = client.get(f"/api/v1/student/exam_attempts/{attempt_id}/result", headers=student_auth_headers)
    assert response.status_code == 400, response.text
    assert "still in progress" in response.json()["detail"]
