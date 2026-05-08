"""Phase 4 acceptance tests for swmf-replicate.

Covers:

* `inspect_artifact(artifact_type="run_dir")` detects multi-realization ensemble
  layout (`run01/`, `run02/`, ..., `run12/` siblings) and surfaces a
  `run_dir_ensemble` finding with realization_count, per-realization status, and
  aggregate counts.
* `inspect_artifact(artifact_type="log")` surfaces `cluster_failure_signatures`
  with a `recovery_family` per signature: walltime_exceeded, oom_killed,
  module_load_failure, license_failure, mpi_rank_signal, file_quota_exceeded,
  node_failure, signal_term. Clean logs do not surface false positives.
* Skills updated for Phase 4: swmf-replicate documents ensemble + restart +
  cluster-boundary recovery; swmf-swmfsolar documents rundir_realizations,
  Restart.pl, and sub_runs.py; swmf-debug adds the cluster_boundary failure
  family.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _import_tool(name: str) -> Any:
    import importlib

    return importlib.import_module(f"swmf_mcp_server.tools.{name}")


def _skill_path(*parts: str) -> Path:
    return _repo_root() / "src" / "agent_assets" / "skills" / Path(*parts)


def _build_realization_dir(parent: Path, idx: int, *,
                            success: bool = False,
                            killed: bool = False,
                            with_log: bool = False,
                            with_param: bool = True,
                            with_executable: bool = True) -> Path:
    name = f"run{idx:02d}"
    run_dir = parent / name
    run_dir.mkdir(parents=True, exist_ok=True)
    if with_param:
        (run_dir / "PARAM.in").write_text("#DESCRIPTION\nfixture\n#END\n", encoding="utf-8")
    if with_executable:
        (run_dir / "SWMF.exe").write_text("", encoding="utf-8")
    if success:
        (run_dir / "SWMF.SUCCESS").write_text("", encoding="utf-8")
    if killed:
        (run_dir / "SWMF.KILL").write_text("", encoding="utf-8")
    if with_log:
        (run_dir / "runlog").write_text(
            "Starting SWMF\nProgress: 100 steps, 1.0 s simulation time, 5.0 s CPU time\n",
            encoding="utf-8",
        )
    return run_dir


def _call_run_dir(path: str) -> dict[str, Any]:
    mod = _import_tool("inspect_artifact")
    return mod.inspect_artifact(
        artifact_type="run_dir",
        path=path,
        swmf_root=str(_repo_root()),
    )


def _call_log(path: str) -> dict[str, Any]:
    mod = _import_tool("inspect_artifact")
    return mod.inspect_artifact(
        artifact_type="log",
        path=path,
        swmf_root=str(_repo_root()),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Ensemble layout detection
# ─────────────────────────────────────────────────────────────────────────────


class TestEnsembleLayoutDetection:
    def test_full_12_realization_ensemble_with_mixed_status(self, tmp_path: Path) -> None:
        sim = tmp_path / "Run_Max_RP"
        sim.mkdir()
        # 8 completed, 1 killed, 1 in-progress, 1 prepared, 1 missing-executable.
        for idx in range(1, 9):
            _build_realization_dir(sim, idx, success=True, with_log=True)
        _build_realization_dir(sim, 9, killed=True, with_log=True)
        _build_realization_dir(sim, 10, with_log=True)
        _build_realization_dir(sim, 11)
        _build_realization_dir(sim, 12, with_executable=False)

        result = _call_run_dir(str(sim))
        ensemble = next(f for f in result["findings"] if f["kind"] == "run_dir_ensemble")
        assert ensemble["realization_count"] == 12
        assert ensemble["realization_indices"] == list(range(1, 13))
        agg = ensemble["aggregate"]
        assert agg["completed"] == 8
        assert agg["killed"] == 1
        assert agg["in_progress_or_crashed"] == 1
        assert agg["prepared"] == 1
        assert agg["missing_executable"] == 1
        assert agg["total"] == 12

        statuses = {r["index"]: r["status"] for r in ensemble["realizations"]}
        assert statuses[1] == "completed"
        assert statuses[9] == "killed"
        assert statuses[10] == "in_progress_or_crashed"
        assert statuses[11] == "prepared"
        assert statuses[12] == "missing_executable"

    def test_single_run_directory_emits_no_ensemble_finding(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run01"
        _build_realization_dir(tmp_path, 1, success=True, with_log=True)
        # Pointing at the single run_dir itself — no siblings.
        result = _call_run_dir(str(run_dir))
        kinds = {f["kind"] for f in result["findings"]}
        assert "run_dir_ensemble" not in kinds

    def test_two_realizations_meets_threshold(self, tmp_path: Path) -> None:
        sim = tmp_path / "Run_Min"
        sim.mkdir()
        _build_realization_dir(sim, 1, success=True, with_log=True)
        _build_realization_dir(sim, 2, success=True, with_log=True)
        result = _call_run_dir(str(sim))
        ensemble = next(f for f in result["findings"] if f["kind"] == "run_dir_ensemble")
        assert ensemble["realization_count"] == 2
        assert ensemble["aggregate"]["completed"] == 2

    def test_non_realization_subdirs_ignored(self, tmp_path: Path) -> None:
        sim = tmp_path / "Run_Mixed"
        sim.mkdir()
        _build_realization_dir(sim, 1, success=True)
        _build_realization_dir(sim, 2, success=True)
        # Distractor: not matching runNN pattern.
        (sim / "scratch").mkdir()
        (sim / "log_archive").mkdir()
        (sim / "run").mkdir()  # no numeric suffix
        result = _call_run_dir(str(sim))
        ensemble = next(f for f in result["findings"] if f["kind"] == "run_dir_ensemble")
        assert ensemble["realization_count"] == 2

    def test_three_digit_realization_indices(self, tmp_path: Path) -> None:
        sim = tmp_path / "Big"
        sim.mkdir()
        _build_realization_dir(sim, 100, success=True)
        _build_realization_dir(sim, 101, success=True)
        result = _call_run_dir(str(sim))
        ensemble = next(f for f in result["findings"] if f["kind"] == "run_dir_ensemble")
        assert ensemble["realization_count"] == 2
        assert ensemble["realization_indices"] == [100, 101]


# ─────────────────────────────────────────────────────────────────────────────
# Cluster-boundary failure signatures
# ─────────────────────────────────────────────────────────────────────────────


_SIGNATURE_FIXTURES: list[tuple[str, str, str]] = [
    (
        "walltime_exceeded",
        "resubmit_with_longer_walltime",
        "slurmstepd: error: *** JOB 12345 ON c123 CANCELLED AT 2024-04-15 DUE TO TIME LIMIT ***\n",
    ),
    (
        "oom_killed",
        "increase_memory_or_reduce_decomp",
        "[c456] OOM Killer invoked\nKilled (out of memory)\n",
    ),
    (
        "module_load_failure",
        "fix_module_environment",
        "Lmod has detected the following error: The following module(s) are unknown: 'intel/2018'\n",
    ),
    (
        "license_failure",
        "license_server_or_compiler_check",
        "Error: Unable to checkout license for 'ifort'. License server connection failed.\n",
    ),
    (
        "mpi_rank_signal",
        "investigate_failing_rank",
        "rank 47: Segmentation fault\nMPI_Abort called from rank 47.\n",
    ),
    (
        "file_quota_exceeded",
        "free_disk_or_change_workdir",
        "write error: Disk quota exceeded\n",
    ),
    (
        "node_failure",
        "resubmit_after_node_drained",
        "slurmd: error: NODE_FAIL — lost contact with node c789\n",
    ),
    (
        "signal_term",
        "scheduler_terminated_job",
        "Caught signal 15 (SIGTERM). Cleaning up...\n",
    ),
]


class TestClusterFailureSignatures:
    def test_each_signature_detected(self, tmp_path: Path) -> None:
        for sig_id, recovery, payload in _SIGNATURE_FIXTURES:
            log = tmp_path / f"{sig_id}.log"
            log.write_text(
                "Starting SWMF\n"
                + payload
                + "Job exited.\n",
                encoding="utf-8",
            )
            result = _call_log(str(log))
            finding = next(
                (f for f in result["findings"] if f["kind"] == "cluster_failure_signatures"),
                None,
            )
            assert finding is not None, f"signature '{sig_id}' was not detected"
            ids = {s["signature_id"] for s in finding["signatures"]}
            assert sig_id in ids, f"signature '{sig_id}' missing from {ids}"
            recovery_for_id = next(
                s["recovery_family"] for s in finding["signatures"]
                if s["signature_id"] == sig_id
            )
            assert recovery_for_id == recovery

    def test_clean_log_emits_no_signatures(self, tmp_path: Path) -> None:
        log = tmp_path / "clean.log"
        log.write_text(
            "Starting SWMF\n"
            "Progress: 100 steps, 1.0 s simulation time, 5.0 s CPU time\n"
            "Progress: 200 steps, 2.0 s simulation time, 10.0 s CPU time\n"
            "SWMF FINISHED.\n"
            "Finished Numerical Simulation\n"
            "SWMF.SUCCESS\n",
            encoding="utf-8",
        )
        result = _call_log(str(log))
        kinds = {f["kind"] for f in result["findings"]}
        assert "cluster_failure_signatures" not in kinds

    def test_multiple_signatures_co_occur(self, tmp_path: Path) -> None:
        # OOM kill that also triggered a SIGTERM cleanup — both should surface.
        log = tmp_path / "combo.log"
        log.write_text(
            "Starting SWMF\n"
            "Out Of Memory: Kill process 12345\n"
            "Caught signal 15 (SIGTERM). Cleaning up...\n",
            encoding="utf-8",
        )
        result = _call_log(str(log))
        finding = next(f for f in result["findings"] if f["kind"] == "cluster_failure_signatures")
        ids = {s["signature_id"] for s in finding["signatures"]}
        assert "oom_killed" in ids
        assert "signal_term" in ids


# ─────────────────────────────────────────────────────────────────────────────
# Skill content updates
# ─────────────────────────────────────────────────────────────────────────────


def test_replicate_skill_documents_ensemble_section() -> None:
    text = _skill_path("swmf-replicate", "SKILL.md").read_text(encoding="utf-8")
    assert "## Multi-realization ensembles" in text
    assert "run_dir_ensemble" in text
    assert "rundir_realizations" in text
    assert "check_postproc" in text
    assert "sub_runs.py" in text


def test_replicate_skill_documents_restart_workflow() -> None:
    text = _skill_path("swmf-replicate", "SKILL.md").read_text(encoding="utf-8")
    assert "## Restart workflow" in text
    assert "Restart.pl" in text
    assert "share/Scripts/Restart.pl" in text
    assert "restart_inventory" in text


def test_replicate_skill_documents_cluster_boundary_recovery() -> None:
    text = _skill_path("swmf-replicate", "SKILL.md").read_text(encoding="utf-8")
    assert "## Cluster-boundary recovery" in text
    for sig_id in (
        "walltime_exceeded",
        "oom_killed",
        "module_load_failure",
        "license_failure",
        "mpi_rank_signal",
        "file_quota_exceeded",
        "node_failure",
        "signal_term",
    ):
        assert sig_id in text, f"cluster signature '{sig_id}' missing from swmf-replicate"


def test_replicate_phase_scope_marks_phase4_current() -> None:
    text = _skill_path("swmf-replicate", "SKILL.md").read_text(encoding="utf-8")
    assert "Phase 4 (current)" in text


def test_swmfsolar_skill_documents_ensemble_and_restart() -> None:
    text = _skill_path("support", "swmf-swmfsolar", "SKILL.md").read_text(encoding="utf-8")
    assert "## Multi-realization ensemble" in text
    assert "rundir_realizations" in text
    assert "sub_runs.py" in text
    assert "## Restart workflow" in text
    assert "Restart.pl" in text


def test_debug_skill_lists_cluster_boundary_family() -> None:
    text = _skill_path("swmf-debug", "SKILL.md").read_text(encoding="utf-8")
    assert "cluster_boundary" in text
    assert "cluster_failure_signatures" in text
