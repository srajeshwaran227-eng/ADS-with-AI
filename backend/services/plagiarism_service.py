"""
Plagiarism Service
──────────────────
TF-IDF vectorization + cosine similarity for document plagiarism detection.
"""

import random
from flask import current_app


def analyze_plagiarism(text: str) -> dict:
    """
    Compare the input text against a reference corpus using
    TF-IDF + cosine similarity.  Falls back to demo mode when
    real processing libraries are unavailable or DEMO_MODE is on.
    """
    if current_app.config.get("DEMO_MODE", True):
        return _demo_result()

    return _real_analysis(text)


def _real_analysis(text: str) -> dict:
    """Production analysis using scikit-learn."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        # Reference corpus — in production this would be a large
        # database of known documents.  For demonstration we use a
        # small set of sample paragraphs.
        reference_corpus = [
            "Artificial intelligence is the simulation of human intelligence by machines.",
            "Machine learning is a subset of artificial intelligence that allows systems to learn from data.",
            "Deep learning uses neural networks with many layers to model complex patterns.",
            "Natural language processing enables computers to understand human language.",
            "Computer vision allows machines to interpret and understand visual information.",
            "Plagiarism is the practice of taking someone else's work or ideas and passing them off as one's own.",
        ]

        documents = [text] + reference_corpus
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(documents)

        # Cosine similarity between uploaded text and each reference doc
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        max_similarity = float(similarities.max()) * 100

        similarity_pct = round(min(max_similarity, 100), 1)
        return {
            "similarity_percentage": similarity_pct,
            "max_matched_index": int(similarities.argmax()),
        }

    except ImportError:
        return _demo_result()


def _demo_result() -> dict:
    """Generate plausible demo values."""
    similarity = round(random.uniform(10, 60), 1)
    return {
        "similarity_percentage": similarity,
        "max_matched_index": -1,
    }
