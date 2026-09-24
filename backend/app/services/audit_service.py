from datetime import datetime, timezone
from typing import Any, Dict, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.audit_repo import AuditRepository


class AuditService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def log_event(
        self,
        business_id: str,
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> str:
        """Records an audit log entry strictly scoped by tenant."""
        repo = AuditRepository(self.db, business_id=business_id)
        doc = {
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "changes": changes or {},
            "user_id": user_id,
            "user_email": user_email,
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc)
        }
        return await repo.insert_one(doc)
