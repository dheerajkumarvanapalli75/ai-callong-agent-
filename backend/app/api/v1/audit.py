from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_current_business_id, require_role
from app.core.database import get_db
from app.models.user import UserRole
from app.repositories.audit_repo import AuditRepository

router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@router.get("/", response_model=List[Dict[str, Any]])
async def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    current_user: Dict[str, Any] = Depends(require_role([UserRole.OWNER, UserRole.ADMIN, UserRole.AGENT_OPERATOR])),
    business_id: str = Depends(get_current_business_id),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Retrieve audit logs strictly scoped to the caller's business."""
    repo = AuditRepository(db, business_id=business_id)
    logs = await repo.get_recent_logs(limit=limit, skip=skip)
    return logs
