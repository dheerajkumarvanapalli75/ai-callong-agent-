from fastapi import APIRouter, Depends, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.rate_limit import check_rate_limit
from app.models.user import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse
)
from app.services.audit_service import AuditService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"], dependencies=[Depends(check_rate_limit)])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request_data: UserRegisterRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Register a new business tenant and its initial owner user."""
    auth_service = AuthService(db)
    token_response = await auth_service.register_tenant_and_owner(request_data)

    # Log audit event
    audit_service = AuditService(db)
    client_ip = request.client.host if request.client else None
    await audit_service.log_event(
        business_id=token_response.business_id,
        action="TENANT_REGISTERED",
        entity_type="business",
        entity_id=token_response.business_id,
        changes={"business_name": request_data.business_name, "owner_email": request_data.email},
        user_id=token_response.user_id,
        user_email=token_response.email,
        ip_address=client_ip
    )

    return token_response


@router.post("/login", response_model=TokenResponse)
async def login(
    request_data: UserLoginRequest,
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Authenticate with email and password to receive JWT access and refresh tokens."""
    auth_service = AuthService(db)
    token_response = await auth_service.authenticate_user(
        email=request_data.email,
        password=request_data.password
    )

    # Log audit event
    audit_service = AuditService(db)
    client_ip = request.client.host if request.client else None
    await audit_service.log_event(
        business_id=token_response.business_id,
        action="USER_LOGIN",
        entity_type="user",
        entity_id=token_response.user_id,
        user_id=token_response.user_id,
        user_email=token_response.email,
        ip_address=client_ip
    )

    return token_response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request_data: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Exchange a valid refresh token for a newly minted access token."""
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(request_data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Retrieve profile and tenant details of the currently authenticated user."""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        business_id=current_user["business_id"],
        is_active=current_user.get("is_active", True)
    )
