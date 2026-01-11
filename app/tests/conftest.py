import os

import pytest
from fastapi.testclient import TestClient

from app.database import create_db_and_tables, drop_db_and_tables
from app.main import create_application

# Override DATABASE_URI for tests
os.environ["DATABASE_URI"] = os.environ.get(
    "DATABASE_URI_TEST", os.environ["DATABASE_URI"]
)


@pytest.fixture(scope="module")
def client():
    """Fixture to provide a test client with database setup and teardown."""
    app = create_application()
    with TestClient(app) as client:
        create_db_and_tables()
        yield client
        drop_db_and_tables()
