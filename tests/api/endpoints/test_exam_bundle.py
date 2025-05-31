from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User
from app.models.subject import Subject
from app.models.student_class import StudentClass
from app.models.question import Question
from app.models.exam_bundle import ExamBundle # To check DB directly
from app.utils.constant.globals import UserRole # For role checking if needed
from app.core.database import get_db # To fetch user for payload

# Tests for Exam Bundle API (prefix="/exam_bundle", tags=['Exam Bundle'])

def test_create_exam_bundle_as_admin(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict,
    test_subject1: Subject,
    test_subject2: Subject,
    test_class1: StudentClass,
    test_questions_s1: list[Question], # Ensure questions are created
    test_questions_s2: list[Question]
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    payload = {
        "name": "Admin Midterm Exam",
        "time_in_mins": "PT60M", # ISO 8601 duration for 60 minutes
        "is_active": True,
        "subject_combinations": {
            str(test_subject1.id): 5, # 5 questions from subject 1
            str(test_subject2.id): 3  # 3 questions from subject 2
        },
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(admin_user.id)
    }

    response = client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json=payload)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Admin Midterm Exam"
    assert len(data["questions"]) == 8 # 5 + 3
    assert str(test_subject1.id) in data["subject_combinations"]
    assert data["subject_combinations"][str(test_subject1.id)] == 5
    assert len(data["student_classes"]) == 1
    assert data["student_classes"][0]["id"] == str(test_class1.id)

    # Check DB
    bundle_in_db = db.query(ExamBundle).filter(ExamBundle.id == data["id"]).first()
    assert bundle_in_db is not None
    assert len(bundle_in_db.questions) == 8
    assert len(bundle_in_db.student_classes) == 1

def test_create_exam_bundle_as_teacher(
    client: TestClient,
    db: Session,
    teacher_auth_headers: dict,
    test_subject1: Subject,
    test_class1: StudentClass,
    test_questions_s1: list[Question]
):
    teacher_user = db.query(User).filter(User.email == "teacher@example.com").first()
    payload = {
        "name": "Teacher Weekly Test",
        "time_in_mins": "PT30M",
        "is_active": True,
        "subject_combinations": {str(test_subject1.id): 3},
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(teacher_user.id) # Required by schema
    }
    response = client.post("/api/v1/exam_bundle/create", headers=teacher_auth_headers, json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Teacher Weekly Test"
    assert len(data["questions"]) == 3

def test_create_exam_bundle_as_student_fails(
    client: TestClient,
    db: Session, # Added db to fetch student user for payload consistency, though it should fail before validation
    student_auth_headers: dict,
    test_subject1: Subject,
    test_class1: StudentClass
):
    student_user = db.query(User).filter(User.email == "student@example.com").first()
    payload = {
        "name": "Student Attempt",
        "time_in_mins": "PT30M",
        "is_active": True,
        "subject_combinations": {str(test_subject1.id): 1},
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(student_user.id) # Required by schema, even if auth fails first
    }
    response = client.post("/api/v1/exam_bundle/create", headers=student_auth_headers, json=payload)
    assert response.status_code == 403, response.text # Forbidden

def test_create_exam_bundle_insufficient_questions(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict,
    test_subject1: Subject,
    test_class1: StudentClass,
    test_questions_s1: list[Question] # Creates 10 questions for subject1
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    payload = {
        "name": "Too Many Questions Test",
        "time_in_mins": "PT60M",
        "is_active": True,
        "subject_combinations": {str(test_subject1.id): 15}, # Request 15, only 10 available
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(admin_user.id)
    }
    response = client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json=payload)
    assert response.status_code == 400, response.text # Bad Request
    assert "Not enough questions available" in response.json()["detail"]

def test_create_exam_bundle_invalid_subject_id(
    client: TestClient, db: Session, admin_auth_headers: dict, test_class1: StudentClass
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    invalid_subject_id = "00000000-0000-0000-0000-000000000000"
    payload = {
        "name": "Invalid Subject Test",
        "time_in_mins": "PT60M",
        "is_active": True,
        "subject_combinations": {invalid_subject_id: 5},
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(admin_user.id)
    }
    response = client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json=payload)
    assert response.status_code == 400, response.text # Bad Request
    assert "Subject with id" in response.json()["detail"] and "not found" in response.json()["detail"]

def test_create_exam_bundle_invalid_class_id(
    client: TestClient, db: Session, admin_auth_headers: dict, test_subject1: Subject, test_questions_s1: list[Question]
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    invalid_class_id = "11111111-1111-1111-1111-111111111111"
    payload = {
        "name": "Invalid Class Test",
        "time_in_mins": "PT60M",
        "is_active": True,
        "subject_combinations": {str(test_subject1.id): 5},
        "class_ids": [invalid_class_id],
        "uploaded_by_id": str(admin_user.id)
    }
    response = client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json=payload)
    assert response.status_code == 400, response.text # Bad Request
    assert "StudentClass with id" in response.json()["detail"] and "not found" in response.json()["detail"]

def test_get_exam_bundle(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict, # Using admin for creation, but any authenticated user should be able to fetch
    test_subject1: Subject,
    test_class1: StudentClass,
    test_questions_s1: list[Question]
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    create_payload = {
        "name": "Fetchable Exam",
        "time_in_mins": "PT45M",
        "is_active": True,
        "subject_combinations": {str(test_subject1.id): 2},
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(admin_user.id)
    }
    create_response = client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json=create_payload)
    assert create_response.status_code == 201
    bundle_id = create_response.json()["id"]

    # Fetch using teacher credentials to show other roles can also fetch
    teacher_user = db.query(User).filter(User.email == "teacher@example.com").first()
    from app.api.endpoints.user.auth import create_access_token
    teacher_token = create_access_token(data={"sub": str(teacher_user.id)})
    headers = {"Authorization": f"Bearer {teacher_token}"}

    response = client.get(f"/api/v1/exam_bundle/{bundle_id}", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == bundle_id
    assert data["name"] == "Fetchable Exam"

def test_get_all_exam_bundles(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict,
    test_subject1: Subject,
    test_class1: StudentClass,
    test_questions_s1: list[Question]
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    # Create a couple of bundles
    client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json={
        "name": "Bundle 1", "time_in_mins": "PT10M", "is_active": True,
        "subject_combinations": {str(test_subject1.id): 1}, "class_ids": [str(test_class1.id)], "uploaded_by_id": str(admin_user.id)
    }).raise_for_status() # Ensure creation succeeded
    client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json={
        "name": "Bundle 2", "time_in_mins": "PT10M", "is_active": True,
        "subject_combinations": {str(test_subject1.id): 1}, "class_ids": [str(test_class1.id)], "uploaded_by_id": str(admin_user.id)
    }).raise_for_status() # Ensure creation succeeded


    response = client.get("/api/v1/exam_bundle/all", headers=admin_auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    # This assertion depends on the test isolation. With Base.metadata.drop_all/create_all per test, it should be 2.
    # If other bundles from other tests persist, this might be > 2.
    # For now, assume clean state from fixtures.
    assert len(data) == 2
    bundle_names = {item["name"] for item in data}
    assert "Bundle 1" in bundle_names
    assert "Bundle 2" in bundle_names


def test_update_exam_bundle_as_admin(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict,
    test_subject1: Subject,
    test_subject2: Subject,
    test_class1: StudentClass,
    test_class2: StudentClass,
    test_questions_s1: list[Question], # Provides 10 for S1
    test_questions_s2: list[Question]  # Provides 7 for S2
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    # Create initial bundle
    create_payload = {
        "name": "Initial Bundle", "time_in_mins": "PT60M", "is_active": True,
        "subject_combinations": {str(test_subject1.id): 3}, # Needs 3 from S1
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(admin_user.id)
    }
    create_response = client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json=create_payload)
    assert create_response.status_code == 201
    bundle_id = create_response.json()["id"]

    update_payload = {
        "name": "Updated Bundle Name",
        "time_in_mins": "PT90M",
        "is_active": False,
        "subject_combinations": {str(test_subject2.id): 4}, # Needs 4 from S2
        "class_ids": [str(test_class2.id)],
        "uploaded_by_id": str(admin_user.id)
    }
    response = client.put(f"/api/v1/exam_bundle/update/{bundle_id}", headers=admin_auth_headers, json=update_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Updated Bundle Name"
    assert data["is_active"] is False
    assert len(data["questions"]) == 4
    assert str(test_subject2.id) in data["subject_combinations"]
    assert data["subject_combinations"][str(test_subject2.id)] == 4
    assert len(data["student_classes"]) == 1
    assert data["student_classes"][0]["id"] == str(test_class2.id)
    assert data["student_classes"][0]["name"] == test_class2.name # Check name as well

def test_delete_exam_bundle_as_teacher(
    client: TestClient,
    db: Session,
    teacher_auth_headers: dict,
    test_subject1: Subject,
    test_class1: StudentClass,
    test_questions_s1: list[Question]
):
    teacher_user = db.query(User).filter(User.email == "teacher@example.com").first()
    # Create a bundle to delete
    create_payload = {
        "name": "To Be Deleted", "time_in_mins": "PT10M", "is_active": True,
        "subject_combinations": {str(test_subject1.id): 1},
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(teacher_user.id)
    }
    create_response = client.post("/api/v1/exam_bundle/create", headers=teacher_auth_headers, json=create_payload)
    assert create_response.status_code == 201
    bundle_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/exam_bundle/delete/{bundle_id}", headers=teacher_auth_headers)
    assert delete_response.status_code == 200, delete_response.text

    # Verify it's gone
    get_response = client.get(f"/api/v1/exam_bundle/{bundle_id}", headers=teacher_auth_headers)
    assert get_response.status_code == 404

# TODO: Add more tests:
# - Update by student (fail 403)
# - Delete by student (fail 403)
# - Update with invalid subject/class IDs (fail 400) - similar to create
# - Update with insufficient questions (fail 400) - similar to create
# - Test `time_in_mins` output format in GET requests if specific (e.g. "PT60M" or total seconds)
# - Test edge cases for subject_combinations (e.g., empty dict, many subjects)
# - Test edge cases for class_ids (e.g., empty list)
# - Test updating only a subset of fields (e.g., only `is_active`)
# - Test deletion of a non-existent bundle (should be 404)
# - Test update of a non-existent bundle (should be 404)
# - Test if questions are indeed different if subject_combinations are changed on update.
# - Test if student_classes are correctly cleared and updated on update.
# - Test that `no_of_participants` is default 0 on create and not changed by update endpoint.
# - Test that `uploaded_by_id` is correctly set and not changed by update payload.
# - Test pagination for `/all` endpoint if many bundles exist.
# - Test that if `class_ids` is an empty list in create/update, `student_classes` becomes empty.
# - Test that if `subject_combinations` is an empty dict, `questions` becomes empty.
#   (Current endpoint logic might require at least one subject, need to check requirements)
#   The current schema for ExamBundleCreate implies subject_combinations is Dict[UUID, int],
#   Pydantic might not allow empty if no default_factory=dict is set for the field.
#   If it's allowed, the endpoint should handle it.
#   The current Question fetching logic iterates `subject_combinations.items()`, so empty dict = no questions.
#   This seems fine.
# - Test if `uploaded_by_id` in payload for update has any effect (it shouldn't, as it's fixed on creation).
#   The schema `ExamBundleCreate` is used for update. If `uploaded_by_id` is in it, it must be provided.
#   The endpoint logic for update does: `db_exam_bundle.subject_combinations = exam_bundle.subject_combinations`
#   but does not update `uploaded_by_id`. This is correct.
# - Test for `questions_per_subject` no longer being a valid field in `ExamBundleCreate`.
#   This will be caught by Pydantic validation if someone tries to send it.
#   A test could explicitly send it and expect a 422 Unprocessable Entity.

def test_update_exam_bundle_clear_classes(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict,
    test_subject1: Subject,
    test_class1: StudentClass,
    test_questions_s1: list[Question]
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    create_payload = {
        "name": "Bundle with Classes", "time_in_mins": "PT60M", "is_active": True,
        "subject_combinations": {str(test_subject1.id): 2},
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(admin_user.id)
    }
    create_response = client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json=create_payload)
    assert create_response.status_code == 201
    bundle_id = create_response.json()["id"]
    assert len(create_response.json()["student_classes"]) == 1

    update_payload = {
        "name": "Bundle with No Classes",
        "time_in_mins": "PT60M",
        "is_active": True,
        "subject_combinations": {str(test_subject1.id): 2},
        "class_ids": [], # Empty list to clear classes
        "uploaded_by_id": str(admin_user.id)
    }
    response = client.put(f"/api/v1/exam_bundle/update/{bundle_id}", headers=admin_auth_headers, json=update_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Bundle with No Classes"
    assert len(data["student_classes"]) == 0

    # Verify in DB
    bundle_in_db = db.query(ExamBundle).filter(ExamBundle.id == bundle_id).first()
    assert len(bundle_in_db.student_classes) == 0

def test_create_exam_bundle_no_classes(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict,
    test_subject1: Subject,
    test_questions_s1: list[Question]
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    payload = {
        "name": "No Classes Bundle",
        "time_in_mins": "PT60M",
        "is_active": True,
        "subject_combinations": {str(test_subject1.id): 1},
        "class_ids": [], # Empty list for class_ids
        "uploaded_by_id": str(admin_user.id)
    }
    response = client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "No Classes Bundle"
    assert len(data["student_classes"]) == 0

    bundle_in_db = db.query(ExamBundle).filter(ExamBundle.id == data["id"]).first()
    assert len(bundle_in_db.student_classes) == 0

def test_create_exam_bundle_with_old_questions_per_subject_fails(
    client: TestClient,
    db: Session,
    admin_auth_headers: dict,
    test_subject1: Subject,
    test_class1: StudentClass
):
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    payload = {
        "name": "Old Field Test",
        "time_in_mins": "PT60M",
        "is_active": True,
        "subject_combinations": {str(test_subject1.id): 5},
        "class_ids": [str(test_class1.id)],
        "uploaded_by_id": str(admin_user.id),
        "questions_per_subject": 5 # This field should cause validation error
    }
    response = client.post("/api/v1/exam_bundle/create", headers=admin_auth_headers, json=payload)
    assert response.status_code == 422, response.text # Unprocessable Entity for Pydantic validation error
    assert "questions_per_subject" in response.text # Check that the error message mentions the field
    assert "extra fields not permitted" in response.text.lower() # Pydantic v2 error message style
