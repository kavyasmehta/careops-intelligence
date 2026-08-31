"""Test configuration.

Uses a real MongoDB (not a mock) pointed at a disposable `careops_test`
database, so repository/service tests exercise actual Mongo query
behavior (indexes, filters, $text search) rather than a mock's
approximation of it. Defaults match the docker-compose local setup;
CI overrides MONGO_URI/MONGO_DB via job env vars.
"""
import os

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27018")
os.environ.setdefault("MONGO_DB", "careops_test")

import pymongo
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def clean_database():
    # Plain PyMongo (sync), deliberately not Motor: the app's Motor client is
    # bound to TestClient's internal event loop, which is torn down when the
    # `client` fixture's `with` block exits. Reusing it here would mean
    # touching a client tied to an already-closed loop. A separate sync
    # client sidesteps event-loop lifetime entirely for this cleanup step.
    yield
    settings = get_settings()
    sync_client = pymongo.MongoClient(settings.mongo_uri)
    db = sync_client[settings.mongo_db]
    for name in db.list_collection_names():
        db[name].delete_many({})
    sync_client.close()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def ops_manager_headers():
    return {"X-Demo-Role": "operations_manager", "X-Demo-User": "Test Operations Manager"}


@pytest.fixture
def intake_headers():
    return {"X-Demo-Role": "intake_specialist", "X-Demo-User": "Test Intake Specialist"}


@pytest.fixture
def auth_specialist_headers():
    return {"X-Demo-Role": "authorization_specialist", "X-Demo-User": "Test Authorization Specialist"}
