from __future__ import annotations

import ast
from pathlib import Path


def test_public_entrypoints_do_not_import_core_knowledge_service() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    paths = [
        repo_root / "src" / "swmf_mcp_server" / "tools" / "knowledge.py",
        repo_root / "src" / "swmf_mcp_server" / "tools" / "param.py",
        repo_root / "src" / "swmf_mcp_server" / "resources" / "param_schema.py",
        repo_root / "src" / "swmf_mcp_server" / "resources" / "source_knowledge.py",
        repo_root / "src" / "swmf_mcp_server" / "server.py",
    ]

    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "swmf_mcp_server.core.knowledge_service"
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert module != "swmf_mcp_server.core.knowledge_service"