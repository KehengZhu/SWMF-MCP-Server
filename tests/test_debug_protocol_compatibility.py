from __future__ import annotations

from pathlib import Path

from swmf_mcp_server import server


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
    payload = server.swmf_diagnose_error(
        error_text="TestParam_ERROR: could not find Config.pl while validating PARAM.in",
        source_hint="testparam",
    )

    assert payload["ok"] is True
    assert payload["detected_domain"] == "testparam"
    assert payload["root_causes"]
    assert payload["protocol_version"] == "swmf-debug/1.0"
    assert payload["protocol_state"] == "classification"
    assert payload["legacy_contract"]["policy"] == "additive_protocol_fields_first"


def test_diagnose_param_has_legacy_fields_plus_protocol_fields(tmp_path: Path) -> None:
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

    payload = server.swmf_diagnose_param(
        param_path=str(param_path),
        swmf_root=str(root),
        run_dir=str(run_dir),
        nproc=1,
    )

    assert payload["ok"] is True
    assert "root_causes" in payload
    assert "authoritative_result" in payload
    assert payload["protocol_version"] == "swmf-debug/1.0"
    assert payload["protocol_state"] == "normalization"
    assert payload["legacy_contract"]["status"] == "active"
