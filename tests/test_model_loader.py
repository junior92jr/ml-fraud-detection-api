from pathlib import Path

import pytest
from chainmock import mocker

from app.core import model_loader


@pytest.fixture(autouse=True)
def _reset_model_bundle():
    model_loader._bundle = None
    yield
    model_loader._bundle = None


def test_get_model_bundle_raises_when_model_path_missing(monkeypatch):
    monkeypatch.delenv("MODEL_PATH", raising=False)

    with pytest.raises(RuntimeError) as exc_info:
        model_loader.get_model_bundle()

    assert str(exc_info.value) == "MODEL_PATH environment variable is not set"


def test_get_model_bundle_raises_when_model_file_missing(monkeypatch, tmp_path):
    missing_model_path = Path(tmp_path) / "does-not-exist-model.joblib"
    monkeypatch.setenv("MODEL_PATH", str(missing_model_path))

    with pytest.raises(RuntimeError) as exc_info:
        model_loader.get_model_bundle()

    assert "Model file not found at" in str(exc_info.value)


def test_get_model_bundle_raises_on_invalid_artifact(monkeypatch, tmp_path):
    model_path = Path(tmp_path) / "model.joblib"
    model_path.write_text("stub", encoding="utf-8")
    monkeypatch.setenv("MODEL_PATH", str(model_path))
    mocker(model_loader.joblib).mock("load").return_value(["invalid"])

    with pytest.raises(RuntimeError) as exc_info:
        model_loader.get_model_bundle()

    assert "Invalid model artifact" in str(exc_info.value)


def test_get_model_and_threshold(monkeypatch, tmp_path):
    model_path = Path(tmp_path) / "model.joblib"
    model_path.write_text("stub", encoding="utf-8")
    monkeypatch.setenv("MODEL_PATH", str(model_path))
    model = object()
    mocker(model_loader.joblib).mock("load").return_value({"model": model})

    assert model_loader.get_model() is model
    assert model_loader.get_threshold(default=0.7) == 0.7
