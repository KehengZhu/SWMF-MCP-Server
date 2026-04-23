from __future__ import annotations

import importlib
import math
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable, Protocol, Sequence

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_MODEL_ENV = "SWMF_KNOWLEDGE_EMBEDDING_MODEL"
EMBEDDING_PROVIDERS_ENV = "SWMF_KNOWLEDGE_EMBEDDING_PROVIDERS"

_CUDA_PROVIDER = "CUDAExecutionProvider"
_APPLE_PROVIDER = "CoreMLExecutionProvider"
_CPU_PROVIDER = "CPUExecutionProvider"


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


def select_fastembed_device(onnxruntime_module: Any) -> str:
    providers = set(_get_available_providers(onnxruntime_module))
    if _CUDA_PROVIDER in providers:
        return "cuda"
    if _APPLE_PROVIDER in providers:
        return "coreml"
    return "cpu"


def resolve_fastembed_providers(onnxruntime_module: Any) -> list[str] | None:
    override = os.environ.get(EMBEDDING_PROVIDERS_ENV, "").strip()
    available = _get_available_providers(onnxruntime_module)

    if override:
        requested = [provider.strip() for provider in override.split(",") if provider.strip()]
        filtered = [provider for provider in requested if provider in available]
        return filtered or None

    if _CUDA_PROVIDER in available:
        return [_CUDA_PROVIDER, _CPU_PROVIDER]
    if _APPLE_PROVIDER in available:
        return [_APPLE_PROVIDER, _CPU_PROVIDER]
    if _CPU_PROVIDER in available:
        return [_CPU_PROVIDER]
    return None


class FastEmbedTextEmbedder:
    def __init__(self, model_name: str | None = None) -> None:
        self._model_name = model_name or os.environ.get(EMBEDDING_MODEL_ENV, DEFAULT_EMBEDDING_MODEL)
        self._backend_name = f"fastembed:{self._model_name}"
        self._availability_message: str | None = None
        self._selected_device: str | None = None
        self._model = None

        try:
            fastembed = importlib.import_module("fastembed")
            model_cls = getattr(fastembed, "TextEmbedding")
        except Exception as exc:  # pragma: no cover - depends on optional dependency
            self._availability_message = f"fastembed unavailable: {exc}"
            return

        try:
            onnxruntime = importlib.import_module("onnxruntime")
        except Exception as exc:  # pragma: no cover - depends on optional dependency
            self._availability_message = f"onnxruntime unavailable: {exc}"
            return

        try:
            self._selected_device = select_fastembed_device(onnxruntime)
            providers = resolve_fastembed_providers(onnxruntime)
            kwargs: dict[str, Any] = {"model_name": self._model_name}
            if providers:
                kwargs["providers"] = providers
            self._model = model_cls(**kwargs)
        except Exception as exc:  # pragma: no cover - model/provider availability depends on runtime env
            self._availability_message = f"fastembed model init failed: {exc}"
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
        passage_embed = getattr(self._model, "passage_embed", None)
        if callable(passage_embed):
            return _vectors_to_lists(passage_embed(list(texts)))
        return _vectors_to_lists(self._model.embed(list(texts)))

    def embed_query(self, text: str) -> list[float]:
        if self._model is None:
            return []
        query_embed = getattr(self._model, "query_embed", None)
        if callable(query_embed):
            vectors = _vectors_to_lists(query_embed(text))
        else:
            vectors = _vectors_to_lists(self._model.embed([text]))
        if not vectors:
            return []
        return vectors[0]


@lru_cache(maxsize=1)
def get_text_embedder() -> TextEmbedder:
    embedder = FastEmbedTextEmbedder()
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


def _get_available_providers(onnxruntime_module: Any) -> list[str]:
    getter = getattr(onnxruntime_module, "get_available_providers", None)
    if not callable(getter):
        return []
    try:
        providers = getter()
    except Exception:
        return []
    return [str(provider) for provider in providers]


def _vectors_to_lists(vectors: Iterable[object]) -> list[list[float]]:
    return [_vector_to_list(vector) for vector in vectors]


def _vector_to_list(vector: object) -> list[float]:
    if hasattr(vector, "tolist"):
        values = vector.tolist()
    else:
        values = list(vector)  # type: ignore[arg-type]
    return [float(value) for value in values]