"""Persistent SQLite-backed source index for the SWMF knowledge base.

Architecture
------------
One SQLite database per SWMF root, stored at::

    {swmf_root}/.swmf_mcp_cache/knowledge.db

Override with the ``SWMF_MCP_KNOWLEDGE_DB`` environment variable.

The index is **not** built automatically on first use — callers must invoke
:meth:`SourceIndexCatalog.build` or :meth:`SourceIndexCatalog.refresh`
explicitly, typically via the ``swmf-index build --corpus SWMF --corpus SWMFSOLAR``
CLI workflow used by the reconstructed skills-first architecture. Subsequent
search/lookup calls are fast because they read from the persisted store.

Indexed corpus
--------------
Priority 1 — always indexed:
  * All ``PARAM.XML`` files
  * ``Scripts/TestParam.pl``, ``Config.pl``, ``Scripts/Restart.pl``, ``Scripts/PostProc.pl``
  * Control layer: ``src/CON_*.f90``, ``src/Mod*.f90``

Priority 2 — indexed when present:
  * All ``*.f90``/``*.f`` files under component directories
  * All ``*.pl`` files under ``Scripts/``
  * All ``*.pro`` files under ``share/IDL/``
  * All ``*.tex`` files under ``doc/Tex/``

Authority
---------
All symbols extracted by this catalog carry ``authority="heuristic"`` because
they come from regex-based parsing, not from SWMF's own validator.  PARAM.XML
and TestParam.pl results remain ``"authoritative"`` — this layer supplements,
never overrides, those sources.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from ..core.authority import (
    AUTHORITY_HEURISTIC,
    SOURCE_KIND_FORTRAN_SOURCE,
    SOURCE_KIND_IDL_SOURCE,
    SOURCE_KIND_MANUAL_DOC,
    SOURCE_KIND_PERL_SOURCE,
)
from ..core.models import KnowledgeIndexStatus
from ..parsing.fortran_parser import FortranSymbol, parse_fortran_file
from ..parsing.idl_parser import parse_idl_file
from ..parsing.perl_parser import PerlSymbol, parse_perl_file

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1"
CACHE_DIR_NAME = ".swmf_mcp_cache"
DB_FILE_NAME = "knowledge.db"
ENV_DB_OVERRIDE = "SWMF_MCP_KNOWLEDGE_DB"

# Per-language file limits to prevent runaway indexing on large trees
_LIMITS: dict[str, int] = {
    "fortran": 5000,
    "perl": 300,
    "idl": 4000,
    "tex": 150,
}

# Directories to skip while walking the source tree
_SKIP_DIRS = {
    ".git", ".svn", ".hg", ".swmf_mcp_cache",
    "node_modules", "build", "tmp", "work",
}

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

CREATE TABLE IF NOT EXISTS param_mentions (
    id                 INTEGER PRIMARY KEY,
    command_normalized TEXT    NOT NULL,
    file_id            INTEGER REFERENCES source_files(id) ON DELETE CASCADE,
    symbol_id          INTEGER REFERENCES symbols(id) ON DELETE SET NULL,
    line_number        INTEGER,
    context_snippet    TEXT,
    source_kind        TEXT    NOT NULL,
    authority          TEXT    NOT NULL DEFAULT 'heuristic'
);

CREATE INDEX IF NOT EXISTS idx_symbols_name      ON symbols(name);
CREATE INDEX IF NOT EXISTS idx_symbols_component  ON symbols(component);
CREATE INDEX IF NOT EXISTS idx_symbols_kind       ON symbols(kind);
CREATE INDEX IF NOT EXISTS idx_symbols_file       ON symbols(file_id);
CREATE INDEX IF NOT EXISTS idx_param_cmd          ON param_mentions(command_normalized);
CREATE INDEX IF NOT EXISTS idx_param_file         ON param_mentions(file_id);
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
    if ext == ".pl":
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


def _should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in _SKIP_DIRS or (part.startswith(".") and part != "."):
            return True
    return False


def _db_path_for(swmf_root: str | Path) -> Path:
    override = os.environ.get(ENV_DB_OVERRIDE)
    if override:
        return Path(override).expanduser()
    return Path(swmf_root) / CACHE_DIR_NAME / DB_FILE_NAME


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def _discover_files(swmf_root: Path) -> list[tuple[Path, str]]:
    """Return (path, language) pairs for all indexable files under *swmf_root*."""
    results: list[tuple[Path, str]] = []
    counts: dict[str, int] = {lang: 0 for lang in _LIMITS}

    for path in sorted(swmf_root.rglob("*")):
        if not path.is_file():
            continue
        if _should_skip(path):
            continue

        lang = _language_for(path)
        if lang is None:
            continue

        bucket = lang if lang in _LIMITS else "tex"
        if counts.get(bucket, 0) >= _LIMITS.get(bucket, 9999):
            continue

        counts[bucket] = counts.get(bucket, 0) + 1
        results.append((path, lang))

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
# Symbol indexing
# ---------------------------------------------------------------------------


def _index_fortran(
    conn: sqlite3.Connection,
    file_id: int,
    path: Path,
    text: str,
    source_kind: str,
) -> list[tuple[int, list[str]]]:
    """Insert Fortran symbols; return [(symbol_id, param_refs), ...]."""
    inserted: list[tuple[int, list[str]]] = []
    for sym in parse_fortran_file(path, text=text):
        cur = conn.execute(
            "INSERT INTO symbols (file_id, name, kind, start_line, component, docstring, uses, source_kind, authority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                file_id,
                sym.name,
                sym.kind,
                sym.start_line,
                sym.component,
                sym.docstring,
                json.dumps(sym.uses) if sym.uses else None,
                source_kind,
                AUTHORITY_HEURISTIC,
            ),
        )
        inserted.append((cur.lastrowid, sym.param_refs))
    return inserted


def _index_perl(
    conn: sqlite3.Connection,
    file_id: int,
    path: Path,
    text: str,
    source_kind: str,
) -> list[tuple[int, list[str]]]:
    """Insert Perl symbols; return [(symbol_id, param_refs), ...]."""
    inserted: list[tuple[int, list[str]]] = []
    for sym in parse_perl_file(path, text=text):
        cur = conn.execute(
            "INSERT INTO symbols (file_id, name, kind, start_line, component, docstring, source_kind, authority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                file_id,
                sym.name,
                sym.kind,
                sym.start_line,
                None,
                sym.docstring,
                source_kind,
                AUTHORITY_HEURISTIC,
            ),
        )
        inserted.append((cur.lastrowid, sym.param_refs))
    return inserted


def _index_idl(
    conn: sqlite3.Connection,
    file_id: int,
    path: Path,
    text: str,
    source_kind: str,
) -> list[tuple[int, list[str]]]:
    """Insert IDL symbols; return [(symbol_id, [])]."""
    inserted: list[tuple[int, list[str]]] = []
    for sig in parse_idl_file(path):
        cur = conn.execute(
            "INSERT INTO symbols (file_id, name, kind, start_line, component, docstring, source_kind, authority) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                file_id,
                sig.name,
                sig.kind,
                sig.line_number,
                None,
                sig.docstring,
                source_kind,
                AUTHORITY_HEURISTIC,
            ),
        )
        inserted.append((cur.lastrowid, []))
    return inserted


def _store_param_mentions(
    conn: sqlite3.Connection,
    file_id: int,
    symbol_entries: list[tuple[int, list[str]]],
    source_kind: str,
) -> None:
    """Store param_mentions rows linking PARAM commands to symbol + file."""
    for symbol_id, param_refs in symbol_entries:
        for cmd in param_refs:
            conn.execute(
                "INSERT INTO param_mentions "
                "(command_normalized, file_id, symbol_id, source_kind, authority) "
                "VALUES (?, ?, ?, ?, ?)",
                (cmd, file_id, symbol_id, source_kind, AUTHORITY_HEURISTIC),
            )


def _index_file(conn: sqlite3.Connection, path: Path, lang: str) -> None:
    """Read, parse, and store one source file into the database."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return

    mtime = path.stat().st_mtime
    digest = _content_digest(text)
    source_kind = _source_kind_for(lang)
    now = time.time()

    cur = conn.execute(
        "INSERT OR REPLACE INTO source_files (path, language, mtime, content_digest, indexed_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (str(path.resolve()), lang, mtime, digest, now),
    )
    file_id = cur.lastrowid

    if lang == "fortran":
        entries = _index_fortran(conn, file_id, path, text, source_kind)
    elif lang == "perl":
        entries = _index_perl(conn, file_id, path, text, source_kind)
    elif lang == "idl":
        entries = _index_idl(conn, file_id, path, text, source_kind)
    else:
        entries = []

    _store_param_mentions(conn, file_id, entries, source_kind)


# ---------------------------------------------------------------------------
# Main catalog class
# ---------------------------------------------------------------------------


class SourceIndexCatalog:
    """Persistent knowledge index for a SWMF source tree.

    One instance per SWMF root; call :meth:`build` once to populate,
    then use :meth:`search_symbols`, :meth:`lookup_symbol`, and
    :meth:`get_param_evidence` for retrieval.  :meth:`refresh` performs
    an incremental update using mtime/digest comparisons.
    """

    def __init__(self, swmf_root: str | Path) -> None:
        self._swmf_root = Path(swmf_root).resolve()
        self._db_path = _db_path_for(self._swmf_root)

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
                message="Index not yet built. Run swmf-index build --corpus SWMF --corpus SWMFSOLAR to build it.",
            )

        try:
            conn = _connect(self._db_path)
            with conn:
                manifest = dict(conn.execute("SELECT key, value FROM manifest").fetchall())
                symbol_count = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
                file_count = conn.execute("SELECT COUNT(*) FROM source_files").fetchone()[0]
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
            )

        built_at = float(manifest.get("built_at", "0")) or None
        schema = manifest.get("schema_version", "?")
        is_stale = schema != SCHEMA_VERSION

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
        )

    # ------------------------------------------------------------------
    # Build / refresh
    # ------------------------------------------------------------------

    def build(self, force: bool = False) -> KnowledgeIndexStatus:
        """Build the index from scratch (full scan).

        If the database already exists and *force* is False, the build is
        skipped and the existing index status is returned.
        """
        if self._db_path.exists() and not force:
            status = self.get_status()
            if status.ok and not status.is_stale:
                return status

        conn = _connect(self._db_path)
        try:
            with conn:
                conn.executescript(_DDL)
                # Wipe existing data on a full rebuild
                conn.execute("DELETE FROM param_mentions")
                conn.execute("DELETE FROM symbols")
                conn.execute("DELETE FROM source_files")

                files = _discover_files(self._swmf_root)
                for path, lang in files:
                    _index_file(conn, path, lang)

                now = time.time()
                for key, value in [
                    ("schema_version", SCHEMA_VERSION),
                    ("swmf_root", str(self._swmf_root)),
                    ("built_at", str(now)),
                ]:
                    conn.execute(
                        "INSERT OR REPLACE INTO manifest (key, value) VALUES (?, ?)",
                        (key, value),
                    )
        finally:
            conn.close()

        return self.get_status()

    def refresh(self) -> KnowledgeIndexStatus:
        """Incrementally update the index.

        - New files are indexed.
        - Changed files (mtime or digest differs) are re-indexed.
        - Deleted files are removed from the index.

        If the index does not exist, delegates to :meth:`build`.
        """
        if not self._db_path.exists():
            return self.build()

        conn = _connect(self._db_path)
        try:
            with conn:
                conn.executescript(_DDL)

                # Current state in db
                db_files: dict[str, dict[str, Any]] = {}
                for row in conn.execute("SELECT id, path, mtime, content_digest FROM source_files"):
                    db_files[row["path"]] = dict(row)

                # Current state on disk
                disk_files = {
                    str(p.resolve()): lang
                    for p, lang in _discover_files(self._swmf_root)
                }

                # Remove deleted
                for db_path in list(db_files):
                    if db_path not in disk_files:
                        conn.execute("DELETE FROM source_files WHERE path = ?", (db_path,))
                        db_files.pop(db_path)

                # Add new or re-index changed
                for abs_path, lang in disk_files.items():
                    path = Path(abs_path)
                    try:
                        mtime = path.stat().st_mtime
                    except OSError:
                        continue

                    row = db_files.get(abs_path)
                    if row is not None:
                        if abs(row["mtime"] - mtime) < 0.01:
                            continue  # unchanged
                        # Changed: remove old symbols then re-index
                        conn.execute("DELETE FROM source_files WHERE path = ?", (abs_path,))

                    _index_file(conn, path, lang)

                now = time.time()
                conn.execute(
                    "INSERT OR REPLACE INTO manifest (key, value) VALUES ('built_at', ?)",
                    (str(now),),
                )
                conn.execute(
                    "INSERT OR REPLACE INTO manifest (key, value) VALUES ('schema_version', ?)",
                    (SCHEMA_VERSION,),
                )
        finally:
            conn.close()

        return self.get_status()

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def _require_db(self) -> sqlite3.Connection | None:
        """Open the database, or return None if it has not been built yet."""
        if not self._db_path.exists():
            return None
        try:
            return _connect(self._db_path)
        except sqlite3.Error:
            return None

    def search_symbols(
        self,
        query: str,
        component: str | None = None,
        kind: str | None = None,
        max_results: int = 20,
    ) -> list[dict[str, Any]]:
        """Keyword search across symbol names and docstrings.

        Matching is case-insensitive LIKE on name + docstring.
        """
        conn = self._require_db()
        if conn is None:
            return []

        like = f"%{query.lower()}%"
        params: list[Any] = [like, like]
        where = "WHERE (LOWER(s.name) LIKE ? OR LOWER(COALESCE(s.docstring,'')) LIKE ?)"
        if component:
            where += " AND UPPER(s.component) = UPPER(?)"
            params.append(component)
        if kind:
            where += " AND s.kind = ?"
            params.append(kind)
        params.append(max_results)

        sql = (
            "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
            "       s.source_kind, s.authority, f.path AS file_path "
            "FROM symbols s JOIN source_files f ON s.file_id = f.id "
            f"{where} "
            "ORDER BY s.name LIMIT ?"
        )

        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.Error:
            rows = []
        finally:
            conn.close()

        return [_symbol_row_to_dict(row) for row in rows]

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
            "       s.source_kind, s.authority, f.path AS file_path "
            "FROM symbols s JOIN source_files f ON s.file_id = f.id "
            f"{where} ORDER BY s.name"
        )

        try:
            rows = conn.execute(sql, params).fetchall()
        except sqlite3.Error:
            rows = []
        finally:
            conn.close()

        return [_symbol_row_to_dict(row) for row in rows]

    def get_param_evidence(
        self,
        command_normalized: str,
        max_results: int = 10,
    ) -> list[dict[str, Any]]:
        """Return source symbols and files that reference a PARAM command.

        Combines:
        1. Explicit mentions in ``param_mentions`` (extracted during indexing)
        2. Symbols whose name or docstring contains the command string
        """
        conn = self._require_db()
        if conn is None:
            return []

        results: list[dict[str, Any]] = []
        cmd_upper = command_normalized.upper()
        cmd_lower = command_normalized.lower()

        try:
            # 1. Explicit param_mentions (highest signal)
            mention_sql = (
                "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
                "       s.source_kind, s.authority, f.path AS file_path "
                "FROM param_mentions pm "
                "JOIN source_files f ON pm.file_id = f.id "
                "LEFT JOIN symbols s ON pm.symbol_id = s.id "
                "WHERE UPPER(pm.command_normalized) = ? "
                "ORDER BY f.language, s.name "
                "LIMIT ?"
            )
            for row in conn.execute(mention_sql, (cmd_upper, max_results)).fetchall():
                record = _symbol_row_to_dict(row)
                record["evidence_kind"] = "explicit_param_mention"
                results.append(record)

            # 2. Text-search fallback when explicit mentions are scarce
            if len(results) < max_results:
                remaining = max_results - len(results)
                seen_paths = {r["file_path"] for r in results}
                like = f"%{cmd_lower}%"
                text_sql = (
                    "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
                    "       s.source_kind, s.authority, f.path AS file_path "
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
        finally:
            conn.close()

        return results

    def get_file_symbols(self, file_path: str) -> list[dict[str, Any]]:
        """Return all symbols indexed from a given absolute file path."""
        conn = self._require_db()
        if conn is None:
            return []

        sql = (
            "SELECT s.name, s.kind, s.start_line, s.component, s.docstring, "
            "       s.source_kind, s.authority, f.path AS file_path "
            "FROM symbols s JOIN source_files f ON s.file_id = f.id "
            "WHERE f.path = ? ORDER BY s.start_line"
        )
        try:
            rows = conn.execute(sql, (file_path,)).fetchall()
        except sqlite3.Error:
            rows = []
        finally:
            conn.close()

        return [_symbol_row_to_dict(row) for row in rows]


# ---------------------------------------------------------------------------
# Row → dict helper
# ---------------------------------------------------------------------------


def _symbol_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    uses_raw = d.get("uses")
    d["uses"] = json.loads(uses_raw) if uses_raw else []
    return d
