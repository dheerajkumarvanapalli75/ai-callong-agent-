import logging
from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class TenantScopedRepository(Generic[T]):
    """
    Mandatory base repository enforcing strict multi-tenancy.
    All read, write, count, and aggregate operations are strictly scoped
    by the instantiated business_id. Unscoped queries are completely prohibited.
    """

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, business_id: str, model_cls: Optional[Type[T]] = None):
        if not business_id or not isinstance(business_id, str) or not business_id.strip():
            raise ValueError("TenantScopedRepository requires a valid, non-empty business_id")

        self.db = db
        self.collection_name = collection_name
        self.collection = db[collection_name]
        self.business_id = business_id.strip()
        self.model_cls = model_cls

    def _scope_filter(self, filter_query: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Injects business_id into every query filter."""
        scoped = dict(filter_query or {})
        scoped["business_id"] = self.business_id
        return scoped

    def _prepare_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Prepares a document for insertion, strictly enforcing business_id and timestamps."""
        doc_copy = dict(doc)
        doc_copy["business_id"] = self.business_id
        now = datetime.now(timezone.utc)
        if "created_at" not in doc_copy:
            doc_copy["created_at"] = now
        if "updated_at" not in doc_copy:
            doc_copy["updated_at"] = now
        return doc_copy

    async def find_one(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document scoped to this tenant."""
        scoped = self._scope_filter(filter_query)
        result = await self.collection.find_one(scoped)
        if result and "_id" in result:
            result["id"] = str(result["_id"])
        return result

    async def find_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Find a document by ID scoped to this tenant."""
        try:
            oid = ObjectId(doc_id) if ObjectId.is_valid(doc_id) else doc_id
        except Exception:
            oid = doc_id
        return await self.find_one({"_id": oid})

    async def find(
        self,
        filter_query: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Find multiple documents scoped to this tenant."""
        scoped = self._scope_filter(filter_query)
        cursor = self.collection.find(scoped)
        if sort:
            cursor = cursor.sort(sort)
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit > 0:
            cursor = cursor.limit(limit)

        results = []
        async for doc in cursor:
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
            results.append(doc)
        return results

    async def insert_one(self, doc: Dict[str, Any]) -> str:
        """Insert a document strictly scoped to this tenant."""
        prepared = self._prepare_document(doc)
        result = await self.collection.insert_one(prepared)
        return str(result.inserted_id)

    async def insert_many(self, docs: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents strictly scoped to this tenant."""
        if not docs:
            return []
        prepared = [self._prepare_document(d) for d in docs]
        result = await self.collection.insert_many(prepared)
        return [str(inserted_id) for inserted_id in result.inserted_ids]

    async def update_one(
        self,
        filter_query: Dict[str, Any],
        update_data: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """Update a document scoped to this tenant."""
        scoped = self._scope_filter(filter_query)

        # Ensure updated_at is refreshed
        update_op = dict(update_data)
        if "$set" in update_op:
            update_op["$set"]["updated_at"] = datetime.now(timezone.utc)
            # Never allow overwriting business_id to a different tenant
            update_op["$set"]["business_id"] = self.business_id
        else:
            update_op = {"$set": update_op}
            update_op["$set"]["updated_at"] = datetime.now(timezone.utc)
            update_op["$set"]["business_id"] = self.business_id

        result = await self.collection.update_one(scoped, update_op, upsert=upsert)
        return result.modified_count > 0 or (upsert and result.upserted_id is not None)

    async def update_by_id(self, doc_id: str, update_fields: Dict[str, Any]) -> bool:
        """Update a document by ID scoped to this tenant."""
        try:
            oid = ObjectId(doc_id) if ObjectId.is_valid(doc_id) else doc_id
        except Exception:
            oid = doc_id
        return await self.update_one({"_id": oid}, {"$set": update_fields})

    async def delete_one(self, filter_query: Dict[str, Any]) -> bool:
        """Delete a document scoped to this tenant."""
        scoped = self._scope_filter(filter_query)
        result = await self.collection.delete_one(scoped)
        return result.deleted_count > 0

    async def delete_by_id(self, doc_id: str) -> bool:
        """Delete a document by ID scoped to this tenant."""
        try:
            oid = ObjectId(doc_id) if ObjectId.is_valid(doc_id) else doc_id
        except Exception:
            oid = doc_id
        return await self.delete_one({"_id": oid})

    async def count(self, filter_query: Optional[Dict[str, Any]] = None) -> int:
        """Count documents scoped to this tenant."""
        scoped = self._scope_filter(filter_query)
        return await self.collection.count_documents(scoped)

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run an aggregation pipeline scoped to this tenant."""
        # Prepend $match stage to enforce business_id isolation
        scoped_pipeline = [{"$match": {"business_id": self.business_id}}] + list(pipeline)
        cursor = self.collection.aggregate(scoped_pipeline)
        results = []
        async for doc in cursor:
            if "_id" in doc:
                doc["id"] = str(doc["_id"])
            results.append(doc)
        return results
