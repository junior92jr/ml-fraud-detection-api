from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PredictionResult:
    label: int
    proba: float


class Predictor:
    def __init__(self, model_path: str | Path):
        self.model_path = Path(model_path)
        self.model = None

    def load(self) -> None:
        # Load once at startup
        self.model = joblib.load(self.model_path)

    def predict_one(self, features: dict[str, Any]) -> PredictionResult:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load() once at startup.")

        # Use DataFrame to preserve feature names and column order
        X = pd.DataFrame([features])

        # Probability (preferred for fraud)
        if hasattr(self.model, "predict_proba"):
            proba = float(self.model.predict_proba(X)[0, 1])
        else:
            # fallback for models without predict_proba
            proba = float(self.model.predict(X)[0])

        label = int(proba >= 0.5)  # choose threshold properly later
        return PredictionResult(label=label, proba=proba)
