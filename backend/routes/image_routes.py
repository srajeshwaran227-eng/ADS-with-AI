"""
Image Analysis Routes
─────────────────────
POST /analyze/image
"""

from flask import Blueprint, request, jsonify, current_app
from utils.file_handler import save_upload, cleanup_file
from services.image_detector import detect_ai_image

image_bp = Blueprint("image", __name__)


@image_bp.route("/analyze/image", methods=["POST"])
def analyze_image():
    """
    Accept a JPG, JPEG, or PNG upload.
    Return AI probability %, confidence level, and result.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request."}), 400

    file = request.files["file"]
    filepath = None

    try:
        allowed = current_app.config["ALLOWED_IMAGE_EXTENSIONS"]
        filepath = save_upload(file, allowed)

        result = detect_ai_image(filepath)

        ai_prob = result["ai_probability"]
        status = "AI Generated" if ai_prob > 60 else "Real"

        return jsonify({
            "similarity": 0,
            "ai_probability": round(ai_prob, 1),
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
