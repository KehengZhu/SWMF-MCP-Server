"""
Data models for the SWMF semantic index engine.

All models are plain dataclasses to keep the package dependency-free at the
core layer. The storage and retrieval layers use these as their interchange types.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ChunkKind(str, Enum):
    """Semantic unit type — matches the SWMF-aware chunking strategy."""
    FORTRAN_MODULE = "fortran_module"
    FORTRAN_SUBROUTINE = "fortran_subroutine"
    FORTRAN_FUNCTION = "fortran_function"
    PERL_SUB = "perl_sub"
    PARAM_COMMAND_BLOCK = "param_command_block"
    TEX_SUBSECTION = "tex_subsection"
    MARKDOWN_SECTION = "markdown_section"
    SKILL_SECTION = "skill_section"
    XML_COMMAND = "xml_command"
    PLAIN_TEXT_BLOCK = "plain_text_block"


class AuthorityTier(int, Enum):
    """
    Authority hierarchy (lower value = higher authority).
    Semantic retrieval never upgrades a chunk's tier.
    """
    SOURCE_VERBATIM = 1       # direct source code read
    SCHEMA_VALIDATED = 2      # PARAM.XML / TestParam.pl validated output
    DETERMINISTIC_MCP = 3     # structured MCP tool output
    SEMANTIC_RETRIEVAL = 4    # swmf_search_source passage
    DOCUMENTATION = 5         # TeX manual, README, analyst markdown


class CorpusSlice(str, Enum):
    """Logical partition of the indexed corpus."""
    SWMF_SOURCE = "swmf_source"
    SWMFSOLAR_SOURCE = "swmfsolar_source"
    SWMF_PARAM_XML = "swmf_param_xml"
    SWMF_MANUALS = "swmf_manuals"
    SWMF_SCRIPTS = "swmf_scripts"
    SWMF_TESTS = "swmf_tests"
    ANALYST_CONTEXT = "analyst_context"   # local markdown notes; never source-of-truth


# ---------------------------------------------------------------------------
# Core chunk record
# ---------------------------------------------------------------------------


@dataclass
class ChunkRecord:
    """
    A single indexed chunk extracted from the corpus.

    chunk_id is a stable content-hash derived from (corpus_root, rel_path,
    start_line) so the same logical chunk always gets the same id across refreshes
    as long as its location does not change.
    """
    chunk_id: str
    corpus_root: str           # abs path to SWMF or SWMFSOLAR root
    rel_path: str              # relative to corpus_root
    kind: ChunkKind
    authority: AuthorityTier
    corpus_slice: CorpusSlice
    start_line: int
    end_line: int
    text: str                  # raw extracted text
    component: Optional[str] = None      # e.g. "GM", "IE", "CON"
    symbol: Optional[str] = None         # subroutine / function / command name
    parent_symbol: Optional[str] = None  # enclosing module or section
    keywords: list[str] = field(default_factory=list)  # extracted keywords for lexical pass
    embedding: Optional[list[float]] = None  # set by embeddings layer; None until indexed

    @staticmethod
    def make_id(corpus_root: str, rel_path: str, start_line: int) -> str:
        raw = f"{corpus_root}|{rel_path}|{start_line}"
        return hashlib.sha1(raw.encode()).hexdigest()[:16]

    @property
    def abs_path(self) -> Path:
        return Path(self.corpus_root) / self.rel_path

    @property
    def location(self) -> str:
        return f"{self.rel_path}:{self.start_line}-{self.end_line}"


# ---------------------------------------------------------------------------
# Retrieval result
# ---------------------------------------------------------------------------


@dataclass
class ScoreComponents:
    """Breakdown of why a chunk was ranked at its position."""
    lexical_score: float = 0.0    # BM25 or keyword match score
    semantic_score: float = 0.0   # cosine similarity from embedding
    component_match: float = 0.0  # bonus for matching the queried component
    symbol_match: float = 0.0     # bonus for matching the queried symbol
    combined: float = 0.0         # final rank score after combination


@dataclass
class RetrievalResult:
    """
    A single result entry returned by the retrieval layer.

    Callers should treat authority_tier as the trust level for the chunk's content.
    Verified claims require a separate deterministic check (see routing skill).
    """
    chunk: ChunkRecord
    scores: ScoreComponents
    rank: int
    retrieval_notes: list[str] = field(default_factory=list)

    @property
    def is_source_code(self) -> bool:
        return self.chunk.kind in {
            ChunkKind.FORTRAN_MODULE,
            ChunkKind.FORTRAN_SUBROUTINE,
            ChunkKind.FORTRAN_FUNCTION,
            ChunkKind.PERL_SUB,
        }

    @property
    def authority_label(self) -> str:
        tier = self.chunk.authority
        labels = {
            AuthorityTier.SOURCE_VERBATIM: "source (verbatim)",
            AuthorityTier.SCHEMA_VALIDATED: "schema-validated",
            AuthorityTier.DETERMINISTIC_MCP: "deterministic-mcp",
            AuthorityTier.SEMANTIC_RETRIEVAL: "semantic-retrieval (derived)",
            AuthorityTier.DOCUMENTATION: "documentation",
        }
        return labels.get(tier, "unknown")


# ---------------------------------------------------------------------------
# Corpus manifest
# ---------------------------------------------------------------------------


@dataclass
class CorpusRoot:
    """One indexed root directory (SWMF or SWMFSOLAR)."""
    abs_path: str
    corpus_slice: CorpusSlice
    file_count: int = 0
    chunk_count: int = 0
    indexed_at: Optional[datetime] = None


@dataclass
class CorpusManifest:
    """
    Metadata artifact written alongside the vector index.
    Stored in the local cache directory as manifest.json.
    """
    schema_version: str = "1.0"
    built_at: Optional[datetime] = None
    embedding_backend: str = "tfidf_bm25"   # default lexical-only backend
    embedding_model: Optional[str] = None   # set when using a neural backend
    embedding_dim: Optional[int] = None
    total_chunks: int = 0
    total_files: int = 0
    roots: list[CorpusRoot] = field(default_factory=list)
    index_path: Optional[str] = None        # abs path to the artifact dir

    def is_stale(self, max_age_seconds: float = 86400.0) -> bool:
        if self.built_at is None:
            return True
        age = (datetime.utcnow() - self.built_at).total_seconds()
        return age > max_age_seconds
