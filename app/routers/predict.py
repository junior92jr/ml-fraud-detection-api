from fastapi import APIRouter, HTTPException, Request

from app.schemas import FraudPredictionRequest, FraudPredictionResponse

router = APIRouter()


@router.post("/predict", response_model=FraudPredictionResponse)
def predict(request: Request, payload: FraudPredictionRequest):
    predictor = request.app.state.predictor

    data = payload.model_dump()
    transaction_id = data.pop("transaction_id", None)

    try:
        result = predictor.predict_one(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FraudPredictionResponse(
        transaction_id=transaction_id,
        is_fraud_pred=result.label,
        fraud_probability=result.proba,
    )
