"""Persistent SQLite-backed source index for the SWMF knowledge base.

Architecture
------------
One SQLite database per primary SWMF root, stored at::

    {swmf_root}/.swmf_mcp_cache/knowledge.db

Override with the ``SWMF_MCP_KNOWLEDGE_DB`` environment variable.

Multi-root indexing
-------------------
Pass additional corpus roots at construction time via ``extra_roots``::

    catalog = SourceIndexCatalog(
        "/path/to/SWMF",
        extra_roots=[
            ("/path/to/SWMFSOLAR",          "swmfsolar_source"),
            ("/path/to/swmf-mcp-prototype", "analyst_context"),
        ],
    )

All roots are indexed into the same SQLite database keyed on the primary
SWMF root path.  The ``corpus_root`` and ``corpus_slice`` columns in
``source_files`` identify which repo each file came from.

Full-text search
----------------
An FTS5 virtual table (``symbols_fts``) mirrors the ``symbols`` table for
fast BM25-ranked retrieval.  A LIKE fallback is used when FTS5 returns no
hits.

Indexed corpus
--------------
Source languages (symbols extracted via parsers):
  * Fortran  (.f90, .f)  — subroutines, modules, functions
  * Perl     (.pl, .pm)  — subroutines
  * IDL      (.pro)      — procedures and functions

Documentation languages (section chunks stored as doc_section symbols):
  * TeX      (.tex)      — \\\\section / \\\\subsection headings
  * Markdown (.md, .rst) — # headings

Authority
---------
All symbols carry ``authority="heuristic"`` — regex-based parsing.
PARAM.XML and TestParam.pl remain authoritative; this index supplements,
never overrides, them.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import time
from pathlib import Path
from typing import Any, Sequence

from ..core.authority import (
    AUTHORITY_HEURISTIC,
    SOURCE_KIND_FORTRAN_SOURCE,
    SOURCE_KIND_IDL_SOURCE,
    SOURCE_KIND_MANUAL_DOC,
    SOURCE_KIND_PERL_SOURCE,
)
from ..core.models import KnowledgeIndexStatus
from ..parsing.fortran_chunker import parse_fortran_chunks
from ..parsing.fortran_parser import parse_fortran_file
from ..parsing.idl_parser import parse_idl_file
from ..parsing.perl_parser import parse_perl_file

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "3"
CACHE_DIR_NAME = ".swmf_mcp_cache"
DB_FILE_NAME = "knowledge.db"
ENV_DB_OVERRIDE = "SWMF_MCP_KNOWLEDGE_DB"
SEARCH_MODE_KEYWORD = "keyword"
_SEARCH_MODES = frozenset({SEARCH_MODE_KEYWORD})

# Corpus slice labels (strings matching CorpusSlice enum values used by
# the old swmf_semantic_index package — kept identical for compatibility)
SLICE_SWMF_SOURCE = "swmf_source"
SLICE_SWMFSOLAR_SOURCE = "swmfsolar_source"
SLICE_SWMF_MANUALS = "swmf_manuals"
SLICE_SWMF_SCRIPTS = "swmf_scripts"
SLICE_SWMF_PARAM_XML = "swmf_param_xml"
SLICE_ANALYST_CONTEXT = "analyst_context"

# Per-language file limits to prevent runaway indexing on large trees
_LIMITS: dict[str, int] = {
    "fortran": 8000,
    "perl": 500,
    "idl": 4000,
    "tex": 300,
    "doc": 600,
}

# Max file size to index (bytes)
_MAX_FILE_BYTES = 500_000

# Max docstring / chunk text stored per symbol (chars)
_MAX_CHUNK_CHARS = 3000

# Directories to skip while walking
_SKIP_DIRS = frozenset({
    ".git", ".svn", ".hg", ".swmf_mcp_cache", ".swmf_semantic_cache",
    "__pycache__", "node_modules", "build", "Build", "tmp", "work",
    "dist", "obj", "CVS", ".venv", "venv",
})

# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------

_DDL = """
CREATE TABLE IF NOT EXISTS manifest (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS source_files (
    id             INTEGER PRIMARY KEY,
    path           TEXT    UNIQUE NOT NULL,
    language       TEXT    NOT NULL,
    component      TEXT,
    corpus_root    TEXT,
    corpus_slice   TEXT,
    mtime          REAL,
    content_digest TEXT,
    indexed_at     REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS symbols (
    id          INTEGER PRIMARY KEY,
    file_id     INTEGER NOT NULL REFERENCES source_files(id) ON DELETE CASCADE,
    name        TEXT    NOT NULL,
    kind        TEXT    NOT NULL,
    start_line  INTEGER,
    component   TEXT,
    docstring   TEXT,
    uses        TEXT,
    source_kind TEXT    NOT NULL,
    authority   TEXT    NOT NULL DEFAULT 'heuristic'
);

CREATE VIRTUAL TABLE IF NOT EXISTS symbols_fts USING fts5(
    name,
    docstring,
    component,
    content='symbols',
    content_rowid='id'
);

CREATE TABLE IF NOT EXISTS code_chunks (
    id          INTEGER PRIMARY KEY,
    file_id     INTEGER NOT NULL REFERENCES source_files(id) ON DELETE CASCADE,
    symbol_name TEXT    NOT NULL,
    chunk_kind  TEXT    NOT NULL,
    label       TEXT    NOT NULL,
    start_line  INTEGER,
    end_line    INTEGER,
    component   TEXT,
    chunk_text  TEXT    NOT NULL,
    uses        TEXT,
    param_refs  TEXT,
    source_kind TEXT    NOT NULL,
    authority   TEXT    NOT NULL DEFAULT 'heuristic'
);

CREATE VIRTUAL TABLE IF NOT EXISTS code_chunks_fts USING fts5(
    symbol_name,
    label,
    chunk_text,
    component,
    content='code_chunks',
    content_rowid='id'
);

CREATE TABLE IF NOT EXISTS param_mentions (
    id                 INTEGER PRIMARY KEY,
    command_normalized TEXT    NOT NULL,
    file_id            INTEGER REFERENCES source_files(id) ON DELETE CASCADE,
    symbol_id          INTEGER REFERENCES symbols(id)      ON DELETE SET NULL,
    line_number        INTEGER,
    context_snippet    TEXT,
    source_kind        TEXT    NOT NULL,
    authority          TEXT    NOT NULL DEFAULT 'heuristic'
);

CREATE INDEX IF NOT EXISTS idx_symbols_name       ON symbols(name);
CREATE INDEX IF NOT EXISTS idx_symbols_component   ON symbols(component);
CREATE INDEX IF NOT EXISTS idx_symbols_kind        ON symbols(kind);
CREATE INDEX IF NOT EXISTS idx_symbols_file        ON symbols(file_id);
CREATE INDEX IF NOT EXISTS idx_chunks_symbol_name  ON code_chunks(symbol_name);
CREATE INDEX IF NOT EXISTS idx_chunks_kind         ON code_chunks(chunk_kind);
CREATE INDEX IF NOT EXISTS idx_chunks_file         ON code_chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_param_cmd           ON param_mentions(command_normalized);
CREATE INDEX IF NOT EXISTS idx_param_file          ON param_mentions(file_id);
CREATE INDEX IF NOT EXISTS idx_files_corpus_root   ON source_files(corpus_root);
CREATE INDEX IF NOT EXISTS idx_files_corpus_slice  ON source_files(corpus_slice);
"""

# FTS5 sync triggers — installed after bulk build to avoid per-row overhead
_FTS_TRIGGERS = """
CREATE TRIGGER IF NOT EXISTS symbols_ai AFTER INSERT ON symbols BEGIN
    INSERT INTO symbols_fts(rowid, name, docstring, component)
    VALUES (new.id, new.name, COALESCE(new.docstring,''), COALESCE(new.component,''));
END;

CREATE TRIGGER IF NOT EXISTS symbols_ad AFTER DELETE ON symbols BEGIN
    INSERT INTO symbols_fts(symbols_fts, rowid, name, docstring, component)
    VALUES ('delete', old.id, old.name, COALESCE(old.docstring,''), COALESCE(old.component,''));
END;

CREATE TRIGGER IF NOT EXISTS symbols_au AFTER UPDATE ON symbols BEGIN
    INSERT INTO symbols_fts(symbols_fts, rowid, name, docstring, component)
    VALUES ('delete', old.id, old.name, COALESCE(old.docstring,''), COALESCE(old.component,''));
    INSERT INTO symbols_fts(rowid, name, docstring, component)
    VALUES (new.id, new.name, COALESCE(new.docstring,''), COALESCE(new.component,''));
END;

CREATE TRIGGER IF NOT EXISTS code_chunks_ai AFTER INSERT ON code_chunks BEGIN
    INSERT INTO code_chunks_fts(rowid, symbol_name, label, chunk_text, component)
    VALUES (new.id, new.symbol_name, new.label, new.chunk_text, COALESCE(new.component,''));
END;

CREATE TRIGGER IF NOT EXISTS code_chunks_ad AFTER DELETE ON code_chunks BEGIN
    INSERT INTO code_chunks_fts(code_chunks_fts, rowid, symbol_name, label, chunk_text, component)
    VALUES ('delete', old.id, old.symbol_name, old.label, old.chunk_text, COALESCE(old.component,''));
END;

CREATE TRIGGER IF NOT EXISTS code_chunks_au AFTER UPDATE ON code_chunks BEGIN
    INSERT INTO code_chunks_fts(code_chunks_fts, rowid, symbol_name, label, chunk_text, component)
    VALUES ('delete', old.id, old.symbol_name, old.label, old.chunk_text, COALESCE(old.component,''));
    INSERT INTO code_chunks_fts(rowid, symbol_name, label, chunk_text, component)
    VALUES (new.id, new.symbol_name, new.label, new.chunk_text, COALESCE(new.component,''));
END;
"""

# Schema teardown for full rebuild
_DROP_TABLES = """
DROP TRIGGER IF EXISTS code_chunks_au;
DROP TRIGGER IF EXISTS code_chunks_ad;
DROP TRIGGER IF EXISTS code_chunks_ai;
DROP TRIGGER IF EXISTS symbols_au;
DROP TRIGGER IF EXISTS symbols_ad;
DROP TRIGGER IF EXISTS symbols_ai;
DROP TABLE IF EXISTS param_mentions;
DROP TABLE IF EXISTS code_chunks_fts;
DROP TABLE IF EXISTS code_chunks;
DROP TABLE IF EXISTS symbols_fts;
DROP TABLE IF EXISTS symbols;
DROP TABLE IF EXISTS source_files;
DROP TABLE IF EXISTS manifest;
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _content_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _language_for(path: Path) -> str | None:
    ext = path.suffix.lower()
    if ext in (".f90", ".f"):
        return "fortran"
    if ext in (".pl", ".pm"):
        return "perl"
    if ext == ".pro":
        return "idl"
    if ext == ".tex":
        return "tex"
    if ext in (".md", ".rst"):
        return "doc"
    return None


def _source_kind_for(language: str) -> str:
    return {
        "fortran": SOURCE_KIND_FORTRAN_SOURCE,
        "perl": SOURCE_KIND_PERL_SOURCE,
        "idl": SOURCE_KIND_IDL_SOURCE,
        "tex": SOURCE_KIND_MANUAL_DOC,
        "doc": SOURCE_KIND_MANUAL_DOC,
    }.get(language, SOURCE_KIND_FORTRAN_SOURCE)


_COPILOT_SESSION_HEADER = b"# \xf0\x9f\xa4\x96 Copilot CLI Session"  # UTF-8 bytes

def _should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in _SKIP_DIRS or (part.startswith(".") and part not in {".", ".."}):
            return True
    # Skip Copilot CLI session log files (they appear as .md files in arbitrary dirs)
    if path.suffix.lower() in (".md", ".rst"):
        try:
            with path.open("rb") as fh:
                header = fh.read(40)
            if header.lstrip(b"\xef\xbb\xbf").startswith(_COPILOT_SESSION_HEADER):
                return True
        except OSError:
            pass
    return False


def _db_path_for(swmf_root: str | Path) -> Path:
    override = os.environ.get(ENV_DB_OVERRIDE)
    if override:
        return Path(override).expanduser()
    return Path(swmf_root) / CACHE_DIR_NAME / DB_FILE_NAME


def _normalize_search_mode(search_mode: str | None) -> str:
    normalized = (search_mode or SEARCH_MODE_KEYWORD).strip().lower()
    if normalized in _SEARCH_MODES:
        return normalized
    return SEARCH_MODE_KEYWORD


def _classify_corpus_slice(lang: str, rel_path: str, default_slice: str) -> str:
    """Determine corpus slice from language, relative path, and root default."""
    if default_slice == SLICE_ANALYST_CONTEXT:
        return SLICE_ANALYST_CONTEXT
    parts = rel_path.lower().replace("\\", "/").split("/")
    if lang == "tex":
        return SLICE_SWMF_MANUALS
    if lang == "doc":
        if any(p in ("doc", "docs", "tex", "manual", "manuals") for p in parts):
            return SLICE_SWMF_MANUALS
        return SLICE_ANALYST_CONTEXT
    if lang == "perl":
        return SLICE_SWMF_SCRIPTS
    # fortran / idl — inherit root default slice
    return default_slice


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def _discover_all_files(
    primary_root: Path,
    extra_roots: list[tuple[Path, str]],
) -> list[tuple[Path, str, str, str]]:
    """Walk all corpus roots; return (path, lang, corpus_root_str, corpus_slice)."""
    roots: list[tuple[Path, str]] = [(primary_root, SLICE_SWMF_SOURCE)]
    roots.extend(extra_roots)

    results: list[tuple[Path, str, str, str]] = []
    counts: dict[str, int] = {lang: 0 for lang in _LIMITS}

    for root_path, default_slice in roots:
        root_str = str(root_path)
        for path in sorted(root_path.rglob("*")):
            if not path.is_file():
                continue
            if _should_skip(path):
                continue
            try:
                if path.stat().st_size > _MAX_FILE_BYTES:
                    continue
            except OSError:
                continue

            lang = _language_for(path)
            if lang is None:
                continue

            bucket = lang if lang in _LIMITS else "doc"
            if counts.get(bucket, 0) >= _LIMITS.get(bucket, 9999):
                continue
            counts[bucket] = counts.get(bucket, 0) + 1

            rel = str(path.relative_to(root_path))
            corpus_slice = _classify_corpus_slice(lang, rel, default_slice)
            results.append((path, lang, root_str, corpus_slice))

    return results


# ---------------------------------------------------------------------------
# Database connection helper
# ---------------------------------------------------------------------------


def _connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Document chunkers (tex / markdown)
# ---------------------------------------------------------------------------

_TEX_SECTION_RE = re.compile(r"\\(?:sub)*section\*?\{([^}]+)\}")
_MD_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)
_COMPONENT_RE = re.compile(
    r"(?:^|[/\\])(GM|IE|IM|IH|SC|OH|RB|UA|PS|SP|CON|BATS|RCM|RIM|PWOM|CIE|CIMI|GITM)"
    r"(?:[/\\$])",
    re.IGNORECASE,
)


def _component_from_path(rel_path: str) -> str | None:
    m = _COMPONENT_RE.search(rel_path)
    return m.group(1).upper() if m else None


def _split_sections(text: str, pattern: re.Pattern) -> list[tuple[str, int, str]]:
    """Split *text* into (heading, 1-based start_line, body) tuples."""
    results: list[tuple[str, int, str]] = []
    last_end = 0
    current_heading = "__preamble__"
    current_start_line = 1

    for m in pattern.finditer(text):
        heading = m.group(1).strip()
        start_char = m.start()
        start_line = text[:start_char].count("\n") + 1

        body = text[last_end:start_char]
        if body.strip():
            results.append((current_heading, current_start_line, body[:_MAX_CHUNK_CHARS]))

        current_heading = heading
        current_start_line = start_line
        last_end = start_char

    remaining = text[last_end:]
    if remaining.strip():
        results.append((current_heading, current_start_line, remaining[:_MAX_CHUNK_CHARS]))

    return results


# ---------------------------------------------------------------------------
# Symbol indexing helpers
# ---------------------------------------------------------------------------


def _index_fortran(
    conn: sqlite3.Connection,
    file_id: int,
    path: Path,
    text: str,
    source_kind: str,
) -> list[tuple[int, list[str]]]:
    inserted: list[tuple[int, list[str]]] = []
    for sym in parse_fortran_file(path, text=text):
        cur = conn.execute(
            "INSERT INTO symbols "
            "(file_id, name, kind, start_line, component, docstring, uses, source_kind, authority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                file_id, sym.name, sym.kind, sym.start_line, sym.component,
                sym.docstring, json.dumps(sym.uses) if sym.uses else None,
                source_kind, AUTHORITY_HEURISTIC,
            ),
        )
        symbol_id = cur.lastrowid
        assert symbol_id is not None
        inserted.append((symbol_id, sym.param_refs))
    return inserted


def _index_perl(
    conn: sqlite3.Connection,
    file_id: int,
    path: Path,
    text: str,
    source_kind: str,
) -> list[tuple[int, list[str]]]:
    inserted: list[tuple[int, list[str]]] = []
    for sym in parse_perl_file(path, text=text):
        cur = conn.execute(
            "INSERT INTO symbols "
            "(file_id, name, kind, start_line, component, docstring, source_kind, authority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                file_id, sym.name, sym.kind, sym.start_line, None,
                sym.docstring, source_kind, AUTHORITY_HEURISTIC,
            ),
        )
        symbol_id = cur.lastrowid
        assert symbol_id is not None
        inserted.append((symbol_id, sym.param_refs))
    return inserted


def _index_idl(
    conn: sqlite3.Connection,
    file_id: int,
    path: Path,
    text: str,
    source_kind: str,
) -> list[tuple[int, list[str]]]:
    inserted: list[tuple[int, list[str]]] = []
    for sig in parse_idl_file(path):
        cur = conn.execute(
            "INSERT INTO symbols "
            "(file_id, name, kind, start_line, component, docstring, source_kind, authority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                file_id, sig.name, sig.kind, sig.line_number, None,
                sig.docstring, source_kind, AUTHORITY_HEURISTIC,
            ),
        )
        symbol_id = cur.lastrowid
        assert symbol_id is not None
        inserted.append((symbol_id, []))
    return inserted


def _index_doc(
    conn: sqlite3.Connection,
    file_id: int,
    path: Path,
    text: str,
    source_kind: str,
    lang: str,
    rel_path: str,
) -> None:
    """Index tex / markdown / rst files as doc_section symbols."""
    pattern = _TEX_SECTION_RE if lang == "tex" else _MD_HEADING_RE
    component = _component_from_path(rel_path)
    sections = _split_sections(text, pattern)
    if not sections:
        sections = [(path.stem, 1, text[:_MAX_CHUNK_CHARS])]
    for heading, start_line, body in sections:
        conn.execute(
            "INSERT INTO symbols "
            "(file_id, name, kind, start_line, component, docstring, source_kind, authority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                file_id, heading, "doc_section", start_line, component,
                body, source_kind, AUTHORITY_HEURISTIC,
            ),
        )


def _store_param_mentions(
    conn: sqlite3.Connection,
    file_id: int,
    symbol_entries: list[tuple[int, list[str]]],
    source_kind: str,
) -> None:
    for symbol_id, param_refs in symbol_entries:
        for cmd in param_refs:
            conn.execute(
                "INSERT INTO param_mentions "
                "(command_normalized, file_id, symbol_id, source_kind, authority) "
                "VALUES (?, ?, ?, ?, ?)",
                (cmd, file_id, symbol_id, source_kind, AUTHORITY_HEURISTIC),
            )


def _index_fortran_chunks(
    conn: sqlite3.Connection,
    file_id: int,
    path: Path,
    text: str,
    source_kind: str,
) -> None:
    for chunk in parse_fortran_chunks(path, text=text):
        conn.execute(
            "INSERT INTO code_chunks "
            "(file_id, symbol_name, chunk_kind, label, start_line, end_line, component, chunk_text, uses, param_refs, source_kind, authority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                file_id,
                chunk.symbol_name,
                chunk.chunk_kind,
                chunk.label,
                chunk.start_line,
                chunk.end_line,
                chunk.component,
                chunk.text[:_MAX_CHUNK_CHARS],
                json.dumps(chunk.uses) if chunk.uses else None,
                json.dumps(chunk.param_refs) if chunk.param_refs else None,
                source_kind,
                AUTHORITY_HEURISTIC,
            ),
        )


def _index_file(
    conn: sqlite3.Connection,
    path: Path,
    lang: str,
    corpus_root: str = "",
    corpus_slice: str = "",
) -> None:
    """Read, parse, and store one source file into the database."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return

    mtime = path.stat().st_mtime
    digest = _content_digest(text)
    source_kind = _source_kind_for(lang)
    now = time.time()

    rel_path = ""
    if corpus_root:
        try:
            rel_path = str(path.relative_to(corpus_root))
        except ValueError:
            rel_path = path.name

    cur = conn.execute(
        "INSERT OR REPLACE INTO source_files "
        "(path, language, corpus_root, corpus_slice, mtime, content_digest, indexed_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (str(path.resolve()), lang, corpus_root, corpus_slice, mtime, digest, now),
    )
    file_id = cur.lastrowid
    assert file_id is not None

    if lang == "fortran":
        entries = _index_fortran(conn, file_id, path, text, source_kind)
        _store_param_mentions(conn, file_id, entries, source_kind)
        _index_fortran_chunks(conn, file_id, path, text, source_kind)
    elif lang == "perl":
        entries = _index_perl(conn, file_id, path, text, source_kind)
        _store_param_mentions(conn, file_id, entries, source_kind)
    elif lang == "idl":
        _index_idl(conn, file_id, path, text, source_kind)
    elif lang in ("tex", "doc"):
        _index_doc(conn, file_id, path, text, source_kind, lang, rel_path)


# ---------------------------------------------------------------------------
# FTS5 query helper
# ---------------------------------------------------------------------------

# English words that appear in natural-language queries but not in Fortran
# symbol names or docstrings.  These are removed before FTS5 AND matching so
# that broad queries like "interpolation methods in SWMF" reduce to the
# meaningful domain token "interpolation" rather than failing because "methods"
# and "in" never appear in a subroutine name.
_FTS_STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "been", "by",
    "do", "does", "for", "from", "get", "getting",
    "how", "in", "into", "is", "it", "its",
    "list", "look", "looking",
    "me", "method", "methods",
    "of", "on", "or",
    "related", "return", "returns",
    "search", "show", "some", "source", "swmf", "swmfsolar",
    "that", "the", "their", "them", "there", "these", "they",
    "this", "to", "type", "types",
    "use", "used", "uses", "using",
    "was", "what", "where", "which", "with",
})


def _safe_fts_query(query: str) -> str:
    """Convert free text to a safe FTS5 MATCH expression (AND semantics).

    English stopwords are stripped before building the expression so that
    natural-language queries (e.g. "interpolation methods in SWMF") match
    domain symbols (e.g. ``interpolation_amr_gc``) instead of failing because
    every token must appear in the symbol text.
    """
    cleaned = re.sub(r'["\(\)\:\*\^\+\-]', " ", query.strip())
    tokens = [
        t for t in cleaned.split()
        if len(t) > 1 and t.lower() not in _FTS_STOPWORDS
    ]
    if not tokens:
        # All tokens were stopwords; fall back to the original cleaned query
        # so callers can still attempt a LIKE search.
        tokens = [t for t in cleaned.split() if len(t) > 1]
    if not tokens:
        return '""'
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# Row -> dict helper
# ---------------------------------------------------------------------------


def _symbol_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    uses_raw = d.get("uses")
    d["uses"] = json.loads(uses_raw) if uses_raw else []
    return d


def _chunk_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    uses_raw = d.get("uses")
    param_refs_raw = d.get("param_refs")
    d["uses"] = json.loads(uses_raw) if uses_raw else []
    d["param_refs"] = json.loads(param_refs_raw) if param_refs_raw else []
    return d


# ---------------------------------------------------------------------------
# Main catalog class
# ---------------------------------------------------------------------------


class SourceIndexCatalog:
    """Persistent knowledge index over one or more corpus roots.

    Parameters
    ----------
    swmf_root:
        Primary SWMF root.  The SQLite database lives at
        ``{swmf_root}/.swmf_mcp_cache/knowledge.db``.
    extra_roots:
        Optional list of ``(path, corpus_slice)`` pairs for additional
        repos, e.g. SWMFSOLAR or the MCP prototype repo.
    """

    def __init__(
        self,
        swmf_root: str | Path,
        *,
        extra_roots: Sequence[tuple[str | Path, str]] | None = None,
    ) -> None:
        self._swmf_root = Path(swmf_root).resolve()
        self._db_path = _db_path_for(self._swmf_root)
        self._extra_roots: list[tuple[Path, str]] = [
            (Path(p).resolve(), s) for p, s in (extra_roots or [])
        ]
        self._read_conn: sqlite3.Connection | None = None

    def _close_read_conn(self) -> None:
        if self._read_conn is None:
            return
        try:
            self._read_conn.close()
        except sqlite3.Error:
            pass
        self._read_conn = None

    @property
    def swmf_root(self) -> str:
        return str(self._swmf_root)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> KnowledgeIndexStatus:
        """Return current index status without modifying anything."""
        if not self._db_path.exists():
            return KnowledgeIndexStatus(
                ok=False,
                db_path=str(self._db_path),
                swmf_root=str(self._swmf_root),
                schema_version=SCHEMA_VERSION,
                symbol_count=0,
                file_count=0,
                last_built_epoch_s=None,
                is_stale=True,
                message="Index not yet built. Run the server with --preindex-knowledge or call get_evidence to build it on demand.",
                corpus_roots=[],
            )

        try:
            conn = _connect(self._db_path)
            with conn:
                manifest = dict(
                    conn.execute("SELECT key, value FROM manifest").fetchall()
                )
                symbol_count = conn.execute(
                    "SELECT COUNT(*) FROM symbols"
                ).fetchone()[0]
                file_count = conn.execute(
                    "SELECT COUNT(*) FROM source_files"
                ).fetchone()[0]
            conn.close()
        except sqlite3.Error as exc:
            return KnowledgeIndexStatus(
                ok=False,
                db_path=str(self._db_path),
                swmf_root=str(self._swmf_root),
                schema_version=SCHEMA_VERSION,
                symbol_count=0,
                file_count=0,
                last_built_epoch_s=None,
                is_stale=True,
                message=f"Database error: {exc}",
                corpus_roots=[],
            )

        built_at = float(manifest.get("built_at", "0")) or None
        schema = manifest.get("schema_version", "?")
        is_stale = schema != SCHEMA_VERSION
        try:
            corpus_roots: list[str] = json.loads(manifest.get("corpus_roots", "[]"))
        except (json.JSONDecodeError, TypeError):
            corpus_roots = [str(self._swmf_root)]

        return KnowledgeIndexStatus(
            ok=True,
            db_path=str(self._db_path),
            swmf_root=str(self._swmf_root),
            schema_version=schema,
            symbol_count=symbol_count,
            file_count=file_count,
            last_built_epoch_s=built_at,
            is_stale=is_stale,
            message=None,
            corpus_roots=corpus_roots,
        )

    # ------------------------------------------------------------------
    # Build / refresh
    # ------------------------------------------------------------------

    def build(self, force: bool = False) -> KnowledgeIndexStatus:
        """Full scan across all corpus roots (drop + rebuild).

        Skipped when the DB is current and *force* is False.
        """
        if self._db_path.exists() and not force:
            status = self.get_status()
            if status.ok and not status.is_stale:
                return status

        self._close_read_conn()
        conn = _connect(self._db_path)
        try:
            # Wipe and recreate schema (executescript auto-commits pending tx)
            conn.executescript(_DROP_TABLES)
            conn.executescript(_DDL)
            # No FTS triggers yet — bulk insert without per-row overhead

            with conn:
                files = _discover_all_files(self._swmf_root, self._extra_roots)
                for path, lang, corpus_root, corpus_slice in files:
                    _index_file(conn, path, lang, corpus_root, corpus_slice)

                # Populate FTS index from the content table in one shot
                conn.execute("INSERT INTO symbols_fts(symbols_fts) VALUES ('rebuild')")
                conn.execute("INSERT INTO code_chunks_fts(code_chunks_fts) VALUES ('rebuild')")

                now = time.time()
                corpus_root_strs = [str(self._swmf_root)] + [
                    str(r) for r, _ in self._extra_roots
                ]
                for key, value in [
                    ("schema_version", SCHEMA_VERSION),
                    ("swmf_root", str(self._swmf_root)),
                    ("built_at", str(now)),
                    ("corpus_roots", json.dumps(corpus_root_strs)),
                ]:
                    conn.execute(
                        "INSERT OR REPLACE INTO manifest (key, value) VALUES (?, ?)",
                        (key, value),
                    )

            # Install FTS sync triggers for future incremental refreshes
            conn.executescript(_FTS_TRIGGERS)
        finally:
            conn.close()

        return self.get_status()

    def refresh(self) -> KnowledgeIndexStatus:
        """Incremental update across all corpus roots.

        - New files are indexed.
        - Changed files (mtime differs) are re-indexed.
        - Deleted files are removed.

        Delegates to :meth:`build` when the DB is absent or schema is stale.
        """
        if not self._db_path.exists():
            return self.build()

        # Schema version check — force rebuild on mismatch
        try:
            conn = _connect(self._db_path)
            row = conn.execute(
                "SELECT value FROM manifest WHERE key = 'schema_version'"
            ).fetchone()
            db_schema = row[0] if row else "0"
            conn.close()
        except sqlite3.Error:
            db_schema = "0"

        if db_schema != SCHEMA_VERSION:
            return self.build(force=True)

        self._close_read_conn()
        conn = _connect(self._db_path)
        try:
            # Ensure FTS triggers exist (no-op if already installed)
            conn.executescript(_FTS_TRIGGERS)

            with conn:
                db_files: dict[str, dict[str, Any]] = {
                    row["path"]: dict(row)
                    for row in conn.execute(
                        "SELECT id, path, mtime, content_digest FROM source_files"
                    )
                }
                disk_files: dict[str, tuple[str, str, str]] = {
                    str(p.resolve()): (lang, corpus_root, corpus_slice)
                    for p, lang, corpus_root, corpus_slice
                    in _discover_all_files(self._swmf_root, self._extra_roots)
                }

                # Remove deleted files (CASCADE removes symbols -> FTS triggers sync)
                for db_path in list(db_files):
                    if db_path not in disk_files:
                        conn.execute(
                            "DELETE FROM source_files WHERE path = ?", (db_path,)
                        )

                # Add new or re-index changed
                for abs_path, (lang, corpus_root, corpus_slice) in disk_files.items():
                    path = Path(abs_path)
                    try:
                        mtime = path.stat().st_mtime
                    except OSError:
                        continue

                    row = db_files.get(abs_path)
                    if row is not None:
                        if abs(row["mtime"] - mtime) < 0.01:
                            continue  # unchanged
                        conn.execute(
                            "DELETE FROM source_files WHERE path = ?", (abs_path,)
                        )

                    _index_file(conn, path, lang, corpus_root, corpus_slice)

                now = time.time()
                corpus_root_strs = [str(self._swmf_root)] + [
                    str(r) for r, _ in self._extra_roots
                ]
                for key, value in [
                    ("built_at", str(now)),
                    ("schema_version", SCHEMA_VERSION),
                    ("corpus_roots", json.dumps(corpus_root_strs)),
                ]:
                    conn.execute(
                        "INSERT OR REPLACE INTO manifest (key, value) VALUES (?, ?)",
                        (key, value),
                    )
        finally:
            conn.close()

        return self.get_status()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_db(self) -> sqlite3.Connection | None:
        if not self._db_path.exists():
            return None
        if self._read_conn is not None:
            try:
                self._read_conn.execute("SELECT 1")
                return self._read_conn
            except sqlite3.Error:
                self._close_read_conn()
        try:
            self._read_conn = _connect(self._db_path)
            return self._read_conn
        except sqlite3.Error:
            self._read_conn = None
            return None

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def search_symbols(
        self,
        query: str,
        component: str | None = None,
        kind: str | None = None,
        corpus_slice: str | None = None,
        max_results: int = 20,
    ) -> list[dict[str, Any]]:
        """Search across symbol names, docstrings, and doc sections.

        Uses FTS5 BM25 ranking when available; falls back to case-insensitive
        LIKE matching.

        Parameters
        ----------
        corpus_slice:
            Optional filter by corpus slice, e.g. ``"swmfsolar_source"``
            or ``"swmf_manuals"``.
        """
        conn = self._require_db()
        if conn is None:
            return []

        results: list[dict[str, Any]] = []
        try:
            results = self._search_fts5(
                conn, query,
                component=component, kind=kind,
                corpus_slice=corpus_slice, max_results=max_results,
            )
        except sqlite3.OperationalError:
            pass

        if not results:
            try:
                results = self._search_like(
                    conn, query,
                    component=component, kind=kind,
                    corpus_slice=corpus_slice, max_results=max_results,
                )
            except sqlite3.Error:
                pass

        return results

    def search_source(
        self,
        query: str,
        component: str | None = None,
        kind: str | None = None,
        corpus_slice: str | None = None,
        max_results: int = 20,
        search_mode: str = SEARCH_MODE_KEYWORD,
    ) -> list[dict[str, Any]]:
        """Keyword source retrieval.

        The catalog domain owns index-backed keyword search only. Semantic and
        hybrid ranking are handled by the knowledge domain.
        """
        _ = _normalize_search_mode(search_mode)
        return self.search_symbols(
            query=query,
            component=component,
            kind=kind,
            corpus_slice=corpus_slice,
            max_results=max_results,
        )

    def search_chunks(
        self,
        query: str,
        component: str | None = None,
        chunk_kind: str | None = None,
        corpus_slice: str | None = None,
        max_results: int = 20,
    ) -> list[dict[str, Any]]:
        """Search meaning-bearing code chunks extracted from source bodies."""
        conn = self._require_db()
        if conn is None:
            return []

        results: list[dict[str, Any]] = []
        try:
            results = self._search_chunks_fts5(
                conn,
                query,
                component=component,
                chunk_kind=chunk_kind,
                corpus_slice=corpus_slice,
                max_results=max_results,
            )
        except sqlite3.OperationalError:
            pass

        if not results:
            try:
                results = self._search_chunks_like(
                    conn,
                    query,
                    component=component,
                    chunk_kind=chunk_kind,
                    corpus_slice=corpus_slice,
                    max_results=max_results,
                )
            except sqlite3.Error:
                pass

        return results

    def list_chunks(
        self,
        component: str | None = None,
        chunk_kind: str | None = None,
        corpus_slice: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return raw indexed chunks for downstream knowledge-domain ranking."""
        conn = self._require_db()
        if conn is None:
            return []
        try:
            return self._list_chunks(
                conn,
                component=component,
                chunk_kind=chunk_kind,
                corpus_slice=corpus_slice,
            )
        except sqlite3.Error:
            return []

    def _search_fts5(
        self,
        conn: sqlite3.Connection,
        query: str,
        *,
        component: str | None,
        kind: str | None,
        corpus_slice: str | None,
        max_results: int,
    ) -> list[dict[str, Any]]:
        fts_q = _safe_fts_query(query)
        params: list[Any] = [fts_q]
        extra_where = ""
        if component:
            extra_where += " AND UPPER(s.component) = UPPER(?)"
            params.append(component)
        if kind:
            extra_where += " AND s.kind = ?"
            params.append(kind)
        if corpus_slice:
            extra_where += " AND f.corpus_slice = ?"
            params.append(corpus_slice)
        params.append(max_results)

        sql = (
            "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
            "       s.source_kind, s.authority, s.uses, "
            "       f.path AS file_path, f.corpus_root, f.corpus_slice "
            "FROM symbols_fts fts "
            "JOIN symbols s ON fts.rowid = s.id "
            "JOIN source_files f ON s.file_id = f.id "
            f"WHERE symbols_fts MATCH ?{extra_where} "
            "ORDER BY rank LIMIT ?"
        )
        rows = conn.execute(sql, params).fetchall()
        return [_symbol_row_to_dict(row) for row in rows]

    def _search_like(
        self,
        conn: sqlite3.Connection,
        query: str,
        *,
        component: str | None,
        kind: str | None,
        corpus_slice: str | None,
        max_results: int,
    ) -> list[dict[str, Any]]:
        # First attempt: full phrase as a single LIKE substring.
        # Second attempt (if first returns nothing): try each content token
        # individually so that broad NL queries like "interpolation methods"
        # still match symbol names like "interpolation_amr_gc".
        candidate_likes: list[str] = [query.lower()]
        content_tokens = [
            t.lower()
            for t in query.split()
            if len(t) > 2 and t.lower() not in _FTS_STOPWORDS
        ]
        candidate_likes.extend(content_tokens)

        for attempt, term in enumerate(candidate_likes):
            like = f"%{term}%"
            params: list[Any] = [like, like]
            where = (
                "WHERE (LOWER(s.name) LIKE ? OR LOWER(COALESCE(s.docstring,'')) LIKE ?)"
            )
            if component:
                where += " AND UPPER(s.component) = UPPER(?)"
                params.append(component)
            if kind:
                where += " AND s.kind = ?"
                params.append(kind)
            if corpus_slice:
                where += " AND f.corpus_slice = ?"
                params.append(corpus_slice)
            params.append(max_results)

            sql = (
                "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
                "       s.source_kind, s.authority, s.uses, "
                "       f.path AS file_path, f.corpus_root, f.corpus_slice "
                "FROM symbols s JOIN source_files f ON s.file_id = f.id "
                f"{where} ORDER BY s.name LIMIT ?"
            )
            rows = conn.execute(sql, params).fetchall()
            if rows:
                return [_symbol_row_to_dict(row) for row in rows]
            # If this was the full-phrase attempt and it failed, fall through
            # to individual token attempts (but only if tokens differ from
            # the full phrase).
            if attempt == 0 and (not content_tokens or content_tokens == [query.lower()]):
                break

        return []

    def _search_chunks_fts5(
        self,
        conn: sqlite3.Connection,
        query: str,
        *,
        component: str | None,
        chunk_kind: str | None,
        corpus_slice: str | None,
        max_results: int,
    ) -> list[dict[str, Any]]:
        fts_q = _safe_fts_query(query)
        params: list[Any] = [fts_q]
        extra_where = ""
        if component:
            extra_where += " AND UPPER(c.component) = UPPER(?)"
            params.append(component)
        if chunk_kind:
            extra_where += " AND c.chunk_kind = ?"
            params.append(chunk_kind)
        if corpus_slice:
            extra_where += " AND f.corpus_slice = ?"
            params.append(corpus_slice)
        params.append(max_results)

        sql = (
            "SELECT c.symbol_name, c.chunk_kind, c.label, c.start_line, c.end_line, c.component, "
            "       c.chunk_text, c.uses, c.param_refs, c.source_kind, c.authority, "
            "       f.path AS file_path, f.corpus_root, f.corpus_slice "
            "FROM code_chunks_fts fts "
            "JOIN code_chunks c ON fts.rowid = c.id "
            "JOIN source_files f ON c.file_id = f.id "
            f"WHERE code_chunks_fts MATCH ?{extra_where} "
            "ORDER BY rank LIMIT ?"
        )
        rows = conn.execute(sql, params).fetchall()
        return [_chunk_row_to_dict(row) for row in rows]

    def _search_chunks_like(
        self,
        conn: sqlite3.Connection,
        query: str,
        *,
        component: str | None,
        chunk_kind: str | None,
        corpus_slice: str | None,
        max_results: int,
    ) -> list[dict[str, Any]]:
        like = f"%{query.lower()}%"
        params: list[Any] = [like, like, like]
        where = (
            "WHERE (LOWER(c.symbol_name) LIKE ? OR LOWER(c.label) LIKE ? OR LOWER(c.chunk_text) LIKE ?)"
        )
        if component:
            where += " AND UPPER(c.component) = UPPER(?)"
            params.append(component)
        if chunk_kind:
            where += " AND c.chunk_kind = ?"
            params.append(chunk_kind)
        if corpus_slice:
            where += " AND f.corpus_slice = ?"
            params.append(corpus_slice)
        params.append(max_results)

        sql = (
            "SELECT c.symbol_name, c.chunk_kind, c.label, c.start_line, c.end_line, c.component, "
            "       c.chunk_text, c.uses, c.param_refs, c.source_kind, c.authority, "
            "       f.path AS file_path, f.corpus_root, f.corpus_slice "
            "FROM code_chunks c JOIN source_files f ON c.file_id = f.id "
            f"{where} ORDER BY c.symbol_name, c.start_line LIMIT ?"
        )
        rows = conn.execute(sql, params).fetchall()
        return [_chunk_row_to_dict(row) for row in rows]

    def _list_chunks(
        self,
        conn: sqlite3.Connection,
        *,
        component: str | None,
        chunk_kind: str | None = None,
        corpus_slice: str | None,
    ) -> list[dict[str, Any]]:
        params: list[Any] = []
        where: list[str] = []
        if component:
            where.append("UPPER(c.component) = UPPER(?)")
            params.append(component)
        if chunk_kind:
            where.append("c.chunk_kind = ?")
            params.append(chunk_kind)
        if corpus_slice:
            where.append("f.corpus_slice = ?")
            params.append(corpus_slice)

        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        sql = (
            "SELECT c.id, c.symbol_name, c.chunk_kind, c.label, c.start_line, c.end_line, c.component, "
            "       c.chunk_text, c.uses, c.param_refs, c.source_kind, c.authority, "
            "       f.path AS file_path, f.corpus_root, f.corpus_slice "
            "FROM code_chunks c JOIN source_files f ON c.file_id = f.id "
            f"{where_sql} ORDER BY f.path, c.start_line"
        )
        rows = conn.execute(sql, params).fetchall()
        return [_chunk_row_to_dict(row) for row in rows]

    def lookup_symbol(self, name: str, kind: str | None = None) -> list[dict[str, Any]]:
        """Exact (case-insensitive) symbol name lookup."""
        conn = self._require_db()
        if conn is None:
            return []

        params: list[Any] = [name.lower()]
        where = "WHERE LOWER(s.name) = ?"
        if kind:
            where += " AND s.kind = ?"
            params.append(kind)

        sql = (
            "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
            "       s.source_kind, s.authority, s.uses, "
            "       f.path AS file_path, f.corpus_root, f.corpus_slice "
            "FROM symbols s JOIN source_files f ON s.file_id = f.id "
            f"{where} ORDER BY s.name"
        )
        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.Error:
            rows = []

        return [_symbol_row_to_dict(row) for row in rows]

    def get_param_evidence(
        self,
        command_normalized: str,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Return source symbols and files that reference a PARAM command.

        Combines explicit ``param_mentions`` with text-search fallback.
        """
        conn = self._require_db()
        if conn is None:
            return []

        results: list[dict[str, Any]] = []
        cmd_upper = command_normalized.upper()
        cmd_lower = command_normalized.lower()

        try:
            mention_sql = (
                "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
                "       s.source_kind, s.authority, s.uses, "
                "       f.path AS file_path, f.corpus_root, f.corpus_slice "
                "FROM param_mentions pm "
                "JOIN source_files f ON pm.file_id = f.id "
                "LEFT JOIN symbols s ON pm.symbol_id = s.id "
                "WHERE UPPER(pm.command_normalized) = ? "
                "ORDER BY f.language, s.name LIMIT ?"
            )
            for row in conn.execute(mention_sql, (cmd_upper, max_results)).fetchall():
                record = _symbol_row_to_dict(row)
                record["evidence_kind"] = "explicit_param_mention"
                results.append(record)

            if len(results) < max_results:
                remaining = max_results - len(results)
                seen_paths = {r["file_path"] for r in results}
                like = f"%{cmd_lower}%"
                text_sql = (
                    "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
                    "       s.source_kind, s.authority, s.uses, "
                    "       f.path AS file_path, f.corpus_root, f.corpus_slice "
                    "FROM symbols s JOIN source_files f ON s.file_id = f.id "
                    "WHERE LOWER(COALESCE(s.name,'')) LIKE ? "
                    "   OR LOWER(COALESCE(s.docstring,'')) LIKE ? "
                    "ORDER BY s.name LIMIT ?"
                )
                for row in conn.execute(text_sql, (like, like, remaining)).fetchall():
                    record = _symbol_row_to_dict(row)
                    if record["file_path"] not in seen_paths:
                        record["evidence_kind"] = "text_match"
                        results.append(record)
        except sqlite3.Error:
            pass

        return results

    def get_file_symbols(self, file_path: str) -> list[dict[str, Any]]:
        """Return all symbols indexed from a given absolute file path."""
        conn = self._require_db()
        if conn is None:
            return []

        sql = (
            "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
            "       s.source_kind, s.authority, s.uses, "
            "       f.path AS file_path, f.corpus_root, f.corpus_slice "
            "FROM symbols s JOIN source_files f ON s.file_id = f.id "
            "WHERE f.path = ? ORDER BY s.start_line"
        )
        try:
            rows = conn.execute(sql, (file_path,)).fetchall()
        except sqlite3.Error:
            rows = []

        return [_symbol_row_to_dict(row) for row in rows]
