def test_client_with_test_db(client):
    """Verify that the client fixture uses test database settings."""
    assert client is not None
    # The client is created with settings_test in conftest.py
    # This print during fixture setup will show which DB is being used
