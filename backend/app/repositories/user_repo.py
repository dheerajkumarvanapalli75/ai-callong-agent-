from typing import Any, Dict, List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.repositories.base import TenantScopedRepository


class UserRepository:
    """Repository for user entity operations."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["users"]

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Global authentication lookup by unique email."""
        doc = await self.collection.find_one({"email": email.lower().strip()})
        if doc and "_id" in doc:
            doc["id"] = str(doc["_id"])
        return doc

    async def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
        except Exception:
            oid = user_id
        doc = await self.collection.find_one({"_id": oid})
        if doc and "_id" in doc:
            doc["id"] = str(doc["_id"])
        return doc

    async def create_user(self, user_data: Dict[str, Any]) -> str:
        data = dict(user_data)
        data["email"] = data["email"].lower().strip()
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    async def get_tenant_scoped_repo(self, business_id: str) -> TenantScopedRepository:
        """Returns a tenant-scoped user repository for team management."""
        return TenantScopedRepository(self.db, "users", business_id)
