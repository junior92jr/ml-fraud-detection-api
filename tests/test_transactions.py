import io
from datetime import UTC, datetime

import pytest
from chainmock import mocker
from fastapi import UploadFile

from app.core.exceptions import (
    CreateOrScoreFailedError,
    InvalidUploadError,
    TransactionNotFoundError,
    UpdateOrRescoreFailedError,
)
from app.enums import MerchantCategory
from app.routers import transactions as transactions_router
from app.routers.transactions import (
    create_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
)
from app.schemas import ScoreRequest, ScoreResponse, TransactionUpdate


@pytest.mark.anyio
async def test_list_transactions(make_transaction):
    mocker(transactions_router.transaction_repo).mock(
        "list_transactions", force_async=True
    ).return_value([make_transaction("tx1"), make_transaction("tx2")])

    response = await list_transactions(limit=10, offset=0)

    assert len(response) == 2
    assert response[0].transaction_id == "tx1"
    assert response[1].transaction_id == "tx2"


@pytest.mark.anyio
async def test_get_transaction_found(make_transaction, make_prediction):
    mocker(transactions_router.transaction_repo).mock(
        "get_transaction_by_external_id", force_async=True
    ).return_value(make_transaction("tx123"))

    mocker(transactions_router.transaction_repo).mock(
        "list_prediction_rows_for_transaction", force_async=True
    ).return_value([make_prediction()])

    response = await get_transaction("tx123")
    assert response.transaction.transaction_id == "tx123"
    assert len(response.predictions) == 1


@pytest.mark.anyio
async def test_get_transaction_not_found():
    mocker(transactions_router.transaction_repo).mock(
        "get_transaction_by_external_id", force_async=True
    ).return_value(None)

    with pytest.raises(TransactionNotFoundError) as exc_info:
        await get_transaction("missing")

    exc = exc_info.value
    assert exc.detail == "Transaction not found: missing"


@pytest.mark.anyio
async def test_create_transaction_success():
    payload = ScoreRequest(
        transaction_id="tx_123",
        amount=100.0,
        transaction_hour=14,
        merchant_category=MerchantCategory.ELECTRONICS,
        foreign_transaction=False,
        location_mismatch=False,
        device_trust_score=80,
        velocity_last_24h=5,
        cardholder_age=30,
    )
    expected = ScoreResponse(
        transaction_id="tx_123",
        fraud_probability=0.7,
        decision=1,
        threshold=0.5,
        scored_at=datetime(2023, 1, 1, tzinfo=UTC),
    )
    mocker(transactions_router).mock(
        "create_or_score_transaction", force_async=True
    ).return_value(expected)

    response = await create_transaction(payload)

    assert response == expected


@pytest.mark.anyio
async def test_create_transaction_failure():
    payload = ScoreRequest(
        transaction_id="tx_456",
        amount=120.0,
        transaction_hour=9,
        merchant_category=MerchantCategory.GROCERY,
        foreign_transaction=False,
        location_mismatch=False,
        device_trust_score=90,
        velocity_last_24h=2,
        cardholder_age=40,
    )
    mocker(transactions_router).mock(
        "create_or_score_transaction", force_async=True
    ).side_effect(RuntimeError("boom"))

    with pytest.raises(CreateOrScoreFailedError) as exc_info:
        await create_transaction(payload)

    exc = exc_info.value
    assert exc.detail == "Create-and-score failed for transaction: tx_456"


@pytest.mark.anyio
async def test_update_transaction_success():
    payload = TransactionUpdate(
        amount=130.0,
        transaction_hour=11,
        merchant_category=MerchantCategory.TRAVEL,
        foreign_transaction=True,
        location_mismatch=False,
        device_trust_score=72,
        velocity_last_24h=4,
        cardholder_age=29,
    )
    expected = ScoreResponse(
        transaction_id="tx_123",
        fraud_probability=0.4,
        decision=0,
        threshold=0.5,
        scored_at=datetime(2023, 1, 1, tzinfo=UTC),
    )
    mocker(transactions_router).mock(
        "update_and_rescore_transaction", force_async=True
    ).return_value(expected)

    response = await update_transaction("tx_123", payload)

    assert response == expected


@pytest.mark.anyio
async def test_update_transaction_not_found():
    payload = TransactionUpdate(
        amount=130.0,
        transaction_hour=11,
        merchant_category=MerchantCategory.TRAVEL,
        foreign_transaction=True,
        location_mismatch=False,
        device_trust_score=72,
        velocity_last_24h=4,
        cardholder_age=29,
    )
    mocker(transactions_router).mock(
        "update_and_rescore_transaction", force_async=True
    ).side_effect(TransactionNotFoundError("tx_missing"))

    with pytest.raises(TransactionNotFoundError) as exc_info:
        await update_transaction("tx_missing", payload)

    exc = exc_info.value
    assert exc.detail == "Transaction not found: tx_missing"


@pytest.mark.anyio
async def test_update_transaction_failure():
    payload = TransactionUpdate(
        amount=130.0,
        transaction_hour=11,
        merchant_category=MerchantCategory.TRAVEL,
        foreign_transaction=True,
        location_mismatch=False,
        device_trust_score=72,
        velocity_last_24h=4,
        cardholder_age=29,
    )
    mocker(transactions_router).mock(
        "update_and_rescore_transaction", force_async=True
    ).side_effect(RuntimeError("boom"))

    with pytest.raises(UpdateOrRescoreFailedError) as exc_info:
        await update_transaction("tx_123", payload)

    exc = exc_info.value
    assert exc.detail == "Update-and-rescore failed for transaction: tx_123"


def test_import_transactions_endpoint_success(client):
    mocker(transactions_router).mock(
        "import_transactions_from_csv", force_async=True
    ).return_value(
        {
            "total_rows": 1,
            "imported": 1,
            "skipped_duplicates": 0,
            "skipped_invalid": 0,
            "skipped_scoring_errors": 0,
            "errors": [],
        }
    )
    csv_content = (
        "transaction_id,amount,transaction_hour,merchant_category,foreign_transaction,"
        "location_mismatch,device_trust_score,velocity_last_24h,cardholder_age\n"
        "tx_1,150.5,14,Electronics,0,0,85,3,35\n"
    )

    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_rows"] == 1
    assert data["imported"] == 1


def test_import_transactions_endpoint_rejects_non_csv(client):
    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.txt", "hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Only .csv files are supported"


@pytest.mark.anyio
async def test_import_transactions_endpoint_requires_filename():
    file = UploadFile(filename="", file=io.BytesIO(b"transaction_id,amount\n"))

    with pytest.raises(InvalidUploadError) as exc_info:
        await transactions_router.import_transactions(file)

    assert exc_info.value.detail == "Filename is required"


def test_import_transactions_endpoint_handles_unexpected_error(client):
    mocker(transactions_router).mock(
        "import_transactions_from_csv", force_async=True
    ).side_effect(RuntimeError("boom"))
    csv_content = (
        "transaction_id,amount,transaction_hour,merchant_category,foreign_transaction,"
        "location_mismatch,device_trust_score,velocity_last_24h,cardholder_age\n"
        "tx_1,150.5,14,Electronics,0,0,85,3,35\n"
    )

    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "CSV import failed for file: transactions.csv"
