import os
from pathlib import Path
from threading import Lock
from typing import Any

import joblib

_lock = Lock()
_bundle: dict[str, Any] | None = None


def get_model_bundle() -> dict[str, Any]:
    """
    Lazy-load model bundle from joblib once per process.
    Expected keys: 'model', 'threshold'
    """
    global _bundle
    if _bundle is not None:
        return _bundle

    with _lock:
        if _bundle is not None:
            return _bundle

        try:
            model_path = Path(os.environ["MODEL_PATH"])
        except KeyError as e:
            raise RuntimeError("MODEL_PATH environment variable is not set") from e

        if not model_path.exists():
            raise RuntimeError(
                f"Model file not found at {model_path}. Set MODEL_PATH correctly."
            )

        loaded = joblib.load(model_path)

        if not isinstance(loaded, dict) or "model" not in loaded:
            raise RuntimeError(
                f"Invalid model artifact at {model_path}. Expected dict with key 'model'. "
                f"Got {type(loaded)}"
            )

        _bundle = loaded
        return _bundle


def get_model():
    return get_model_bundle()["model"]


def get_threshold(default: float = 0.5) -> float:
    bundle = get_model_bundle()
    return float(bundle.get("threshold", default))
