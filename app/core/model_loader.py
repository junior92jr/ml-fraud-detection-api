import os
from pathlib import Path
from threading import Lock
from typing import Any

import joblib as _joblib  # type: ignore[import-untyped]
from joblib import numpy_pickle  # type: ignore[import-untyped]

from app.core.logfire import get_logger

_lock = Lock()
_bundle: dict[str, Any] | None = None
logger = get_logger(__name__)


class _JoblibCompat:
    """Compat layer for environments with a broken/namespace-only joblib import."""

    @staticmethod
    def load(path: Path) -> Any:
        return numpy_pickle.load(path)


joblib: Any = _joblib if hasattr(_joblib, "load") else _JoblibCompat()


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
            msg = "MODEL_PATH environment variable is not set"
            raise RuntimeError(msg) from e

        if not model_path.exists():
            msg = f"Model file not found at {model_path}. Set MODEL_PATH correctly."
            raise RuntimeError(msg)

        loaded = joblib.load(model_path)
        logger.info("Loaded model bundle from %s", model_path)

        if not isinstance(loaded, dict) or "model" not in loaded:
            msg = (
                f"Invalid model artifact at {model_path}. "
                "Expected dict with key 'model'. "
                f"Got {type(loaded)}"
            )
            raise RuntimeError(msg)

        _bundle = loaded
        return _bundle


def get_model():
    return get_model_bundle()["model"]


def get_threshold(default: float = 0.5) -> float:
    bundle = get_model_bundle()
    return float(bundle.get("threshold", default))
