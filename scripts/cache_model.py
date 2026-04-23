#!/usr/bin/env python3
"""Warm the local FastEmbed cache for the configured embedding model."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))

from swmf_mcp_server.knowledge.embeddings import (  # noqa: E402
    DEFAULT_EMBEDDING_MODEL,
    EMBEDDING_MODEL_ENV,
    get_text_embedder,
    get_text_embedder_runtime_payload,
)


def main() -> int:
    model_name = __import__("os").environ.get(EMBEDDING_MODEL_ENV, DEFAULT_EMBEDDING_MODEL)
    print(f"    Embedding model: {model_name}")
    print("    Downloading/warming local cache…")

    embedder = get_text_embedder()
    if not embedder.is_available:
        payload = get_text_embedder_runtime_payload(embedder)
        print(
            f"ERROR: embedding backend unavailable: {payload.get('availability_message')}",
            file=sys.stderr,
        )
        return 1

    _ = embedder.embed_query("warm local embedding cache")
    payload = get_text_embedder_runtime_payload(embedder)
    print(f"    Cached model ready: {payload.get('model_name')}")
    print(f"    Backend: {payload.get('backend_name')}")
    print(f"    Selected device: {payload.get('selected_device')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())