from __future__ import annotations

from pathlib import Path

from swmf_mcp_server import server


class _DummyResult:
    def __init__(self, returncode: int, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _make_fake_swmf_root(tmp_path: Path) -> tuple[Path, Path]:
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

    run_dir = root / "runs" / "demo"
    run_dir.mkdir(parents=True)
    return root, run_dir


def test_swmf_diagnose_param_single_call_authoritative(tmp_path: Path) -> None:
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
        ),
        encoding="utf-8",
    )

    payload = server.swmf_diagnose_param(
        param_path=str(param_path),
        swmf_root=str(root),
        run_dir=str(run_dir),
        nproc=1,
    )

    assert payload["ok"] is True
    assert "summary" in payload
    assert "root_causes" in payload
    assert "fastest_likely_fix" in payload
    assert "authoritative_result" in payload
    assert "recommended_commands" in payload
    assert "recommended_next_step" in payload
    assert "authority_by_field" in payload
    assert payload["authoritative_result"]["executed"] is True


def test_swmf_diagnose_param_fallback_nproc_runs_authoritative(tmp_path: Path) -> None:
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
        ),
        encoding="utf-8",
    )

    payload = server.swmf_diagnose_param(
        param_path=str(param_path),
        swmf_root=str(root),
        run_dir=str(run_dir),
        nproc=None,
        job_script_path=None,
    )

    assert payload["ok"] is True
    assert payload["preflight"]["nproc_source_for_authoritative"] in {"fast_default", "diagnostic_fallback", "job_script_inference"}
    assert payload["authoritative_result"]["executed"] is True


def test_swmf_diagnose_param_requires_input(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)

    payload = server.swmf_diagnose_param(
        param_path=None,
        param_text=None,
        swmf_root=str(root),
        run_dir=str(run_dir),
    )

    assert payload["ok"] is False
    assert payload["error_code"] == "PARAM_INPUT_MISSING"


def test_swmf_diagnose_param_prioritizes_launch_context_failure(monkeypatch, tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    param_path = run_dir / "PARAM.in"
    param_path.write_text(
        "\n".join(
            [
                "#TIMEACCURATE",
                "T DoTimeAccurate",
                "#COMPONENTMAP",
                "SC 0 -1 1",
                "missing_input.dat NameMagnetogramFile",
                "#STOP",
                "3600.0 tSimulationMax",
                "-1 MaxIteration",
                "#END",
            ]
        ),
        encoding="utf-8",
    )

    def fake_run(cmd, cwd, capture_output, text, check):
        _ = (cmd, cwd, capture_output, text, check)
        return _DummyResult(returncode=2, stderr="TestParam_ERROR: could not find Config.pl")

    monkeypatch.setattr("swmf_mcp_server.services.testparam_service.subprocess.run", fake_run)

    payload = server.swmf_diagnose_param(
        param_path=str(param_path),
        swmf_root=str(root),
        run_dir=str(run_dir),
        nproc=2,
    )

    assert payload["ok"] is True
    assert payload["root_causes"][0]["code"] == "TESTPARAM_LAUNCH_CONTEXT_INVALID"
    assert all(item["code"] != "MISSING_EXTERNAL_INPUTS" for item in payload["root_causes"][1:])
    assert payload["authoritative_result"]["error_code"] == "TESTPARAM_LAUNCH_CONTEXT_INVALID"


def test_swmf_diagnose_param_explicit_context_regression(monkeypatch, tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    param_path = run_dir / "PARAM.in"
    param_path.write_text("#STOP\n3600.0 tSimulationMax\n-1 MaxIteration\n#END\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_run(cmd, cwd, capture_output, text, check):
        captured["cwd"] = cwd
        _ = (cmd, capture_output, text, check)
        return _DummyResult(returncode=0, stdout="")

    monkeypatch.setattr("swmf_mcp_server.services.testparam_service.subprocess.run", fake_run)

    payload = server.swmf_diagnose_param(
        param_path=str(param_path.resolve()),
        swmf_root=str(root.resolve()),
        run_dir=str(run_dir.resolve()),
        nproc=4,
    )

    assert payload["ok"] is True
    assert payload["authoritative_result"]["executed"] is True
    assert payload["authoritative_result"]["ok"] is True
    assert captured["cwd"] == str(root.resolve())
