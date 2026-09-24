import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient
from scripts.init_indexes import create_all_indexes, INDEX_SPECIFICATIONS


@pytest_asyncio.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client["test_phone_agent_db"]
    yield db
    client.close()


@pytest.mark.asyncio
async def test_init_indexes_creates_all_collections(mock_db):
    await create_all_indexes(mock_db)
    assert len(INDEX_SPECIFICATIONS) == 29
