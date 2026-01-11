import pytest
from fastapi.testclient import TestClient

from app.config import settings_test
from app.database import create_db_and_tables, drop_db_and_tables
from app.main import create_application


@pytest.fixture(scope="function")
def client():
    """Test client using test settings."""
    app = create_application(settings_test)
    # Create test tables before each test
    create_db_and_tables(app.state.engine)
    with TestClient(app) as client:
        yield client
    # Drop tables after test
    drop_db_and_tables(app.state.engine)
