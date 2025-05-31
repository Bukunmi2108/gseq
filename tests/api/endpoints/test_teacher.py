import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.user import User # For type hinting current_user if needed by fixtures
from app.models.teacher import Teacher # For DB checks
from app.schemas.teacher import TeacherCreate # For payload structure reference
from app.utils.constant.globals import UserRole

# Fixtures from conftest: client, db, admin_auth_headers, teacher_auth_headers, student_auth_headers

API_V1_STR = "/api/v1" # Assuming this is the API prefix used in main.py

def test_create_teacher_by_admin_success(client: TestClient, db: Session, admin_auth_headers: dict):
    unique_email = f"newteacher_{uuid4().hex[:6]}@example.com"
    payload = {
        "email": unique_email,
        "password": "password123",
        "first_name": "New",
        "last_name": "Teacher"
        # TeacherCreate schema might have other fields, ensure they are covered if mandatory
    }
    response = client.post(f"{API_V1_STR}/teacher/create", headers=admin_auth_headers, json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == unique_email
    assert data["role"] == UserRole.TEACHER.value # Check if role is correctly set

    # Verify in DB
    teacher_in_db = db.query(Teacher).filter(Teacher.email == unique_email).first()
    assert teacher_in_db is not None
    assert teacher_in_db.role == UserRole.TEACHER

def test_create_teacher_by_teacher_fails(client: TestClient, teacher_auth_headers: dict):
    unique_email = f"newteacher_t_{uuid4().hex[:6]}@example.com"
    payload = {
        "email": unique_email, "password": "password123",
        "first_name": "NewT", "last_name": "TeacherT"
    }
    response = client.post(f"{API_V1_STR}/teacher/create", headers=teacher_auth_headers, json=payload)
    assert response.status_code == 403, response.text

def test_create_teacher_by_student_fails(client: TestClient, student_auth_headers: dict):
    unique_email = f"newteacher_s_{uuid4().hex[:6]}@example.com"
    payload = {
        "email": unique_email, "password": "password123",
        "first_name": "NewS", "last_name": "TeacherS"
    }
    response = client.post(f"{API_V1_STR}/teacher/create", headers=student_auth_headers, json=payload)
    assert response.status_code == 403, response.text

def test_create_teacher_duplicate_email(client: TestClient, db: Session, admin_auth_headers: dict):
    # First, create a teacher
    email1 = f"teacher_dup_email_{uuid4().hex[:6]}@example.com"
    payload1 = {"email": email1, "password": "pw1", "first_name": "F1", "last_name": "L1"}
    response1 = client.post(f"{API_V1_STR}/teacher/create", headers=admin_auth_headers, json=payload1)
    assert response1.status_code == 201

    # Attempt to create another teacher with the same email
    payload2 = {"email": email1, "password": "pw2", "first_name": "F2", "last_name": "L2"}
    response2 = client.post(f"{API_V1_STR}/teacher/create", headers=admin_auth_headers, json=payload2)
    assert response2.status_code == 400, response2.text
    assert "Email already registered" in response2.json()["detail"]
