from __future__ import annotations

import ast
from pathlib import Path

from swmf_mcp_server.tools.reference import swmf_get_component


def _make_fake_swmf_root(tmp_path: Path) -> Path:
    root = tmp_path / "SWMF"
    (root / "Scripts").mkdir(parents=True)
    (root / "GM" / "BATSRUS").mkdir(parents=True)
    (root / "share" / "IDL").mkdir(parents=True)
    (root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "PARAM.XML").write_text("<commandList/>\n", encoding="utf-8")
    (root / "GM" / "BATSRUS" / "PARAM.XML").write_text(
        "\n".join(
            [
                "<commandList>",
                '  <command name="#STOP" type="real" default="3600.0">',
                "  Defines simulation stop criteria.",
                "  </command>",
                "</commandList>",
            ]
        ),
        encoding="utf-8",
    )
    (root / "share" / "IDL" / "plot_test.pro").write_text(
        "pro plot_test\nprint, 'ok'\nend\n",
        encoding="utf-8",
    )
    return root


def test_reference_modules_do_not_import_catalog() -> None:
    package_root = Path(__file__).resolve().parents[1] / "src" / "swmf_mcp_server" / "reference"

    for path in sorted(package_root.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("swmf_mcp_server.catalog")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert not module.startswith("swmf_mcp_server.catalog")
                assert not (node.level >= 1 and module.startswith("catalog"))


def test_reference_entry_points_do_not_import_catalog() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    paths = [
        repo_root / "src" / "swmf_mcp_server" / "tools" / "reference.py",
        repo_root / "src" / "swmf_mcp_server" / "tools" / "param.py",
        repo_root / "src" / "swmf_mcp_server" / "tools" / "retrieve.py",
        repo_root / "src" / "swmf_mcp_server" / "resources" / "catalog_reference.py",
        repo_root / "src" / "swmf_mcp_server" / "resources" / "examples.py",
        repo_root / "src" / "swmf_mcp_server" / "resources" / "idl_reference.py",
        repo_root / "src" / "swmf_mcp_server" / "resources" / "param_schema.py",
    ]

    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert not alias.name.startswith("swmf_mcp_server.catalog")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                assert not module.startswith("swmf_mcp_server.catalog")
                assert not (node.level >= 1 and module.startswith("catalog"))


def test_lookup_component_uses_reference_service(tmp_path: Path) -> None:
    root = _make_fake_swmf_root(tmp_path)

    result = swmf_get_component(component="GM", swmf_root=str(root))

    assert result["ok"] is True
    assert result["component"] == "GM"
    assert result["versions"] == ["BATSRUS"]
    assert result["source_kind"] == "component PARAM.XML"