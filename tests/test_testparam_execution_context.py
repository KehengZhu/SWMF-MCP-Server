from __future__ import annotations

from pathlib import Path

from swmf_mcp_server.tools.param import run_testparam


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
    (root / "PARAM.XML").write_text("<param/>\n", encoding="utf-8")

    run_dir = root / "runs" / "demo"
    run_dir.mkdir(parents=True)
    return root, run_dir


def test_run_testparam_uses_swmf_root_as_cwd(monkeypatch, tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    param_path = run_dir / "PARAM.in"
    param_path.write_text("#END\n", encoding="utf-8")

    captured: dict[str, object] = {}

    def fake_run(cmd, cwd, capture_output, text, check):
        captured["cmd"] = cmd
        captured["cwd"] = cwd
        return _DummyResult(returncode=0)

    monkeypatch.setattr("swmf_mcp_server.tools.param.subprocess.run", fake_run)

    payload = run_testparam(
        param_path=str(param_path),
        swmf_root_resolved=str(root),
        nproc=4,
        run_dir=str(run_dir),
    )

    assert payload["ok"] is True
    assert captured["cwd"] == str(root.resolve())
    assert captured["cwd"] != str(run_dir.resolve())
    assert payload["execution_cwd"] == str(root.resolve())


def test_run_testparam_launch_context_failure_classification(monkeypatch, tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    param_path = run_dir / "PARAM.in"
    param_path.write_text("#END\n", encoding="utf-8")

    stderr = "TestParam_ERROR: could not find Config.pl\n"

    def fake_run(cmd, cwd, capture_output, text, check):
        return _DummyResult(returncode=2, stderr=stderr)

    monkeypatch.setattr("swmf_mcp_server.tools.param.subprocess.run", fake_run)

    payload = run_testparam(
        param_path=str(param_path),
        swmf_root_resolved=str(root),
        nproc=2,
        run_dir=str(run_dir),
    )

    assert payload["ok"] is False
    assert payload["error_code"] == "TESTPARAM_LAUNCH_CONTEXT_INVALID"
    assert payload["execution_context_ok"] is False
    assert "execution context" in payload["quick_interpretation"].lower()
    assert any("config.pl" in line.lower() for line in payload["key_evidence_lines"])


def test_run_testparam_cache_avoids_repeat_execution(monkeypatch, tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    param_path = run_dir / "PARAM.in"
    param_path.write_text("#END\n", encoding="utf-8")

    calls = {"count": 0}

    def fake_run(cmd, cwd, capture_output, text, check):
        _ = (cmd, cwd, capture_output, text, check)
        calls["count"] += 1
        return _DummyResult(returncode=0)

    monkeypatch.setattr("swmf_mcp_server.tools.param.subprocess.run", fake_run)

    first = run_testparam(
        param_path=str(param_path),
        swmf_root_resolved=str(root),
        nproc=2,
        run_dir=str(run_dir),
    )
    second = run_testparam(
        param_path=str(param_path),
        swmf_root_resolved=str(root),
        nproc=2,
        run_dir=str(run_dir),
    )

    assert first["ok"] is True
    assert second["ok"] is True
    assert first["from_cache"] is False
    assert second["from_cache"] is True
    assert calls["count"] == 1
