from __future__ import annotations

import importlib
import math
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol, Sequence

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_MODEL_ENV = "SWMF_KNOWLEDGE_EMBEDDING_MODEL"


class TextEmbedder(Protocol):
    @property
    def is_available(self) -> bool: ...

    @property
    def backend_name(self) -> str: ...

    @property
    def availability_message(self) -> str | None: ...

    @property
    def model_name(self) -> str | None: ...

    @property
    def selected_device(self) -> str | None: ...

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


@dataclass
class UnavailableTextEmbedder:
    backend_name: str = "unavailable"
    availability_message: str | None = None
    model_name: str | None = None
    selected_device: str | None = None

    @property
    def is_available(self) -> bool:
        return False

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return []

    def embed_query(self, text: str) -> list[float]:
        return []


def select_torch_device(torch_module: Any) -> str:
    cuda = getattr(torch_module, "cuda", None)
    if cuda is not None and callable(getattr(cuda, "is_available", None)) and cuda.is_available():
        return "cuda"

    backends = getattr(torch_module, "backends", None)
    mps = getattr(backends, "mps", None) if backends is not None else None
    if (
        mps is not None
        and callable(getattr(mps, "is_available", None))
        and callable(getattr(mps, "is_built", None))
        and mps.is_available()
        and mps.is_built()
    ):
        return "mps"

    return "cpu"


class SentenceTransformersTextEmbedder:
    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or os.environ.get(EMBEDDING_MODEL_ENV, DEFAULT_EMBEDDING_MODEL)
        self._backend_name = f"sentence-transformers:{self._model_name}"
        self._availability_message: str | None = None
        self._selected_device: str | None = None
        self._model = None

        try:
            torch = importlib.import_module("torch")
        except Exception as exc:  # pragma: no cover - depends on optional dependency
            self._availability_message = f"torch unavailable: {exc}"
            return

        try:
            sentence_transformers = importlib.import_module("sentence_transformers")
            model_cls = getattr(sentence_transformers, "SentenceTransformer")
        except Exception as exc:  # pragma: no cover - depends on optional dependency
            self._availability_message = f"sentence-transformers unavailable: {exc}"
            return

        try:
            self._selected_device = select_torch_device(torch)
            self._model = model_cls(self._model_name, device=self._selected_device)
        except Exception as exc:  # pragma: no cover - model/device availability depends on runtime env
            self._availability_message = f"sentence-transformers model init failed: {exc}"
            self._model = None
            self._selected_device = None

    @property
    def is_available(self) -> bool:
        return self._model is not None

    @property
    def backend_name(self) -> str:
        return self._backend_name

    @property
    def availability_message(self) -> str | None:
        return self._availability_message

    @property
    def model_name(self) -> str | None:
        return self._model_name

    @property
    def selected_device(self) -> str | None:
        return self._selected_device

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if self._model is None or not texts:
            return []
        encoded = self._model.encode(list(texts), convert_to_numpy=True, normalize_embeddings=True)
        return [_vector_to_list(vector) for vector in encoded]

    def embed_query(self, text: str) -> list[float]:
        if self._model is None:
            return []
        encoded = self._model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
        if len(encoded) == 0:
            return []
        return _vector_to_list(encoded[0])


@lru_cache(maxsize=1)
def get_text_embedder() -> TextEmbedder:
    embedder = SentenceTransformersTextEmbedder()
    if embedder.is_available:
        return embedder
    return UnavailableTextEmbedder(
        availability_message=embedder.availability_message,
        model_name=embedder.model_name,
        selected_device=embedder.selected_device,
    )


def reset_text_embedder_cache() -> None:
    get_text_embedder.cache_clear()


def get_text_embedder_runtime_payload(embedder: TextEmbedder | None = None) -> dict[str, Any]:
    resolved = embedder or get_text_embedder()
    return {
        "available": bool(getattr(resolved, "is_available", False)),
        "backend_name": getattr(resolved, "backend_name", "unavailable"),
        "model_name": getattr(resolved, "model_name", None),
        "selected_device": getattr(resolved, "selected_device", None),
        "availability_message": getattr(resolved, "availability_message", None),
    }


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(float(a) * float(b) for a, b in zip(left, right))
    left_norm = math.sqrt(sum(float(value) * float(value) for value in left))
    right_norm = math.sqrt(sum(float(value) * float(value) for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


def _vector_to_list(vector: object) -> list[float]:
    if hasattr(vector, "tolist"):
        values = vector.tolist()
    else:
        values = list(vector)  # type: ignore[arg-type]
    return [float(value) for value in values]