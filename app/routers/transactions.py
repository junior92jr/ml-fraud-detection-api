from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Prediction, Transaction
from app.schemas import TransactionRead

router = APIRouter()


@router.get("", response_model=List[TransactionRead])
def list_transactions(
    limit: int = Query(50, le=100),
    offset: int = 0,
    db: Session = Depends(get_session),
):
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
    db: Session = Depends(get_session),
):
    tx = (
        db.query(Transaction)
        .filter(Transaction.transaction_id == transaction_id)
        .one_or_none()
    )

    if tx is None:
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
