from datetime import UTC, datetime
from types import SimpleNamespace

import numpy as np
import pytest
from chainmock import mocker

from app.core.exceptions import TransactionNotFoundError
from app.enums import MerchantCategory
from app.services import scoring as scoring_service
from app.services.scoring import (
    create_or_score_transaction,
    score_payload,
    update_and_rescore_transaction,
)


class _DummyTxContext:
    async def __aenter__(self):
        return "conn"

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _PredictProbaModel:
    def predict_proba(self, df):
        return np.array([[0.2, 0.8]])


class _PredictModel:
    def predict(self, df):
        return [0.3]


def _score_request_payload():
    return {
        "transaction_id": "tx_1",
        "amount": 100.0,
        "transaction_hour": 12,
        "merchant_category": MerchantCategory.ELECTRONICS,
        "foreign_transaction": False,
        "location_mismatch": False,
        "device_trust_score": 80,
        "velocity_last_24h": 5,
        "cardholder_age": 30,
    }


def test_score_payload_uses_predict_proba():
    payload = scoring_service.ScoreRequest(**_score_request_payload())

    fraud_probability, decision, threshold = score_payload(
        payload, model=_PredictProbaModel(), threshold=0.5
    )

    assert fraud_probability == 0.8
    assert decision == 1
    assert threshold == 0.5


def test_score_payload_falls_back_to_predict():
    payload = scoring_service.ScoreRequest(**_score_request_payload())

    fraud_probability, decision, threshold = score_payload(
        payload, model=_PredictModel(), threshold=0.5
    )

    assert fraud_probability == 0.3
    assert decision == 0
    assert threshold == 0.5


@pytest.mark.anyio
async def test_create_or_score_transaction_success(make_transaction):
    payload = scoring_service.ScoreRequest(**_score_request_payload())
    prediction = SimpleNamespace(scored_at=datetime.now(UTC))
    mocker(scoring_service).mock("in_transaction").return_value(_DummyTxContext())
    mocker(scoring_service).mock("score_payload").return_value((0.77, 1, 0.5))
    mocker(scoring_service.transaction_repo).mock(
        "get_or_create_transaction", force_async=True
    ).return_value((make_transaction("tx_1"), True)).awaited_once()
    mocker(scoring_service.transaction_repo).mock(
        "create_prediction", force_async=True
    ).return_value(prediction).awaited_once()

    result = await create_or_score_transaction(payload)

    assert result.transaction_id == "tx_1"
    assert result.fraud_probability == 0.77
    assert result.decision == 1
    assert result.threshold == 0.5
    assert result.scored_at == prediction.scored_at


@pytest.mark.anyio
async def test_update_and_rescore_transaction_success_with_partial_payload(
    make_transaction,
):
    tx = make_transaction("tx_1")
    prediction = SimpleNamespace(scored_at=datetime.now(UTC))
    payload = scoring_service.TransactionUpdate(amount=250.0)
    mocker(scoring_service).mock("in_transaction").return_value(_DummyTxContext())
    mocker(scoring_service.transaction_repo).mock(
        "get_transaction_for_update", force_async=True
    ).return_value(tx).awaited_once()
    mocker(scoring_service).mock("score_payload").return_value((0.61, 1, 0.5))
    mocker(scoring_service.transaction_repo).mock(
        "update_transaction_fields", force_async=True
    ).awaited_once()
    mocker(scoring_service.transaction_repo).mock(
        "create_prediction", force_async=True
    ).return_value(prediction).awaited_once()

    result = await update_and_rescore_transaction("tx_1", payload)

    assert result.transaction_id == "tx_1"
    assert result.fraud_probability == 0.61
    assert result.decision == 1
    assert result.threshold == 0.5
    assert result.scored_at == prediction.scored_at


@pytest.mark.anyio
async def test_update_and_rescore_transaction_not_found_raises():
    payload = scoring_service.TransactionUpdate(amount=250.0)
    mocker(scoring_service).mock("in_transaction").return_value(_DummyTxContext())
    mocker(scoring_service.transaction_repo).mock(
        "get_transaction_for_update", force_async=True
    ).return_value(None)

    with pytest.raises(TransactionNotFoundError):
        await update_and_rescore_transaction("missing", payload)
