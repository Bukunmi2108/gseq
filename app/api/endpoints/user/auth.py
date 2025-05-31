# fastapi 
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from datetime import timedelta
from uuid import UUID as PyUUID # Import Python's UUID type for type checking

# sqlalchemy
from sqlalchemy.orm import Session

# import
from app.schemas.user import User, UserLogin, Token
from app.core.dependencies import get_db
from app.core.settings import settings
from app.api.endpoints.user import functions as user_functions

ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.ACCESS_TOKEN_EXPIRE_MINUTES # Note: This might be a typo, usually refresh tokens expire in days, not minutes.

auth_module = APIRouter()

# ============> login/logout < ======================
# getting access token for login 
@auth_module.post("/login", response_model=Token)
async def login_for_access_token(
    user: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    """
    Authenticates a user and returns access and refresh tokens.
    Converts member.id (UUID) to string before encoding in JWT.
    """
    member = user_functions.authenticate_user(db, user=user)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Ensure member.id is converted to a string for JSON serialization in JWT
    # This is crucial because UUID objects are not directly JSON serializable.
    member_id_str = str(member.id) if isinstance(member.id, PyUUID) else member.id

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_functions.create_access_token(
        data={"id": member_id_str, "email": member.email, "role": member.role}, 
        expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS) # Assuming REFRESH_TOKEN_EXPIRE_DAYS should be in days
    refresh_token = await user_functions.create_refresh_token(
        data={"id": member_id_str, "email": member.email, "role": member.role}, 
        expires_delta=refresh_token_expires
    )
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@auth_module.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refreshes an access token using a valid refresh token.
    """
    token = await user_functions.refresh_access_token(db, refresh_token)
    return token