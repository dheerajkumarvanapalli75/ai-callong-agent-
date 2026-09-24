from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from app.api.deps import get_current_business_id, get_current_user, require_role
from app.core.database import get_db
from app.models.business import BusinessResponse
from app.models.user import UserRole
from app.repositories.business_repo import BusinessRepository
from app.services.audit_service import AuditService

router = APIRouter(prefix="/businesses", tags=["Business"])


class UpdateBusinessRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone_number: str | None = None
    website: str | None = None
    industry: str | None = None
    timezone: str = "Asia/Kolkata"


@router.get("/my-business", response_model=BusinessResponse)
async def get_my_business(
    business_id: str = Depends(get_current_business_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve details of the authenticated user's business tenant."""
    repo = BusinessRepository(db)
    business = await repo.find_by_id(business_id)
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")

    return BusinessResponse(
        id=business["id"],
        name=business["name"],
        owner_id=business.get("owner_id"),
        phone_number=business.get("phone_number"),
        website=business.get("website"),
        industry=business.get("industry"),
        timezone=business.get("timezone", "Asia/Kolkata"),
        is_active=business.get("is_active", True)
    )


@router.put("/my-business", response_model=BusinessResponse)
async def update_my_business(
    update_data: UpdateBusinessRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(require_role([UserRole.OWNER, UserRole.ADMIN])),
    business_id: str = Depends(get_current_business_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Update tenant business configuration (Owner and Admin only)."""
    repo = BusinessRepository(db)
    update_dict = update_data.model_dump(exclude_unset=True)
    success = await repo.update_business(business_id, update_dict)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update business")

    # Audit log
    audit_service = AuditService(db)
    client_ip = request.client.host if request.client else None
    await audit_service.log_event(
        business_id=business_id,
        action="BUSINESS_PROFILE_UPDATED",
        entity_type="business",
        entity_id=business_id,
        changes=update_dict,
        user_id=current_user.get("id"),
        user_email=current_user.get("email"),
        ip_address=client_ip
    )

    updated = await repo.find_by_id(business_id)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found."
        )
    return BusinessResponse(
        id=updated["id"],
        name=updated["name"],
        owner_id=updated.get("owner_id"),
        phone_number=updated.get("phone_number"),
        website=updated.get("website"),
        industry=updated.get("industry"),
        timezone=updated.get("timezone", "Asia/Kolkata"),
        is_active=updated.get("is_active", True)
    )
