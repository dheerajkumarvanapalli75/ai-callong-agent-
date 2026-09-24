import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password
)
from app.models.user import UserRegisterRequest
from app.services.auth_service import AuthService


@pytest_asyncio.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client["test_phone_agent_db"]
    yield db
    client.close()


def test_argon2_password_hashing():
    raw_password = "superSecretPassword123!"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert hashed.startswith("$argon2")
    assert verify_password(raw_password, hashed) is True
    assert verify_password("wrongPassword", hashed) is False


def test_jwt_token_lifecycle():
    access_token = create_access_token(
        subject="user_123",
        business_id="biz_456",
        role="owner",
        email="test@example.com"
    )
    decoded = decode_token(access_token)
    assert decoded["sub"] == "user_123"
    assert decoded["business_id"] == "biz_456"
    assert decoded["role"] == "owner"
    assert decoded["type"] == "access"

    refresh_token = create_refresh_token(subject="user_123", business_id="biz_456")
    decoded_refresh = decode_token(refresh_token)
    assert decoded_refresh["sub"] == "user_123"
    assert decoded_refresh["type"] == "refresh"


@pytest.mark.asyncio
async def test_register_and_authenticate_tenant(mock_db):
    auth_service = AuthService(mock_db)

    # 1. Register new tenant
    register_req = UserRegisterRequest(
        business_name="Amma Home Foods",
        email="owner@ammahomefoods.com",
        password="ValidPassword123!",
        full_name="Lakshmi Devi"
    )
    token_resp = await auth_service.register_tenant_and_owner(register_req)

    assert token_resp.access_token is not None
    assert token_resp.business_id is not None
    assert token_resp.role == "owner"
    assert token_resp.business_name == "Amma Home Foods"

    # 2. Authenticate user
    login_resp = await auth_service.authenticate_user(
        email="owner@ammahomefoods.com",
        password="ValidPassword123!"
    )
    assert login_resp.user_id == token_resp.user_id
    assert login_resp.business_id == token_resp.business_id

    # 3. Refresh token
    refreshed = await auth_service.refresh_tokens(login_resp.refresh_token)
    assert refreshed.access_token is not None
    assert refreshed.user_id == token_resp.user_id
