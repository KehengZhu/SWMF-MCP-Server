from __future__ import annotations

from pathlib import Path

from swmf_mcp_server import server


def test_swmf_diagnose_error_testparam_context() -> None:
    payload = server.swmf_diagnose_error(
        error_text="TestParam_ERROR: could not find Config.pl while validating PARAM.in",
        source_hint="testparam",
    )

    assert payload["ok"] is True
    assert payload["detected_domain"] == "testparam"
    assert payload["root_causes"][0]["code"] == "TESTPARAM_LAUNCH_CONTEXT_INVALID"
    assert any("SWMF_ROOT" in item for item in payload["possible_solutions"])
    assert "swmf_run_testparam" in payload["recommended_next_tools"]


def test_swmf_diagnose_error_build_compile_signature() -> None:
    payload = server.swmf_diagnose_error(
        error_text=(
            "Fatal Error: Cannot open module file 'ModKind.f90' for reading at (1)\n"
            "make: *** [foo.o] Error 1"
        )
    )

    assert payload["ok"] is True
    assert payload["detected_domain"] == "build_compile"
    assert any(cause["code"] == "FORTRAN_MODULE_NOT_FOUND" for cause in payload["root_causes"])


def test_swmf_diagnose_error_runtime_log_source_hint() -> None:
    payload = server.swmf_diagnose_error(
        error_text="CFL condition violated at iteration 245; dt too large",
        source_hint="runtime_log",
    )

    assert payload["ok"] is True
    assert payload["detected_domain"] == "runtime_log"
    assert payload["root_causes"][0]["code"] == "RUNTIME_STABILITY_CFL"


def test_swmf_diagnose_error_unknown_fallback() -> None:
    payload = server.swmf_diagnose_error(error_text="unexpected issue happened in workflow")

    assert payload["ok"] is True
    assert payload["root_causes"][0]["code"] == "UNCLASSIFIED_SWMF_ERROR"
    assert payload["detected_domain"] == "unknown"


def test_swmf_diagnose_error_source_hint_alias_compile() -> None:
    payload = server.swmf_diagnose_error(
        error_text="undefined reference to `foo_bar` during link stage",
        source_hint="compile",
    )

    assert payload["ok"] is True
    assert payload["source_hint_normalized"] == "build_compile"


def test_swmf_diagnose_error_includes_source_paths() -> None:
    payload = server.swmf_diagnose_error(
        error_text="restart file not found",
        source_hint="restart",
        param_path="run/PARAM.in",
        log_path="run/logfile.out",
    )

    assert payload["ok"] is True
    assert payload["detected_domain"] == "restart"
    assert payload["source_paths"] == ["run/PARAM.in", "run/logfile.out"]


def test_swmf_diagnose_error_missing_input() -> None:
    payload = server.swmf_diagnose_error(error_text="")

    assert payload["ok"] is False
    assert payload["error_code"] == "ERROR_TEXT_MISSING"


def test_swmf_diagnose_error_resolves_root_context(tmp_path: Path) -> None:
    root = tmp_path / "SWMF"
    (root / "Scripts").mkdir(parents=True)
    (root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "PARAM.XML").write_text("<commandList/>\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")

    payload = server.swmf_diagnose_error(
        error_text="TestParam failed",
        source_hint="testparam",
        swmf_root=str(root),
    )

    assert payload["ok"] is True
    assert payload["swmf_root_resolved"] == str(root.resolve())
