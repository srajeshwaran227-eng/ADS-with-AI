"""
Configuration for AuthentiGuard AI Backend.
Toggle DEMO_MODE to use mock results when real AI models are not loaded.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # ── Demo Mode ──────────────────────────────────────────────
    # Set to False when real AI models are available
    DEMO_MODE = True

    # ── Flask ──────────────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    # ── File Uploads ───────────────────────────────────────────
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB

    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "docx", "txt"}
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov"}
    ALLOWED_AUDIO_EXTENSIONS = {"mp3", "wav"}

    # ── CORS ───────────────────────────────────────────────────
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # ── Hugging Face ───────────────────────────────────────────
    HF_MODEL_NAME = os.getenv("HF_MODEL_NAME", "roberta-base-openai-detector")
    HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")

    # ── Model Paths (optional, for local weights) ──────────────
    IMAGE_MODEL_PATH = os.getenv("IMAGE_MODEL_PATH", "")
    VIDEO_MODEL_PATH = os.getenv("VIDEO_MODEL_PATH", "")
    AUDIO_MODEL_PATH = os.getenv("AUDIO_MODEL_PATH", "")
