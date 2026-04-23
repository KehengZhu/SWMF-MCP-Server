"""Compatibility shim for the knowledge service.

The real service now lives in ``swmf_mcp_server.knowledge.service``.
New code should import from the knowledge package directly.
"""
from ..knowledge.service import (
    SEARCH_MODE_HYBRID,
    SEARCH_MODE_KEYWORD,
    SEARCH_MODE_SEMANTIC,
    SLICE_ANALYST_CONTEXT,
    SLICE_SWMFSOLAR_SOURCE,
    _EXTRA_ROOTS_KEY_BY_ROOT,
    _INDEX_BY_ROOT,
    _get_catalog,
    build_index,
    ensure_index_ready,
    get_agent_context_pack,
    get_file_symbols,
    get_index_status,
    get_param_evidence,
    lookup_symbol,
    refresh_index,
    search_chunks,
    search_source,
    search_symbols,
    status_as_payload,
    understand_source_query,
)

__all__ = [
    "SEARCH_MODE_HYBRID",
    "SEARCH_MODE_KEYWORD",
    "SEARCH_MODE_SEMANTIC",
    "SLICE_ANALYST_CONTEXT",
    "SLICE_SWMFSOLAR_SOURCE",
    "_EXTRA_ROOTS_KEY_BY_ROOT",
    "_INDEX_BY_ROOT",
    "_get_catalog",
    "build_index",
    "ensure_index_ready",
    "get_agent_context_pack",
    "get_file_symbols",
    "get_index_status",
    "get_param_evidence",
    "understand_source_query",
    "lookup_symbol",
    "refresh_index",
    "search_chunks",
    "search_source",
    "search_symbols",
    "status_as_payload",
]
