"""
Video Analysis Routes
─────────────────────
POST /analyze/video
"""

from flask import Blueprint, request, jsonify, current_app
from utils.file_handler import save_upload, cleanup_file
from services.video_detector import detect_deepfake_video

video_bp = Blueprint("video", __name__)


@video_bp.route("/analyze/video", methods=["POST"])
def analyze_video():
    """
    Accept an MP4, AVI, or MOV upload.
    Return deepfake probability %, confidence, and classification.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request."}), 400

    file = request.files["file"]
    filepath = None

    try:
        allowed = current_app.config["ALLOWED_VIDEO_EXTENSIONS"]
        filepath = save_upload(file, allowed)

        result = detect_deepfake_video(filepath)

        prob = result["deepfake_probability"]
        status = "Deepfake Detected" if prob > 60 else "Likely Authentic"

        return jsonify({
            "similarity": 0,
            "ai_probability": round(prob, 1),
            "confidence": result["confidence_level"],
            "status": status,
            "details": result,
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
    finally:
        cleanup_file(filepath)
