"""MCP tool registrations for the SWMF knowledge domain.

The knowledge domain owns semantic understanding, query interpretation, and
agent-facing context assembly. It may consume the catalog and reference
domains, but it is not the authoritative source of truth.
"""
from __future__ import annotations

from typing import Any

from ..core.authority import AUTHORITY_HEURISTIC
from ..knowledge import service as ks
from ._helpers import resolve_root_or_failure, with_root


def swmf_build_knowledge_index(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_rebuild: bool = False,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> dict[str, Any]:
    """Prepare the evidence index used by knowledge search and context packs."""
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    status = ks.build_index(
        root.swmf_root_resolved,
        force=force_rebuild,
        swmfsolar_root=swmfsolar_root,
        mcp_repo_root=mcp_repo_root,
    )

    payload = ks.status_as_payload(status)
    payload["action"] = "force_rebuild" if force_rebuild else "build"
    return with_root(payload, root)


def swmf_search_knowledge(
    query: str,
    component: str | None = None,
    kind: str | None = None,
    corpus_slice: str | None = None,
    max_results: int = 20,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    search_mode: str | None = None,
    similarity_threshold: float | None = None,
) -> dict[str, Any]:
    """Run knowledge retrieval with query understanding and semantic ranking when available."""
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    query_analysis = ks.understand_source_query(query)
    requested_mode = search_mode or query_analysis.get("preferred_search_mode") or "keyword"
    status = ks.ensure_index_ready(root.swmf_root_resolved)
    if not status.ok or status.is_stale:
        return with_root(
            {
                "ok": False,
                "error_code": "KNOWLEDGE_INDEX_PREP_FAILED",
                "message": "Knowledge index could not be prepared automatically.",
                "how_to_fix": [
                    "Call swmf_refresh_knowledge_index to build or update the index manually."
                ],
                "index_status": ks.status_as_payload(status),
                "authority": AUTHORITY_HEURISTIC,
            },
            root,
        )

    max_results = min(max(1, max_results), 100)
    attempted_queries = [query]
    search_payload = ks.search_source(
        root.swmf_root_resolved,
        query=query,
        component=component,
        kind=kind,
        corpus_slice=corpus_slice,
        max_results=max_results,
        search_mode=requested_mode,
        similarity_threshold=similarity_threshold,
        ensure_ready=False,
    )
    if not search_payload["results"]:
        for term in query_analysis.get("focus_terms", []):
            if term == query:
                continue
            attempted_queries.append(term)
            candidate_payload = ks.search_source(
                root.swmf_root_resolved,
                query=term,
                component=component,
                kind=kind,
                corpus_slice=corpus_slice,
                max_results=max_results,
                search_mode=requested_mode,
                similarity_threshold=similarity_threshold,
                ensure_ready=False,
            )
            if candidate_payload["results"]:
                search_payload = candidate_payload
                break
    results = list(search_payload["results"])

    return with_root(
        {
            "ok": True,
            "query": query,
            "filters": {
                "component": component,
                "kind": kind,
                "corpus_slice": corpus_slice,
                "search_mode": search_payload["search_mode_requested"],
                "similarity_threshold": similarity_threshold,
            },
            "query_analysis": query_analysis,
            "attempted_queries": attempted_queries,
            "result_count": len(results),
            "results": results,
            "search_method": search_payload["search_method"],
            "search_mode_requested": search_payload["search_mode_requested"],
            "semantic_available": search_payload["semantic_available"],
            "semantic_degraded_reason": search_payload["semantic_degraded_reason"],
            "semantic_runtime": search_payload["semantic_runtime"],
            "similarity_threshold": search_payload["similarity_threshold"],
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": "source_index",
            "note": (
                "Results are heuristic (regex/FTS5-based). "
                "Use PARAM.XML and TestParam.pl for authoritative validation."
            ),
        },
        root,
    )


def swmf_understand_source_query(query: str) -> dict[str, Any]:
    """Classify a source question and recommend evidence slices for retrieval."""
    payload = ks.understand_source_query(query)
    payload["ok"] = True
    return payload


def swmf_get_agent_context_pack(
    query: str,
    max_results: int = 8,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    search_mode: str | None = None,
    similarity_threshold: float | None = None,
) -> dict[str, Any]:
    """Build an agent-facing context pack grounded in catalog and reference evidence."""
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    payload = ks.get_agent_context_pack(
        root.swmf_root_resolved,
        query=query,
        max_results=max_results,
        search_mode=search_mode,
        similarity_threshold=similarity_threshold,
        ensure_ready=True,
    )
    return with_root(payload, root)

def swmf_get_knowledge_status(
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Return the current knowledge readiness status and embedding runtime details."""
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    status = ks.get_index_status(root.swmf_root_resolved)
    payload = ks.status_as_payload(status)
    if not status.ok or status.is_stale:
        payload.setdefault(
            "how_to_fix",
            ["Call swmf_build_knowledge_index to prepare the knowledge evidence index."],
        )
    return with_root(payload, root)


def register(app: Any) -> None:
    app.tool(
        description=(
            "Prepare the evidence index used by SWMF knowledge retrieval and agent context generation. "
            "The embedding runtime is loaded lazily after the index is prepared."
        )
    )(swmf_build_knowledge_index)
    app.tool(
        description=(
            "Search SWMF knowledge using query understanding plus keyword, semantic, or hybrid ranking depending on availability."
        )
    )(swmf_search_knowledge)
    app.tool(
        description=(
            "Classify a source question and return recommended components, PARAM commands, and corpus slices before retrieval."
        )
    )(swmf_understand_source_query)
    app.tool(
        description=(
            "Build an agent-facing context pack grounded in catalog results and authoritative reference lookups."
        )
    )(swmf_get_agent_context_pack)
    app.tool(
        description=(
            "Return the current knowledge readiness status, including embedding runtime metadata and index staleness."
        )
    )(swmf_get_knowledge_status)
