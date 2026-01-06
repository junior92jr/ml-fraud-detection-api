class DummyFraudModel:
    """
    Placeholder model object.
    In a real setup this could be a sklearn, xgboost, torch, etc. model.
    """

    version = "dummy-v1"

    def predict_proba(self, features: dict) -> float:
        """
        Very naive fraud probability logic.
        """
        score = 0.0

        if features["amount"] > 500:
            score += 0.3
        if features["foreign_transaction"]:
            score += 0.25
        if features["location_mismatch"]:
            score += 0.25
        if features["velocity_last_24h"] > 5:
            score += 0.15
        if features["device_trust_score"] < 40:
            score += 0.2

        return min(score, 1.0)


_model_instance = None


def get_model():
    """
    Simple singleton loader.
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = DummyFraudModel()
    return _model_instance
