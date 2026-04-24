from typing import Any

import pandas as pd  # type: ignore[import-untyped]

from app.schemas import ScoreRequest


def score_request(
    payload: ScoreRequest,
    *,
    model: Any,
    threshold: float,
) -> tuple[float, int]:
    features = payload.model_dump()
    features.pop("transaction_id", None)
    features_df = pd.DataFrame([features])

    if hasattr(model, "predict_proba"):
        fraud_probability = float(model.predict_proba(features_df)[0, 1])
    else:
        fraud_probability = float(model.predict(features_df)[0])

    decision = int(fraud_probability >= threshold)
    return fraud_probability, decision
