"""Public API tool: get_context.

Purpose
-------
Give the agent compact repo/task orientation — not proof, not policy.
Returns entities, components, files, params, and symbols relevant to the
question so the agent can decide what to retrieve next.

Internal backends (hidden from caller)
---------------------------------------
- catalog
- semantic / knowledge index
- codebase map

Output contract
---------------
{
  "summary": str,
  "entities": {
    "components": list[str],
    "files": list[str],
    "params": list[str],
    "symbols": list[str]
  },
  "evidence": list[EvidenceItem],
  "provenance": {"backend_used": str},
  "uncertainty": {"known_unknowns": list[str]}
}

Example request
---------------
{
  "question": "How does GM couple to IE in this setup?",
  "scope": ["GM", "IE"],
  "task_type": "architecture",
  "detail": "brief"
}

Example response
----------------
{
  "summary": "GM-IE coupling involves CON-mediated timing and shared coupling parameters.",
  "entities": {
    "components": ["GM", "IE", "CON"],
    "files": ["PARAM.in", "CON/Config.pl"],
    "params": ["DoCoupleGMIE", "DtCouple"],
    "symbols": []
  },
  "evidence": [],
  "provenance": {"backend_used": "catalog+semantic"},
  "uncertainty": {"known_unknowns": ["current case-specific runtime state not inspected"]}
}

Field semantics
---------------
question   : Required. The question or topic to orient around.
scope      : Optional list of SWMF component IDs to restrict orientation (e.g. ["GM","IE"]).
task_type  : Optional hint for the backend router.
             One of "architecture", "debug", "lookup", "workflow", "compare".
             Default "architecture".
detail     : Optional verbosity level: "brief" | "normal" | "deep". Default "normal".
swmf_root  : Optional explicit SWMF source root path.
run_dir    : Optional run directory used for root resolution.
"""

from __future__ import annotations

from typing import Any

from ._helpers import resolve_root_or_failure, with_root
from ._router import (
    enrich_entities_from_evidence,
    extract_entities_from_analysis,
    run_evidence_search,
)
from ..knowledge import service as ks

_VALID_TASK_TYPES = frozenset({"architecture", "debug", "lookup", "workflow", "compare"})
_VALID_DETAIL_LEVELS = frozenset({"brief", "normal", "deep"})

# top_k values per detail level
_DETAIL_TOP_K: dict[str, int] = {"brief": 4, "normal": 8, "deep": 16}


def get_context(
    question: str,
    scope: list[str] | None = None,
    task_type: str | None = None,
    detail: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Give the agent compact repo/task orientation for a question.

    Use for vague questions, architecture questions, multi-component questions,
    or 'what area of the codebase matters?'
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    resolved_task_type = task_type if task_type in _VALID_TASK_TYPES else "architecture"
    resolved_detail = detail if detail in _VALID_DETAIL_LEVELS else "normal"
    resolved_scope: list[str] = [s.upper() for s in (scope or [])]
    top_k = _DETAIL_TOP_K[resolved_detail]

    assert root.swmf_root_resolved is not None

    # --- Entity extraction (always done) ---
    query_analysis = ks.understand_source_query(question)
    entities = extract_entities_from_analysis(query_analysis)

    # Merge scope into entities.components
    for comp in resolved_scope:
        if comp not in entities["components"]:
            entities["components"].append(comp)

    # --- Evidence search ---
    mode = "hybrid" if resolved_task_type in ("architecture", "debug", "compare") else "keyword"
    evidence, mode_used, ev_summary, degraded_reason = run_evidence_search(
        swmf_root=root.swmf_root_resolved,
        query=question,
        mode=mode,
        scope=resolved_scope,
        top_k=top_k,
        goal=resolved_task_type,
    )

    entities = enrich_entities_from_evidence(entities, evidence)

    # --- Summary assembly ---
    n_components = len(entities["components"])
    n_files = len(entities["files"])
    if n_components:
        summary = (
            f"Orientation for '{question}': {n_components} component(s) "
            f"({', '.join(entities['components'][:4])}), {n_files} file(s) in scope. {ev_summary}."
        )
    else:
        summary = f"Orientation for '{question}': {ev_summary}."

    known_unknowns: list[str] = []
    if degraded_reason:
        known_unknowns.append(degraded_reason)
    known_unknowns.append("Runtime state and current PARAM.in not inspected.")

    payload: dict[str, Any] = {
        "ok": True,
        "question": question,
        "task_type": resolved_task_type,
        "detail": resolved_detail,
        "scope": resolved_scope,
        "summary": summary,
        "entities": entities,
        "evidence": evidence,
        "provenance": {"backend_used": f"knowledge_index:{mode_used}"},
        "uncertainty": {"known_unknowns": known_unknowns},
    }
    return with_root(payload, root)


def register(app: Any) -> None:
    app.tool(
        description=(
            "Give the agent compact repo/task orientation for a question. "
            "Use for architecture questions, multi-component questions, or 'what area of the "
            "codebase matters?' Returns entities (components, files, params, symbols), "
            "a compact summary, and provenance."
        )
    )(get_context)
