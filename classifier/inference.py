from pathlib import Path

import joblib


MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"

_model = None


def _load_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Classifier model not found at {MODEL_PATH}. "
                f"Run `python classifier/train.py` to generate it."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def classify_text(text: str) -> tuple[str, float]:
    if not text or not text.strip():
        return ("other", 0.0)

    model = _load_model()
    label = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0]
    confidence = float(probabilities.max())
    return (label, confidence)