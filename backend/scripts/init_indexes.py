import asyncio
import logging
# pyrefly: ignore [missing-import]
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.database import db_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_indexes")


INDEX_SPECIFICATIONS = [
    # Auth & Multi-Tenancy
    ("users", [([("email", 1)], {"unique": True}), ([("business_id", 1)], {})]),
    ("businesses", [([("owner_id", 1)], {})]),
    ("audit_logs", [([("business_id", 1), ("timestamp", -1)], {})]),

    # Agent Configurations & Versioning
    ("agents", [([("business_id", 1)], {})]),
    ("agent_versions", [([("business_id", 1), ("agent_id", 1), ("version", 1)], {"unique": True})]),
    ("agent_tasks", [([("business_id", 1), ("priority", 1)], {})]),
    ("agent_rules", [([("business_id", 1), ("priority", 1)], {})]),
    ("agent_examples", [([("business_id", 1)], {})]),
    ("agent_objections", [([("business_id", 1)], {})]),
    ("agent_permissions", [([("business_id", 1), ("agent_id", 1)], {})]),
    ("agent_intents", [([("business_id", 1), ("name", 1)], {})]),
    ("agent_lead_rules", [([("business_id", 1)], {})]),
    ("agent_handoff_rules", [([("business_id", 1)], {})]),
    ("agent_workflows", [([("business_id", 1), ("agent_id", 1)], {})]),
    ("languages", [([("business_id", 1), ("code", 1)], {})]),

    # Knowledge Base & Vector Retrieval
    ("knowledge_documents", [([("business_id", 1), ("category", 1), ("approved", 1)], {})]),
    ("knowledge_chunks", [
        ([("business_id", 1), ("category", 1), ("approved", 1)], {}),
        ([("document_id", 1)], {}),
        ([("business_id", 1), ("doc_version", 1)], {})
    ]),

    # Customer & Calls Memory
    ("customers", [
        ([("business_id", 1), ("phone", 1)], {"unique": True}),
        ([("business_id", 1), ("customer_id", 1)], {"unique": True})
    ]),
    ("calls", [([("business_id", 1), ("customer_id", 1), ("timestamp", -1)], {})]),
    ("conversation_messages", [([("business_id", 1), ("call_id", 1), ("timestamp", 1)], {})]),
    ("call_summaries", [([("business_id", 1), ("call_id", 1)], {})]),
    ("leads", [([("business_id", 1), ("status", 1)], {})]),
    ("follow_ups", [([("business_id", 1), ("status", 1), ("scheduled_at", 1)], {})]),
    ("registrations", [([("business_id", 1), ("customer_id", 1)], {})]),

    # Tool Execution Audit & Testing
    ("agent_actions", [([("business_id", 1), ("call_id", 1), ("timestamp", -1)], {})]),
    ("test_scenarios", [([("business_id", 1), ("category", 1)], {})]),
    ("test_runs", [([("business_id", 1), ("agent_version_id", 1), ("timestamp", -1)], {})]),
    ("integrations", [([("business_id", 1), ("provider", 1)], {})]),
    ("consent_records", [([("business_id", 1), ("customer_id", 1)], {})]),
]


async def create_all_indexes(db: AsyncIOMotorDatabase):
    """Creates all defined indexes across all 29 collections in the specification."""
    logger.info("Starting index verification and creation...")
    created_count = 0

    for collection_name, indexes in INDEX_SPECIFICATIONS:
        collection = db[collection_name]
        for keys, kwargs in indexes:
            try:
                name = await collection.create_index(keys, **kwargs)
                logger.info(f"Created index '{name}' on collection '{collection_name}' with keys {keys}")
                created_count += 1
            except Exception as e:
                logger.warning(f"Note on index {keys} for collection '{collection_name}': {e}")

    logger.info(f"Successfully processed {created_count} indexes across {len(INDEX_SPECIFICATIONS)} collections.")


ATLAS_VECTOR_SEARCH_INDEX_DEFINITION = {
    "name": "vector_index",
    "type": "vectorSearch",
    "definition": {
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": 1536,
                "similarity": "cosine"
            },
            {
                "type": "filter",
                "path": "business_id"
            },
            {
                "type": "filter",
                "path": "category"
            },
            {
                "type": "filter",
                "path": "approved"
            }
        ]
    }
}


if __name__ == "__main__":
    async def main():
        db = await db_manager.connect()
        await create_all_indexes(db)
        await db_manager.disconnect()

    asyncio.run(main())
