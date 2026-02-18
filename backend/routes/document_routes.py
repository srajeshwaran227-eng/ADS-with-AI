"""
Document Analysis Routes
────────────────────────
POST /analyze/document
"""

from flask import Blueprint, request, jsonify, current_app
from utils.file_handler import save_upload, cleanup_file
from utils.preprocessing import extract_text_from_file, clean_text
from services.plagiarism_service import analyze_plagiarism
from services.text_ai_detector import detect_ai_text

document_bp = Blueprint("document", __name__)


@document_bp.route("/analyze/document", methods=["POST"])
def analyze_document():
    """
    Accept a PDF, DOCX, or TXT upload.
    Return similarity %, AI probability %, confidence, and status.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request."}), 400

    file = request.files["file"]
    filepath = None

    try:
        allowed = current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"]
        filepath = save_upload(file, allowed)

        # Extract and clean text
        raw_text = extract_text_from_file(filepath)
        if not raw_text.strip():
            return jsonify({"error": "Could not extract text from file."}), 400

        cleaned = clean_text(raw_text, remove_stopwords=True)

        # Run analyses
        plagiarism = analyze_plagiarism(cleaned)
        ai_result = detect_ai_text(raw_text)

        similarity = plagiarism["similarity_percentage"]
        ai_prob = ai_result["ai_probability"]

        # Composite confidence
        if ai_prob > 75 or similarity > 70:
            confidence = "High"
        elif ai_prob > 50 or similarity > 40:
            confidence = "Moderate"
        else:
            confidence = "Low"

        status = "AI Generated" if ai_prob > 60 else "Human Written"

        return jsonify({
            "similarity": round(similarity, 1),
            "ai_probability": round(ai_prob, 1),
            "confidence": confidence,
            "status": status,
            "details": {
                "plagiarism": plagiarism,
                "ai_detection": ai_result,
            },
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500
    finally:
        cleanup_file(filepath)
