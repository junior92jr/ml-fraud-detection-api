from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from api.config import SettingsTest
from api.enums import MerchantCategory
from api.main import create_application


@pytest.fixture
def client():
    settings_test = SettingsTest()
    app = create_application(settings_test)

    with TestClient(app) as client:
        yield client


@pytest.fixture
def make_transaction():
    def _make_transaction(transaction_id: str = "tx_1", **overrides):
        base = {
            "id": 1,
            "transaction_id": transaction_id,
            "amount": 100.0,
            "transaction_hour": 12,
            "merchant_category": MerchantCategory.ELECTRONICS,
            "foreign_transaction": False,
            "location_mismatch": False,
            "device_trust_score": 80,
            "velocity_last_24h": 5,
            "cardholder_age": 30,
        }
        base.update(overrides)
        return SimpleNamespace(**base)

    return _make_transaction


@pytest.fixture
def make_prediction():
    def _make_prediction(**overrides):
        base = {
            "id": 1,
            "fraud_probability": 0.75,
            "decision": 1,
            "scored_at": datetime.now(UTC),
        }
        base.update(overrides)
        return base

    return _make_prediction
