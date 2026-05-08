"""Phase 1 acceptance tests for the run-replication scaffolding.

Covers:

* `inspect_artifact(artifact_type="jobscript")` parses SLURM and PBS scripts.
* `inspect_artifact(artifact_type="param", check_rules=True)` flags a synthetic broken
  PARAM with `severity=block`.
* `compare_artifacts(comparison_type="run_dir")` returns a `param_diff` block when both
  sides have a PARAM.in.
* No advice fields ("recommended_*", "suggested_*", "next_tool") leak from the new MCP
  outputs.
* Skill-layout files for the new entry/support skills exist and avoid advice language.
* Rules-directory skeleton is present.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _import_tool(name: str) -> Any:
    import importlib

    return importlib.import_module(f"swmf_mcp_server.tools.{name}")


_ADVICE_SUBSTRINGS = (
    "recommended_next_tool",
    "recommended_workflow",
    "suggested_steps",
    "best_workflow",
    "you should now",
)


def _assert_no_advice_leak(payload: Any) -> None:
    """Walk the payload and assert no advice-shaped fields are present."""
    if isinstance(payload, dict):
        for key, value in payload.items():
            assert not any(s in key for s in ("recommended_next", "suggested_steps", "best_workflow")), (
                f"Advice field leaked: {key!r}"
            )
            _assert_no_advice_leak(value)
    elif isinstance(payload, list):
        for item in payload:
            _assert_no_advice_leak(item)
    elif isinstance(payload, str):
        for needle in _ADVICE_SUBSTRINGS:
            assert needle not in payload, f"Advice substring leaked: {needle!r} in {payload[:120]}"


# ─────────────────────────────────────────────────────────────────────────────
# Jobscript inspection
# ─────────────────────────────────────────────────────────────────────────────


class TestJobscriptInspection:
    def _call(self, path: str) -> dict[str, Any]:
        mod = _import_tool("inspect_artifact")
        return mod.inspect_artifact(
            artifact_type="jobscript",
            path=path,
            swmf_root=str(_repo_root()),
        )

    def test_slurm_jobscript_parses(self, tmp_path: Path) -> None:
        script = tmp_path / "job.frontera"
        script.write_text(
            "#!/bin/bash\n"
            "#SBATCH -J amap01\n"
            "#SBATCH -N 30\n"
            "#SBATCH --tasks-per-node 56\n"
            "#SBATCH -t 8:00:00\n"
            "ibrun -n 1 ./PostProc.pl >& PostProc.log &\n"
            "ibrun -o 56 -n $(( (SLURM_NNODES - 1 ) *56 )) ./SWMF.exe > runlog\n",
            encoding="utf-8",
        )
        result = self._call(str(script))
        assert result["ok"] is True
        layout = next(f for f in result["findings"] if f["kind"] == "jobscript_layout")
        invocations = next(f for f in result["findings"] if f["kind"] == "executable_invocations")
        assert layout["scheduler"] == "slurm"
        assert layout["nodes"] == 30
        assert layout["tasks_per_node"] == 56
        assert layout["total_ranks"] == 30 * 56
        assert layout["walltime"] == "8:00:00"
        assert invocations["swmf_invoked"] is True
        assert invocations["postproc_present"] is True
        assert any(
            (inv.get("executable") or "").endswith("SWMF.exe")
            for inv in invocations["executable_invocations"]
        )
        _assert_no_advice_leak(result)

    def test_pbs_jobscript_parses(self, tmp_path: Path) -> None:
        script = tmp_path / "job.pfe"
        script.write_text(
            "#!/bin/csh\n"
            "#PBS -N amap01\n"
            "#PBS -l select=40:ncpus=28:model=bro\n"
            "#PBS -l walltime=8:00:00\n"
            "mpiexec ./FDIPS.exe > FDIPS.log\n"
            "mpiexec ./SWMF.exe > runlog\n",
            encoding="utf-8",
        )
        result = self._call(str(script))
        assert result["ok"] is True
        layout = next(f for f in result["findings"] if f["kind"] == "jobscript_layout")
        invocations = next(f for f in result["findings"] if f["kind"] == "executable_invocations")
        assert layout["scheduler"] == "pbs"
        assert layout["nodes"] == 40
        assert layout["tasks_per_node"] == 28
        assert layout["walltime"] == "8:00:00"
        assert invocations["fdips_invoked"] is True
        assert invocations["swmf_invoked"] is True
        _assert_no_advice_leak(result)


# ─────────────────────────────────────────────────────────────────────────────
# PARAM rule evaluation
# ─────────────────────────────────────────────────────────────────────────────


_BROKEN_PARAM = """\
#DESCRIPTION
synthetic broken case

#TIMEACCURATE
F                       IsTimeAccurate

#BEGIN_COMP SC
#CME
GL                      TypeCme
T                       UseCme
33.0                    LongitudeCme
26.0                    LatitudeCme
1276                    uCme
#END_COMP SC

#STOP
-1                      MaxIter
3600.0                  TimeMax

#END
"""


class TestCheckRules:
    def _call(self, path: str, check_rules: bool) -> dict[str, Any]:
        mod = _import_tool("inspect_artifact")
        return mod.inspect_artifact(
            artifact_type="param",
            path=path,
            check_rules=check_rules,
            swmf_root=str(_repo_root()),
        )

    def test_signature_has_check_rules(self) -> None:
        import inspect as _inspect

        mod = _import_tool("inspect_artifact")
        sig = _inspect.signature(mod.inspect_artifact)
        assert "check_rules" in sig.parameters

    def test_check_rules_default_false_does_not_attach_rule_findings(self, tmp_path: Path) -> None:
        param_path = tmp_path / "PARAM.in"
        param_path.write_text(_BROKEN_PARAM, encoding="utf-8")
        result = self._call(str(param_path), check_rules=False)
        assert all(f["kind"] != "rule_violations" for f in result["findings"])

    def test_check_rules_blocks_cme_without_starttime(self, tmp_path: Path) -> None:
        param_path = tmp_path / "PARAM.in"
        param_path.write_text(_BROKEN_PARAM, encoding="utf-8")
        result = self._call(str(param_path), check_rules=True)
        rule_finding = next(f for f in result["findings"] if f["kind"] == "rule_violations")
        summary = rule_finding["rule_check_summary"]
        assert summary["block"] >= 1
        block_ids = {v["rule_id"] for v in rule_finding["rule_violations"] if v["severity"] == "block"}
        assert "cme_requires_starttime" in block_ids
        assert "cme_requires_timeaccurate" in block_ids
        _assert_no_advice_leak(result)

    def test_check_rules_clean_on_real_prior_run_param(self) -> None:
        prior = (
            _repo_root().parent / "SWMFSOLAR" / "Run_Max_RP_CME3" / "run01" / "PARAM.in"
        )
        if not prior.is_file():
            pytest.skip(f"Prior run PARAM not present at {prior}")
        result = self._call(str(prior), check_rules=True)
        rule_finding = next(f for f in result["findings"] if f["kind"] == "rule_violations")
        summary = rule_finding["rule_check_summary"]
        assert summary["block"] == 0


# ─────────────────────────────────────────────────────────────────────────────
# compare_artifacts(run_dir) param_diff extension
# ─────────────────────────────────────────────────────────────────────────────


class TestRunDirParamDiff:
    def _call(self, left: str, right: str) -> dict[str, Any]:
        mod = _import_tool("compare_artifacts")
        return mod.compare_artifacts(
            left=left,
            right=right,
            comparison_type="run_dir",
            swmf_root=str(_repo_root()),
        )

    def test_param_diff_present_when_both_sides_have_param(self, tmp_path: Path) -> None:
        left = tmp_path / "left"
        right = tmp_path / "right"
        left.mkdir()
        right.mkdir()
        (left / "PARAM.in").write_text(
            "#DESCRIPTION\nbaseline\n\n#TIMEACCURATE\nF\tIsTimeAccurate\n\n#STOP\n-1\tMaxIter\n100.0\tTimeMax\n\n#END\n",
            encoding="utf-8",
        )
        (right / "PARAM.in").write_text(
            "#DESCRIPTION\nmodified\n\n#TIMEACCURATE\nT\tIsTimeAccurate\n\n#STOP\n-1\tMaxIter\n200.0\tTimeMax\n\n#END\n",
            encoding="utf-8",
        )
        result = self._call(str(left), str(right))
        assert result["ok"] is True
        param_entry = next(d for d in result["differences"] if d["kind"] == "param_diff")
        assert param_entry["param_changed"] is True
        assert param_entry["entries"], "expected entries to record diff"
        _assert_no_advice_leak(result)

    def test_param_diff_absent_when_one_side_missing_param(self, tmp_path: Path) -> None:
        left = tmp_path / "left"
        right = tmp_path / "right"
        left.mkdir()
        right.mkdir()
        (left / "PARAM.in").write_text("#DESCRIPTION\nbaseline\n#END\n", encoding="utf-8")
        (right / "other.txt").write_text("placeholder\n", encoding="utf-8")
        result = self._call(str(left), str(right))
        assert all(d["kind"] != "param_diff" for d in result["differences"])


# ─────────────────────────────────────────────────────────────────────────────
# Skill files and rules directory
# ─────────────────────────────────────────────────────────────────────────────


def _skill_path(*parts: str) -> Path:
    return _repo_root() / "src" / "agent_assets" / "skills" / Path(*parts)


def test_swmf_replicate_skill_exists() -> None:
    skill = _skill_path("swmf-replicate", "SKILL.md")
    assert skill.is_file()
    text = skill.read_text(encoding="utf-8")
    for term in (
        "swmf-replicate",
        "intent",
        "Launch Gate",
        "authoring ladder",
        "swmf-jobscript",
    ):
        assert term in text


def test_swmf_jobscript_skill_exists() -> None:
    skill = _skill_path("support", "swmf-jobscript", "SKILL.md")
    assert skill.is_file()
    text = skill.read_text(encoding="utf-8")
    for term in ('artifact_type = "jobscript"', "scheduler", "Frontera", "Pleiades"):
        assert term in text


def test_phase1_support_stubs_exist() -> None:
    for name in ("swmf-magnetogram", "swmf-cme-setup", "swmf-validation", "swmf-swmfsolar"):
        assert _skill_path("support", name, "SKILL.md").is_file()


def test_rules_directory_skeleton_present() -> None:
    rules = _skill_path("support", "swmf-params", "rules")
    assert (rules / "physical_constraints.yaml").is_file()
    assert (rules / "numerical_practices.md").is_file()
    assert (rules / "case_recipes" / "awsom_cme_eruption.md").is_file()
    assert (rules / "templates" / "awsom_cme.yaml").is_file()
    assert (rules / "derivations" / "geometric.yaml").is_file()
    assert (rules / "defaults" / "ops_guards.yaml").is_file()
