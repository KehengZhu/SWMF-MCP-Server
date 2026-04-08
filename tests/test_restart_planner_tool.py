from __future__ import annotations

from pathlib import Path

from swmf_mcp_server import server


def _make_fake_swmf_root(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "SWMF"
    (root / "Scripts").mkdir(parents=True)
    (root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "PARAM.XML").write_text("<param/>\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")

    run_dir = root / "run_demo"
    run_dir.mkdir(parents=True)
    (run_dir / "Restart.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (run_dir / "PARAM.in").write_text("#END\n", encoding="utf-8")
    (run_dir / "RESULTS" / "RESTART").mkdir(parents=True)
    return root, run_dir


def test_plan_restart_from_background_slurm_preview(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    (run_dir / "job.long").write_text("#!/bin/bash\n#SBATCH -N 2\n", encoding="utf-8")

    result = server.swmf_plan_restart_from_background(
        run_dir=str(run_dir),
        swmf_root=str(root),
        background_results_dir="RESULTS",
        restart_subdir="RESTART",
        nproc=112,
        scheduler_hint="slurm",
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert result["requires_manual_execution"] is True
    assert result["scheduler_resolved"] == "slurm"
    assert result["restart_mode_effective"] in {"auto", "framework"}
    examples = result["optional_command_examples"]
    assert any(" -c " in cmd for cmd in examples["restart_check"])
    assert any("Restart.pl" in cmd and "-i -v" in cmd for cmd in examples["restart_link"])
    assert any("TestParam.pl -n=112" in cmd for cmd in examples["validate"])
    assert examples["submit_preview"] == ["sbatch job.long"]
    assert result["workflow_guidance"]
    assert result["decision_branches"]
    assert "RESTART_MODE" in result["variable_guidance"]
    assert "restart_option_reference" in result
    assert "restart_time_unit_reference" in result
    assert "restart_component_mappings" in result
    assert "optional_command_examples" in result
    assert "authority_by_field" in result


def test_plan_restart_from_background_auto_scheduler_detects_pbs(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    (run_dir / "job.long").write_text("#!/bin/bash\n#PBS -N test\n", encoding="utf-8")

    result = server.swmf_plan_restart_from_background(
        run_dir=str(run_dir),
        swmf_root=str(root),
        background_results_dir="RESULTS",
        scheduler_hint="auto",
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert result["scheduler_resolved"] == "pbs"
    assert result["optional_command_examples"]["submit_preview"] == ["qsub job.long"]
    assert result["workflow_guidance"]


def test_plan_restart_from_background_missing_restart_source(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)

    result = server.swmf_plan_restart_from_background(
        run_dir=str(run_dir),
        swmf_root=str(root),
        background_results_dir="RESULTS",
        restart_subdir="MISSING",
    )

    assert result["ok"] is False
    assert result["hard_error"] is True
    assert result["error_code"] == "RESTART_SOURCE_NOT_FOUND"
    assert result["path_search_hints"]
    assert "path_search_roots" in result
    assert "path_search_candidates" in result


def test_plan_restart_from_background_missing_param_when_validation_requested(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    (run_dir / "PARAM.in").unlink()

    result = server.swmf_plan_restart_from_background(
        run_dir=str(run_dir),
        swmf_root=str(root),
        background_results_dir="RESULTS",
        include_validation_commands=True,
    )

    assert result["ok"] is False
    assert result["hard_error"] is True
    assert result["error_code"] == "PARAM_NOT_FOUND"
    assert result["requires_manual_execution"] is True
    assert result["path_search_hints"]
    assert "path_search_candidates" in result


def test_plan_restart_from_background_finds_nested_restart_script(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)
    (run_dir / "Restart.pl").unlink()
    nested_script = run_dir / "share" / "Scripts" / "Restart.pl"
    nested_script.parent.mkdir(parents=True)
    nested_script.write_text("#!/usr/bin/env perl\n", encoding="utf-8")

    result = server.swmf_plan_restart_from_background(
        run_dir=str(run_dir),
        swmf_root=str(root),
        background_results_dir="RESULTS",
        include_submit_preview=False,
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert str(nested_script.resolve()) in result["source_paths"]
    assert any(str(nested_script.resolve()) in cmd for cmd in result["optional_command_examples"]["restart_link"])


def test_plan_restart_from_background_restart_mode_and_warn_only_flags(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root(tmp_path)

    result = server.swmf_plan_restart_from_background(
        run_dir=str(run_dir),
        swmf_root=str(root),
        background_results_dir="RESULTS",
        restart_mode="framework",
        warn_only=True,
        include_submit_preview=False,
        include_validation_commands=False,
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert result["restart_mode_effective"] == "framework"
    link_cmd = result["optional_command_examples"]["restart_link"][0]
    assert "-m=framework" in link_cmd
    assert "-W" in link_cmd
    assert result["variable_guidance"]["WARN_ONLY"]["selected"] is True
