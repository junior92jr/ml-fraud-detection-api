from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.logfire import get_logger
from app.database import get_session
from app.models import Prediction, Transaction
from app.schemas import TransactionRead

router = APIRouter()
DBSession = Annotated[Session, Depends(get_session)]
logger = get_logger(__name__)


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    db: DBSession,
    limit: int = Query(50, le=100),
    offset: int = 0,
):
    logger.debug("Listing transactions with limit=%s offset=%s", limit, offset)
    return (
        db.query(Transaction)
        .order_by(Transaction.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{transaction_id}")
def get_transaction(
    transaction_id: str,
    db: DBSession,
):
    logger.debug("Fetching transaction %s", transaction_id)
    tx = (
        db.query(Transaction)
        .filter(Transaction.transaction_id == transaction_id)
        .one_or_none()
    )

    if tx is None:
        logger.info("Transaction not found: %s", transaction_id)
        return {"error": "Transaction not found"}

    predictions = (
        db.query(Prediction)
        .filter(Prediction.transaction_id == transaction_id)
        .order_by(Prediction.scored_at.desc())
        .all()
    )

    return {
        "transaction": tx,
        "predictions": predictions,
    }
