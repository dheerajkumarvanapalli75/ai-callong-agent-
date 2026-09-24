import asyncio
import logging
from datetime import datetime, timezone
from typing import Callable, Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration_runner")


class MigrationRunner:
    """Versioned schema and data migration runner."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["schema_migrations"]

    async def get_applied_migrations(self) -> List[str]:
        cursor = self.collection.find({}, {"version": 1})
        applied = []
        async for doc in cursor:
            applied.append(doc["version"])
        return applied

    async def record_migration(self, version: str, description: str):
        await self.collection.insert_one({
            "version": version,
            "description": description,
            "applied_at": datetime.now(timezone.utc)
        })

    async def run_migrations(self, migrations: List[Dict]):
        applied = set(await self.get_applied_migrations())
        for m in migrations:
            v = m["version"]
            desc = m["description"]
            func: Callable = m["up"]
            if v not in applied:
                logger.info(f"Applying migration {v}: {desc}...")
                await func(self.db)
                await self.record_migration(v, desc)
                logger.info(f"Migration {v} successfully applied.")
            else:
                logger.info(f"Migration {v} already applied. Skipping.")


# Migration definitions
async def m001_initial_schema(db: AsyncIOMotorDatabase):
    """Ensure baseline collections exist."""
    collections = [
        "users", "businesses", "agents", "agent_versions", "knowledge_documents",
        "knowledge_chunks", "customers", "calls", "audit_logs"
    ]
    existing = await db.list_collection_names()
    for col in collections:
        if col not in existing:
            await db.create_collection(col)


MIGRATIONS = [
    {
        "version": "001_initial_schema",
        "description": "Initialize baseline collections for multi-tenant phone agent platform",
        "up": m001_initial_schema
    }
]


if __name__ == "__main__":
    async def main():
        db = await db_manager.connect()
        runner = MigrationRunner(db)
        await runner.run_migrations(MIGRATIONS)
        await db_manager.disconnect()

    asyncio.run(main())
