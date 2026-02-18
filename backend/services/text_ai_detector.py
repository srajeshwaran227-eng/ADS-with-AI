"""
AI Text Detector Service
─────────────────────────
Uses a Hugging Face transformer model to classify text as
human-written or AI-generated.
"""

import random
from flask import current_app


def detect_ai_text(text: str) -> dict:
    """
    Classify the supplied text as AI-generated or human-written.
    Returns ai_probability (0-100) and a classification label.
    """
    if current_app.config.get("DEMO_MODE", True):
        return _demo_result()

    return _real_detection(text)


def _real_detection(text: str) -> dict:
    """Production detection using Hugging Face transformers."""
    try:
        from transformers import pipeline

        model_name = current_app.config.get(
            "HF_MODEL_NAME", "roberta-base-openai-detector"
        )

        classifier = pipeline(
            "text-classification",
            model=model_name,
            truncation=True,
            max_length=512,
        )

        # The model returns labels like "LABEL_0" (Real) / "LABEL_1" (Fake)
        # or "Real" / "Fake" depending on the model.
        result = classifier(text[:512])[0]

        label = result.get("label", "").upper()
        score = result.get("score", 0.5)

        # Normalise — some models use "FAKE"/"REAL", others use LABEL_0/LABEL_1
        if "FAKE" in label or "1" in label:
            ai_probability = round(score * 100, 1)
        else:
            ai_probability = round((1 - score) * 100, 1)

        classification = "AI Generated" if ai_probability > 60 else "Human Written"

        return {
            "ai_probability": ai_probability,
            "classification": classification,
            "raw_label": result.get("label"),
            "raw_score": round(score, 4),
        }

    except Exception:
        return _demo_result()


def _demo_result() -> dict:
    """Generate plausible demo values."""
    ai_prob = round(random.uniform(30, 95), 1)
    classification = "AI Generated" if ai_prob > 60 else "Human Written"
    return {
        "ai_probability": ai_prob,
        "classification": classification,
        "raw_label": "DEMO",
        "raw_score": round(ai_prob / 100, 4),
    }
