"""Public API tool: get_evidence.

Purpose
-------
Retrieve grounded local evidence for a query. This is the main retrieval tool.
All evidence is local (source files, PARAM.XML, catalogs, knowledge index).
The caller specifies a query and optional retrieval mode; the server routes
internally across keyword, semantic, or hybrid backends. Workflow discovery is
handled as a `task_type` use case rather than a separate tool.

Internal backends (hidden from caller)
---------------------------------------
- keyword search (BM25 / catalog)
- semantic search (embedding index)
- hybrid (default: keyword + semantic, reranked)
- symbol lookup
- catalog lookup

Output contract
---------------
{
  "summary": str,
  "evidence": list[EvidenceItem],
  "provenance": {"mode_used": str, "scope": list[str]},
  "uncertainty": {"known_unknowns": list[str]}
}

EvidenceItem shape
------------------
{
  "type": "param_spec" | "code" | "doc" | "example" | "coupling" | "idl",
  "path": str,
  "snippet": str,
  "score": float,
  "metadata": {
    "kind": str,
    "relative_path": str,
    "why_relevant": str
  }
}

Example request
---------------
{
  "query": "DoCoupleGMIE",
  "mode": "hybrid",
  "scope": ["GM", "IE"],
  "top_k": 8,
  "goal": "find definition and usage"
}

Example response
----------------
{
  "summary": "4 relevant evidence items found for DoCoupleGMIE",
  "evidence": [
    {"type": "param_spec", "path": "PARAM.XML", "snippet": "...", "score": 0.91},
    {"type": "code", "path": "GM/src/ModUser.f90", "snippet": "...", "score": 0.87}
  ],
  "provenance": {"mode_used": "hybrid", "scope": ["GM", "IE"]},
  "uncertainty": {"known_unknowns": ["runtime behavior not inspected"]}
}

Field semantics
---------------
query   : Required. The search query, token, symbol name, or natural-language question.
mode    : Optional retrieval mode.
          "hybrid"   — keyword + semantic, reranked (default).
          "keyword"  — BM25 / catalog / exact match. Use when query contains precise tokens.
          "semantic" — embedding similarity only.
scope   : Optional list of SWMF component IDs to restrict retrieval (e.g. ["GM","IE"]).
top_k   : Optional max number of evidence items to return. Default 8, max 100.
goal    : Optional freeform description of what the agent is trying to accomplish.
          Used to improve reranking and snippet selection.
task_type: Optional workflow hint. Use "lookup" for ordinary evidence retrieval,
          or "configuration", "build", "run", "analysis" for workflow evidence.
module  : Optional component hint used when collecting workflow evidence.
swmf_root : Optional explicit SWMF source root path.
run_dir   : Optional run directory used for root resolution.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ._helpers import resolve_root_or_failure, with_root
from ._router import run_evidence_search
from ._workflow import discover_workflow_entrypoints

_VALID_MODES = frozenset({"hybrid", "keyword", "semantic"})
_VALID_TASK_TYPES = frozenset({"lookup", "configuration", "build", "run", "analysis"})
_DEFAULT_TOP_K = 8
_MAX_TOP_K = 100


def _normalize_task_type(task_type: str | None) -> str:
    if task_type in _VALID_TASK_TYPES:
        return task_type
    return "lookup"


def _normalize_module(module: str | None) -> str | None:
    value = (module or "").strip().upper()
    return value or None


def _append_unique_scope(scope: list[str], module: str | None) -> list[str]:
    resolved = [item.upper() for item in scope]
    if module and module not in resolved:
        resolved.append(module)
    return resolved


def _relative_path(root: Path, candidate_path: str) -> str:
    candidate = Path(candidate_path)
    try:
        if candidate.is_absolute():
            return str(candidate.resolve().relative_to(root.resolve()))
        return str(candidate)
    except Exception:
        return str(candidate)


def _workflow_metadata(
    root: Path,
    item: dict[str, Any],
    *,
    default_kind: str,
    default_why: str,
) -> dict[str, Any]:
    metadata = dict(item.get("metadata") or {})
    metadata.setdefault("kind", item.get("kind") or default_kind)
    metadata.setdefault("relative_path", _relative_path(root, item.get("path", "")))
    metadata.setdefault("why_relevant", default_why)
    return metadata


def _merge_evidence(
    primary: list[dict[str, Any]],
    secondary: list[dict[str, Any]],
    top_k: int,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in primary + secondary:
        key = (str(item.get("path", "")), str(item.get("snippet", "")))
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
        if len(merged) >= top_k:
            break
    return merged


def get_evidence(
    query: str,
    mode: str | None = None,
    scope: list[str] | None = None,
    top_k: int = _DEFAULT_TOP_K,
    goal: str | None = None,
    task_type: str | None = None,
    module: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Retrieve grounded local evidence for a query.

    Use for symbol/param/file lookup, exact questions, supporting snippets for
    a claim, or evidence gathering before answering. Hybrid mode (default) runs
    keyword + semantic search and reranks. Use keyword when the query is a
    precise token or symbol name. Use semantic for natural-language questions.
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    resolved_mode = mode if mode in _VALID_MODES else "hybrid"
    resolved_task_type = _normalize_task_type(task_type)
    resolved_module = _normalize_module(module)
    resolved_scope = _append_unique_scope(list(scope or []), resolved_module)
    resolved_top_k = max(1, min(int(top_k), _MAX_TOP_K))
    goal_text = goal or query

    assert root.swmf_root_resolved is not None

    workflow_evidence: list[dict[str, Any]] = []
    if resolved_task_type != "lookup":
        workflow_items = discover_workflow_entrypoints(
            root.swmf_root_resolved,
            resolved_module,
            resolved_task_type,
        )
        root_path = Path(root.swmf_root_resolved)
        for item in workflow_items:
            item["metadata"] = _workflow_metadata(
                root_path,
                item,
                default_kind="workflow_entrypoint",
                default_why=f"Known {resolved_task_type} entrypoint",
            )
        workflow_evidence = workflow_items

    evidence, mode_used, support_summary, degraded_reason = run_evidence_search(
        swmf_root=root.swmf_root_resolved,
        query=f"{resolved_module} {goal_text}".strip() if resolved_module else goal_text,
        mode=resolved_mode,
        scope=resolved_scope,
        top_k=resolved_top_k,
        goal=goal_text,
    )

    root_path = Path(root.swmf_root_resolved)
    if resolved_task_type != "lookup":
        for item in evidence:
            item["metadata"] = _workflow_metadata(
                root_path,
                item,
                default_kind=item.get("kind") or item.get("type", "code"),
                default_why=f"Supporting {resolved_task_type} evidence from search",
            )

    if resolved_task_type == "lookup":
        combined_evidence = evidence
        summary = support_summary
    else:
        combined_evidence = _merge_evidence(workflow_evidence, evidence, resolved_top_k)
        workflow_returned = min(len(workflow_evidence), len(combined_evidence))
        support_count = max(0, len(combined_evidence) - workflow_returned)
        summary = (
            f"{workflow_returned} workflow evidence item(s) and "
            f"{support_count} supporting evidence item(s) found for '{query}'"
        )

    known_unknowns: list[str] = []
    if degraded_reason:
        known_unknowns.append(degraded_reason)
    known_unknowns.append("Runtime behavior for the current case not inspected.")

    payload: dict[str, Any] = {
        "ok": True,
        "query": query,
        "mode": resolved_mode,
        "scope": resolved_scope,
        "top_k": resolved_top_k,
        "goal": goal or "",
        "task_type": resolved_task_type,
        "module": resolved_module,
        "summary": summary,
        "evidence": combined_evidence,
        "provenance": {"mode_used": mode_used, "scope": resolved_scope},
        "uncertainty": {"known_unknowns": known_unknowns},
    }
    return with_root(payload, root)


def register(app: Any) -> None:
    app.tool(
        description=(
            "Retrieve grounded local evidence for a query (source code, PARAM.XML, docs, "
            "examples, IDL). Use mode='keyword' for precise token/symbol lookup, "
            "mode='semantic' for natural-language questions, mode='hybrid' (default) "
            "for general retrieval. Use task_type='configuration'|'build'|'run'|'analysis' "
            "when you want workflow entrypoint evidence returned through the same tool. "
            "Optionally restrict to SWMF components via scope or module."
        )
    )(get_evidence)
