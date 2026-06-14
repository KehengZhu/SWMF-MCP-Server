"""Tests for the local `swmf` CLI surface (replacement for the MCP server)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from swmf_mcp_server import cli


_REPO = Path(__file__).resolve().parents[1]
_EXAMPLE_PARAM = (
    _REPO / "examples" / "CCMC_run_weihao" / "Weihao_Liu_011326_SH_1_PARAM.expand.start"
)


def _resolve_swmf_root() -> Path | None:
    env = os.environ.get("SWMF_ROOT")
    if env and Path(env).is_dir():
        return Path(env)
    link = _REPO / "SWMF"
    if link.exists():
        return link.resolve()
    return None


_SWMF_ROOT = _resolve_swmf_root()
_PARAM_XML = (_SWMF_ROOT / "SC" / "BATSRUS" / "PARAM.XML") if _SWMF_ROOT else None


def _run(args: list[str], capsys) -> tuple[int, dict]:
    code = cli.main(args)
    out = capsys.readouterr().out
    return code, json.loads(out)


# --------------------------------------------------------------------------- #
# Dispatch / argparse
# --------------------------------------------------------------------------- #
def test_cli_help_lists_all_subcommands(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for sub in ("get-context", "get-evidence", "inspect", "compare", "index"):
        assert sub in out


def test_cli_unknown_subcommand_is_rejected() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["frobnicate"])
    assert exc.value.code != 0


def test_cli_missing_required_arg_is_rejected() -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["get-context"])  # --question is required
    assert exc.value.code != 0


# --------------------------------------------------------------------------- #
# JSON contract + exit codes
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(not _EXAMPLE_PARAM.is_file(), reason="example PARAM not present")
def test_cli_inspect_emits_json_and_zero_exit(capsys) -> None:
    code, payload = _run(["inspect", "--type", "param", "--path", str(_EXAMPLE_PARAM)], capsys)
    assert code == 0
    assert payload["ok"] is True
    assert payload["artifact_type"] == "param"


def test_cli_inspect_missing_file_still_emits_structured_json(capsys) -> None:
    # The tool contract returns a parseable payload (not a crash) for a missing file.
    _code, payload = _run(["inspect", "--type", "param", "--path", "/no/such/file.in"], capsys)
    assert "ok" in payload


# --------------------------------------------------------------------------- #
# XML audit gate persists across SEPARATE CLI processes
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(
    _PARAM_XML is None or not _PARAM_XML.is_file(),
    reason="SC/BATSRUS/PARAM.XML not present; live-XML CLI audit test skipped.",
)
@pytest.mark.skipif(not _EXAMPLE_PARAM.is_file(), reason="example PARAM not present")
def test_cli_audit_gate_persists_across_processes(tmp_path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    # Process 1: record a commandgroup read under run_dir.
    subprocess.run(
        [
            sys.executable, "-m", "swmf_mcp_server.cli", "inspect",
            "--type", "xml", "--xml-scope", "commandgroup:SCHEME PARAMETERS",
            "--path", str(_PARAM_XML), "--run-dir", str(run_dir),
        ],
        cwd=_REPO, check=True, capture_output=True, text=True,
    )
    audit_file = run_dir / ".swmf_ai" / "audit.json"
    assert audit_file.is_file()
    assert "SC:SCHEME PARAMETERS" in audit_file.read_text(encoding="utf-8")

    # Process 2 (separate process): the param audit reads the recorded group back.
    result = subprocess.run(
        [
            sys.executable, "-m", "swmf_mcp_server.cli", "inspect",
            "--type", "param", "--path", str(_EXAMPLE_PARAM),
            "--check-xml-audit", "--run-dir", str(run_dir),
        ],
        cwd=_REPO, check=True, capture_output=True, text=True,
    )
    payload = json.loads(result.stdout)
    xml_audit = next(f for f in payload["findings"] if f["kind"] == "xml_audit")
    assert "SC:SCHEME PARAMETERS" in xml_audit["groups_read"]


def test_cli_audit_fresh_run_dir_is_isolated(tmp_path) -> None:
    from swmf_mcp_server.audit import get_audit_store

    assert get_audit_store().get_reads(str(tmp_path / "never-recorded")) == set()
