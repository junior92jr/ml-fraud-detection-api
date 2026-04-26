import csv
from typing import TextIO

from pydantic import ValidationError

from api.core.exceptions import InvalidCSVError
from api.core.logfire import get_logger
from api.core.model_loader import get_model, get_threshold
from api.enums import MerchantCategory
from api.repositories import transactions as transaction_repo
from api.schemas import (
    ScoreRequest,
    TransactionImportError,
    TransactionImportResponse,
)
from api.services.scoring import score_payload

logger = get_logger(__name__)

CSV_REQUIRED_COLUMNS = {
    "transaction_id",
    "amount",
    "transaction_hour",
    "merchant_category",
    "foreign_transaction",
    "location_mismatch",
    "device_trust_score",
    "velocity_last_24h",
    "cardholder_age",
}

TRUE_VALUES = {"1", "true", "t", "yes", "y"}
FALSE_VALUES = {"0", "false", "f", "no", "n"}
MERCHANT_CATEGORIES: dict[str, MerchantCategory] = {
    category.value: category for category in MerchantCategory
}


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    msg = f"Invalid boolean value: {value}"
    raise ValueError(msg)


def _build_score_request(row: dict[str, str]) -> ScoreRequest:
    merchant_category = MERCHANT_CATEGORIES[row["merchant_category"]]
    return ScoreRequest(
        transaction_id=row["transaction_id"],
        amount=float(row["amount"]),
        transaction_hour=int(row["transaction_hour"]),
        merchant_category=merchant_category,
        foreign_transaction=parse_bool(row["foreign_transaction"]),
        location_mismatch=parse_bool(row["location_mismatch"]),
        device_trust_score=int(row["device_trust_score"]),
        velocity_last_24h=int(row["velocity_last_24h"]),
        cardholder_age=int(row["cardholder_age"]),
    )


async def import_transactions_from_csv(
    *,
    csv_stream: TextIO,
    max_error_details: int = 50,
) -> TransactionImportResponse:
    reader = csv.DictReader(csv_stream)
    if reader.fieldnames is None:
        msg = "CSV header is missing"
        raise InvalidCSVError(msg)

    missing_columns = CSV_REQUIRED_COLUMNS - set(reader.fieldnames)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        msg = f"CSV missing required columns: {missing}"
        raise InvalidCSVError(msg)

    errors: list[TransactionImportError] = []
    total_rows = 0
    imported = 0
    skipped_duplicates = 0
    skipped_invalid = 0
    skipped_scoring_errors = 0
    seen_transaction_ids: set[str] = set()

    model = get_model()
    threshold = get_threshold()

    for line_number, row in enumerate(reader, start=2):
        total_rows += 1
        tx_id = row.get("transaction_id")

        try:
            payload = _build_score_request(row)
        except (KeyError, TypeError, ValidationError, ValueError) as exc:
            skipped_invalid += 1
            if len(errors) < max_error_details:
                errors.append(
                    TransactionImportError(
                        line=line_number,
                        transaction_id=tx_id,
                        error=f"Invalid row: {exc}",
                    )
                )
            continue

        if payload.transaction_id in seen_transaction_ids:
            skipped_duplicates += 1
            continue

        existing = await transaction_repo.get_transaction_by_external_id(
            payload.transaction_id
        )
        if existing is not None:
            skipped_duplicates += 1
            seen_transaction_ids.add(payload.transaction_id)
            continue

        try:
            fraud_probability, decision, _ = score_payload(
                payload, model=model, threshold=threshold
            )
        except Exception as exc:  # noqa: BLE001
            skipped_scoring_errors += 1
            if len(errors) < max_error_details:
                errors.append(
                    TransactionImportError(
                        line=line_number,
                        transaction_id=payload.transaction_id,
                        error=f"Scoring failed: {exc}",
                    )
                )
            continue

        transaction = await transaction_repo.create_transaction(payload.model_dump())
        await transaction_repo.create_prediction(
            transaction=transaction,
            fraud_probability=fraud_probability,
            decision=decision,
        )
        seen_transaction_ids.add(payload.transaction_id)
        imported += 1

    summary = TransactionImportResponse(
        total_rows=total_rows,
        imported=imported,
        skipped_duplicates=skipped_duplicates,
        skipped_invalid=skipped_invalid,
        skipped_scoring_errors=skipped_scoring_errors,
        errors=errors,
    )
    logger.info(
        "CSV import complete: total=%s imported=%s duplicates=%s invalid=%s scoring_errors=%s",
        summary.total_rows,
        summary.imported,
        summary.skipped_duplicates,
        summary.skipped_invalid,
        summary.skipped_scoring_errors,
    )
    return summary
