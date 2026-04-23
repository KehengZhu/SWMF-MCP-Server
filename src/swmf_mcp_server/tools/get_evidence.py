"""Public API tool: get_evidence.

Purpose
-------
Retrieve grounded local evidence for a query. This is the main retrieval tool.
All evidence is local (source files, PARAM.XML, catalogs, knowledge index).
The caller specifies a query and optional retrieval mode; the server routes
internally across keyword, semantic, or hybrid backends.

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
  "score": float
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
swmf_root : Optional explicit SWMF source root path.
run_dir   : Optional run directory used for root resolution.
"""

from __future__ import annotations

from typing import Any

from ._helpers import resolve_root_or_failure, with_root
from ._router import run_evidence_search

_VALID_MODES = frozenset({"hybrid", "keyword", "semantic"})
_DEFAULT_TOP_K = 8
_MAX_TOP_K = 100


def get_evidence(
    query: str,
    mode: str | None = None,
    scope: list[str] | None = None,
    top_k: int = _DEFAULT_TOP_K,
    goal: str | None = None,
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
    resolved_scope: list[str] = [s.upper() for s in (scope or [])]
    resolved_top_k = max(1, min(int(top_k), _MAX_TOP_K))

    assert root.swmf_root_resolved is not None
    evidence, mode_used, summary, degraded_reason = run_evidence_search(
        swmf_root=root.swmf_root_resolved,
        query=query,
        mode=resolved_mode,
        scope=resolved_scope,
        top_k=resolved_top_k,
        goal=goal or "",
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
        "summary": summary,
        "evidence": evidence,
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
            "for general retrieval. Optionally restrict to SWMF components via scope."
        )
    )(get_evidence)
