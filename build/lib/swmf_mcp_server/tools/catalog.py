"""Named MCP tools for the catalog domain.

The catalog domain owns source indexing and keyword retrieval only.
Semantic ranking and agent grounding are exposed separately through the
knowledge-domain tool family.
"""

from __future__ import annotations

from typing import Any

from ..core.authority import AUTHORITY_HEURISTIC
from ..knowledge import service as ks
from ._helpers import resolve_root_or_failure, with_root


def _catalog_status_payload(status: Any) -> dict[str, Any]:
    payload = ks.status_as_payload(status)
    payload.pop("semantic_runtime", None)
    return payload


def swmf_build_catalog_index(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_rebuild: bool = False,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> dict[str, Any]:
    """Build the keyword catalog index used for source lookup."""
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
    payload = _catalog_status_payload(status)
    payload["action"] = "force_rebuild" if force_rebuild else "build"
    return with_root(payload, root)


def swmf_refresh_catalog_index(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> dict[str, Any]:
    """Incrementally refresh the keyword catalog index."""
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    status = ks.refresh_index(
        root.swmf_root_resolved,
        swmfsolar_root=swmfsolar_root,
        mcp_repo_root=mcp_repo_root,
    )
    payload = _catalog_status_payload(status)
    payload["action"] = "refresh"
    return with_root(payload, root)


def swmf_get_catalog_status(
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Return the current keyword catalog index status."""
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    status = ks.get_index_status(root.swmf_root_resolved)
    payload = _catalog_status_payload(status)
    if not status.ok or status.is_stale:
        payload.setdefault(
            "how_to_fix",
            ["Call swmf_build_catalog_index or swmf_refresh_catalog_index to prepare the catalog index."],
        )
    return with_root(payload, root)


def swmf_search_catalog(
    query: str,
    component: str | None = None,
    kind: str | None = None,
    corpus_slice: str | None = None,
    max_results: int = 20,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Run keyword-only catalog search across indexed SWMF sources."""
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    status = ks.ensure_index_ready(root.swmf_root_resolved)
    if not status.ok or status.is_stale:
        return with_root(
            {
                "ok": False,
                "error_code": "CATALOG_INDEX_PREP_FAILED",
                "message": "Catalog index could not be prepared automatically.",
                "how_to_fix": [
                    "Call swmf_build_catalog_index to build the index or swmf_refresh_catalog_index to refresh it."
                ],
                "index_status": _catalog_status_payload(status),
                "authority": AUTHORITY_HEURISTIC,
            },
            root,
        )

    max_results = min(max(1, max_results), 100)
    results = ks.search_symbols(
        root.swmf_root_resolved,
        query=query,
        component=component,
        kind=kind,
        corpus_slice=corpus_slice,
        max_results=max_results,
        ensure_ready=False,
    )
    return with_root(
        {
            "ok": True,
            "query": query,
            "filters": {
                "component": component,
                "kind": kind,
                "corpus_slice": corpus_slice,
            },
            "result_count": len(results),
            "results": results,
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": "catalog_index",
            "search_method": "keyword",
            "note": "Catalog search is keyword-only. Use knowledge tools for semantic ranking and agent grounding.",
        },
        root,
    )


def swmf_lookup_catalog_symbol(
    name: str,
    kind: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Look up an exact symbol name in the keyword catalog."""
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    status = ks.ensure_index_ready(root.swmf_root_resolved)
    if not status.ok or status.is_stale:
        return with_root(
            {
                "ok": False,
                "error_code": "CATALOG_INDEX_PREP_FAILED",
                "message": "Catalog index could not be prepared automatically.",
                "how_to_fix": [
                    "Call swmf_build_catalog_index to build the index or swmf_refresh_catalog_index to refresh it."
                ],
                "index_status": _catalog_status_payload(status),
            },
            root,
        )

    matches = ks.lookup_symbol(
        root.swmf_root_resolved,
        name=name,
        kind=kind,
        ensure_ready=False,
    )
    return with_root(
        {
            "ok": True,
            "name": name,
            "kind_filter": kind,
            "match_count": len(matches),
            "matches": matches,
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": "catalog_index",
        },
        root,
    )


def register(app: Any) -> None:
    app.tool(
        description="Build the keyword-only SWMF catalog index used for source lookup."
    )(swmf_build_catalog_index)
    app.tool(
        description="Incrementally refresh the keyword-only SWMF catalog index."
    )(swmf_refresh_catalog_index)
    app.tool(
        description="Return keyword catalog status without modifying the index."
    )(swmf_get_catalog_status)
    app.tool(
        description="Run keyword-only search across indexed SWMF symbols and docs."
    )(swmf_search_catalog)
    app.tool(
        description="Look up an exact symbol name in the keyword-only SWMF catalog."
    )(swmf_lookup_catalog_symbol)