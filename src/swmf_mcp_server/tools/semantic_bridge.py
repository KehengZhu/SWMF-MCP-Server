"""
MCP bridge adapter for swmf_semantic_index.

Exposes two thin MCP tools that delegate to the standalone semantic engine:

  swmf_semantic_search
      Full-text + semantic search over the indexed SWMF and SWMFSOLAR corpus.
      Requires the semantic index to be built with: swmf-index build --corpus SWMF

  swmf_semantic_index_status
      Check whether the semantic index is built and up-to-date.

Design contract:
- This module does NOT own any indexing, chunking, or embedding logic.
- It imports from swmf_semantic_index (the sibling package) as a read-only client.
- If swmf_semantic_index is not installed, tools degrade gracefully with a clear message.
- Deterministic MCP tools are always preferred for exact facts; this bridge is for
  broad exploratory queries only. See .github/skills/swmf-agent-routing/SKILL.md.
"""

from __future__ import annotations

from typing import Any, Optional


_IMPORT_ERROR: Optional[str] = None
try:
    from swmf_semantic_index.retrieval import SemanticIndex
    from swmf_semantic_index.models import CorpusSlice
    _INDEX_AVAILABLE = True
except ImportError as _e:
    _INDEX_AVAILABLE = False
    _IMPORT_ERROR = str(_e)


_NOT_BUILT_MESSAGE = (
    "Semantic index is not built. "
    "Run: swmf-index build --corpus /path/to/SWMF --corpus /path/to/SWMFSOLAR"
)
_NOT_AVAILABLE_MESSAGE = (
    "swmf_semantic_index package is not installed. "
    "It is a sibling package — install with: pip install -e ."
)


def swmf_semantic_search(
    query: str,
    component: str | None = None,
    symbol: str | None = None,
    top_k: int = 10,
    cache_dir: str | None = None,
) -> dict[str, Any]:
    """Search the SWMF semantic index for relevant source passages.

    Uses hybrid lexical + keyword retrieval over indexed Fortran, Perl, PARAM XML,
    TeX manuals, and Markdown files from SWMF and SWMFSOLAR.

    **Authority note**: Results are semantic evidence (tier 4/5), not verified facts.
    For execution-sensitive answers, verify key claims with deterministic MCP tools.
    See the swmf-agent-routing skill for routing guidance.

    Parameters
    ----------
    query:
        Natural language or keyword query. Include component names, symbol names,
        or PARAM command names to improve ranking.
    component:
        Optional two-letter component filter to narrow results (e.g. ``"IH"``, ``"SC"``).
    symbol:
        Optional symbol name hint to boost ranking for matching subroutines/modules.
    top_k:
        Number of results to return (default 10, max 30).
    cache_dir:
        Path to the semantic index cache directory. Uses default (.swmf_semantic_cache)
        if not specified.
    """
    if not _INDEX_AVAILABLE:
        return {
            "ok": False,
            "error_code": "SEMANTIC_INDEX_PACKAGE_UNAVAILABLE",
            "message": _NOT_AVAILABLE_MESSAGE,
            "import_error": _IMPORT_ERROR,
            "authority": "none",
        }

    from pathlib import Path

    top_k = min(max(1, top_k), 30)
    idx = SemanticIndex(cache_dir=Path(cache_dir) if cache_dir else None)
    try:
        status = idx.get_status()
        if not status.get("built"):
            return {
                "ok": False,
                "error_code": "SEMANTIC_INDEX_NOT_BUILT",
                "message": _NOT_BUILT_MESSAGE,
                "how_to_fix": ["Run: swmf-index build --corpus /path/to/SWMF --corpus /path/to/SWMFSOLAR"],
                "index_status": status,
                "authority": "none",
            }

        results = idx.search(
            query,
            component=component,
            symbol=symbol,
            top_k=top_k,
        )

        return {
            "ok": True,
            "query": query,
            "filters": {"component": component, "symbol": symbol},
            "result_count": len(results),
            "results": [
                {
                    "rank": r.rank,
                    "chunk_id": r.chunk.chunk_id,
                    "location": r.chunk.location,
                    "kind": r.chunk.kind.value,
                    "component": r.chunk.component,
                    "symbol": r.chunk.symbol,
                    "authority_tier": r.authority_label,
                    "score": round(r.scores.combined, 4),
                    "excerpt": r.chunk.text[:500],
                }
                for r in results
            ],
            "authority": "semantic_retrieval",
            "authority_note": (
                "Semantic results are tier-4 evidence. They supplement but do not override "
                "deterministic MCP outputs. Verify status-sensitive claims with source tools."
            ),
            "routing_note": (
                "For coupling implementation status, follow with swmf_collect_source_context "
                "on the coupler file to check for CON_stop stubs."
            ),
        }
    finally:
        idx.close()


def swmf_semantic_index_status(cache_dir: str | None = None) -> dict[str, Any]:
    """Check whether the SWMF semantic index is built and up-to-date.

    Returns index build time, corpus statistics, and whether the index needs refresh.
    Does not modify the index.

    If the index is not built, returns instructions for building it.
    """
    if not _INDEX_AVAILABLE:
        return {
            "ok": False,
            "error_code": "SEMANTIC_INDEX_PACKAGE_UNAVAILABLE",
            "message": _NOT_AVAILABLE_MESSAGE,
        }

    from pathlib import Path

    idx = SemanticIndex(cache_dir=Path(cache_dir) if cache_dir else None)
    try:
        status = idx.get_status()
        if not status.get("built"):
            status["how_to_build"] = (
                "swmf-index build --corpus /path/to/SWMF --corpus /path/to/SWMFSOLAR"
            )
        return {"ok": True, **status}
    finally:
        idx.close()


def register(app: Any) -> None:
    app.tool(
        description=(
            "Search the SWMF semantic index for relevant source passages, subroutines, "
            "PARAM command blocks, or manual sections. Uses hybrid lexical+keyword retrieval. "
            "Requires the semantic index to be built first (swmf-index build). "
            "Authority tier: semantic_retrieval (derived). Always verify status-sensitive claims "
            "with deterministic source tools before presenting as facts."
        )
    )(swmf_semantic_search)

    app.tool(
        description=(
            "Check whether the SWMF semantic index is built, and get corpus statistics "
            "(total chunks, files indexed, build time, stale status). "
            "Call this before routing to swmf_semantic_search."
        )
    )(swmf_semantic_index_status)
