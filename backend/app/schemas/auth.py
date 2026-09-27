from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    college_name: Optional[str] = None
    semester: Optional[str] = None
    branch: Optional[str] = None
    monthly_budget_target: Optional[str] = "10000"

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str

class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    college_name: Optional[str] = None
    semester: Optional[str] = None
    branch: Optional[str] = None
    monthly_budget_target: Optional[str] = "10000"
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    college_name: Optional[str] = None
    semester: Optional[str] = None
    branch: Optional[str] = None
    monthly_budget_target: Optional[str] = None
    avatar_url: Optional[str] = None
