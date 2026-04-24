import io
from pathlib import Path

import numpy as np
import pytest
from chainmock import mocker

from app.core.exceptions import InvalidCSVError
from app.schemas import TransactionImportResponse
from app.services import csv_import
from app.services.csv_import import import_transactions_from_csv
from scripts import import_transactions as import_script
from scripts.import_transactions import import_transactions_from_path


class MockModel:
    def predict_proba(self, df):
        return np.array([[0.1, 0.9]])


@pytest.mark.anyio
async def test_import_transactions_service_creates_records():
    csv_content = (
        "transaction_id,amount,transaction_hour,merchant_category,foreign_transaction,"
        "location_mismatch,device_trust_score,velocity_last_24h,cardholder_age\n"
        "tx_1,150.5,14,Electronics,0,0,85,3,35\n"
    )
    mocker(csv_import).mock("get_model").return_value(MockModel())
    mocker(csv_import).mock("get_threshold").return_value(0.5)
    mocker(csv_import.transaction_repo).mock(
        "get_transaction_by_external_id", force_async=True
    ).return_value(None)
    mocker(csv_import.transaction_repo).mock(
        "create_transaction", force_async=True
    ).return_value(object()).awaited_once()
    mocker(csv_import.transaction_repo).mock(
        "create_prediction", force_async=True
    ).awaited_once()

    summary = await import_transactions_from_csv(csv_stream=io.StringIO(csv_content))
    assert summary.imported == 1
    assert summary.skipped_duplicates == 0
    assert summary.skipped_invalid == 0
    assert summary.skipped_scoring_errors == 0


@pytest.mark.anyio
async def test_import_script_reuses_app_service(tmp_path):
    csv_path = Path(tmp_path) / "seed.csv"
    csv_path.write_text(
        "transaction_id,amount,transaction_hour,merchant_category,foreign_transaction,"
        "location_mismatch,device_trust_score,velocity_last_24h,cardholder_age\n",
        encoding="utf-8",
    )

    mocker(import_script).mock("init_db", force_async=True).awaited_once()
    mocker(import_script).mock("close_db", force_async=True).awaited_once()
    mocker(import_script).mock(
        "import_transactions_from_csv", force_async=True
    ).return_value(
        TransactionImportResponse(
            total_rows=0,
            imported=0,
            skipped_duplicates=0,
            skipped_invalid=0,
            skipped_scoring_errors=0,
            errors=[],
        )
    )

    await import_transactions_from_path(csv_path)


@pytest.mark.anyio
async def test_import_transactions_missing_header_raises():
    with pytest.raises(InvalidCSVError) as exc_info:
        await import_transactions_from_csv(csv_stream=io.StringIO(""))

    assert exc_info.value.detail == "CSV header is missing"


@pytest.mark.anyio
async def test_import_transactions_missing_required_columns_raises():
    csv_content = "transaction_id,amount\n"

    with pytest.raises(InvalidCSVError) as exc_info:
        await import_transactions_from_csv(csv_stream=io.StringIO(csv_content))

    assert "CSV missing required columns:" in exc_info.value.detail


@pytest.mark.anyio
async def test_import_transactions_invalid_row_increments_skipped_invalid():
    csv_content = (
        "transaction_id,amount,transaction_hour,merchant_category,foreign_transaction,"
        "location_mismatch,device_trust_score,velocity_last_24h,cardholder_age\n"
        "tx_1,150.5,14,Electronics,not_bool,0,85,3,35\n"
    )
    mocker(csv_import).mock("get_model").return_value(MockModel())
    mocker(csv_import).mock("get_threshold").return_value(0.5)

    summary = await import_transactions_from_csv(csv_stream=io.StringIO(csv_content))

    assert summary.imported == 0
    assert summary.skipped_invalid == 1
    assert len(summary.errors) == 1
    assert summary.errors[0].transaction_id == "tx_1"


@pytest.mark.anyio
async def test_import_transactions_duplicate_in_file_is_skipped():
    csv_content = (
        "transaction_id,amount,transaction_hour,merchant_category,foreign_transaction,"
        "location_mismatch,device_trust_score,velocity_last_24h,cardholder_age\n"
        "tx_1,150.5,14,Electronics,0,0,85,3,35\n"
        "tx_1,160.5,14,Electronics,0,0,85,3,35\n"
    )
    mocker(csv_import).mock("get_model").return_value(MockModel())
    mocker(csv_import).mock("get_threshold").return_value(0.5)
    mocker(csv_import.transaction_repo).mock(
        "get_transaction_by_external_id", force_async=True
    ).return_value(None)
    mocker(csv_import.transaction_repo).mock(
        "create_transaction", force_async=True
    ).return_value(object()).awaited_once()
    mocker(csv_import.transaction_repo).mock(
        "create_prediction", force_async=True
    ).awaited_once()

    summary = await import_transactions_from_csv(csv_stream=io.StringIO(csv_content))

    assert summary.imported == 1
    assert summary.skipped_duplicates == 1


@pytest.mark.anyio
async def test_import_transactions_duplicate_in_db_is_skipped():
    csv_content = (
        "transaction_id,amount,transaction_hour,merchant_category,foreign_transaction,"
        "location_mismatch,device_trust_score,velocity_last_24h,cardholder_age\n"
        "tx_1,150.5,14,Electronics,0,0,85,3,35\n"
    )
    mocker(csv_import).mock("get_model").return_value(MockModel())
    mocker(csv_import).mock("get_threshold").return_value(0.5)
    mocker(csv_import.transaction_repo).mock(
        "get_transaction_by_external_id", force_async=True
    ).return_value(object())
    mocker(csv_import.transaction_repo).mock(
        "create_transaction", force_async=True
    ).not_awaited()
    mocker(csv_import.transaction_repo).mock(
        "create_prediction", force_async=True
    ).not_awaited()

    summary = await import_transactions_from_csv(csv_stream=io.StringIO(csv_content))

    assert summary.imported == 0
    assert summary.skipped_duplicates == 1


@pytest.mark.anyio
async def test_import_transactions_scoring_failure_is_tracked():
    csv_content = (
        "transaction_id,amount,transaction_hour,merchant_category,foreign_transaction,"
        "location_mismatch,device_trust_score,velocity_last_24h,cardholder_age\n"
        "tx_1,150.5,14,Electronics,0,0,85,3,35\n"
    )
    mocker(csv_import).mock("get_model").return_value(MockModel())
    mocker(csv_import).mock("get_threshold").return_value(0.5)
    mocker(csv_import.transaction_repo).mock(
        "get_transaction_by_external_id", force_async=True
    ).return_value(None)
    mocker(csv_import).mock("score_payload").side_effect(RuntimeError("model crash"))
    mocker(csv_import.transaction_repo).mock(
        "create_transaction", force_async=True
    ).not_awaited()

    summary = await import_transactions_from_csv(csv_stream=io.StringIO(csv_content))

    assert summary.imported == 0
    assert summary.skipped_scoring_errors == 1
    assert len(summary.errors) == 1
    assert summary.errors[0].error.startswith("Scoring failed:")
