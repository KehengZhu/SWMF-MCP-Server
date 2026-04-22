from __future__ import annotations

import ast
from pathlib import Path


def test_catalog_index_does_not_import_embedding_modules() -> None:
    path = Path(__file__).resolve().parents[1] / "src" / "swmf_mcp_server" / "catalog" / "source_index_catalog.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    forbidden = {
        "swmf_mcp_server.core.semantic_search",
        "swmf_mcp_server.knowledge",
        "torch",
        "sentence_transformers",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name not in forbidden
                assert not alias.name.startswith("swmf_mcp_server.knowledge")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert module not in forbidden
            assert not module.startswith("swmf_mcp_server.knowledge")
            assert not (node.level >= 1 and module.startswith("knowledge"))