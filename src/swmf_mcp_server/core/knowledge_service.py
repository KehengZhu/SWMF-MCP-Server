"""Shared retrieval API for the SWMF knowledge base.

All specialist skills (param-specialist, build-specialist, coupling-specialist,
etc.) should call this service instead of building their own search logic.  The
service maintains one :class:`~swmf_mcp_server.catalog.source_index_catalog.SourceIndexCatalog`
per resolved SWMF root and provides a stable, domain-aware query interface.

Authority contract
------------------
All results from this service carry ``authority="heuristic"`` — they are
derived from regex-based source parsing.  They supplement but never override
authoritative sources (PARAM.XML, TestParam.pl outputs).  Callers must keep
this tier split explicit in their MCP responses.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..catalog.source_index_catalog import SourceIndexCatalog
from ..core.models import KnowledgeIndexStatus

# ---------------------------------------------------------------------------
# Singleton service
# ---------------------------------------------------------------------------

_INDEX_BY_ROOT: dict[str, SourceIndexCatalog] = {}


def _get_catalog(swmf_root: str) -> SourceIndexCatalog:
    """Return (cached) :class:`SourceIndexCatalog` for *swmf_root*."""
    key = str(Path(swmf_root).resolve())
    if key not in _INDEX_BY_ROOT:
        _INDEX_BY_ROOT[key] = SourceIndexCatalog(key)
    return _INDEX_BY_ROOT[key]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_index_status(swmf_root: str) -> KnowledgeIndexStatus:
    """Return the current index status without triggering a build."""
    return _get_catalog(swmf_root).get_status()


def build_index(swmf_root: str, force: bool = False) -> KnowledgeIndexStatus:
    """Build or rebuild the knowledge index for *swmf_root*.

    If the index is already fresh and *force* is False the call is a no-op.
    """
    return _get_catalog(swmf_root).build(force=force)


def refresh_index(swmf_root: str) -> KnowledgeIndexStatus:
    """Incrementally update the index (add new, re-index changed, drop deleted)."""
    return _get_catalog(swmf_root).refresh()


def search_symbols(
    swmf_root: str,
    query: str,
    component: str | None = None,
    kind: str | None = None,
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """Keyword search across symbol names and docstrings.

    Returns a list of symbol records, each with:
    ``name``, ``kind``, ``file_path``, ``start_line``, ``component``,
    ``docstring``, ``source_kind``, ``authority``, ``uses``.
    """
    return _get_catalog(swmf_root).search_symbols(
        query=query, component=component, kind=kind, max_results=max_results
    )


def lookup_symbol(
    swmf_root: str,
    name: str,
    kind: str | None = None,
) -> list[dict[str, Any]]:
    """Exact (case-insensitive) symbol name lookup.

    Returns all matching symbols across all indexed languages.
    """
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
    return _get_catalog(swmf_root).get_param_evidence(
        command_normalized=command_normalized.upper(),
        max_results=max_results,
    )


def get_file_symbols(swmf_root: str, file_path: str) -> list[dict[str, Any]]:
    """Return all symbols indexed from *file_path* (absolute path)."""
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
    }
