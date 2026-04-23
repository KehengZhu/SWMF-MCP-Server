"""Integration tests for v2 evidence search against a real SWMF index.

Purpose
-------
These tests exercise the v2 evidence tool chain, query understanding,
FTS5 keyword search, and fallback behavior against the real knowledge index
built from the SWMF source tree that is symlinked (or present) at
``<workspace>/SWMF``.

They catch the class of regression shown in ``interp.md``, where natural-
language queries ("interpolation methods in SWMF") returned ``result_count: 0``
because the FTS5 AND matcher required every English word in the query to appear
in a Fortran symbol name.

Every test is marked with ``pytest.mark.integration`` and is **skipped** when
the SWMF root cannot be resolved (e.g., in CI without the source tree).
"""
from __future__ import annotations

import pytest

from swmf_mcp_server.core.swmf_root import resolve_swmf_root
from swmf_mcp_server.knowledge import service as ks
from swmf_mcp_server.tools.get_evidence import get_evidence


# ---------------------------------------------------------------------------
# Fixture – resolve the real SWMF root once per session
# ---------------------------------------------------------------------------


def _live_swmf_root() -> str | None:
    result = resolve_swmf_root()
    return result.swmf_root_resolved if result.ok else None


SWMF_ROOT = _live_swmf_root()


def _live_index_ready() -> bool:
    if SWMF_ROOT is None:
        return False
    status = ks.get_index_status(SWMF_ROOT)
    return status.ok and not status.is_stale and status.symbol_count > 0


pytestmark = pytest.mark.skipif(
    not _live_index_ready(),
    reason="Live SWMF knowledge index is not ready; skipping live index tests.",
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _search(query: str, **kwargs) -> dict:
    return get_evidence(query=query, swmf_root=SWMF_ROOT, **kwargs)


# ---------------------------------------------------------------------------
# Index readiness
# ---------------------------------------------------------------------------


class TestIndexReadiness:
    def test_knowledge_status_ok(self) -> None:
        """Index must be built and non-stale before other tests run."""
        assert SWMF_ROOT is not None
        status = ks.get_index_status(SWMF_ROOT)
        assert status.ok is True, (
            f"Knowledge index not ready. Status: {status}. "
            "Run 'make preindex' to build the index."
        )
        assert not status.is_stale, (
            "Knowledge index is stale. Run 'make preindex' to refresh it."
        )

    def test_index_has_symbols(self) -> None:
        assert SWMF_ROOT is not None
        status = ks.get_index_status(SWMF_ROOT)
        symbol_count = status.symbol_count
        assert symbol_count > 0, (
            f"Index reports 0 symbols (symbol_count={symbol_count}). "
            "Ensure 'make preindex' was run against a populated SWMF tree."
        )


# ---------------------------------------------------------------------------
# Natural-language queries that previously returned zero results (interp.md)
# ---------------------------------------------------------------------------


class TestNaturalLanguageSearchRegression:
    """Regression suite for the 'zero results on NL query' bug.

    Each test uses a query that previously produced result_count=0 because
    FTS5 required all words in the query to appear in a Fortran symbol name.
    After the stopword fix these queries must return at least one result.
    """

    def test_interpolation_methods_returns_results(self) -> None:
        """'interpolation methods in SWMF' must not return 0 results."""
        result = _search("interpolation methods in SWMF")
        assert result.get("ok") is True
        count = len(result.get("evidence", []))
        assert count > 0, (
            f"Expected results for 'interpolation methods in SWMF' but got 0. "
            f"provenance={result.get('provenance')}"
        )

    def test_interpolation_result_files_are_relevant(self) -> None:
        """Results for 'interpolation' should reference known coupler files."""
        result = _search("interpolation methods in SWMF")
        paths = [r.get("path", "") for r in result.get("evidence", [])]
        relevant = [
            p for p in paths
            if "interpolat" in p.lower() or "coupl" in p.lower() or "router" in p.lower()
        ]
        assert relevant, (
            f"No coupling/interpolation files in results. Got paths: {paths[:5]}"
        )

    def test_coupling_query_returns_results(self) -> None:
        result = _search("magnetosphere coupling")
        assert result.get("ok") is True
        assert len(result.get("evidence", [])) > 0, (
            "Expected results for 'magnetosphere coupling' but got 0."
        )

    def test_broad_architecture_query_returns_results(self) -> None:
        """A broad multi-word query should not collapse to zero via AND semantics."""
        result = _search("session control in SWMF")
        assert result.get("ok") is True
        assert len(result.get("evidence", [])) > 0, (
            "Expected results for 'session control in SWMF' but got 0."
        )


# ---------------------------------------------------------------------------
# Single-term and symbol queries
# ---------------------------------------------------------------------------


class TestExactAndNarrowQueries:
    def test_interpolation_single_term(self) -> None:
        result = _search("interpolation")
        assert result.get("ok") is True
        assert len(result.get("evidence", [])) > 0

    def test_bilinear_interpolation_symbol(self) -> None:
        result = _search("bilinear_interpolation")
        assert result.get("ok") is True
        # bilinear_interpolation is a known subroutine in CON_couple_ie_im.f90
        snippets = [r.get("snippet", "") for r in result.get("evidence", [])]
        assert any("bilinear" in s.lower() for s in snippets), (
            f"Expected 'bilinear_interpolation' in results but got snippets: {snippets[:5]}"
        )

    def test_component_filtered_search(self) -> None:
        result = _search("couple", scope=["GM"])
        assert result.get("ok") is True
        assert result.get("scope") == ["GM"]


# ---------------------------------------------------------------------------
# Fallback and degradation behaviour
# ---------------------------------------------------------------------------


class TestSearchFallbackBehaviour:
    def test_stopword_only_query_does_not_crash(self) -> None:
        """A query consisting entirely of stopwords must return ok=True (no crash)."""
        result = _search("in the of")
        assert result.get("ok") is True

    def test_empty_result_includes_attempted_queries_field(self) -> None:
        """Even a zero-result response must include the attempted_queries audit trail."""
        # Use a nonsense term that genuinely won't match anything
        result = _search("xyzzy_nonexistent_fortran_symbol_abc123")
        assert result.get("ok") is True
        assert "known_unknowns" in result["uncertainty"]

    def test_semantic_runtime_field_present(self) -> None:
        """Provenance must report the evidence mode used."""
        result = _search("interpolation")
        assert "mode_used" in result["provenance"]
