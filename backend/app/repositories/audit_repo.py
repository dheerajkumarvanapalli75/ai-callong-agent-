from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import TenantScopedRepository


class AuditRepository(TenantScopedRepository):
    """Repository for querying and creating tenant-scoped audit logs."""

    def __init__(self, db: AsyncIOMotorDatabase, business_id: str):
        super().__init__(db, "audit_logs", business_id)

    async def get_recent_logs(self, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        return await self.find(
            filter_query={},
            sort=[("timestamp", -1)],
            limit=limit,
            skip=skip
        )
