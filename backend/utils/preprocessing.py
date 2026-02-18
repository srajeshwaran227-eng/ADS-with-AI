"""
Preprocessing Utility
─────────────────────
Text extraction from PDF / DOCX / TXT, text cleaning, and
helper functions for image / audio normalisation.
"""

import re
import string


# ── Text Extraction ────────────────────────────────────────

def extract_text_from_file(filepath: str) -> str:
    """Extract plain text from a PDF, DOCX, or TXT file."""
    ext = filepath.rsplit(".", 1)[-1].lower()

    if ext == "txt":
        return _read_txt(filepath)
    elif ext == "pdf":
        return _read_pdf(filepath)
    elif ext == "docx":
        return _read_docx(filepath)
    else:
        raise ValueError(f"Unsupported file format: .{ext}")


def _read_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _read_pdf(filepath: str) -> str:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        raise ImportError("PyPDF2 is required for PDF processing. Install it: pip install PyPDF2")

    reader = PdfReader(filepath)
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n".join(pages)


def _read_docx(filepath: str) -> str:
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx is required for DOCX processing. Install it: pip install python-docx")

    doc = Document(filepath)
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


# ── Text Cleaning ──────────────────────────────────────────

# Common English stopwords (subset — avoids requiring nltk download on first run)
_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall", "can",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how",
    "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "just", "because", "about", "up", "it",
    "its", "this", "that", "these", "those", "i", "me", "my", "we",
    "our", "you", "your", "he", "him", "his", "she", "her", "they",
    "them", "their", "what", "which", "who", "whom",
}


def clean_text(text: str, remove_stopwords: bool = True) -> str:
    """
    Lowercase, strip punctuation, collapse whitespace,
    and optionally remove common English stopwords.
    """
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()

    if remove_stopwords:
        words = text.split()
        words = [w for w in words if w not in _STOPWORDS]
        text = " ".join(words)

    return text


# ── Image Helpers ──────────────────────────────────────────

def load_and_preprocess_image(filepath: str, target_size: tuple = (224, 224)):
    """
    Load an image with OpenCV, resize, and normalise pixel values to [0, 1].
    Returns a numpy array of shape (1, H, W, 3).
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        raise ImportError("opencv-python and numpy are required. pip install opencv-python numpy")

    img = cv2.imread(filepath)
    if img is None:
        raise ValueError("Could not read image file.")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, target_size)
    img = img.astype(np.float32) / 255.0
    img = np.expand_dims(img, axis=0)  # batch dimension
    return img


# ── Audio Helpers ──────────────────────────────────────────

def load_audio_spectrogram(filepath: str, sr: int = 22050, n_mels: int = 128):
    """
    Load audio with librosa, compute a mel spectrogram, and return it
    as a numpy array suitable for a CNN input.
    """
    try:
        import librosa
        import numpy as np
    except ImportError:
        raise ImportError("librosa and numpy are required. pip install librosa numpy")

    y, _ = librosa.load(filepath, sr=sr, mono=True)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
    S_db = librosa.power_to_db(S, ref=np.max)

    # Normalise to [0, 1]
    S_norm = (S_db - S_db.min()) / (S_db.max() - S_db.min() + 1e-8)
    S_norm = np.expand_dims(S_norm, axis=(0, -1))  # (1, n_mels, time, 1)
    return S_norm
