"""
Audio Analysis Routes
─────────────────────
POST /analyze/audio
"""

from flask import Blueprint, request, jsonify, current_app
from utils.file_handler import save_upload, cleanup_file
from services.audio_detector import detect_ai_audio

audio_bp = Blueprint("audio", __name__)


@audio_bp.route("/analyze/audio", methods=["POST"])
def analyze_audio():
    """
    Accept an MP3 or WAV upload.
    Return AI voice probability % and classification.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request."}), 400

    file = request.files["file"]
    filepath = None

    try:
        allowed = current_app.config["ALLOWED_AUDIO_EXTENSIONS"]
        filepath = save_upload(file, allowed)

        result = detect_ai_audio(filepath)

        prob = result["ai_voice_probability"]
        status = "AI Synthesized Voice" if prob > 60 else "Real Human Voice"

        return jsonify({
            "similarity": 0,
            "ai_probability": round(prob, 1),
            "confidence": "High" if prob > 75 else ("Moderate" if prob > 50 else "Low"),
            "status": status,
            "details": result,
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
    finally:
        cleanup_file(filepath)
