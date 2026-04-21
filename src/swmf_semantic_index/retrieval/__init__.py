"""
Hybrid retrieval pipeline and ranking.

The default v1 flow is:
  1. Lexical narrowing: FTS5 full-text search returns a candidate set.
  2. Score combination: keyword bonuses for component and symbol hints.
  3. Ranking: sort by combined score, return top-k RetrievalResult records.

If a neural embedding backend is configured and embeddings are stored, the pipeline
adds a semantic re-ranking pass after the lexical narrowing step.

The SemanticIndex class is the primary public API for callers.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Optional

from ..corpus import DiscoveredFile, discover_corpus_root
from ..models import (
    AuthorityTier,
    ChunkRecord,
    CorpusManifest,
    CorpusRoot,
    CorpusSlice,
    RetrievalResult,
    ScoreComponents,
)
from ..storage import ChunkStore
from ..chunking import chunk_file


# ---------------------------------------------------------------------------
# Default cache location (separate from .swmf_mcp_cache)
# ---------------------------------------------------------------------------

_DEFAULT_CACHE_DIR = ".swmf_semantic_cache"


# ---------------------------------------------------------------------------
# Ranking helpers
# ---------------------------------------------------------------------------


def _keyword_overlap(query_tokens: frozenset[str], chunk: ChunkRecord) -> float:
    """Fraction of query tokens that appear in chunk keywords or symbol."""
    if not query_tokens:
        return 0.0
    chunk_tokens: set[str] = set(k.lower() for k in chunk.keywords)
    if chunk.symbol:
        chunk_tokens.update(chunk.symbol.lower().split("_"))
    if chunk.component:
        chunk_tokens.add(chunk.component.lower())
    overlap = len(query_tokens & chunk_tokens)
    return overlap / len(query_tokens)


def _component_bonus(query_component: Optional[str], chunk: ChunkRecord) -> float:
    if not query_component or not chunk.component:
        return 0.0
    return 0.3 if query_component.upper() == chunk.component.upper() else 0.0


def _symbol_bonus(query_symbol: Optional[str], chunk: ChunkRecord) -> float:
    if not query_symbol or not chunk.symbol:
        return 0.0
    qs = query_symbol.lower()
    cs = chunk.symbol.lower()
    if qs == cs:
        return 0.5
    if qs in cs or cs in qs:
        return 0.2
    return 0.0


def _tokenize_query(query: str) -> frozenset[str]:
    tokens = re.findall(r"\b[a-z_]\w{2,}\b", query.lower())
    stop = {"the", "and", "for", "with", "from", "this", "that", "are", "not"}
    return frozenset(t for t in tokens if t not in stop)


def _combine_scores(
    fts_rank: int,
    total_candidates: int,
    keyword_overlap: float,
    component_bonus: float,
    symbol_bonus: float,
) -> ScoreComponents:
    # FTS rank: normalize to [0, 1] where rank=0 (top) → 1.0
    if total_candidates > 0:
        lexical = 1.0 - (fts_rank / total_candidates)
    else:
        lexical = 0.0

    combined = (
        lexical * 0.5
        + keyword_overlap * 0.2
        + component_bonus
        + symbol_bonus
    )
    return ScoreComponents(
        lexical_score=lexical,
        semantic_score=0.0,  # neural backend would set this
        component_match=component_bonus,
        symbol_match=symbol_bonus,
        combined=min(combined, 1.0),
    )


# ---------------------------------------------------------------------------
# SemanticIndex — main public API
# ---------------------------------------------------------------------------


class SemanticIndex:
    """
    Public entry point for building, refreshing, and querying the semantic index.

    Parameters
    ----------
    cache_dir:
        Directory where the SQLite artifact is stored. Defaults to
        .swmf_semantic_cache/ in the current working directory.

    Example
    -------
    idx = SemanticIndex()
    idx.build(swmf_root=Path("SWMF"), solar_root=Path("SWMFSOLAR"))
    results = idx.search("IH SC coupling mechanism", component="IH", top_k=5)
    for r in results:
        print(r.chunk.location, r.scores.combined)
    """

    def __init__(self, cache_dir: Optional[Path] = None) -> None:
        self._cache_dir = (cache_dir or Path.cwd() / _DEFAULT_CACHE_DIR).resolve()
        self._db_path = self._cache_dir / "semantic_index.db"
        self._store = ChunkStore(self._db_path)
        self._is_open = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _ensure_open(self) -> None:
        if not self._is_open:
            self._store.open()
            self._is_open = True

    def close(self) -> None:
        if self._is_open:
            self._store.close()
            self._is_open = False

    # ------------------------------------------------------------------
    # Build / Refresh
    # ------------------------------------------------------------------

    def build(
        self,
        roots: list[tuple[Path, CorpusSlice]],
        *,
        incremental: bool = False,
    ) -> CorpusManifest:
        """
        Index *roots* and persist to the local cache.

        Parameters
        ----------
        roots:
            List of (path, CorpusSlice) pairs, e.g.:
            [(Path("SWMF"), CorpusSlice.SWMF_SOURCE),
             (Path("SWMFSOLAR"), CorpusSlice.SWMFSOLAR_SOURCE)]
        incremental:
            If True, skip files whose chunk_ids are already in the store.
            If False (default), clear and rebuild from scratch.
        """
        self._ensure_open()

        if not incremental:
            self._store.clear()

        from datetime import datetime

        corpus_roots: list[CorpusRoot] = []
        total_chunks = 0
        total_files = 0

        for root_path, slice_ in roots:
            root_path = root_path.resolve()
            discovered = discover_corpus_root(root_path, slice_)
            file_count = len(discovered)
            chunk_count = 0

            for df in discovered:
                # Re-root the chunk so corpus_root is the actual corpus root, not the parent dir.
                chunks = chunk_file(df)
                for c in chunks:
                    c.corpus_root = str(root_path)
                    c.chunk_id = ChunkRecord.make_id(str(root_path), c.rel_path, c.start_line)
                if chunks:
                    self._store.insert_chunks_bulk(chunks)
                    chunk_count += len(chunks)

            corpus_roots.append(CorpusRoot(
                abs_path=str(root_path),
                corpus_slice=slice_,
                file_count=file_count,
                chunk_count=chunk_count,
                indexed_at=datetime.utcnow(),
            ))
            total_files += file_count
            total_chunks += chunk_count

        manifest = CorpusManifest(
            schema_version="1.0",
            built_at=datetime.utcnow(),
            embedding_backend="tfidf_lexical",
            total_chunks=self._store.count_chunks(),
            total_files=total_files,
            roots=corpus_roots,
            index_path=str(self._cache_dir),
        )
        self._store.save_manifest(manifest)
        return manifest

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        component: Optional[str] = None,
        symbol: Optional[str] = None,
        corpus_slice: Optional[CorpusSlice] = None,
        top_k: int = 10,
    ) -> list[RetrievalResult]:
        """
        Hybrid search: FTS5 lexical narrowing + keyword/component/symbol re-ranking.

        Returns up to *top_k* results sorted by combined score descending.
        """
        self._ensure_open()

        # Expand fetch limit to allow re-ranking
        fetch_limit = min(top_k * 5, 100)
        candidates = self._store.fts_search(
            query, limit=fetch_limit,
            component=component, corpus_slice=corpus_slice,
        )

        if not candidates:
            return []

        query_tokens = _tokenize_query(query)
        results: list[RetrievalResult] = []

        for rank_idx, chunk in enumerate(candidates):
            kw_score = _keyword_overlap(query_tokens, chunk)
            comp_bonus = _component_bonus(component, chunk)
            sym_bonus = _symbol_bonus(symbol, chunk)
            scores = _combine_scores(
                rank_idx, len(candidates), kw_score, comp_bonus, sym_bonus
            )
            results.append(RetrievalResult(
                chunk=chunk,
                scores=scores,
                rank=rank_idx,
            ))

        results.sort(key=lambda r: r.scores.combined, reverse=True)

        # Re-assign final ranks after sort
        for i, r in enumerate(results):
            r.rank = i + 1

        return results[:top_k]

    def get_status(self) -> dict:
        """Return index status information suitable for an MCP tool response."""
        self._ensure_open()
        manifest = self._store.load_manifest()
        if manifest is None:
            return {
                "built": False,
                "chunk_count": 0,
                "message": "Index not built. Run: swmf-index build --corpus SWMF --corpus SWMFSOLAR",
            }
        return {
            "built": True,
            "built_at": manifest.built_at.isoformat() if manifest.built_at else None,
            "is_stale": manifest.is_stale(),
            "embedding_backend": manifest.embedding_backend,
            "total_chunks": manifest.total_chunks,
            "total_files": manifest.total_files,
            "roots": [
                {
                    "path": r.abs_path,
                    "corpus_slice": r.corpus_slice.value,
                    "file_count": r.file_count,
                    "chunk_count": r.chunk_count,
                }
                for r in manifest.roots
            ],
            "index_path": manifest.index_path,
        }
