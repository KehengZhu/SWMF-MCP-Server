from __future__ import annotations

from pathlib import Path

from swmf_mcp_server import server


def _make_fake_swmf_root_with_postprocess_scripts(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "SWMF"
    scripts_dir = root / "share" / "Scripts"
    scripts_dir.mkdir(parents=True)
    (root / "Scripts").mkdir(parents=True)
    (root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "PARAM.XML").write_text("<param/>\n", encoding="utf-8")

    (scripts_dir / "Restart.pl").write_text(
        "\n".join(
            [
                "#!/usr/bin/env perl -s",
                "my $RestartOutFile = \"RESTART.out\";",
                "my $RestartInFile = \"RESTART.in\";",
                "my %RestartOutDir = (GM => \"GM/restartOUT\", SC => \"SC/restartOUT\");",
                "my %RestartInDir = (GM => \"GM/restartIN\", SC => \"SC/restartIN\");",
                "my %UnitSecond = (\"s\" => 1, \"h\" => 3600, \"date\" => -1);",
                "Usage:",
                "    Restart.pl [-o] [-i] [-c] [-v] [-W] [-t=UNIT] [-r=REPEAT] [-m=a|f|s] [DIR]",
                "    -o -output  Create restart tree from output directories but do not link.",
                "    -i -input   Link to existing restart tree.",
                "    -c -check   Check only mode.",
                "    -m=MODE     Mode selection.",
                "    -W -warn    Warning-only mode.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (scripts_dir / "PostProc.pl").write_text(
        "\n".join(
            [
                "#!/usr/bin/env perl -s",
                "my $StopFile = \"PostProc.STOP\";",
                "my $ParamIn = \"PARAM.in\";",
                "my $RunLog = \"runlog runlog_[0-9]*\";",
                "my %PlotDir = (GM => \"GM/IO2\", SC => \"SC/IO2\");",
                "Usage:",
                "    PostProc.pl [-h] [-v] [-c] [-g] [-r=REPEAT] [-s=STOP] [-rsync=TARGET] [DIR]",
                "    -c -cat     Concatenate log/satellite series files.",
                "    -g -gzip    Gzip large ASCII files.",
                "    -r=REPEAT   Repeat post processing every REPEAT seconds.",
                "    -s=STOP     Exit script after STOP days.",
                "    -rsync=TARGET  Copy processed plot files into another directory.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (scripts_dir / "Resubmit.pl").write_text(
        "\n".join(
            [
                "#!/usr/bin/env perl -s",
                "my $Success1 = \"SWMF.SUCCESS\";",
                "my $Success2 = \"BATSRUS.SUCCESS\";",
                "my $Done1 = \"SWMF.DONE\";",
                "my $Done2 = \"BATSRUS.DONE\";",
                "if($pbs){ $command = \"qsub $jobfile\"; }",
                "if($slurm){ $command = \"sbatch $jobfile\"; }",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (scripts_dir / "Preplot.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (scripts_dir / "convert2vtk.jl").write_text("# julia helper\n", encoding="utf-8")
    (scripts_dir / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")

    run_dir = root / "run_demo"
    run_dir.mkdir(parents=True)
    (run_dir / "job.long").write_text("#!/bin/bash\n#SBATCH -N 1\n", encoding="utf-8")

    return root, run_dir


def test_plan_postprocess_guidance_fields(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root_with_postprocess_scripts(tmp_path)

    result = server.swmf_plan_postprocess(
        run_dir=str(run_dir),
        swmf_root=str(root),
        repeat_seconds=300,
        stop_days=3,
        rsync_target="ME@HOST:results",
        include_concat=True,
        include_gzip=True,
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert result["workflow_guidance"]
    assert result["decision_branches"]
    assert "REPEAT_SECONDS" in result["variable_guidance"]
    assert result["postproc_option_reference"]
    assert result["postproc_plot_dir_mappings"]["GM"] == "GM/IO2"
    assert result["postproc_control_files"]["StopFile"] == "PostProc.STOP"
    assert "optional_command_examples" in result
    assert any("PostProc.pl" in path for path in result["source_paths"])


def test_plan_postprocess_rejects_repeat_with_output_dir(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root_with_postprocess_scripts(tmp_path)

    result = server.swmf_plan_postprocess(
        run_dir=str(run_dir),
        swmf_root=str(root),
        repeat_seconds=120,
        output_dir="OUTPUT/run1",
    )

    assert result["ok"] is False
    assert result["hard_error"] is True
    assert result["error_code"] == "INPUT_INVALID"


def test_plan_resubmit_guidance_fields(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root_with_postprocess_scripts(tmp_path)

    result = server.swmf_plan_resubmit(
        run_dir=str(run_dir),
        swmf_root=str(root),
        job_script="job.long",
        sleep_seconds=15,
        scheduler_hint="auto",
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert result["scheduler_resolved"] == "slurm"
    assert result["workflow_guidance"]
    assert result["decision_branches"]
    assert "JOB_SCRIPT" in result["variable_guidance"]
    assert result["resubmit_control_files"]["Success1"] == "SWMF.SUCCESS"
    assert result["resubmit_scheduler_branches"]
    assert "optional_command_examples" in result
    assert any("Resubmit.pl" in path for path in result["source_paths"])


def test_plan_resubmit_missing_job_script(tmp_path: Path) -> None:
    root, run_dir = _make_fake_swmf_root_with_postprocess_scripts(tmp_path)

    result = server.swmf_plan_resubmit(
        run_dir=str(run_dir),
        swmf_root=str(root),
        job_script="missing.job",
    )

    assert result["ok"] is False
    assert result["hard_error"] is True
    assert result["error_code"] == "JOB_SCRIPT_NOT_FOUND"
    assert result["path_search_hints"]
    assert "path_search_roots" in result
