from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.base import TenantScopedModel


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    AGENT_OPERATOR = "agent-operator"
    VIEWER = "viewer"


class User(TenantScopedModel):
    email: EmailStr = Field(..., description="Unique email address per user")
    hashed_password: str = Field(..., description="Argon2 hashed password")
    full_name: str = Field(..., description="User's full name")
    role: UserRole = Field(default=UserRole.OWNER, description="Role-based access level")
    is_active: bool = Field(default=True)


# API Schemas
class UserRegisterRequest(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str
    business_id: str
    business_name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    business_id: str
    is_active: bool
