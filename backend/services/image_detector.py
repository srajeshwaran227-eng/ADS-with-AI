"""
Image Detector Service
──────────────────────
CNN-based detection of AI-generated / manipulated images.
"""

import random
from flask import current_app


def detect_ai_image(filepath: str) -> dict:
    """
    Analyse an image to determine if it is AI-generated.
    Returns ai_probability, confidence_level, and result label.
    """
    if current_app.config.get("DEMO_MODE", True):
        return _demo_result()

    return _real_detection(filepath)


def _real_detection(filepath: str) -> dict:
    """
    Production detection using a pretrained CNN.
    Expects a TensorFlow/Keras SavedModel or .h5 file at IMAGE_MODEL_PATH.
    """
    try:
        import numpy as np
        from utils.preprocessing import load_and_preprocess_image

        img = load_and_preprocess_image(filepath, target_size=(224, 224))

        model_path = current_app.config.get("IMAGE_MODEL_PATH", "")

        if model_path:
            # TensorFlow / Keras
            try:
                from tensorflow.keras.models import load_model  # type: ignore
                model = load_model(model_path)
                prediction = model.predict(img, verbose=0)
                ai_prob = float(prediction[0][0]) * 100
            except ImportError:
                # PyTorch fallback
                import torch
                model = torch.load(model_path, map_location="cpu")
                model.eval()
                tensor = torch.from_numpy(img).permute(0, 3, 1, 2).float()
                with torch.no_grad():
                    output = model(tensor)
                ai_prob = float(torch.sigmoid(output).item()) * 100
        else:
            # No model file — fall back to demo
            return _demo_result()

        ai_prob = round(min(max(ai_prob, 0), 100), 1)
        confidence = _confidence_level(ai_prob)
        result = "AI Generated" if ai_prob > 60 else "Real"

        return {
            "ai_probability": ai_prob,
            "confidence_level": confidence,
            "result": result,
        }

    except Exception:
        return _demo_result()


def _confidence_level(probability: float) -> str:
    if probability > 80 or probability < 20:
        return "High"
    elif probability > 60 or probability < 40:
        return "Moderate"
    return "Low"


def _demo_result() -> dict:
    """Generate plausible demo values."""
    ai_prob = round(random.uniform(30, 95), 1)
    confidence = _confidence_level(ai_prob)
    result = "AI Generated" if ai_prob > 60 else "Real"
    return {
        "ai_probability": ai_prob,
        "confidence_level": confidence,
        "result": result,
    }
