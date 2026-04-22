from __future__ import annotations

from types import SimpleNamespace

from swmf_mcp_server.knowledge import embeddings


def _fake_torch(*, cuda: bool, mps_available: bool, mps_built: bool):
    return SimpleNamespace(
        cuda=SimpleNamespace(is_available=lambda: cuda),
        backends=SimpleNamespace(
            mps=SimpleNamespace(
                is_available=lambda: mps_available,
                is_built=lambda: mps_built,
            )
        ),
    )


def test_select_torch_device_prefers_cuda() -> None:
    torch = _fake_torch(cuda=True, mps_available=True, mps_built=True)

    assert embeddings.select_torch_device(torch) == "cuda"


def test_select_torch_device_uses_mps_when_cuda_unavailable() -> None:
    torch = _fake_torch(cuda=False, mps_available=True, mps_built=True)

    assert embeddings.select_torch_device(torch) == "mps"


def test_select_torch_device_falls_back_to_cpu() -> None:
    torch = _fake_torch(cuda=False, mps_available=False, mps_built=False)

    assert embeddings.select_torch_device(torch) == "cpu"


def test_get_text_embedder_returns_unavailable_when_dependencies_missing(monkeypatch) -> None:
    real_import_module = embeddings.importlib.import_module

    def fake_import_module(name: str):
        if name == "torch":
            raise ImportError("missing torch")
        return real_import_module(name)

    embeddings.reset_text_embedder_cache()
    monkeypatch.setattr(embeddings.importlib, "import_module", fake_import_module)

    embedder = embeddings.get_text_embedder()

    assert embedder.is_available is False
    assert embedder.availability_message is not None
    assert "torch unavailable" in embedder.availability_message

    embeddings.reset_text_embedder_cache()


def test_sentence_transformer_embedder_reports_selected_device(monkeypatch) -> None:
    class FakeSentenceTransformer:
        def __init__(self, model_name: str, device: str) -> None:
            self.model_name = model_name
            self.device = device

        def encode(self, texts, convert_to_numpy=True, normalize_embeddings=True):
            return [[1.0, 0.0] for _ in texts]

    def fake_import_module(name: str):
        if name == "torch":
            return _fake_torch(cuda=False, mps_available=True, mps_built=True)
        if name == "sentence_transformers":
            return SimpleNamespace(SentenceTransformer=FakeSentenceTransformer)
        raise AssertionError(f"unexpected import: {name}")

    embeddings.reset_text_embedder_cache()
    monkeypatch.setattr(embeddings.importlib, "import_module", fake_import_module)

    embedder = embeddings.get_text_embedder()

    assert embedder.is_available is True
    assert embedder.selected_device == "mps"
    assert embedder.model_name == embeddings.DEFAULT_EMBEDDING_MODEL
    assert embedder.backend_name.startswith("sentence-transformers:")

    embeddings.reset_text_embedder_cache()


def test_get_text_embedder_runtime_payload_reports_backend_metadata(monkeypatch) -> None:
    class FakeEmbedder:
        backend_name = "sentence-transformers:test-model"
        availability_message = None
        model_name = "test-model"
        selected_device = "cuda"

        @property
        def is_available(self) -> bool:
            return True

    monkeypatch.setattr(embeddings, "get_text_embedder", lambda: FakeEmbedder())

    payload = embeddings.get_text_embedder_runtime_payload()

    assert payload == {
        "available": True,
        "backend_name": "sentence-transformers:test-model",
        "model_name": "test-model",
        "selected_device": "cuda",
        "availability_message": None,
    }