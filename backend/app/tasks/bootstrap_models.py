from app.services.ml.model_loader import ensure_model_artifacts


def bootstrap_models() -> None:
    ensure_model_artifacts()
