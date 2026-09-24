import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient
from app.repositories.base import TenantScopedRepository


@pytest_asyncio.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client["test_phone_agent_db"]
    yield db
    client.close()


@pytest.mark.asyncio
async def test_tenant_repository_requires_business_id(mock_db):
    """Verifies that an empty or missing business_id is strictly rejected."""
    with pytest.raises(ValueError):
        TenantScopedRepository(mock_db, "customers", "")

    with pytest.raises(ValueError):
        TenantScopedRepository(mock_db, "customers", "   ")


@pytest.mark.asyncio
async def test_strict_tenant_isolation_reads_and_writes(mock_db):
    """
    Validates complete data isolation:
    - Tenant A inserts records.
    - Tenant B inserts records.
    - Tenant A can never read, count, or query Tenant B records.
    - Tenant B can never read, count, or query Tenant A records.
    """
    repo_a = TenantScopedRepository(mock_db, "customers", business_id="tenant_a_id")
    repo_b = TenantScopedRepository(mock_db, "customers", business_id="tenant_b_id")

    # Insert document under Tenant A
    doc_a_id = await repo_a.insert_one({
        "customer_id": "cust_101",
        "name": "Alice Corp",
        "phone": "+14155550001",
        "lead_status": "INTERESTED"
    })

    # Insert document under Tenant B
    doc_b_id = await repo_b.insert_one({
        "customer_id": "cust_201",
        "name": "Bob Enterprise",
        "phone": "+14155550002",
        "lead_status": "NOT_INTERESTED"
    })

    # 1. Tenant A cannot find Tenant B's doc by ID
    found_by_a = await repo_a.find_by_id(doc_b_id)
    assert found_by_a is None, "Tenant A must NOT be able to find Tenant B's document by ID"

    # 2. Tenant B cannot find Tenant A's doc by ID
    found_by_b = await repo_b.find_by_id(doc_a_id)
    assert found_by_b is None, "Tenant B must NOT be able to find Tenant A's document by ID"

    # 3. Tenant A query only returns Tenant A documents
    all_a_docs = await repo_a.find({})
    assert len(all_a_docs) == 1
    assert all_a_docs[0]["customer_id"] == "cust_101"
    assert all_a_docs[0]["business_id"] == "tenant_a_id"

    # 4. Tenant B count only reflects Tenant B documents
    count_b = await repo_b.count({})
    assert count_b == 1

    # 5. Cross-tenant update must have no effect
    updated = await repo_a.update_one({"customer_id": "cust_201"}, {"name": "Hacked Name"})
    assert updated is False, "Tenant A must NOT be able to modify Tenant B's record"

    b_doc = await repo_b.find_by_id(doc_b_id)
    assert b_doc is not None
    assert b_doc["name"] == "Bob Enterprise"

    # 6. Cross-tenant deletion must have no effect
    deleted = await repo_a.delete_by_id(doc_b_id)
    assert deleted is False, "Tenant A must NOT be able to delete Tenant B's record"

    b_doc_after = await repo_b.find_by_id(doc_b_id)
    assert b_doc_after is not None, "Tenant B's document must remain intact"


@pytest.mark.asyncio
async def test_tenant_forced_on_insert_and_aggregation(mock_db):
    """
    Verifies that if an insert payload attempts to pass a malicious business_id,
    the repository strictly overwrites it with the authorized tenant ID.
    Also verifies aggregation pipeline is automatically scoped.
    """
    repo = TenantScopedRepository(mock_db, "agent_rules", business_id="tenant_legit")

    # Attempt to inject another business_id
    doc_id = await repo.insert_one({
        "rule_name": "Test Rule",
        "business_id": "tenant_spoofed_victim"
    })

    inserted = await repo.find_by_id(doc_id)
    assert inserted is not None
    assert inserted["business_id"] == "tenant_legit", "business_id must be forced to authorized tenant"

    # Aggregation pipeline scoping
    agg_result = await repo.aggregate([
        {"$group": {"_id": "$business_id", "total": {"$sum": 1}}}
    ])
    assert len(agg_result) == 1
    assert agg_result[0]["_id"] == "tenant_legit"
    assert agg_result[0]["total"] == 1
