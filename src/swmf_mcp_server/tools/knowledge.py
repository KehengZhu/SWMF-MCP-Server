"""MCP tool registrations for the SWMF knowledge base.

Tools exposed
-------------
swmf_refresh_knowledge_index
    Build or incrementally refresh the persistent source index.

swmf_search_source
    Keyword search across indexed symbols (names + docstrings).

swmf_lookup_source_symbol
    Exact symbol name lookup across all indexed languages.

swmf_get_param_source_evidence
    Retrieve heuristic source evidence for a PARAM command.

swmf_get_knowledge_index_status
    Check the current status of the persistent index without modifying it.

Authority contract
------------------
All results carry ``authority="heuristic"``.  They supplement but never
override PARAM.XML definitions or TestParam.pl validation results.
"""
from __future__ import annotations

from typing import Any

from ..core import knowledge_service as ks
from ..core.authority import AUTHORITY_HEURISTIC
from ._helpers import resolve_root_or_failure, with_root


def swmf_refresh_knowledge_index(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_rebuild: bool = False,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> dict[str, Any]:
    """Build or refresh the persistent SWMF source knowledge index.

    On first call this performs a full scan of the SWMF source tree; subsequent
    calls do an incremental update (only changed or new files are re-indexed).
    Pass ``force_rebuild=True`` to wipe and rebuild from scratch.

    The index is stored at ``{swmf_root}/.swmf_mcp_cache/knowledge.db`` (or
    ``$SWMF_MCP_KNOWLEDGE_DB`` if set).  This directory is not checked into git.

    Parameters
    ----------
    swmfsolar_root:
        Optional path to an SWMFSOLAR checkout to co-index alongside SWMF.
    mcp_repo_root:
        Optional path to the MCP prototype repo; its Markdown docs will be
        indexed as ``analyst_context`` for broad knowledge queries.

    Returns the index status after the build/refresh completes.
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    if force_rebuild:
        status = ks.build_index(
            root.swmf_root_resolved, force=True,
            swmfsolar_root=swmfsolar_root, mcp_repo_root=mcp_repo_root,
        )
    else:
        status = ks.refresh_index(
            root.swmf_root_resolved,
            swmfsolar_root=swmfsolar_root, mcp_repo_root=mcp_repo_root,
        )

    payload = ks.status_as_payload(status)
    payload["action"] = "force_rebuild" if force_rebuild else "refresh"
    return with_root(payload, root)


def swmf_search_source(
    query: str,
    component: str | None = None,
    kind: str | None = None,
    corpus_slice: str | None = None,
    max_results: int = 20,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Broad keyword search across the indexed SWMF corpus.

    Searches symbol names, docstrings, and documentation sections using FTS5
    BM25 ranking (falls back to LIKE matching).  Covers Fortran, Perl, IDL
    source files plus TeX manuals and Markdown docs from all indexed repos.

    Parameters
    ----------
    query:
        Search term (e.g. ``"ReadParam"``, ``"magnetogram"``, ``"STOP"``,
        ``"IH SC coupling"``).
    component:
        Optional two-letter component filter (e.g. ``"GM"``, ``"SC"``).
    kind:
        Optional symbol kind filter: ``"subroutine"``, ``"function"``,
        ``"module"``, ``"sub"`` (Perl), ``"pro"`` (IDL), or
        ``"doc_section"`` for documentation chunks.
    corpus_slice:
        Optional corpus partition filter: ``"swmf_source"``,
        ``"swmfsolar_source"``, ``"swmf_manuals"``, ``"swmf_scripts"``,
        or ``"analyst_context"``.
    max_results:
        Maximum number of results to return (default 20, max 100).
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
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
    results = ks.search_symbols(
        root.swmf_root_resolved,
        query=query,
        component=component,
        kind=kind,
        corpus_slice=corpus_slice,
        max_results=max_results,
    )

    return with_root(
        {
            "ok": True,
            "query": query,
            "filters": {"component": component, "kind": kind, "corpus_slice": corpus_slice},
            "result_count": len(results),
            "results": results,
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": "source_index",
            "note": (
                "Results are heuristic (regex/FTS5-based). "
                "Use PARAM.XML and TestParam.pl for authoritative validation."
            ),
        },
        root,
    )


def swmf_lookup_source_symbol(
    name: str,
    kind: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Exact (case-insensitive) symbol name lookup in the knowledge index.

    Returns all definitions across indexed languages (Fortran, Perl, IDL).

    Parameters
    ----------
    name:
        Exact symbol name, e.g. ``"ReadParam"`` or ``"read_magnetogram_file"``.
    kind:
        Optional kind filter (``"subroutine"``, ``"function"``, etc.).
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
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
            },
            root,
        )

    matches = ks.lookup_symbol(root.swmf_root_resolved, name=name, kind=kind)
    return with_root(
        {
            "ok": True,
            "name": name,
            "kind_filter": kind,
            "match_count": len(matches),
            "matches": matches,
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": "source_index",
        },
        root,
    )


def swmf_get_param_source_evidence(
    command: str,
    max_results: int = 10,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Retrieve heuristic source evidence for a PARAM command.

    Searches the knowledge index for symbols and files that reference the
    given PARAM command (e.g. ``"#STOP"`` or ``"STOP"`` or ``"#MAGNETOGRAM"``).

    Returns explicit ``param_mentions`` (extracted during indexing) plus
    text-match fallbacks.  All results carry ``authority="heuristic"``.

    This is meant to *supplement* authoritative PARAM.XML and TestParam.pl
    results, not replace them.
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
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
            },
            root,
        )

    # Normalize: strip leading '#' and uppercase
    normalized = command.lstrip("#").strip().upper()
    max_results = min(max(1, max_results), 50)
    evidence = ks.get_param_evidence(
        root.swmf_root_resolved,
        command_normalized=normalized,
        max_results=max_results,
    )

    return with_root(
        {
            "ok": True,
            "command": f"#{normalized}",
            "command_normalized": normalized,
            "evidence_count": len(evidence),
            "evidence": evidence,
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": "source_index",
            "note": (
                "Source evidence is heuristic. "
                "Authoritative parameter definitions remain in PARAM.XML; "
                "authoritative validation is performed by TestParam.pl."
            ),
        },
        root,
    )


def swmf_get_knowledge_index_status(
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Check the current status of the persistent knowledge index.

    Returns symbol count, file count, build time, and whether the index is
    stale.  Does not modify the index.
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    assert root.swmf_root_resolved is not None
    status = ks.get_index_status(root.swmf_root_resolved)
    payload = ks.status_as_payload(status)
    if not status.ok or status.is_stale:
        payload.setdefault(
            "how_to_fix",
            ["Call swmf_refresh_knowledge_index to build or update the index."],
        )
    return with_root(payload, root)


def register(app: Any) -> None:
    app.tool(
        description=(
            "Broad keyword search across the indexed SWMF corpus: Fortran subroutines, "
            "Perl subs, IDL procedures, TeX manual sections, and Markdown docs from all "
            "indexed repos (SWMF, SWMFSOLAR, MCP repo). Uses FTS5 BM25 ranking. "
            "All results are heuristic; the index is prepared automatically on first use."
        )
    )(swmf_search_source)
    app.tool(
        description=(
            "Look up a specific symbol by name in the SWMF knowledge index. "
            "Returns definition location, kind, and docstring. Heuristic only; auto-builds the index on first use."
        )
    )(swmf_lookup_source_symbol)
    app.tool(
        description=(
            "Check the current status of the SWMF knowledge index: symbol count, "
            "file count, build time, and staleness. Does not modify the index."
        )
    )(swmf_get_knowledge_index_status)
