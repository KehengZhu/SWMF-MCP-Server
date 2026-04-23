from __future__ import annotations

from pathlib import Path

from swmf_mcp_server.tools.debug_protocol import (
    extract_first_error,
    collect_param_context,
)


def _make_fake_swmf_root(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "SWMF"
    (root / "Scripts").mkdir(parents=True)
    (root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "PARAM.XML").write_text("<commandList/>\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")

    run_dir = root / "runs" / "demo"
    run_dir.mkdir(parents=True)
    return root, run_dir


def test_diagnose_error_has_legacy_fields_plus_protocol_fields() -> None:
    payload = extract_first_error(log_text="INFO startup\nERROR: failed to initialize module\n")

    assert payload["ok"] is True
    assert payload["protocol_version"] == "swmf-debug/1.0"
    assert payload["protocol_state"] == "normalization"
    assert payload["failure_family"] == "runtime_crash_stop"
    assert payload["legacy_contract"]["policy"] == "additive_protocol_fields_first"


def test_collect_param_context_has_legacy_fields_plus_protocol_fields(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    param_path = run_dir / "PARAM.in"
    param_path.write_text(
        "\n".join(
            [
                "#TIMEACCURATE",
                "T DoTimeAccurate",
                "#COMPONENTMAP",
                "SC 0 -1 1",
                "#STOP",
                "3600.0 tSimulationMax",
                "-1 MaxIteration",
                "#END",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    payload = collect_param_context(
        param_path=str(param_path),
        run_dir=str(run_dir),
        nproc=1,
    )

    assert payload["ok"] is True
    assert payload["session_count"] == 1
    assert payload["protocol_version"] == "swmf-debug/1.0"
    assert payload["protocol_state"] == "evidence_collection"
    assert payload["legacy_contract"]["status"] == "active"
