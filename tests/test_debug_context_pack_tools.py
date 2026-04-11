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


def test_collect_param_context_extracts_sessions_and_component_map(tmp_path: Path) -> None:
    _, run_dir = _make_fake_swmf_root(tmp_path)
    (run_dir / "INCLUDE_A.in").write_text("#END\n", encoding="utf-8")

    param_path = run_dir / "PARAM.in"
    param_path.write_text(
        "\n".join(
            [
                "#INCLUDE",
                "INCLUDE_A.in",
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

    payload = server.swmf_collect_param_context(param_path=str(param_path), run_dir=str(run_dir), nproc=4)

    assert payload["ok"] is True
    assert payload["session_count"] == 1
    assert payload["component_map_rows"]
    assert payload["protocol_version"] == "swmf-debug/1.0"
    assert payload["failure_family"] == "input_schema"


def test_resolve_param_includes_reports_missing_file(tmp_path: Path) -> None:
    _, run_dir = _make_fake_swmf_root(tmp_path)

    payload = server.swmf_resolve_param_includes(
        param_text="#INCLUDE\nmissing_include.in\n#END\n",
        run_dir=str(run_dir),
    )

    assert payload["ok"] is False
    assert payload["missing_include_paths"]
    assert payload["protocol_state"] == "normalization"


def test_extract_first_error_and_stacktrace_from_text() -> None:
    log_text = "\n".join(
        [
            "INFO startup",
            "ERROR: failed to initialize module",
            "Traceback (most recent call last):",
            "  File 'x.py', line 2, in <module>",
            "RuntimeError: boom",
        ]
    )

    first_error = server.swmf_extract_first_error(log_text=log_text)
    stacktrace = server.swmf_extract_stacktrace(log_text=log_text)

    assert first_error["ok"] is True
    assert first_error["first_error"]["line_number"] == 2
    assert stacktrace["ok"] is True
    assert stacktrace["stacktrace_lines"]


def test_compare_run_artifacts_file_diff(tmp_path: Path) -> None:
    left = tmp_path / "left.out"
    right = tmp_path / "right.out"
    left.write_text("a\nb\nc\n", encoding="utf-8")
    right.write_text("a\nb\nd\n", encoding="utf-8")

    payload = server.swmf_compare_run_artifacts(reference_path=str(left), candidate_path=str(right))

    assert payload["ok"] is True
    assert payload["comparison_type"] == "file"
    assert payload["changed"] is True
    assert payload["protocol_state"] == "validation"
