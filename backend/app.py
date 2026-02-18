"""
AuthentiGuard AI — Flask Application Entry Point
──────────────────────────────────────────────────
Registers blueprints for each detection modality and
configures CORS, upload folder, and error handlers.
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── CORS ───────────────────────────────────────────────
    CORS(app, origins=app.config["CORS_ORIGINS"])

    # ── Ensure upload directory exists ─────────────────────
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Register Blueprints ────────────────────────────────
    from routes.document_routes import document_bp
    from routes.image_routes import image_bp
    from routes.video_routes import video_bp
    from routes.audio_routes import audio_bp

    app.register_blueprint(document_bp)
    app.register_blueprint(image_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(audio_bp)

    # ── Health Check ───────────────────────────────────────
    @app.route("/", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "service": "AuthentiGuard AI Backend",
            "demo_mode": app.config["DEMO_MODE"],
        })

    # ── Error Handlers ─────────────────────────────────────
    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({
            "error": "File too large. Maximum allowed size is 20 MB."
        }), 413

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error": "Internal server error."}), 500

    return app


# ── Run directly ───────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
