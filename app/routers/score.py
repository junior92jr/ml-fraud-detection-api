from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.model_loader import get_model, get_threshold
from app.database import get_session
from app.models import Prediction, Transaction
from app.schemas import ScoreRequest, ScoreResponse

router = APIRouter()


@router.post("", response_model=ScoreResponse)
def score_transaction(
    request: Request,
    payload: ScoreRequest,
    db: Session = Depends(get_session),
):
    tx = (
        db.query(Transaction)
        .filter(Transaction.transaction_id == payload.transaction_id)
        .one_or_none()
    )

    if tx is None:
        tx = Transaction(**payload.model_dump())
        db.add(tx)
        db.commit()

    model = get_model()
    threshold = get_threshold()

    data = payload.model_dump()
    data.pop("transaction_id", None)

    X = pd.DataFrame([data])

    if hasattr(model, "predict_proba"):
        fraud_probability = float(model.predict_proba(X)[0, 1])
    else:
        fraud_probability = float(model.predict(X)[0])

    decision = int(fraud_probability >= threshold)

    prediction = Prediction(
        transaction_id=payload.transaction_id,
        fraud_probability=fraud_probability,
        decision=decision,
        model_version=getattr(model, "version", "unknown"),
        scored_at=datetime.now(timezone.utc),
    )

    db.add(prediction)
    db.commit()

    return ScoreResponse(
        transaction_id=payload.transaction_id,
        fraud_probability=fraud_probability,
        decision=decision,
        threshold=threshold,
        model_version=getattr(model, "version", "unknown"),
        scored_at=prediction.scored_at.isoformat(),
    )
