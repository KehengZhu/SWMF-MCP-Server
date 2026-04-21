"""Shared retrieval API for the SWMF knowledge base.

All specialist skills should call this service rather than building their own
search logic.  The service maintains one
:class:`~swmf_mcp_server.catalog.source_index_catalog.SourceIndexCatalog`
per resolved SWMF root and provides a stable, domain-aware query interface.

Multi-root support
------------------
``build_index`` and ``refresh_index`` accept optional ``swmfsolar_root`` and
``mcp_repo_root`` parameters.  When supplied, those directories are indexed
alongside the primary SWMF root into the same SQLite database.

Authority contract
------------------
All results carry ``authority="heuristic"`` — they are derived from
regex-based source parsing.  They supplement but never override authoritative
sources (PARAM.XML, TestParam.pl outputs).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..catalog.source_index_catalog import (
    SLICE_SWMFSOLAR_SOURCE,
    SLICE_ANALYST_CONTEXT,
    SourceIndexCatalog,
)
from ..core.models import KnowledgeIndexStatus

# ---------------------------------------------------------------------------
# Singleton service
# ---------------------------------------------------------------------------

_INDEX_BY_ROOT: dict[str, SourceIndexCatalog] = {}


def _looks_like_swmfsolar_root(path: Path) -> bool:
    return (path / "Makefile").is_file() and (path / "Scripts").is_dir()


def _looks_like_mcp_repo_root(path: Path) -> bool:
    return (path / "pyproject.toml").is_file() and (path / "src" / "swmf_mcp_server").is_dir()


def _dedupe_extra_roots(roots: list[tuple[str, str]]) -> list[tuple[str, str]]:
    deduped: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw_path, slice_name in roots:
        key = (str(Path(raw_path).resolve()), slice_name)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(key)
    return deduped


def _discover_default_swmfsolar_root(swmf_root: str) -> str | None:
    primary_root = Path(swmf_root).resolve()
    candidate = primary_root.parent / "SWMFSOLAR"
    if _looks_like_swmfsolar_root(candidate):
        return str(candidate.resolve())
    return None


def _discover_default_mcp_repo_root(swmf_root: str) -> str | None:
    primary_root = Path(swmf_root).resolve()
    repo_root = Path(__file__).resolve().parents[3]
    if primary_root.parent != repo_root.parent:
        return None
    if _looks_like_mcp_repo_root(repo_root):
        return str(repo_root.resolve())
    return None


def _get_catalog(
    swmf_root: str,
    extra_roots: list[tuple[str, str]] | None = None,
) -> SourceIndexCatalog:
    """Return (possibly cached) :class:`SourceIndexCatalog` for *swmf_root*.

    When *extra_roots* is provided, a fresh catalog is created and cached so
    subsequent read calls (search, lookup) use the same extra-roots config.
    """
    key = str(Path(swmf_root).resolve())
    if extra_roots is not None:
        inst = SourceIndexCatalog(key, extra_roots=extra_roots)
        _INDEX_BY_ROOT[key] = inst
        return inst
    if key not in _INDEX_BY_ROOT:
        _INDEX_BY_ROOT[key] = SourceIndexCatalog(key)
    return _INDEX_BY_ROOT[key]


def _build_extra_roots(
    swmf_root: str,
    swmfsolar_root: str | None,
    mcp_repo_root: str | None,
) -> list[tuple[str, str]] | None:
    """Collect extra_roots list from optional root paths; None if empty."""
    roots: list[tuple[str, str]] = []
    if swmfsolar_root:
        roots.append((swmfsolar_root, SLICE_SWMFSOLAR_SOURCE))
    else:
        auto_swmfsolar_root = _discover_default_swmfsolar_root(swmf_root)
        if auto_swmfsolar_root:
            roots.append((auto_swmfsolar_root, SLICE_SWMFSOLAR_SOURCE))
    if mcp_repo_root:
        roots.append((mcp_repo_root, SLICE_ANALYST_CONTEXT))
    else:
        auto_mcp_repo_root = _discover_default_mcp_repo_root(swmf_root)
        if auto_mcp_repo_root:
            roots.append((auto_mcp_repo_root, SLICE_ANALYST_CONTEXT))
    deduped = _dedupe_extra_roots(roots)
    return deduped if deduped else None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_index_status(swmf_root: str) -> KnowledgeIndexStatus:
    """Return the current index status without triggering a build."""
    return _get_catalog(swmf_root).get_status()


def build_index(
    swmf_root: str,
    force: bool = False,
    *,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> KnowledgeIndexStatus:
    """Build or rebuild the knowledge index for *swmf_root*.

    Parameters
    ----------
    swmfsolar_root:
        Optional path to an SWMFSOLAR checkout.  Its files will be indexed
        alongside the primary SWMF root with corpus_slice ``"swmfsolar_source"``.
    mcp_repo_root:
        Optional path to the MCP prototype repo.  Markdown docs will be
        indexed with corpus_slice ``"analyst_context"``.
    """
    extra = _build_extra_roots(swmf_root, swmfsolar_root, mcp_repo_root)
    return _get_catalog(swmf_root, extra_roots=extra).build(force=force)


def refresh_index(
    swmf_root: str,
    *,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> KnowledgeIndexStatus:
    """Incrementally update the index (add new, re-index changed, drop deleted)."""
    extra = _build_extra_roots(swmf_root, swmfsolar_root, mcp_repo_root)
    return _get_catalog(swmf_root, extra_roots=extra).refresh()


def ensure_index_ready(
    swmf_root: str,
    *,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> KnowledgeIndexStatus:
    """Ensure the knowledge index exists and is current before retrieval.

    Retrieval callers use this to avoid a separate manual build step on the
    first search/lookup/evidence request.
    """
    extra = _build_extra_roots(swmf_root, swmfsolar_root, mcp_repo_root)
    catalog = _get_catalog(swmf_root, extra_roots=extra)
    status = catalog.get_status()
    if not status.ok or status.is_stale:
        return catalog.refresh()
    return status


def search_symbols(
    swmf_root: str,
    query: str,
    component: str | None = None,
    kind: str | None = None,
    corpus_slice: str | None = None,
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """Keyword search across symbol names, docstrings, and doc sections.

    Returns a list of symbol records, each with:
    ``name``, ``kind``, ``file_path``, ``start_line``, ``component``,
    ``docstring``, ``source_kind``, ``authority``, ``uses``,
    ``corpus_root``, ``corpus_slice``.
    """
    ensure_index_ready(swmf_root)
    return _get_catalog(swmf_root).search_symbols(
        query=query, component=component, kind=kind,
        corpus_slice=corpus_slice, max_results=max_results,
    )


def lookup_symbol(
    swmf_root: str,
    name: str,
    kind: str | None = None,
) -> list[dict[str, Any]]:
    """Exact (case-insensitive) symbol name lookup.

    Returns all matching symbols across all indexed languages.
    """
    ensure_index_ready(swmf_root)
    return _get_catalog(swmf_root).lookup_symbol(name=name, kind=kind)


def get_param_evidence(
    swmf_root: str,
    command_normalized: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Return heuristic source evidence for a PARAM command.

    Combines explicit ``param_mentions`` extracted during indexing with a
    text-search fallback.  All results carry ``authority="heuristic"``.

    Parameters
    ----------
    command_normalized:
        PARAM command name without the ``#`` prefix and uppercased,
        e.g. ``"STOP"`` or ``"MAGNETOGRAM"``.
    """
    ensure_index_ready(swmf_root)
    return _get_catalog(swmf_root).get_param_evidence(
        command_normalized=command_normalized.upper(),
        max_results=max_results,
    )


def get_file_symbols(swmf_root: str, file_path: str) -> list[dict[str, Any]]:
    """Return all symbols indexed from *file_path* (absolute path)."""
    ensure_index_ready(swmf_root)
    return _get_catalog(swmf_root).get_file_symbols(file_path=file_path)


def status_as_payload(status: KnowledgeIndexStatus) -> dict[str, Any]:
    """Serialize a :class:`KnowledgeIndexStatus` to a clean MCP response dict."""
    return {
        "ok": status.ok,
        "db_path": status.db_path,
        "swmf_root": status.swmf_root,
        "schema_version": status.schema_version,
        "symbol_count": status.symbol_count,
        "file_count": status.file_count,
        "last_built_epoch_s": status.last_built_epoch_s,
        "is_stale": status.is_stale,
        "message": status.message,
        "corpus_roots": status.corpus_roots,
    }
