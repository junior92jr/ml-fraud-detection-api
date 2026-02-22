import pytest
from fastapi.testclient import TestClient

from app.config import settings_test
from app.database import drop_db_and_tables
from app.main import create_application


@pytest.fixture
def client():
    app = create_application(settings_test)

    with TestClient(app) as client:
        yield client
        drop_db_and_tables(app.state.engine)
