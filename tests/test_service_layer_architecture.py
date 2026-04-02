from __future__ import annotations

from pathlib import Path

from swmf_mcp_server.catalog.catalog_service import CatalogService
from swmf_mcp_server.core.swmf_root import resolve_swmf_root
from swmf_mcp_server.tools.build_run import detect_setup_commands
from swmf_mcp_server.tools.param import explain_param, run_testparam, validate_param


def _make_fake_swmf_root(tmp_path: Path) -> Path:
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
                "</commandList>",
            ]
        ),
        encoding="utf-8",
    )
    return root


def test_explain_service_prefers_authoritative_when_catalog_available(tmp_path: Path) -> None:
    root = _make_fake_swmf_root(tmp_path)
    catalog = CatalogService().get_catalog(str(root), force_refresh=True)

    result = explain_param(name="#STOP", catalog=catalog)

    assert result["found"] is True
    assert result["authority"] == "authoritative"
    assert result["source_paths"]


def test_validation_service_is_lightweight_only(tmp_path: Path) -> None:
    _ = _make_fake_swmf_root(tmp_path)
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

    result = validate_param(param_text=param_text)

    assert result["ok"] is True
    assert result["validation_mode"] == "lightweight_parser_only"
    assert result["authoritative_next_tool"] == "swmf_run_testparam"
    assert result["requires_authoritative_validation"] is True


def test_testparam_service_uses_authoritative_script(monkeypatch, tmp_path: Path) -> None:
    root = _make_fake_swmf_root(tmp_path)
    run_dir = tmp_path / "runs" / "demo"
    run_dir.mkdir(parents=True)
    param_path = run_dir / "PARAM.in"
    param_path.write_text("#END\n", encoding="utf-8")

    class DummyResult:
        returncode = 0
        stdout = ""
        stderr = ""

    def fake_run(*args, **kwargs):
        return DummyResult()

    monkeypatch.setattr("swmf_mcp_server.tools.param.subprocess.run", fake_run)

    payload = run_testparam(
        param_path=str(param_path),
        swmf_root_resolved=str(root),
        nproc=2,
        run_dir=str(run_dir),
    )

    assert payload["ok"] is True
    assert payload["authoritative"] is True
    assert payload["tool"] == "Scripts/TestParam.pl"
    assert payload["source_kind"] == "TestParam.pl"


def test_run_service_detect_setup_commands_whitelist() -> None:
    result = detect_setup_commands(
        param_text="\n".join(
            [
                "! Config.pl -v=Empty,SC/BATSRUS",
                "! make -j8",
                "! rm -rf /tmp/not_allowed",
            ]
        )
    )

    assert result["ok"] is True
    assert result["found"] is True
    assert "./Config.pl -v=Empty,SC/BATSRUS" in result["commands"]
    assert "make -j8" in result["commands"]
    assert result["authority"] == "derived"


def test_discovery_detects_repo_symlink_candidate(tmp_path: Path) -> None:
    root = _make_fake_swmf_root(tmp_path)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "linked_swmf").symlink_to(root)

    run_dir = workspace / "runs" / "case1"
    run_dir.mkdir(parents=True)

    resolved = resolve_swmf_root(run_dir=str(run_dir))
    assert resolved.ok is True
    assert resolved.swmf_root_resolved == str(root.resolve())
