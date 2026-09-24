from typing import Any, Dict, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class BusinessRepository:
    """Repository for tenant / business entity management."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["businesses"]

    async def create_business(self, business_data: Dict[str, Any]) -> str:
        result = await self.collection.insert_one(business_data)
        return str(result.inserted_id)

    async def find_by_id(self, business_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(business_id) if ObjectId.is_valid(business_id) else business_id
        except Exception:
            oid = business_id
        doc = await self.collection.find_one({"_id": oid})
        if doc and "_id" in doc:
            doc["id"] = str(doc["_id"])
        return doc

    async def update_business(self, business_id: str, update_fields: Dict[str, Any]) -> bool:
        try:
            oid = ObjectId(business_id) if ObjectId.is_valid(business_id) else business_id
        except Exception:
            oid = business_id
        result = await self.collection.update_one({"_id": oid}, {"$set": update_fields})
        return result.modified_count > 0
