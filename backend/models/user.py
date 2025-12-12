"""
User models and authentication
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    tier: str = "free"
    generation_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    username: str
    tier: str
    generation_count: int
    created_at: datetime


class UserInDB(User):
    password_hash: str


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Decode JWT token and return current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if email is None or user_id is None:
            raise credentials_exception
    
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    from services.supabase_client import supabase
    
    user_data = supabase.table("users").select("*").eq("email", email).single().execute()
    
    if not user_data.data:
        raise credentials_exception
    
    return User(**user_data.data)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Verify user is active
    """
    # Add any additional checks (e.g., account suspension)
    return current_user
