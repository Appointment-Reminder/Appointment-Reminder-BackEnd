import os
import pytest
from pyasn1.debug import scope

from app.Database.client import client

@pytest.mark.asyncio(scope="session")
async def test_db_connection():
    # Force tests to use the test DB
    db = client[os.environ["MONGO_DB"]]

    # Check server is alive
    server_info = await client.server_info()
    assert "version" in server_info, "MongoDB server is not responding"

    # Check if DB actually exists by listing all DBs and confirming our name is there
    dbs = await client.list_database_names()
    assert os.environ["MONGO_DB"] in dbs, f"Database {os.environ['MONGO_DB']} does not exist yet"

    # Check required collections exist
    collections = await db.list_collection_names()
    required_collections = ["photographers", "appointments", "reminders"]
    for col in required_collections:
        assert col in collections, f"Collection '{col}' does not exist in the database"


@pytest.mark.asyncio(scope="session")
async def test_photographers_seeded():
    db = client[os.environ["MONGO_DB"]]
    cursor = db["photographers"].find({})

    # Proper async iteration
    photographers = []
    async for doc in db["photographers"].find({}):
        photographers.append(doc)

    assert len(photographers) == 2
    names = [p["name"] for p in photographers]
    assert "Alice" in names
    assert "Bob" in names
