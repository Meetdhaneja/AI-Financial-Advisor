from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from app.core.config import get_settings


def ensure_model_artifacts() -> None:
    settings = get_settings()
    model_dir = Path(settings.model_dir)
    required = [
        model_dir / "expense_regressor.joblib",
        model_dir / "overspending_classifier.joblib",
        model_dir / "anomaly_detector.joblib",
        model_dir / "model_metadata.joblib",
    ]
    if all(path.exists() for path in required):
        return

    from ml.pipelines.train_models import train_and_save_models

    train_and_save_models()


def load_artifact(filename: str) -> Any:
    ensure_model_artifacts()
    settings = get_settings()
    artifact_path = Path(settings.model_dir) / filename
    try:
        return joblib.load(artifact_path)
    except Exception:
        from ml.pipelines.train_models import train_and_save_models

        train_and_save_models()
        return joblib.load(artifact_path)
