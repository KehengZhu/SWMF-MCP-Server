from __future__ import annotations

from pathlib import Path

import pytest

from swmf_mcp_server import server
from swmf_mcp_server.swmf_root import resolve_swmf_root


@pytest.fixture()
def fake_swmf_root(tmp_path: Path) -> Path:
    root = tmp_path / "SWMF"
    (root / "Scripts").mkdir(parents=True)
    (root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")

    (root / "PARAM.XML").write_text(
        "\n".join(
            [
                "<commandList>",
                '  <command name="#STOP" type="real" default="3600.0" min="0" max="100000">',
                "  Defines simulation stop criteria.",
                "  </command>",
                '  <command name="#TIMEACCURATE" type="logical" default="T" />',
                "</commandList>",
            ]
        ),
        encoding="utf-8",
    )

    (root / "GM" / "BATSRUS").mkdir(parents=True)
    (root / "GM" / "BATSRUS" / "PARAM.XML").write_text(
        "\n".join(
            [
                "<commandList>",
                '  <command name="#TIMESTEP" type="real" default="0.5" />',
                "</commandList>",
            ]
        ),
        encoding="utf-8",
    )

    (root / "SC" / "BATSRUS").mkdir(parents=True)
    (root / "SC" / "BATSRUS" / "PARAM.XML").write_text(
        "\n".join(
            [
                "<commandList>",
                '  <command name="#MAGNETOGRAM" type="string" />',
                "</commandList>",
            ]
        ),
        encoding="utf-8",
    )

    (root / "Param").mkdir(parents=True)
    (root / "Param" / "PARAM.in.test.sc").write_text(
        "\n".join(
            [
                "#TIMEACCURATE",
                "T DoTimeAccurate",
                "#STOP",
                "1000 tSimulationMax",
                "#END",
            ]
        ),
        encoding="utf-8",
    )

    return root


def test_resolve_swmf_root_via_symlink_heuristic(tmp_path: Path, fake_swmf_root: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "SWMF").symlink_to(fake_swmf_root)

    run_dir = workspace / "runs" / "demo"
    run_dir.mkdir(parents=True)

    resolved = resolve_swmf_root(run_dir=str(run_dir))
    assert resolved.ok is True
    assert resolved.swmf_root_resolved == str(fake_swmf_root.resolve())


def test_explain_param_prefers_authoritative_xml(fake_swmf_root: Path) -> None:
    result = server.swmf_explain_param(
        name="#STOP",
        swmf_root=str(fake_swmf_root),
        force_refresh=True,
    )

    assert result["found"] is True
    assert result["authority"] == "authoritative"
    assert "PARAM.XML" in result["source_kinds"]
    assert any(str(fake_swmf_root / "PARAM.XML") in item for item in result["source_paths"])
    assert "default" in result["defaults"]


def test_list_components_and_versions_from_component_xml(fake_swmf_root: Path) -> None:
    result = server.swmf_list_available_components(
        swmf_root=str(fake_swmf_root),
        force_refresh=True,
    )

    assert result["ok"] is True
    components = {item["component"]: item["versions"] for item in result["components"]}
    assert "GM" in components
    assert "BATSRUS" in components["GM"]


def test_trace_param_command_includes_definition_and_examples(fake_swmf_root: Path) -> None:
    result = server.swmf_trace_param_command(
        name="#TIMEACCURATE",
        swmf_root=str(fake_swmf_root),
        force_refresh=True,
    )

    assert result["ok"] is True
    assert result["defined_in"]
    assert result["example_usage_files"]


def test_validate_param_classifies_unresolved_references(fake_swmf_root: Path) -> None:
    param_text = "\n".join(
        [
            "#TIMEACCURATE",
            "T DoTimeAccurate",
            "#COMPONENTMAP",
            "SC 0 -1 1",
            "missing_input.dat NameMagnetogramFile",
            "#END",
        ]
    )
    result = server.swmf_validate_param(
        param_text=param_text,
        swmf_root=str(fake_swmf_root),
    )

    assert result["ok"] is True
    assert result["requires_authoritative_validation"] is True
    assert result["authoritative_next_tool"] == "swmf_run_testparam"
    assert result["syntax_or_structure_errors"]
    assert any(item.endswith("missing_input.dat") for item in result["unresolved_references"])
