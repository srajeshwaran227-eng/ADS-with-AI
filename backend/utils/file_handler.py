"""
File Handler Utility
────────────────────
Validates uploads, saves files securely, and cleans up temp files.
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if the file extension is permitted."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def get_extension(filename: str) -> str:
    """Return the lowercase file extension."""
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def save_upload(file, allowed_extensions: set) -> str:
    """
    Validate and save an uploaded file.

    Returns the absolute path to the saved file.
    Raises ValueError on validation failure.
    """
    if file is None or file.filename == "":
        raise ValueError("No file provided.")

    if not allowed_file(file.filename, allowed_extensions):
        allowed = ", ".join(sorted(allowed_extensions)).upper()
        raise ValueError(f"Invalid file type. Allowed: {allowed}")

    # Secure the filename and add a UUID prefix to prevent collisions
    original = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex[:12]}_{original}"

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, unique_name)

    # Prevent path traversal
    abs_upload = os.path.abspath(upload_dir)
    abs_file = os.path.abspath(filepath)
    if not abs_file.startswith(abs_upload):
        raise ValueError("Invalid file path detected.")

    file.save(filepath)
    return filepath


def cleanup_file(filepath: str) -> None:
    """Delete a temporary file if it exists."""
    try:
        if filepath and os.path.isfile(filepath):
            os.remove(filepath)
    except OSError:
        pass
