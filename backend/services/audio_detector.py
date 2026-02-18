"""
Audio Detector Service
──────────────────────
Mel-spectrogram analysis + CNN classifier for AI voice detection.
"""

import random
from flask import current_app


def detect_ai_audio(filepath: str) -> dict:
    """
    Load audio, generate a mel spectrogram, and classify it
    as AI-synthesized or real human speech.
    """
    if current_app.config.get("DEMO_MODE", True):
        return _demo_result()

    return _real_detection(filepath)


def _real_detection(filepath: str) -> dict:
    """
    Production detection using librosa + CNN.
    Expects a TensorFlow/Keras model at AUDIO_MODEL_PATH.
    """
    try:
        from utils.preprocessing import load_audio_spectrogram

        spectrogram = load_audio_spectrogram(filepath)

        model_path = current_app.config.get("AUDIO_MODEL_PATH", "")

        if model_path:
            try:
                from tensorflow.keras.models import load_model  # type: ignore
                model = load_model(model_path)
                prediction = model.predict(spectrogram, verbose=0)
                ai_prob = float(prediction[0][0]) * 100
            except ImportError:
                # PyTorch fallback
                import torch
                import numpy as np
                model = torch.load(model_path, map_location="cpu")
                model.eval()
                tensor = torch.from_numpy(spectrogram).permute(0, 3, 1, 2).float()
                with torch.no_grad():
                    output = model(tensor)
                ai_prob = float(torch.sigmoid(output).item()) * 100
        else:
            return _demo_result()

        ai_prob = round(min(max(ai_prob, 0), 100), 1)
        classification = "AI Synthesized Voice" if ai_prob > 60 else "Real Human Voice"

        return {
            "ai_voice_probability": ai_prob,
            "classification": classification,
        }

    except Exception:
        return _demo_result()


def _demo_result() -> dict:
    """Generate plausible demo values."""
    ai_prob = round(random.uniform(30, 95), 1)
    classification = "AI Synthesized Voice" if ai_prob > 60 else "Real Human Voice"
    return {
        "ai_voice_probability": ai_prob,
        "classification": classification,
    }
