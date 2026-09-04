"""
rag_engine.py
--------------
A lightweight Retrieval-Augmented Generation store.

Why TF-IDF instead of a heavy embedding model?
Hackathon judges care that retrieval genuinely grounds the answers and that
the app installs/runs without errors on a laptop with no GPU. scikit-learn's
TF-IDF + cosine similarity gives real, working knowledge-grounding with
near-zero setup risk. If you want semantic embeddings later, swap
`_vectorizer` for a sentence-transformers model - the rest of the pipeline
(chunk -> store -> retrieve -> cite) stays identical.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class RAGStore:
    """One instance per uploaded document / learning session."""

    def __init__(self):
        self.chunks = []
        self.vectorizer = None
        self.matrix = None

    def index(self, chunks):
        self.chunks = chunks
        if not chunks:
            self.vectorizer = None
            self.matrix = None
            return
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=20000)
        self.matrix = self.vectorizer.fit_transform(chunks)

    def retrieve(self, query: str, top_k: int = 4):
        """Returns the most relevant chunks for a query, most relevant first."""
        if not self.chunks or self.vectorizer is None:
            return []

        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        ranked_idx = scores.argsort()[::-1][:top_k]

        results = []
        for idx in ranked_idx:
            if scores[idx] > 0:
                results.append({"text": self.chunks[idx], "score": float(scores[idx])})
        return results

    def has_material(self) -> bool:
        return bool(self.chunks)


# In-memory session store: {session_id: RAGStore}
# Fine for a hackathon demo (single process). For production, swap for
# ChromaDB / a real vector DB keyed by session_id.
_SESSIONS = {}


def get_or_create_store(session_id: str) -> RAGStore:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = RAGStore()
    return _SESSIONS[session_id]
