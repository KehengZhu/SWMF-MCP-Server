"""Acceptance tests for the slim PARAM inspector contract.

Locks in the post-Phase-2 refactor (docs/run_replication_plan.md §5.3.1):

* `inspect_artifact(artifact_type="param")` emits structural primitives only.
* Semantic-summary findings (`session_commands`, `param_session_timeline`,
  `param_control_settings`, `param_saveplot_blocks`) are gone — the agent reads
  PARAM.in directly for intent.
* Rule evaluation, include/external-ref resolution, and compare integration are
  unaffected by the refactor.
* `inspect_artifact(artifact_type="run_dir")` continues to surface
  `run_dir_param_summary` and `component_output_artifacts` (those use an internal
  saveplot extraction; not the same path as the trimmed param inspector).
"""
from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any


def _import_tool(name: str):
    import importlib

    return importlib.import_module(f"swmf_mcp_server.tools.{name}")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


_PARAM_WITH_SAVEPLOT_AND_CONTROL = textwrap.dedent("""\
    #DESCRIPTION
    slim-inspector test fixture

    #COMPONENTMAP
    SC 0 -1 1     CompMap
    IH 0 -1 1     CompMap

    #TIMEACCURATE
    F             IsTimeAccurate

    #STARTTIME
    2023
    02
    24
    20
    29
    0
    0.0

    #SAVERESTART
    T             DoSaveRestart
    -1            DnSaveRestart
    3600.0        DtSaveRestart

    #BEGIN_COMP SC

    #SAVEPLOT
    1                  nPlotFile
    z=0 VAR idl        StringPlot
    -1                 DnSavePlot
    3600.0             DtSavePlot
    -1.0               DxSavePlot
    {MHD} bx by bz     NameVars
    {default}          NamePars

    #END_COMP SC

    #STOP
    1000          MaxIter
    -1.0          TimeMax

    #END
    """)


# ─────────────────────────────────────────────────────────────────────────────


_REMOVED_FINDING_KINDS = {
    "session_commands",
    "param_session_timeline",
    "param_control_settings",
    "param_saveplot_blocks",
}


def _call_param(path: str, **kwargs: Any) -> dict[str, Any]:
    mod = _import_tool("inspect_artifact")
    return mod.inspect_artifact(
        artifact_type="param",
        path=path,
        swmf_root=str(_repo_root()),
        **kwargs,
    )


class TestSlimParamInspectorEmitsStructuralOnly:
    def test_no_semantic_summary_findings(self, tmp_path: Path) -> None:
        param_path = tmp_path / "PARAM.in"
        param_path.write_text(_PARAM_WITH_SAVEPLOT_AND_CONTROL, encoding="utf-8")
        result = _call_param(str(param_path))
        kinds = {f["kind"] for f in result["findings"]}
        leaked = kinds & _REMOVED_FINDING_KINDS
        assert leaked == set(), f"slim contract violated; semantic findings present: {leaked}"

    def test_param_structure_present_with_typed_fields(self, tmp_path: Path) -> None:
        param_path = tmp_path / "PARAM.in"
        param_path.write_text(_PARAM_WITH_SAVEPLOT_AND_CONTROL, encoding="utf-8")
        result = _call_param(str(param_path))
        structure = next(f for f in result["findings"] if f["kind"] == "param_structure")
        assert structure["session_count"] == 1
        assert structure["required_components"] == ["SC", "IH"]
        assert structure["parser_errors"] == []
        assert structure["parser_warnings"] == []

    def test_component_map_present(self, tmp_path: Path) -> None:
        param_path = tmp_path / "PARAM.in"
        param_path.write_text(_PARAM_WITH_SAVEPLOT_AND_CONTROL, encoding="utf-8")
        result = _call_param(str(param_path))
        compmap = next(f for f in result["findings"] if f["kind"] == "component_map")
        assert compmap["components"] == ["SC", "IH"]
        # Two #COMPONENTMAP rows, each with proc0=0 / procend=-1 / stride=1.
        assert len(compmap["rows"]) == 2

    def test_external_references_or_includes_appear_only_when_present(self, tmp_path: Path) -> None:
        # Fixture has no #INCLUDE and no external refs; those findings should be absent.
        param_path = tmp_path / "PARAM.in"
        param_path.write_text(_PARAM_WITH_SAVEPLOT_AND_CONTROL, encoding="utf-8")
        result = _call_param(str(param_path))
        kinds = {f["kind"] for f in result["findings"]}
        assert "include_files" not in kinds
        assert "external_references" not in kinds

    def test_summary_redirects_to_direct_read(self, tmp_path: Path) -> None:
        param_path = tmp_path / "PARAM.in"
        param_path.write_text(_PARAM_WITH_SAVEPLOT_AND_CONTROL, encoding="utf-8")
        result = _call_param(str(param_path))
        summary = result["summary"].lower()
        assert "read the file directly" in summary

    def test_uncertainty_documents_slim_contract(self, tmp_path: Path) -> None:
        param_path = tmp_path / "PARAM.in"
        param_path.write_text(_PARAM_WITH_SAVEPLOT_AND_CONTROL, encoding="utf-8")
        result = _call_param(str(param_path))
        notes = " ".join(result["uncertainty"]["known_unknowns"]).lower()
        assert "structural primitives only" in notes
        assert "read param.in directly" in notes


class TestSlimRefactorPreservesRuleEval:
    def test_check_rules_still_attaches_violations(self, tmp_path: Path) -> None:
        broken = tmp_path / "broken.in"
        broken.write_text(
            "#DESCRIPTION\nbroken\n\n"
            "#TIMEACCURATE\nF\tIsTimeAccurate\n\n"
            "#BEGIN_COMP SC\n#CME\nGL\tTypeCme\nT\tUseCme\n#END_COMP SC\n\n"
            "#STOP\n-1\tMaxIter\n3600.0\tTimeMax\n\n#END\n",
            encoding="utf-8",
        )
        result = _call_param(str(broken), check_rules=True)
        rule_finding = next(f for f in result["findings"] if f["kind"] == "rule_violations")
        assert rule_finding["rule_check_summary"]["block"] >= 1


class TestSlimRefactorPreservesRunDirSavePlotMapping:
    """The run-dir inspector must still surface component_output_artifacts even though
    the param inspector no longer returns saveplot_blocks.
    """

    def test_component_output_artifacts_present(self, tmp_path: Path) -> None:
        run_dir = tmp_path / "run01"
        ih_dir = run_dir / "IH"
        ih_dir.mkdir(parents=True)
        (run_dir / "PARAM.in").write_text(_PARAM_WITH_SAVEPLOT_AND_CONTROL, encoding="utf-8")
        (ih_dir / "z=0_var_3_t0001.out").write_text("x y z bx by\n", encoding="utf-8")

        # Provide a fake SWMF root so resolution succeeds.
        swmf_root = tmp_path / "SWMF"
        (swmf_root / "Scripts").mkdir(parents=True)
        (swmf_root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        (swmf_root / "PARAM.XML").write_text("<param></param>\n", encoding="utf-8")
        (swmf_root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")

        mod = _import_tool("inspect_artifact")
        result = mod.inspect_artifact(
            artifact_type="run_dir",
            path=str(run_dir),
            question="animate IH z=0 .out snapshots",
            swmf_root=str(swmf_root),
        )
        kinds = {f["kind"] for f in result["findings"]}
        # Run-dir saveplot mapping is internal and unaffected by the param-inspector trim.
        assert "component_output_artifacts" in kinds


class TestSlimRefactorPreservesCompare:
    """compare_artifacts(comparison_type='run_dir') still emits a param_diff entry when
    both sides have a PARAM.in. The param_diff path uses parse_param_text directly,
    not the param inspector findings.
    """

    def test_param_diff_still_present(self, tmp_path: Path) -> None:
        left = tmp_path / "left"
        right = tmp_path / "right"
        left.mkdir()
        right.mkdir()
        (left / "PARAM.in").write_text(_PARAM_WITH_SAVEPLOT_AND_CONTROL, encoding="utf-8")
        (right / "PARAM.in").write_text(
            _PARAM_WITH_SAVEPLOT_AND_CONTROL.replace("F             IsTimeAccurate", "T             IsTimeAccurate"),
            encoding="utf-8",
        )
        mod = _import_tool("compare_artifacts")
        result = mod.compare_artifacts(
            left=str(left),
            right=str(right),
            comparison_type="run_dir",
            swmf_root=str(_repo_root()),
        )
        param_entry = next(d for d in result["differences"] if d["kind"] == "param_diff")
        assert param_entry["param_changed"] is True
