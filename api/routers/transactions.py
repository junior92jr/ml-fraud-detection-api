import io
from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile

from app.core.exceptions import (
    AppError,
    CreateOrScoreFailedError,
    CSVImportFailedError,
    InvalidUploadError,
    TransactionNotFoundError,
    UpdateOrRescoreFailedError,
)
from app.core.logfire import get_logger
from app.repositories import transactions as transaction_repo
from app.schemas import (
    PredictionRead,
    ScoreRequest,
    ScoreResponse,
    TransactionDetailResponse,
    TransactionsCountResponse,
    TransactionImportResponse,
    TransactionRead,
    TransactionUpdate,
)
from app.services.csv_import import import_transactions_from_csv
from app.services.scoring import (
    create_or_score_transaction,
    update_and_rescore_transaction,
)

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=list[TransactionRead])
async def list_transactions(
    limit: int = Query(50, le=100),
    offset: int = 0,
):
    logger.debug("Listing transactions with limit=%s offset=%s", limit, offset)
    return await transaction_repo.list_transactions(limit=limit, offset=offset)


@router.get("/count", response_model=TransactionsCountResponse)
async def count_transactions():
    total = await transaction_repo.count_transactions()
    return TransactionsCountResponse(total=total)


@router.get("/scores", response_model=list[PredictionRead])
async def list_scores(
    limit: int = Query(50, le=100),
    offset: int = 0,
):
    logger.debug("Listing scores with limit=%s offset=%s", limit, offset)
    predictions = await transaction_repo.list_scores(limit=limit, offset=offset)
    return [PredictionRead(**prediction) for prediction in predictions]


@router.get("/scores/count", response_model=TransactionsCountResponse)
async def count_scores():
    total = await transaction_repo.count_scores()
    return TransactionsCountResponse(total=total)


@router.get("/{transaction_id}", response_model=TransactionDetailResponse)
async def get_transaction(
    transaction_id: str,
):
    logger.debug("Fetching transaction %s", transaction_id)
    tx = await transaction_repo.get_transaction_by_external_id(transaction_id)

    if tx is None:
        logger.info("Transaction not found: %s", transaction_id)
        raise TransactionNotFoundError(transaction_id)

    predictions = await transaction_repo.list_prediction_rows_for_transaction(tx)
    transaction_read = TransactionRead.model_validate(tx, from_attributes=True)
    prediction_reads = [
        PredictionRead(
            id=prediction["id"],
            transaction_id=tx.transaction_id,
            fraud_probability=prediction["fraud_probability"],
            decision=prediction["decision"],
            scored_at=prediction["scored_at"],
        )
        for prediction in predictions
    ]

    return TransactionDetailResponse(
        transaction=transaction_read,
        predictions=prediction_reads,
    )


@router.post("", response_model=ScoreResponse)
async def create_transaction(
    payload: ScoreRequest,
):
    logger.debug("Creating and scoring transaction %s", payload.transaction_id)
    try:
        response = await create_or_score_transaction(payload)
    except Exception as exc:
        logger.exception(
            "Create-and-score failed for transaction %s", payload.transaction_id
        )
        raise CreateOrScoreFailedError(payload.transaction_id) from exc

    return response


@router.put("/{transaction_id}", response_model=ScoreResponse)
async def update_transaction(
    transaction_id: str,
    payload: TransactionUpdate,
):
    logger.debug("Updating and rescoring transaction %s", transaction_id)
    try:
        response = await update_and_rescore_transaction(transaction_id, payload)
    except TransactionNotFoundError:
        raise
    except Exception as exc:
        logger.exception("Update-and-rescore failed for transaction %s", transaction_id)
        raise UpdateOrRescoreFailedError(transaction_id) from exc

    return response


@router.post("/import", response_model=TransactionImportResponse)
async def import_transactions(
    file: Annotated[UploadFile, File(...)],
):
    if not file.filename:
        msg = "Filename is required"
        raise InvalidUploadError(msg)
    if not file.filename.lower().endswith(".csv"):
        msg = "Only .csv files are supported"
        raise InvalidUploadError(msg)

    text_stream = io.TextIOWrapper(file.file, encoding="utf-8-sig", newline="")
    try:
        return await import_transactions_from_csv(csv_stream=text_stream)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("CSV import failed for file %s", file.filename)
        raise CSVImportFailedError(file.filename) from exc
    finally:
        text_stream.detach()
