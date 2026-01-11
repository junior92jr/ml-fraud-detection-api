import datetime
from unittest.mock import Mock, patch

import numpy as np
from sqlalchemy.orm import Session

from app.routers.score import score_transaction
from app.schemas import ScoreRequest


class MockModel:
    def predict_proba(self, df):
        return np.array([[0.3, 0.7]])


class MockTransaction:
    def __init__(self, transaction_id):
        self.transaction_id = transaction_id


@patch("app.routers.score.get_model")
@patch("app.routers.score.get_threshold")
@patch("app.routers.score.datetime")
def test_score_transaction_existing_transaction(
    mock_datetime, mock_get_threshold, mock_get_model
):
    """Test scoring when transaction already exists in DB."""
    payload = ScoreRequest(
        transaction_id="test_tx_123",
        amount=100.0,
        transaction_hour=14,
        merchant_category="Electronics",
        foreign_transaction=False,
        location_mismatch=False,
        device_trust_score=80,
        velocity_last_24h=5,
        cardholder_age=30,
    )

    mock_db = Mock(spec=Session)
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = (
        MockTransaction("test_tx_123")
    )

    mock_get_model.return_value = MockModel()
    mock_get_threshold.return_value = 0.5
    mock_datetime.now.return_value = datetime.datetime(
        2023, 1, 1, tzinfo=datetime.timezone.utc
    )

    mock_db.add.return_value = None
    mock_db.commit.return_value = None

    response = score_transaction(None, payload, mock_db)

    assert response.transaction_id == "test_tx_123"
    assert response.fraud_probability == 0.7
    assert response.decision == 1
    assert response.threshold == 0.5
    assert response.model_version == "unknown"


@patch("app.routers.score.get_model")
@patch("app.routers.score.get_threshold")
@patch("app.routers.score.datetime")
@patch("app.routers.score.Transaction")
@patch("app.routers.score.Prediction")
def test_score_transaction_new_transaction(
    mock_prediction_class,
    mock_transaction_class,
    mock_datetime,
    mock_get_threshold,
    mock_get_model,
):
    """Test scoring when transaction does not exist, creates new one."""
    payload = ScoreRequest(
        transaction_id="new_tx_456",
        amount=200.0,
        transaction_hour=22,
        merchant_category="Travel",
        foreign_transaction=True,
        location_mismatch=True,
        device_trust_score=20,
        velocity_last_24h=10,
        cardholder_age=25,
    )

    mock_db = Mock(spec=Session)
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = (
        None  # No existing transaction
    )

    mock_get_model.return_value = MockModel()
    mock_get_threshold.return_value = 0.6
    mock_datetime.now.return_value = datetime.datetime(
        2023, 1, 1, tzinfo=datetime.timezone.utc
    )

    mock_transaction_instance = MockTransaction("new_tx_456")
    mock_transaction_class.return_value = mock_transaction_instance

    mock_prediction_instance = Mock()
    mock_prediction_instance.scored_at = datetime.datetime(
        2023, 1, 1, tzinfo=datetime.timezone.utc
    )
    mock_prediction_class.return_value = mock_prediction_instance

    mock_db.add.return_value = None
    mock_db.commit.return_value = None

    response = score_transaction(None, payload, mock_db)

    assert response.transaction_id == "new_tx_456"
    assert response.fraud_probability == 0.7
    assert response.decision == 1  # 0.7 >= 0.6
    assert response.threshold == 0.6
    assert response.model_version == "unknown"


@patch("app.routers.score.get_model")
@patch("app.routers.score.get_threshold")
@patch("app.routers.score.datetime")
def test_score_transaction_model_without_predict_proba(
    mock_datetime, mock_get_threshold, mock_get_model
):
    """Test scoring with a model that only has predict method."""
    payload = ScoreRequest(
        transaction_id="tx_789",
        amount=50.0,
        transaction_hour=10,
        merchant_category="Grocery",
        foreign_transaction=False,
        location_mismatch=False,
        device_trust_score=90,
        velocity_last_24h=2,
        cardholder_age=40,
    )

    class MockModelPredict:
        def predict(self, df):
            return np.array([1])  # Fraud

    mock_db = Mock(spec=Session)
    mock_db.query.return_value.filter.return_value.one_or_none.return_value = (
        MockTransaction("tx_789")
    )

    mock_get_model.return_value = MockModelPredict()
    mock_get_threshold.return_value = 0.8
    mock_datetime.now.return_value = datetime.datetime(
        2023, 1, 1, tzinfo=datetime.timezone.utc
    )

    mock_db.add.return_value = None
    mock_db.commit.return_value = None

    response = score_transaction(None, payload, mock_db)

    assert response.transaction_id == "tx_789"
    assert response.fraud_probability == 1.0
    assert response.decision == 1
    assert response.threshold == 0.8
