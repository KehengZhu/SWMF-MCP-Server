from __future__ import annotations

from types import SimpleNamespace

from swmf_mcp_server.knowledge import embeddings


def _fake_onnxruntime(*, providers: list[str]):
    return SimpleNamespace(get_available_providers=lambda: providers)


def test_select_fastembed_device_prefers_cuda() -> None:
    onnxruntime = _fake_onnxruntime(
        providers=["CUDAExecutionProvider", "CoreMLExecutionProvider", "CPUExecutionProvider"]
    )

    assert embeddings.select_fastembed_device(onnxruntime) == "cuda"


def test_select_fastembed_device_uses_coreml_when_cuda_unavailable() -> None:
    onnxruntime = _fake_onnxruntime(providers=["CoreMLExecutionProvider", "CPUExecutionProvider"])

    assert embeddings.select_fastembed_device(onnxruntime) == "coreml"


def test_select_fastembed_device_falls_back_to_cpu() -> None:
    onnxruntime = _fake_onnxruntime(providers=["CPUExecutionProvider"])

    assert embeddings.select_fastembed_device(onnxruntime) == "cpu"


def test_get_text_embedder_returns_unavailable_when_dependencies_missing(monkeypatch) -> None:
    real_import_module = embeddings.importlib.import_module

    def fake_import_module(name: str):
        if name == "fastembed":
            raise ImportError("missing fastembed")
        return real_import_module(name)

    embeddings.reset_text_embedder_cache()
    monkeypatch.setattr(embeddings.importlib, "import_module", fake_import_module)

    embedder = embeddings.get_text_embedder()

    assert embedder.is_available is False
    assert embedder.availability_message is not None
    assert "fastembed unavailable" in embedder.availability_message

    embeddings.reset_text_embedder_cache()


def test_fastembed_embedder_reports_selected_device(monkeypatch) -> None:
    class FakeTextEmbedding:
        def __init__(self, model_name: str, providers: list[str]) -> None:
            self.model_name = model_name
            self.providers = providers

        def query_embed(self, text: str):
            return [[1.0, 0.0]]

        def passage_embed(self, texts):
            return [[1.0, 0.0] for _ in texts]

    def fake_import_module(name: str):
        if name == "onnxruntime":
            return _fake_onnxruntime(providers=["CoreMLExecutionProvider", "CPUExecutionProvider"])
        if name == "fastembed":
            return SimpleNamespace(TextEmbedding=FakeTextEmbedding)
        raise AssertionError(f"unexpected import: {name}")

    embeddings.reset_text_embedder_cache()
    monkeypatch.setattr(embeddings.importlib, "import_module", fake_import_module)

    embedder = embeddings.get_text_embedder()

    assert embedder.is_available is True
    assert embedder.selected_device == "coreml"
    assert embedder.model_name == embeddings.DEFAULT_EMBEDDING_MODEL
    assert embedder.backend_name.startswith("fastembed:")

    embeddings.reset_text_embedder_cache()


def test_get_text_embedder_runtime_payload_reports_backend_metadata(monkeypatch) -> None:
    class FakeEmbedder:
        backend_name = "fastembed:test-model"
        availability_message = None
        model_name = "test-model"
        selected_device = "coreml"

        @property
        def is_available(self) -> bool:
            return True

    monkeypatch.setattr(embeddings, "get_text_embedder", lambda: FakeEmbedder())

    payload = embeddings.get_text_embedder_runtime_payload()

    assert payload == {
        "available": True,
        "backend_name": "fastembed:test-model",
        "model_name": "test-model",
        "selected_device": "coreml",
        "availability_message": None,
    }