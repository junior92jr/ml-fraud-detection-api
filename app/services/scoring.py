from app.schemas import ScoreRequest


class FraudScorer:
    def __init__(self, model):
        self.model = model
        self.threshold = 0.6
        self.model_version = getattr(model, "version", "unknown")

    def score(self, payload: ScoreRequest) -> tuple[float, str]:
        """
        Returns (fraud_probability, decision)
        """

        features = payload.model_dump()

        fraud_probability = self.model.predict_proba(features)

        if fraud_probability >= self.threshold:
            decision = "reject"
        elif fraud_probability >= 0.4:
            decision = "review"
        else:
            decision = "approve"

        return fraud_probability, decision
