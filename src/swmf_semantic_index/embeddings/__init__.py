"""
Embedding backend abstraction.

The v1 default backend is a pure-Python TF-IDF/BM25-style lexical scorer that
requires no external dependencies. This lets the engine work out of the box.

A neural backend can be plugged in by implementing EmbeddingBackend and registering
it via get_backend(name). The interface contract is:
  - encode(texts) → list[list[float]]  (one vector per text)
  - similarity(vec_a, vec_b) → float
  - dim → int

The storage layer stores None for embeddings when using the lexical-only backend,
and the retrieval layer falls back to keyword scoring.
"""

from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from collections import Counter
from typing import Optional


class EmbeddingBackend(ABC):
    """Abstract interface for embedding backends."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def dim(self) -> int: ...

    @abstractmethod
    def encode(self, texts: list[str]) -> list[list[float]]:
        """Return a list of dense vectors, one per input text."""
        ...

    @abstractmethod
    def similarity(self, vec_a: list[float], vec_b: list[float]) -> float: ...


class LexicalBackend(EmbeddingBackend):
    """
    Lexical-only backend using TF-IDF bag-of-words.

    Does not produce true dense embeddings. The encode() method returns
    a sparse vector as a dense list (padded with zeros), which is only
    useful for similarity() comparisons within this class.

    Primary use: BM25-style keyword ranking in the retrieval layer without
    requiring any ML dependency.
    """

    _TOKENIZE = re.compile(r"\b[a-z_]\w{2,}\b", re.IGNORECASE)
    _STOP = frozenset([
        "the", "and", "for", "with", "from", "this", "that",
        "are", "not", "use", "end", "call", "module",
    ])

    def __init__(self) -> None:
        self._vocab: dict[str, int] = {}
        self._idf: dict[str, float] = {}
        self._corpus_size: int = 0

    @property
    def name(self) -> str:
        return "tfidf_lexical"

    @property
    def dim(self) -> int:
        return len(self._vocab)

    def fit(self, texts: list[str]) -> None:
        """Build vocabulary and IDF from a list of texts."""
        self._vocab = {}
        doc_freq: Counter[str] = Counter()
        self._corpus_size = len(texts)

        for text in texts:
            tokens = set(self._tokenize(text))
            for tok in tokens:
                doc_freq[tok] += 1

        for tok, df in doc_freq.items():
            self._vocab[tok] = len(self._vocab)
            self._idf[tok] = math.log((1 + self._corpus_size) / (1 + df)) + 1.0

    def _tokenize(self, text: str) -> list[str]:
        return [
            t.lower() for t in self._TOKENIZE.findall(text)
            if t.lower() not in self._STOP
        ]

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Encode texts as TF-IDF vectors. Vocabulary must be fitted first."""
        results = []
        for text in texts:
            tokens = self._tokenize(text)
            tf: Counter[str] = Counter(tokens)
            vec = [0.0] * len(self._vocab)
            for tok, count in tf.items():
                if tok in self._vocab:
                    idx = self._vocab[tok]
                    tf_val = count / max(len(tokens), 1)
                    vec[idx] = tf_val * self._idf.get(tok, 1.0)
            results.append(vec)
        return results

    def similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Cosine similarity between two vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, type[EmbeddingBackend]] = {
    "tfidf_lexical": LexicalBackend,
}


def get_backend(name: str = "tfidf_lexical") -> EmbeddingBackend:
    """Instantiate a registered backend by name."""
    cls = _REGISTRY.get(name)
    if cls is None:
        available = list(_REGISTRY.keys())
        raise ValueError(f"Unknown embedding backend '{name}'. Available: {available}")
    return cls()


def register_backend(name: str, cls: type[EmbeddingBackend]) -> None:
    """Register a custom backend (e.g., a neural backend from an optional dependency)."""
    _REGISTRY[name] = cls
