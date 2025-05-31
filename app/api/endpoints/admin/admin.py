from fastapi import APIRouter, status, Depends, UploadFile, File, HTTPException
from app.core.dependencies import get_db
from app.models.user import User
from app.models.admin import Admin
from app.schemas.admin import AdminSchema, AdminCreate
from app.api.endpoints.user.functions import get_current_admin_user
from app.api.endpoints.user.functions import get_password_hash
from sqlalchemy.orm import Session 
from typing import List
from app.utils.constant.globals import UserRole


router = APIRouter(prefix="/admin", tags=['Admins'])

@router.post("/create", response_model=AdminSchema, status_code=status.HTTP_201_CREATED)
def create_admin(admin: AdminCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    # Only an existing admin can create another admin
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only existing admins can create new admin accounts"
        )

    db_user = db.query(User).filter(User.email == admin.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(admin.password)
    db_admin = Admin(
        email=admin.email,
        password=hashed_password,
        first_name=admin.first_name,
        last_name=admin.last_name,
        role=UserRole.ADMIN # Explicitly set role to ADMIN
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.get("/admins/{admin_id}", response_model=AdminSchema)
def read_admin(admin_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return db_admin

@router.get("/admins/", response_model=List[AdminSchema])
def read_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    admins = db.query(Admin).offset(skip).limit(limit).all()
    return admins

@router.put("/admins/{admin_id}", response_model=AdminSchema)
def update_admin(
    admin_id: int,
    admin: AdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # An admin can update their own profile or another admin's profile if they are an admin
    if current_user.id != admin_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to update this admin")

    db_admin.email = admin.email
    db_admin.first_name = admin.first_name
    db_admin.last_name = admin.last_name
    if admin.password:
        db_admin.password = get_password_hash(admin.password)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@router.delete("/admins/{admin_id}", response_model=AdminSchema)
def delete_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # An admin can delete another admin, but typically not themselves if they are the last admin
    if current_user.id == admin_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own admin account")

    db.delete(db_admin)
    db.commit()
    return db_admin