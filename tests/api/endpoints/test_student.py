import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.models.user import User # For type hinting current_user if needed by fixtures
from app.models.student import Student # For DB checks
from app.schemas.student import StudentCreate # For payload structure reference
from app.utils.constant.globals import UserRole

# Fixtures from conftest: client, db, admin_auth_headers, teacher_auth_headers, student_auth_headers
# test_admin_user, test_teacher_user, test_student_user (to get their IDs if needed for payloads, though not directly for create)

API_V1_STR = "/api/v1" # Assuming this is the API prefix used in main.py

def test_create_student_by_admin_success(client: TestClient, db: Session, admin_auth_headers: dict):
    unique_email = f"newstudent_{uuid4().hex[:6]}@example.com"
    unique_admin_no = f"S{uuid4().hex[:6]}"
    payload = {
        "email": unique_email,
        "password": "password123",
        "first_name": "New",
        "last_name": "Student",
        "admin_no": unique_admin_no
    }
    response = client.post(f"{API_V1_STR}/student/create", headers=admin_auth_headers, json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == unique_email
    assert data["admin_no"] == unique_admin_no
    assert data["role"] == UserRole.STUDENT.value # Check if role is correctly set

    # Verify in DB
    student_in_db = db.query(Student).filter(Student.email == unique_email).first()
    assert student_in_db is not None
    assert student_in_db.admin_no == unique_admin_no
    assert student_in_db.role == UserRole.STUDENT

def test_create_student_by_teacher_fails(client: TestClient, teacher_auth_headers: dict):
    unique_email = f"newstudent_t_{uuid4().hex[:6]}@example.com"
    unique_admin_no = f"ST{uuid4().hex[:6]}"
    payload = {
        "email": unique_email, "password": "password123",
        "first_name": "NewT", "last_name": "StudentT", "admin_no": unique_admin_no
    }
    response = client.post(f"{API_V1_STR}/student/create", headers=teacher_auth_headers, json=payload)
    assert response.status_code == 403, response.text

def test_create_student_by_student_fails(client: TestClient, student_auth_headers: dict):
    unique_email = f"newstudent_s_{uuid4().hex[:6]}@example.com"
    unique_admin_no = f"SS{uuid4().hex[:6]}"
    payload = {
        "email": unique_email, "password": "password123",
        "first_name": "NewS", "last_name": "StudentS", "admin_no": unique_admin_no
    }
    response = client.post(f"{API_V1_STR}/student/create", headers=student_auth_headers, json=payload)
    assert response.status_code == 403, response.text

def test_create_student_duplicate_email(client: TestClient, db: Session, admin_auth_headers: dict):
    # First, create a student
    email1 = f"student_dup_email_{uuid4().hex[:6]}@example.com"
    admin_no1 = f"S_DE{uuid4().hex[:6]}"
    payload1 = {"email": email1, "password": "pw1", "first_name": "F1", "last_name": "L1", "admin_no": admin_no1}
    response1 = client.post(f"{API_V1_STR}/student/create", headers=admin_auth_headers, json=payload1)
    assert response1.status_code == 201

    # Attempt to create another student with the same email
    admin_no2 = f"S_DE_2{uuid4().hex[:6]}"
    payload2 = {"email": email1, "password": "pw2", "first_name": "F2", "last_name": "L2", "admin_no": admin_no2}
    response2 = client.post(f"{API_V1_STR}/student/create", headers=admin_auth_headers, json=payload2)
    assert response2.status_code == 400, response2.text
    assert "Email already registered" in response2.json()["detail"]

def test_create_student_duplicate_admin_no(client: TestClient, db: Session, admin_auth_headers: dict):
    # First, create a student
    email1 = f"student_dup_admin_email1_{uuid4().hex[:6]}@example.com"
    admin_no1 = f"S_DA{uuid4().hex[:6]}"
    payload1 = {"email": email1, "password": "pw1", "first_name": "F1", "last_name": "L1", "admin_no": admin_no1}
    response1 = client.post(f"{API_V1_STR}/student/create", headers=admin_auth_headers, json=payload1)
    assert response1.status_code == 201

    # Attempt to create another student with the same admin_no
    email2 = f"student_dup_admin_email2_{uuid4().hex[:6]}@example.com"
    payload2 = {"email": email2, "password": "pw2", "first_name": "F2", "last_name": "L2", "admin_no": admin_no1}
    response2 = client.post(f"{API_V1_STR}/student/create", headers=admin_auth_headers, json=payload2)
    assert response2.status_code == 400, response2.text
    assert "Admin number already registered" in response2.json()["detail"]
