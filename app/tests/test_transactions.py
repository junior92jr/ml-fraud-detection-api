from unittest.mock import Mock, patch

from sqlalchemy.orm import Session

from app.routers.transactions import get_transaction, list_transactions


class MockTransaction:
    def __init__(self, transaction_id, amount=100.0):
        self.transaction_id = transaction_id
        self.amount = amount
        self.transaction_hour = 12
        self.merchant_category = "Electronics"
        self.foreign_transaction = False
        self.location_mismatch = False
        self.device_trust_score = 80
        self.velocity_last_24h = 5
        self.cardholder_age = 30
        self.created_at = "2023-01-01T00:00:00Z"


class MockPrediction:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id
        self.fraud_probability = 0.5
        self.decision = 0
        self.model_version = "v1"
        self.scored_at = "2023-01-01T00:00:00Z"


@patch("app.routers.transactions.get_session")
def test_list_transactions(mock_get_session):
    """Test listing transactions with default parameters."""
    mock_db = Mock(spec=Session)
    mock_get_session.return_value = mock_db

    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.all.return_value = [MockTransaction("tx1"), MockTransaction("tx2")]

    response = list_transactions(limit=10, offset=0, db=mock_db)

    assert len(response) == 2
    assert response[0].transaction_id == "tx1"
    assert response[1].transaction_id == "tx2"


@patch("app.routers.transactions.get_session")
def test_get_transaction_found(mock_get_session):
    """Test getting a transaction that exists."""
    mock_db = Mock(spec=Session)
    mock_get_session.return_value = mock_db

    mock_tx = MockTransaction("tx123")
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = mock_tx

    mock_predictions_query = Mock()
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        MockPrediction("tx123")
    ]

    response = get_transaction("tx123", db=mock_db)

    assert "transaction" in response
    assert "predictions" in response
    assert response["transaction"].transaction_id == "tx123"
    assert len(response["predictions"]) == 1


@patch("app.routers.transactions.get_session")
def test_get_transaction_not_found(mock_get_session):
    """Test getting a transaction that does not exist."""
    mock_db = Mock(spec=Session)
    mock_get_session.return_value = mock_db

    mock_db.query.return_value.filter.return_value.one_or_none.return_value = None

    response = get_transaction("nonexistent", db=mock_db)

    assert response == {"error": "Transaction not found"}
