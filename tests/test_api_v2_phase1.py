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
