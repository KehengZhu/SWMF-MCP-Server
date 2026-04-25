"""Phase 1 API surface tests.

Validates:
1. All four public API tools are importable and callable.
2. Each tool returns the required output contract fields.
3. Input validation (task_type/detail/mode/artifact_type normalization).
4. Legacy swmf_* callables and schema mappings are absent.
5. Schema document exists.
"""

from __future__ import annotations

import importlib
import inspect
import struct
from pathlib import Path
from typing import Any

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _tools_pkg() -> Any:
    return importlib.import_module("swmf_mcp_server.tools")


def _import_tool(name: str) -> Any:
    return importlib.import_module(f"swmf_mcp_server.tools.{name}")


def _assert_base_output_contract(result: dict[str, Any], tool_name: str) -> None:
    """Every Phase 1 tool must return these keys."""
    for field in ("ok", "summary", "evidence", "provenance", "uncertainty"):
        assert field in result, f"{tool_name}: missing '{field}' in output"
    assert isinstance(result["evidence"], list), f"{tool_name}: 'evidence' must be a list"
    assert "known_unknowns" in result["uncertainty"], (
        f"{tool_name}: 'uncertainty' must contain 'known_unknowns'"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1: get_context
# ─────────────────────────────────────────────────────────────────────────────

class TestGetContext:
    def _call(self, **kwargs: Any) -> dict[str, Any]:
        mod = _import_tool("get_context")
        # Provide a fake swmf_root so resolution succeeds in CI without SWMF installed.
        kwargs.setdefault("swmf_root", str(Path(__file__).parents[1]))
        return mod.get_context(**kwargs)

    def test_importable(self) -> None:
        mod = _import_tool("get_context")
        assert hasattr(mod, "get_context")
        assert hasattr(mod, "register")

    def test_signature_has_required_params(self) -> None:
        mod = _import_tool("get_context")
        sig = inspect.signature(mod.get_context)
        assert "question" in sig.parameters
        assert "scope" in sig.parameters
        assert "task_type" in sig.parameters
        assert "detail" in sig.parameters
        assert "swmf_root" in sig.parameters
        assert "run_dir" in sig.parameters

    def test_output_contract(self) -> None:
        result = self._call(question="How does GM couple to IE?", scope=["GM", "IE"])
        _assert_base_output_contract(result, "get_context")
        assert "entities" in result
        for key in ("components", "files", "params", "symbols"):
            assert key in result["entities"]

    def test_invalid_task_type_defaults(self) -> None:
        result = self._call(question="test", task_type="not_valid")
        assert result["task_type"] == "architecture"

    def test_invalid_detail_defaults(self) -> None:
        result = self._call(question="test", detail="not_valid")
        assert result["detail"] == "normal"

    def test_scope_normalized_to_uppercase(self) -> None:
        result = self._call(question="test", scope=["gm", "ie"])
        assert result["scope"] == ["GM", "IE"]

    def test_valid_task_types(self) -> None:
        for tt in ("architecture", "debug", "lookup", "workflow", "compare"):
            result = self._call(question="test", task_type=tt)
            assert result["task_type"] == tt

    def test_valid_detail_levels(self) -> None:
        for detail in ("brief", "normal", "deep"):
            result = self._call(question="test", detail=detail)
            assert result["detail"] == detail


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2: get_evidence
# ─────────────────────────────────────────────────────────────────────────────

class TestGetEvidence:
    def _call(self, **kwargs: Any) -> dict[str, Any]:
        mod = _import_tool("get_evidence")
        kwargs.setdefault("swmf_root", str(Path(__file__).parents[1]))
        return mod.get_evidence(**kwargs)

    def test_importable(self) -> None:
        mod = _import_tool("get_evidence")
        assert hasattr(mod, "get_evidence")
        assert hasattr(mod, "register")

    def test_signature_has_required_params(self) -> None:
        mod = _import_tool("get_evidence")
        sig = inspect.signature(mod.get_evidence)
        for param in ("query", "mode", "scope", "top_k", "goal", "swmf_root", "run_dir"):
            assert param in sig.parameters

    def test_output_contract(self) -> None:
        result = self._call(query="DoCoupleGMIE", scope=["GM", "IE"])
        _assert_base_output_contract(result, "get_evidence")
        assert "mode" in result
        assert "mode_used" in result["provenance"]
        assert "scope" in result["provenance"]

    def test_invalid_mode_defaults_to_hybrid(self) -> None:
        result = self._call(query="test", mode="not_valid")
        assert result["mode"] == "hybrid"

    def test_valid_modes(self) -> None:
        for mode in ("hybrid", "keyword", "semantic"):
            result = self._call(query="test", mode=mode)
            assert result["mode"] == mode

    def test_top_k_clamped(self) -> None:
        result_low = self._call(query="test", top_k=0)
        assert result_low["top_k"] == 1

        result_high = self._call(query="test", top_k=999)
        assert result_high["top_k"] == 100

    def test_scope_normalized(self) -> None:
        result = self._call(query="test", scope=["gm", "ie"])
        assert result["scope"] == ["GM", "IE"]

    def test_idl_procedure_query_uses_catalog_evidence(self, tmp_path: Path) -> None:
        swmf_root = tmp_path / "SWMF"
        (swmf_root / "Scripts").mkdir(parents=True)
        (swmf_root / "share" / "IDL" / "General").mkdir(parents=True)
        (swmf_root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        (swmf_root / "PARAM.XML").write_text("<param></param>\n", encoding="utf-8")
        (swmf_root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        (swmf_root / "share" / "IDL" / "General" / "procedures.pro").write_text(
            "; Plot functions from data already read by read_data.\n"
            "pro plot_data, func=func, plotmode=plotmode\n"
            "end\n",
            encoding="utf-8",
        )

        result = self._call(
            query="plot_data",
            mode="keyword",
            goal="IDL procedure signature and usage",
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "get_evidence")
        assert result["evidence"]
        first = result["evidence"][0]
        assert first["type"] == "idl"
        assert first["name"] == "plot_data"
        assert first["metadata"]["kind"] == "idl_procedure_signature"
        assert first["metadata"]["relative_path"].endswith("share/IDL/General/procedures.pro")

    def test_idl_inventory_query_lists_catalog_rows(self, tmp_path: Path) -> None:
        swmf_root = tmp_path / "SWMF"
        (swmf_root / "Scripts").mkdir(parents=True)
        (swmf_root / "share" / "IDL" / "General").mkdir(parents=True)
        (swmf_root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        (swmf_root / "PARAM.XML").write_text("<param></param>\n", encoding="utf-8")
        (swmf_root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        (swmf_root / "share" / "IDL" / "General" / "procedures.pro").write_text(
            "pro plot_data\n"
            "end\n"
            "pro read_data\n"
            "end\n",
            encoding="utf-8",
        )

        result = self._call(
            query="list IDL plotting procedures",
            mode="keyword",
            top_k=5,
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "get_evidence")
        assert any(item["name"] == "plot_data" for item in result["evidence"])
        assert all(item["type"] == "idl" for item in result["evidence"][:1])

    def test_idl_manual_plotmode_query_returns_manual_evidence(self, tmp_path: Path) -> None:
        swmf_root = tmp_path / "SWMF"
        (swmf_root / "Scripts").mkdir(parents=True)
        (swmf_root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        (swmf_root / "PARAM.XML").write_text("<param></param>\n", encoding="utf-8")
        (swmf_root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")

        result = self._call(
            query="plotmode",
            mode="keyword",
            goal="IDL visualization manual detail",
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "get_evidence")
        assert result["evidence"]
        first = result["evidence"][0]
        assert first["type"] == "idl"
        assert first["metadata"]["kind"] == "idl_manual_section"
        assert first["metadata"]["relative_path"].endswith("docs/idl.md") or "docs/idl.md" in first["path"]
        assert "Plotting modes" in first["snippet"]
        assert all("recommended" not in item for item in result["evidence"])
        assert all("next_action" not in item for item in result["evidence"])

    def test_idl_func_query_returns_manual_or_funcdef_evidence(self, tmp_path: Path) -> None:
        swmf_root = tmp_path / "SWMF"
        general_dir = swmf_root / "share" / "IDL" / "General"
        (swmf_root / "Scripts").mkdir(parents=True)
        general_dir.mkdir(parents=True)
        (swmf_root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        (swmf_root / "PARAM.XML").write_text("<param></param>\n", encoding="utf-8")
        (swmf_root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        (general_dir / "funcdef.pro").write_text(
            "function funcdef, xx, w, func\n"
            "functiondef = $\n"
            "  strlowcase(transpose([ $\n"
            "  ['calfven', 'b/sqrt(rho*mu0A)'], $\n"
            "  ['pbeta', 'p/(bb/(2*mu0))'] $ \n"
            "  ]))\n"
            "end\n",
            encoding="utf-8",
        )

        result = self._call(
            query="func",
            mode="keyword",
            goal="IDL visualization manual detail",
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "get_evidence")
        kinds = {item.get("metadata", {}).get("kind") for item in result["evidence"]}
        assert "idl_manual_section" in kinds
        assert "idl_funcdef_inventory" in kinds
        funcdef_item = next(item for item in result["evidence"] if item["metadata"]["kind"] == "idl_funcdef_inventory")
        assert "calfven" in funcdef_item["snippet"]


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3: get_evidence workflow modes
# ─────────────────────────────────────────────────────────────────────────────


class TestGetEvidenceWorkflowModes:
    def _call(self, **kwargs: Any) -> dict[str, Any]:
        mod = _import_tool("get_evidence")
        kwargs.setdefault("swmf_root", str(Path(__file__).parents[1]))
        return mod.get_evidence(**kwargs)

    def test_signature_has_required_params(self) -> None:
        mod = _import_tool("get_evidence")
        sig = inspect.signature(mod.get_evidence)
        for param in (
            "query",
            "mode",
            "scope",
            "top_k",
            "goal",
            "task_type",
            "module",
            "swmf_root",
            "run_dir",
        ):
            assert param in sig.parameters

    def test_invalid_task_type_defaults_to_lookup(self) -> None:
        result = self._call(query="test", task_type="not_valid")
        assert result["task_type"] == "lookup"

    def test_valid_task_types(self) -> None:
        for tt in ("lookup", "configuration", "build", "run", "analysis"):
            result = self._call(query="test", task_type=tt)
            assert result["task_type"] == tt

    def test_module_normalized_to_uppercase(self) -> None:
        result = self._call(query="test", module="gm")
        assert result["module"] == "GM"

    def test_lookup_mode_keeps_base_contract(self) -> None:
        result = self._call(query="DoCoupleGMIE", scope=["GM", "IE"])
        _assert_base_output_contract(result, "get_evidence")
        assert "mode" in result
        assert "mode_used" in result["provenance"]
        assert "scope" in result["provenance"]
        assert result["task_type"] == "lookup"
        assert result["module"] is None

    def test_workflow_modes_return_metadata_without_legacy_fields(self, tmp_path: Path) -> None:
        swmf_root = tmp_path / "SWMF"
        gm_dir = swmf_root / "GM"
        scripts_dir = gm_dir / "Scripts"
        scripts_dir.mkdir(parents=True)
        for rel_path in ("Config.pl", "Makefile", "PostProc.pl", "Scripts/TestParam.pl"):
            target = gm_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("#!/usr/bin/env perl\n", encoding="utf-8")

        result = self._call(
            query="configure GM",
            goal="configure GM",
            task_type="configuration",
            module="gm",
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "get_evidence")
        assert result["task_type"] == "configuration"
        assert result["module"] == "GM"
        for field in ("entrypoints", "usage_evidence", "required_inputs", "constraints"):
            assert field not in result
        assert any("metadata" in item for item in result["evidence"])
        assert any(
            item.get("metadata", {}).get("relative_path", "").endswith("Config.pl")
            for item in result["evidence"]
        )


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4: inspect_artifact
# ─────────────────────────────────────────────────────────────────────────────

class TestInspectArtifact:
    def _call(self, **kwargs: Any) -> dict[str, Any]:
        mod = _import_tool("inspect_artifact")
        kwargs.setdefault("swmf_root", str(Path(__file__).parents[1]))
        return mod.inspect_artifact(**kwargs)

    def _make_fake_swmf_root(self, workspace: Path) -> Path:
        swmf_root = workspace / "SWMF"
        (swmf_root / "Scripts").mkdir(parents=True)
        (swmf_root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        (swmf_root / "PARAM.XML").write_text("<param></param>\n", encoding="utf-8")
        (swmf_root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
        return swmf_root

    def _write_fake_idl_real4_plot(self, path: Path) -> None:
        def record(payload: bytes) -> bytes:
            marker = struct.pack("<I", len(payload))
            return marker + payload + marker

        headline = b"km Mp/cc km/s km/s km/s nT nT nT nPa".ljust(79, b" ")
        header = struct.pack("<ifiii", 77, 60.360603, 2, 2, 7)
        nx = struct.pack("<2i", 2, 3)
        eqpar = struct.pack("<2f", 1000.0, 1.66667)
        names = b"x y Rho Ux Uy Uz Bx By Bz xSI gamma".ljust(79, b" ")
        ncell = 6
        x = struct.pack(f"<{2 * ncell}f", *([0.0] * (2 * ncell)))
        w_records = b"".join(record(struct.pack(f"<{ncell}f", *([0.0] * ncell))) for _ in range(7))
        path.write_bytes(
            record(headline)
            + record(header)
            + record(nx)
            + record(eqpar)
            + record(names)
            + record(x)
            + w_records
        )

    def test_importable(self) -> None:
        mod = _import_tool("inspect_artifact")
        assert hasattr(mod, "inspect_artifact")
        assert hasattr(mod, "register")

    def test_signature_has_required_params(self) -> None:
        mod = _import_tool("inspect_artifact")
        sig = inspect.signature(mod.inspect_artifact)
        for param in ("artifact_type", "path", "question", "swmf_root", "run_dir"):
            assert param in sig.parameters

    def test_output_contract(self) -> None:
        result = self._call(artifact_type="log", path="run/log.ie")
        _assert_base_output_contract(result, "inspect_artifact")
        assert "findings" in result
        assert isinstance(result["findings"], list)
        assert "artifact_type" in result["provenance"]
        assert "path" in result["provenance"]

    def test_valid_artifact_types(self) -> None:
        for at in ("log", "param", "xml", "run_dir", "build_output", "result"):
            result = self._call(artifact_type=at, path="some/path")
            assert result["artifact_type"] == at

    def test_unknown_artifact_type_defaults_to_log_with_warning(self) -> None:
        result = self._call(artifact_type="unknown_type", path="some/path")
        assert result["artifact_type"] == "log"
        assert "warnings" in result
        assert any("unknown_type" in w for w in result["warnings"])

    def test_question_defaults_to_empty_string(self) -> None:
        result = self._call(artifact_type="log", path="some/path")
        assert result["question"] == ""

    def test_log_inspection_streams_full_log_past_front_cap(self, tmp_path: Path) -> None:
        log_path = tmp_path / "runtime-transcript.txt"
        progress_lines = [
            f"Progress:  {500000 + i * 10} steps,  {54000.0 + i:.6E} s simulation time,   {1000.0 + i:.2f} s CPU time, Date: 20240801_151250\n"
            for i in range(3500)
        ]
        log_path.write_text(
            "TACC: Starting parallel tasks\n"
            + "".join(progress_lines)
            + "    Finished Numerical Simulation\n"
            + "    Finished Finalizing SWMF\n"
            + "TACC:  Shutdown complete. Exiting.\n",
            encoding="utf-8",
        )

        result = self._call(artifact_type="log", path=str(log_path))

        compaction = next(item for item in result["findings"] if item["kind"] == "log_compaction")
        status = next(item for item in result["findings"] if item["kind"] == "run_status")
        progress = next(item for item in result["findings"] if item["kind"] == "progress_summary")
        assert compaction["line_count"] == 3504
        assert compaction["bytes"] > 200_000
        assert len(compaction["tail_lines"]) <= 24
        assert status["status"] == "completed"
        assert progress["count"] == 3500
        assert any(item["kind"] == "run_completed" for item in result["findings"])

    def test_log_inspection_deduplicates_repeated_mpi_rank_errors(self, tmp_path: Path) -> None:
        log_path = tmp_path / "runtime-transcript.txt"
        repeated = "\n".join(
            [
                f"Error in component SC in session  1\n ERROR: aborting execution on processor {rank:4d}  with message:\nERROR: Fix #STARTTIME command in PARAM.in"
                for rank in range(100)
            ]
        )
        log_path.write_text(repeated + "\nTACC:  MPI job exited with code: 1\n", encoding="utf-8")

        result = self._call(artifact_type="log", path=str(log_path))

        status = next(item for item in result["findings"] if item["kind"] == "run_status")
        first_error = next(item for item in result["findings"] if item["kind"] == "first_error")
        diagnostics = next(item for item in result["findings"] if item["kind"] == "diagnostic_summary")
        assert status["status"] == "failed"
        assert "Fix #STARTTIME" in first_error["description"]
        assert any(
            item["count"] == 100 and "Fix #STARTTIME" in item["pattern"]
            for item in diagnostics["diagnostics"]
        )

    def test_run_dir_log_discovery_uses_full_log_stream(self, tmp_path: Path) -> None:
        workspace = tmp_path / "workspace"
        swmf_root = self._make_fake_swmf_root(workspace)
        run_dir = workspace / "run01"
        run_dir.mkdir(parents=True)
        (run_dir / "runlog").write_text(
            "".join(
                f"Progress:  {i} steps,  {float(i):.6E} s simulation time,   {float(i):.2f} s CPU time, Date: 20240801_151250\n"
                for i in range(3500)
            )
            + "Finished Finalizing SWMF\n",
            encoding="utf-8",
        )

        result = self._call(artifact_type="run_dir", path=str(run_dir), swmf_root=str(swmf_root))

        log_finding = next(item for item in result["findings"] if item["kind"] == "log_discovery")
        assert log_finding["line_count"] == 3501
        assert log_finding["bytes"] > 200_000
        assert log_finding["status"] == "completed"
        assert log_finding["progress"]["count"] == 3500

    def test_run_dir_not_found_returns_swmfsolar_path_candidates(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        workspace = tmp_path / "workspace"
        swmf_root = self._make_fake_swmf_root(workspace)
        run_dir = workspace / "SWMFSOLAR" / "Run_Max_RP_CME3" / "run01"
        ih_dir = run_dir / "IH"
        ih_dir.mkdir(parents=True)
        (ih_dir / "z=0_var_3_t0001.out").write_text("x y z bx by\n", encoding="utf-8")
        (workspace / "SWMFSOLAR" / "Run_Max_RP_CME3.tar.gz").write_text("archive\n", encoding="utf-8")

        other_cwd = tmp_path / "elsewhere"
        other_cwd.mkdir()
        monkeypatch.chdir(other_cwd)

        result = self._call(
            artifact_type="run_dir",
            path="Run_Max_RP_CME3",
            question="animate IH results from z=0 .out cut planes",
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "inspect_artifact")
        finding = next(item for item in result["findings"] if item["kind"] == "run_dir_not_found")
        candidates = finding["path_search_candidates"]
        assert str(run_dir) in candidates
        assert all(not candidate.endswith(".tar.gz") for candidate in candidates)
        assert candidates.index(str(run_dir)) == 0

    def test_run_dir_reports_component_snapshot_output_groups(self, tmp_path: Path) -> None:
        workspace = tmp_path / "workspace"
        swmf_root = self._make_fake_swmf_root(workspace)
        run_dir = workspace / "SWMFSOLAR" / "Run_Max_RP_CME3" / "run01"
        ih_dir = run_dir / "IH"
        ih_dir.mkdir(parents=True)
        (ih_dir / "z=0_var_3_t0001.out").write_text("x y z bx by\n", encoding="utf-8")
        (ih_dir / "z=0_var_3_t0002.out").write_text("x y z bx by\n", encoding="utf-8")

        result = self._call(
            artifact_type="run_dir",
            path=str(run_dir),
            question="animate IH z=0 .out snapshots",
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "inspect_artifact")
        finding = next(
            item
            for item in result["findings"]
            if item["kind"] == "component_output_files" and item["component"] == "IH"
        )
        assert finding["patterns"]["z=0*.out"]["count"] == 2
        assert "z=0_var_3_t0001.out" in finding["patterns"]["z=0*.out"]["samples"]
        group = next(item for item in finding["snapshot_groups"] if item["pattern"] == "z=0_var_3_t*.out")
        assert group["combined_outs"] == "z=0_var_3.outs"
        assert group["combined_outs_exists"] is False
        assert group["first_frame"] == "z=0_var_3_t0001.out"
        assert group["middle_frame"] == "z=0_var_3_t0002.out"
        assert group["last_frame"] == "z=0_var_3_t0002.out"
        assert group["first_frame_path"].endswith("z=0_var_3_t0001.out")

    def test_run_dir_groups_timestep_and_iteration_snapshot_names(self, tmp_path: Path) -> None:
        workspace = tmp_path / "workspace"
        swmf_root = self._make_fake_swmf_root(workspace)
        run_dir = workspace / "run01"
        ih_dir = run_dir / "IH"
        ih_dir.mkdir(parents=True)
        (ih_dir / "z=0_var_3_t00020000_n00005000.out").write_text("x y z bx by\n", encoding="utf-8")
        (ih_dir / "z=0_var_3_t00030000_n00007500.out").write_text("x y z bx by\n", encoding="utf-8")
        (ih_dir / "z=0_var_3_t00040000_n00010000.out").write_text("x y z bx by\n", encoding="utf-8")
        (ih_dir / "z=0_var_3.outs").write_text("combined\n", encoding="utf-8")

        result = self._call(
            artifact_type="run_dir",
            path=str(run_dir),
            question="animate IH z=0 .out snapshots",
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "inspect_artifact")
        finding = next(item for item in result["findings"] if item["kind"] == "component_output_files")
        group = next(item for item in finding["snapshot_groups"] if item["base"] == "z=0_var_3")
        assert group["pattern"] == "z=0_var_3_t*_n*.out"
        assert group["count"] == 3
        assert group["expected_outs"] == "z=0_var_3.outs"
        assert group["combined_outs_exists"] is True
        assert group["first_frame"] == "z=0_var_3_t00020000_n00005000.out"
        assert group["middle_frame"] == "z=0_var_3_t00030000_n00007500.out"
        assert group["last_frame"] == "z=0_var_3_t00040000_n00010000.out"
        assert group["middle_frame_path"].endswith("z=0_var_3_t00030000_n00007500.out")

    def test_run_dir_includes_param_summary_and_saveplot_findings(self, tmp_path: Path) -> None:
        workspace = tmp_path / "workspace"
        swmf_root = self._make_fake_swmf_root(workspace)
        run_dir = workspace / "run01"
        (run_dir / "IH").mkdir(parents=True)
        (run_dir / "PARAM.in").write_text(
            "\n".join(
                [
                    "#TIMEACCURATE",
                    "T DoTimeAccurate",
                    "#COMPONENTMAP",
                    "IH 0 3 1",
                    "#SAVEPLOT",
                    "2 nPlotFile",
                    "z=0 VAR idl StringPlot",
                    "-1 DnSavePlot",
                    "600.0 DtSavePlot",
                    "{MHD} bx by NameVars",
                    "{default} NamePars",
                    "x=0 VAR ascii StringPlot",
                    "-1 DnSavePlot",
                    "1200.0 DtSavePlot",
                    "ux uy NameVars",
                    "#STOP",
                    "-1 MaxIter",
                    "4 h TimeMax",
                    "#RUN",
                    "#STOP",
                    "-1 MaxIter",
                    "8 h TimeMax",
                    "#END",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        result = self._call(
            artifact_type="run_dir",
            path=str(run_dir),
            question="summarize saveplot cadence and run sessions",
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "inspect_artifact")
        summary_finding = next(item for item in result["findings"] if item["kind"] == "run_dir_param_summary")
        assert summary_finding["session_count"] == 2
        assert summary_finding["saveplot_block_count"] == 1
        assert "IH" in summary_finding["required_components"]
        assert any(item["key"] == "TimeMax" for item in summary_finding["control_settings"])
        assert any(item["command"] == "#SAVEPLOT" for item in summary_finding["key_command_timeline"])

        saveplot_finding = next(item for item in result["findings"] if item["kind"] == "run_dir_param_saveplot")
        saveplot_block = saveplot_finding["saveplot_blocks"][0]
        assert saveplot_block["declared_plot_count"] == 2
        assert saveplot_block["entry_count"] == 2
        assert saveplot_block["plot_forms"] == ["ascii", "idl"]

        first_entry = saveplot_block["entries"][0]
        assert first_entry["plot_area"] == "z=0"
        assert first_entry["plot_form"] == "idl"
        assert first_entry["cadence"]["DtSavePlot"] == 600.0
        assert "bx" in first_entry["name_vars"]

    def test_run_dir_explicitly_reports_missing_param_in_file(self, tmp_path: Path) -> None:
        workspace = tmp_path / "workspace"
        swmf_root = self._make_fake_swmf_root(workspace)
        run_dir = workspace / "run01"
        ih_dir = run_dir / "IH"
        ih_dir.mkdir(parents=True)
        (ih_dir / "z=0_var_3_t0001.out").write_text("x y z bx by\n", encoding="utf-8")

        result = self._call(
            artifact_type="run_dir",
            path=str(run_dir),
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "inspect_artifact")
        missing_param = next(item for item in result["findings"] if item["kind"] == "run_dir_param_missing")
        assert missing_param["location"].endswith("PARAM.in")
        assert "missing" in missing_param["description"].lower()

    def test_result_extracts_binary_idl_plot_header(self, tmp_path: Path) -> None:
        swmf_root = self._make_fake_swmf_root(tmp_path)
        plot_file = tmp_path / "z=0_var_3_t00020000_n00005000.out"
        self._write_fake_idl_real4_plot(plot_file)

        result = self._call(
            artifact_type="result",
            path=str(plot_file),
            swmf_root=str(swmf_root),
        )

        _assert_base_output_contract(result, "inspect_artifact")
        finding = next(item for item in result["findings"] if item["kind"] == "idl_plot_file_header")
        assert finding["filetype"] == "real4"
        assert finding["npictinfile"] == 1
        assert finding["headline"].startswith("km Mp/cc")
        assert finding["it"] == 77
        assert finding["ndim"] == 2
        assert finding["neqpar"] == 2
        assert finding["nw"] == 7
        assert finding["nx"] == [2, 3]
        assert finding["coord_names"] == ["x", "y"]
        assert finding["variable_names"] == ["Rho", "Ux", "Uy", "Uz", "Bx", "By", "Bz"]
        assert finding["parameter_names"] == ["xSI", "gamma"]


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4: compare_artifacts
# ─────────────────────────────────────────────────────────────────────────────

class TestCompareArtifacts:
    def _call(self, **kwargs: Any) -> dict[str, Any]:
        mod = _import_tool("compare_artifacts")
        kwargs.setdefault("swmf_root", str(Path(__file__).parents[1]))
        return mod.compare_artifacts(**kwargs)

    def test_importable(self) -> None:
        mod = _import_tool("compare_artifacts")
        assert hasattr(mod, "compare_artifacts")
        assert hasattr(mod, "register")

    def test_signature_has_required_params(self) -> None:
        mod = _import_tool("compare_artifacts")
        sig = inspect.signature(mod.compare_artifacts)
        for param in ("left", "right", "comparison_type", "question", "swmf_root", "run_dir"):
            assert param in sig.parameters

    def test_output_contract(self) -> None:
        result = self._call(left="run_a/PARAM.in", right="run_b/PARAM.in")
        _assert_base_output_contract(result, "compare_artifacts")
        assert "differences" in result
        assert isinstance(result["differences"], list)
        assert "left" in result["provenance"]
        assert "right" in result["provenance"]
        assert "comparison_type" in result["provenance"]

    def test_comparison_type_inferred_from_extension(self) -> None:
        result = self._call(left="run_a/PARAM.in", right="run_b/PARAM.in")
        assert result["comparison_type"] == "param"

    def test_comparison_type_inferred_log(self) -> None:
        result = self._call(left="run_a/log.stdout", right="run_b/log.stdout")
        assert result["comparison_type"] == "log"

    def test_explicit_comparison_type_respected(self) -> None:
        result = self._call(
            left="run_a/output",
            right="run_b/output",
            comparison_type="run_dir",
        )
        assert result["comparison_type"] == "run_dir"

    def test_invalid_explicit_type_falls_back_to_inference(self) -> None:
        result = self._call(
            left="run_a/PARAM.in",
            right="run_b/PARAM.in",
            comparison_type="not_valid",
        )
        # Should fall back to inferring from .in extension → "param"
        assert result["comparison_type"] == "param"


# ─────────────────────────────────────────────────────────────────────────────
# Removal gate: no legacy swmf_* tools exposed on server surface
# ─────────────────────────────────────────────────────────────────────────────

def test_no_legacy_tools_exposed_on_server() -> None:
    """Removal gate: server.py must not export any swmf_* callable after cutover."""
    server = importlib.import_module("swmf_mcp_server.server")

    legacy_names = [
        name
        for name in dir(server)
        if name.startswith("swmf_") and callable(getattr(server, name))
    ]
    assert legacy_names == [], (
        "Legacy tools still exported from server.py. Remove before cutover:\n"
        + "\n".join(f"  - {t}" for t in sorted(legacy_names))
    )


def test_schema_document_exists() -> None:
    schema_path = Path(__file__).parents[1] / "docs" / "api_v2_schema.yaml"
    assert schema_path.is_file(), "docs/api_v2_schema.yaml must exist"
    content = schema_path.read_text(encoding="utf-8")
    for tool_name in ("get_context", "get_evidence", "inspect_artifact", "compare_artifacts"):
        assert tool_name in content, f"Schema document missing entry for '{tool_name}'"
    assert "existing_tool_mapping" not in content
    assert "admin_tools" not in content


def test_no_legacy_swmf_functions_remain_in_tools() -> None:
    """Cutover gate: no swmf_* callables may remain in the tools package."""
    import re

    tools_dir = Path(__file__).parents[1] / "src" / "swmf_mcp_server" / "tools"
    legacy_functions: list[str] = []
    for py_file in sorted(tools_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        source = py_file.read_text(encoding="utf-8")
        for match in re.finditer(r"^def (swmf_\w+)\(", source, re.MULTILINE):
            legacy_functions.append(f"{py_file.name}:{match.group(1)}")

    assert legacy_functions == [], (
        "Legacy swmf_* functions remain in tools/*.py after v2 cutover:\n"
        + "\n".join(f"  - {item}" for item in sorted(legacy_functions))
    )


def test_four_public_tool_modules_exist() -> None:
    for mod_name in (
        "get_context",
        "get_evidence",
        "inspect_artifact",
        "compare_artifacts",
    ):
        mod = _import_tool(mod_name)
        assert mod is not None
        assert hasattr(mod, "register"), f"{mod_name} must expose a register() function"
