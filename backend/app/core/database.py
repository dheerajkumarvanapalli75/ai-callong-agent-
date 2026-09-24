import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    is_mock: bool = False

    async def connect(self, uri: Optional[str] = None, db_name: Optional[str] = None) -> AsyncIOMotorDatabase:
        connection_uri = uri or settings.MONGODB_URI
        target_db = db_name or settings.MONGODB_DB_NAME

        try:
            logger.info(f"Connecting to MongoDB at {connection_uri}...")
            client = AsyncIOMotorClient(
                connection_uri,
                serverSelectionTimeoutMS=2000,
                maxPoolSize=50,
                minPoolSize=5
            )
            # Ping to verify active connection
            await client.admin.command('ping')
            self.client = client
            self.db = client[target_db]
            self.is_mock = False
            logger.info(f"Connected successfully to MongoDB database: {target_db}")
            return self.db
        except Exception as e:
            if settings.USE_IN_MEMORY_DB_IF_UNAVAILABLE:
                logger.warning(
                    f"Real MongoDB connection failed ({e}). "
                    "Falling back to mongomock-motor in-memory database for local execution."
                )
                try:
                    from mongomock_motor import AsyncMongoMockClient
                    mock_client = AsyncMongoMockClient()
                    self.client = mock_client  # type: ignore
                    self.db = mock_client[target_db]
                    self.is_mock = True
                    logger.info(f"Initialized in-memory AsyncMongoMockClient for database: {target_db}")
                    return self.db
                except ImportError:
                    logger.error("mongomock-motor is not installed. Real MongoDB is required.")
                    raise e
            else:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise e

    async def disconnect(self):
        if self.client:
            logger.info("Closing MongoDB connection pool.")
            self.client.close()
            self.client = None
            self.db = None

    def get_database(self) -> AsyncIOMotorDatabase:
        if self.db is None:
            raise RuntimeError("Database is not connected. Call connect() first.")
        return self.db


db_manager = DatabaseManager()


async def get_db() -> AsyncIOMotorDatabase:
    """Dependency helper to get active database instance."""
    return db_manager.get_database()
