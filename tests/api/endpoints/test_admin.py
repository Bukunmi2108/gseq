import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # db fixture might be needed if checking DB state
from uuid import uuid4

from app.models.user import User # For type hinting and DB checks
from app.schemas.admin import AdminCreate # For payload structure reference
from app.utils.constant.globals import UserRole

# Fixtures from conftest: client, db, admin_auth_headers, teacher_auth_headers, student_auth_headers

API_V1_STR = "/api/v1" # Assuming this is the API prefix

def test_create_admin_by_admin_success(client: TestClient, db: Session, admin_auth_headers: dict):
    # The create_admin endpoint in admin.py uses current_user from get_current_admin_user
    # which itself checks for admin role. So, admin_auth_headers should work.
    unique_email = f"newadmin_{uuid4().hex[:6]}@example.com"
    payload = {
        "email": unique_email,
        "password": "newadminpassword",
        "first_name": "New",
        "last_name": "Admin",
        # Add other fields from AdminCreate schema if any (e.g. is_super_admin)
        # Current AdminCreate schema: email, password, first_name, last_name
    }
    response = client.post(f"{API_V1_STR}/admin/create_admin", headers=admin_auth_headers, json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == unique_email
    assert data["role"] == UserRole.ADMIN.value

    # Verify in DB
    admin_in_db = db.query(User).filter(User.email == unique_email, User.role == UserRole.ADMIN).first()
    assert admin_in_db is not None

def test_create_admin_by_teacher_fails(client: TestClient, teacher_auth_headers: dict):
    unique_email = f"newadmin_t_{uuid4().hex[:6]}@example.com"
    payload = {
        "email": unique_email, "password": "password123",
        "first_name": "AttemptT", "last_name": "AdminT"
    }
    response = client.post(f"{API_V1_STR}/admin/create_admin", headers=teacher_auth_headers, json=payload)
    # The get_current_admin_user dependency will raise a 403 if the role is not ADMIN
    assert response.status_code == 403, response.text
    assert "Only admins can perform this action" in response.json()["detail"] # Or similar message from get_current_admin_user

def test_create_admin_by_student_fails(client: TestClient, student_auth_headers: dict):
    unique_email = f"newadmin_s_{uuid4().hex[:6]}@example.com"
    payload = {
        "email": unique_email, "password": "password123",
        "first_name": "AttemptS", "last_name": "AdminS"
    }
    response = client.post(f"{API_V1_STR}/admin/create_admin", headers=student_auth_headers, json=payload)
    assert response.status_code == 403, response.text
    assert "Only admins can perform this action" in response.json()["detail"] # Or similar message from get_current_admin_user

def test_create_admin_duplicate_email(client: TestClient, db: Session, admin_auth_headers: dict):
    email1 = f"admin_dup_email_{uuid4().hex[:6]}@example.com"
    payload1 = {"email": email1, "password": "pw1", "first_name": "F1", "last_name": "L1"}
    response1 = client.post(f"{API_V1_STR}/admin/create_admin", headers=admin_auth_headers, json=payload1)
    assert response1.status_code == 201

    payload2 = {"email": email1, "password": "pw2", "first_name": "F2", "last_name": "L2"}
    response2 = client.post(f"{API_V1_STR}/admin/create_admin", headers=admin_auth_headers, json=payload2)
    assert response2.status_code == 400, response2.text # From the User.email unique constraint
    assert "Email already registered" in response2.json()["detail"] # Endpoint specific check
