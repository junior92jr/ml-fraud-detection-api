from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.model_loader import get_model
from app.database import get_session
from app.models import Prediction, Transaction
from app.schemas import ScoreRequest, ScoreResponse
from app.services.scoring import FraudScorer

router = APIRouter()


@router.post("", response_model=ScoreResponse)
def score_transaction(
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
    scorer = FraudScorer(model=model)

    try:
        fraud_probability, decision = scorer.score(payload)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Model inference failed",
        ) from exc

    prediction = Prediction(
        transaction_id=payload.transaction_id,
        fraud_probability=fraud_probability,
        decision=decision,
        model_version=scorer.model_version,
        scored_at=datetime.now(timezone.utc),
    )

    db.add(prediction)
    db.commit()

    return ScoreResponse(
        transaction_id=payload.transaction_id,
        fraud_probability=fraud_probability,
        decision=decision,
        threshold=scorer.threshold,
        model_version=scorer.model_version,
        scored_at=prediction.scored_at.isoformat(),
    )
