from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password
)
from app.models.user import TokenResponse, UserRegisterRequest, UserRole
from app.repositories.business_repo import BusinessRepository
from app.repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.user_repo = UserRepository(db)
        self.business_repo = BusinessRepository(db)

    async def register_tenant_and_owner(self, request: UserRegisterRequest) -> TokenResponse:
        """Atomically provisions a new business tenant and registers its primary owner."""
        # Check if email is already taken
        existing_user = await self.user_repo.find_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists."
            )

        now = datetime.now(timezone.utc)

        # 1. Create Business Tenant
        business_data = {
            "name": request.business_name.strip(),
            "created_at": now,
            "updated_at": now,
            "is_active": True,
            "settings": {}
        }
        business_id = await self.business_repo.create_business(business_data)

        # 2. Hash password with Argon2
        hashed_pw = hash_password(request.password)

        # 3. Create Owner User
        user_data = {
            "email": request.email.lower().strip(),
            "hashed_password": hashed_pw,
            "full_name": request.full_name.strip(),
            "role": UserRole.OWNER.value,
            "business_id": business_id,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        user_id = await self.user_repo.create_user(user_data)

        # Update business with owner_id reference
        await self.business_repo.update_business(business_id, {"owner_id": user_id})

        # 4. Generate JWT Access and Refresh Tokens
        access_token = create_access_token(
            subject=user_id,
            business_id=business_id,
            role=UserRole.OWNER.value,
            email=request.email.lower().strip()
        )
        refresh_token = create_refresh_token(
            subject=user_id,
            business_id=business_id
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user_id,
            email=request.email.lower().strip(),
            role=UserRole.OWNER.value,
            business_id=business_id,
            business_name=request.business_name.strip()
        )

    async def authenticate_user(self, email: str, password: str) -> TokenResponse:
        """Authenticates user credentials and issues tokens."""
        user = await self.user_repo.find_by_email(email)
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )

        if not verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )

        business = await self.business_repo.find_by_id(user["business_id"])
        business_name = business["name"] if business else "Unknown Business"

        access_token = create_access_token(
            subject=user["id"],
            business_id=user["business_id"],
            role=user["role"],
            email=user["email"]
        )
        refresh_token = create_refresh_token(
            subject=user["id"],
            business_id=user["business_id"]
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user["id"],
            email=user["email"],
            role=user["role"],
            business_id=user["business_id"],
            business_name=business_name
        )

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Validates refresh token and generates a new access token."""
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token."
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type."
            )

        user_id = payload.get("sub")
        if not user_id or not isinstance(user_id, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject."
            )
        user = await self.user_repo.find_by_id(user_id)
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive."
            )

        business = await self.business_repo.find_by_id(user["business_id"])
        business_name = business["name"] if business else ""

        new_access = create_access_token(
            subject=user["id"],
            business_id=user["business_id"],
            role=user["role"],
            email=user["email"]
        )
        new_refresh = create_refresh_token(
            subject=user["id"],
            business_id=user["business_id"]
        )

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",
            user_id=user["id"],
            email=user["email"],
            role=user["role"],
            business_id=user["business_id"],
            business_name=business_name
        )
