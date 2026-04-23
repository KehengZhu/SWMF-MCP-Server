"""Public API tool: get_workflow_guidance.

Purpose
-------
Expose likely workflow entrypoints and usage evidence for a goal.
Does NOT execute anything and does NOT synthesize the final workflow.
Returns affordances (scripts, config entrypoints, command patterns) and
evidence so the agent can construct the actual workflow.

Internal backends (hidden from caller)
---------------------------------------
- catalog (script discovery)
- exact lookup (help text extraction)
- semantic context (relevance scoring)
- script inspection (usage extraction)

Output contract
---------------
{
  "summary": str,
  "entrypoints": list[EntrypointItem],
  "usage_evidence": list[EvidenceItem],
  "required_inputs": list[str],
  "constraints": list[str],
  "evidence": list[EvidenceItem],
  "provenance": {"backend_used": str},
  "uncertainty": {"known_unknowns": list[str]}
}

EntrypointItem shape
--------------------
{
  "path": str,
  "kind": "script" | "makefile_target" | "command" | "config_file",
  "why_relevant": str
}

EvidenceItem shape
------------------
{
  "path": str,
  "snippet": str,
  "score": float
}

Example request
---------------
{
  "goal": "configure GM for this case",
  "module": "GM",
  "task_type": "configuration",
  "context": {"case_dir": "/run/GM", "related_components": ["IE"]}
}

Example response
----------------
{
  "summary": "One primary configuration entrypoint found for GM.",
  "entrypoints": [
    {
      "path": "GM/Config.pl",
      "kind": "script",
      "why_relevant": "main GM configuration script"
    }
  ],
  "usage_evidence": [
    {"path": "GM/Config.pl", "snippet": "Usage: Config.pl -install ...", "score": 0.89}
  ],
  "required_inputs": ["module settings", "case directory"],
  "constraints": ["may overwrite generated configuration files"],
  "evidence": [],
  "provenance": {"backend_used": "catalog+keyword"},
  "uncertainty": {"known_unknowns": ["case-specific flags not yet inspected"]}
}

Field semantics
---------------
goal       : Required. Freeform description of what the agent wants to accomplish.
module     : Optional SWMF component/module name to scope entrypoint search (e.g. "GM").
task_type  : Optional hint for the backend router.
             One of "configuration", "build", "run", "analysis". Default "configuration".
context    : Optional dict of auxiliary context (e.g. case_dir, related_components).
swmf_root  : Optional explicit SWMF source root path.
run_dir    : Optional run directory used for root resolution.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ._helpers import resolve_root_or_failure, with_root
from ._router import raw_result_to_evidence_item, _check_index
from ..knowledge import service as ks
from ..catalog.source_index_catalog import SLICE_SWMF_SCRIPTS

_VALID_TASK_TYPES = frozenset({"configuration", "build", "run", "analysis"})

# Scripts that are authoritative entrypoints for each task type
_TASK_SCRIPT_HINTS: dict[str, list[str]] = {
    "configuration": ["Config.pl"],
    "build": ["Config.pl", "Makefile"],
    "run": ["Scripts/TestParam.pl", "Restart.pl"],
    "analysis": ["PostProc.pl"],
}


def _discover_entrypoints(swmf_root: str, module: str | None, task_type: str) -> list[dict[str, Any]]:
    """Return EntrypointItem list from known authoritative scripts."""
    root_path = Path(swmf_root)
    hint_names = set(_TASK_SCRIPT_HINTS.get(task_type, ["Config.pl"]))
    entrypoints: list[dict[str, Any]] = []

    # Walk the root for the hinted scripts
    for candidate_path in root_path.rglob("*.pl"):
        name = candidate_path.name
        if name not in hint_names:
            continue
        # If a module filter is given, only include scripts under that component dir
        if module:
            parts = [p.upper() for p in candidate_path.parts]
            if module.upper() not in parts:
                continue
        rel = str(candidate_path.relative_to(root_path))
        entrypoints.append({
            "path": str(candidate_path.resolve()),
            "relative_path": rel,
            "kind": "script",
            "why_relevant": f"Known {task_type} entrypoint: {name}",
        })

    # Include Config.pl in component subdir if module given
    if module:
        comp_config = root_path / module.upper() / "Config.pl"
        if not comp_config.exists():
            # Try case-insensitive by scanning
            for d in root_path.iterdir():
                if d.is_dir() and d.name.upper() == module.upper():
                    comp_config = d / "Config.pl"
                    break
        if comp_config.is_file():
            rel = str(comp_config.relative_to(root_path))
            existing_paths = {e["relative_path"] for e in entrypoints}
            if rel not in existing_paths:
                entrypoints.append({
                    "path": str(comp_config.resolve()),
                    "relative_path": rel,
                    "kind": "config",
                    "why_relevant": f"Component-level configuration for {module}",
                })

    return entrypoints[:12]


def get_workflow_guidance(
    goal: str,
    module: str | None = None,
    task_type: str | None = None,
    context: dict[str, Any] | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Return workflow entrypoints and usage evidence for a goal.

    Use for 'how do I configure module X?', 'what script or entrypoint is
    usually used?', 'what are the relevant build/run/config steps?'. Returns
    affordances and evidence — NOT a hard-coded execution sequence.
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    resolved_task_type = task_type if task_type in _VALID_TASK_TYPES else "configuration"
    resolved_module = (module or "").upper() or None

    assert root.swmf_root_resolved is not None

    # --- Entrypoints from filesystem ---
    entrypoints = _discover_entrypoints(root.swmf_root_resolved, resolved_module, resolved_task_type)

    # --- Usage evidence from knowledge index (scripts corpus slice) ---
    index_ready, degraded_reason = _check_index(root.swmf_root_resolved)
    usage_evidence: list[dict[str, Any]] = []

    search_query = goal
    if resolved_module:
        search_query = f"{resolved_module} {goal}"

    raw_payload = ks.search_source(
        root.swmf_root_resolved,
        query=search_query,
        component=resolved_module,
        max_results=8,
        search_mode="keyword",
        ensure_ready=False,
        corpus_slice=SLICE_SWMF_SCRIPTS,
    )
    for r in raw_payload.get("results", []):
        item = raw_result_to_evidence_item(r)
        item["type"] = "code"
        usage_evidence.append(item)

    # Also do a general evidence search if no scripts results
    if not usage_evidence:
        general = ks.search_source(
            root.swmf_root_resolved,
            query=search_query,
            component=resolved_module,
            max_results=6,
            search_mode="keyword",
            ensure_ready=False,
        )
        usage_evidence = [raw_result_to_evidence_item(r) for r in general.get("results", [])]

    n_ep = len(entrypoints)
    n_ev = len(usage_evidence)
    summary_parts: list[str] = [f"{n_ep} entrypoint(s) found for '{goal}' ({resolved_task_type} task type)."]
    if n_ev:
        summary_parts.append(f"{n_ev} usage evidence snippet(s) retrieved.")

    known_unknowns: list[str] = []
    if degraded_reason:
        known_unknowns.append(degraded_reason)
    known_unknowns.append("Help text for scripts not parsed; check script source for exact usage.")

    payload: dict[str, Any] = {
        "ok": True,
        "goal": goal,
        "module": resolved_module,
        "task_type": resolved_task_type,
        "context": context or {},
        "summary": " ".join(summary_parts),
        "entrypoints": entrypoints,
        "usage_evidence": usage_evidence,
        "required_inputs": [],
        "constraints": [],
        "evidence": usage_evidence,
        "provenance": {"backend_used": "filesystem+knowledge_index"},
        "uncertainty": {"known_unknowns": known_unknowns},
    }
    return with_root(payload, root)


def register(app: Any) -> None:
    app.tool(
        description=(
            "Return workflow entrypoints and usage evidence for a goal. "
            "Use for 'how do I configure/build/run module X?' or 'what scripts are needed?'. "
            "Returns affordances (scripts, config entrypoints, command patterns) and evidence "
            "so the agent can construct the actual workflow. Does NOT execute anything."
        )
    )(get_workflow_guidance)
