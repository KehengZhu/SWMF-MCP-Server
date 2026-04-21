"""
SQLite-backed storage for chunks and the corpus manifest.

Schema:
  chunks table: all ChunkRecord fields except embedding (stored separately)
  manifest table: single-row CorpusManifest JSON blob
  roots table: CorpusRoot rows

The storage layer does not own the embedding vectors directly — for the lexical
backend they are not stored at all. If a neural backend is configured, the caller
must call store_embeddings() after encode().

All writes are wrapped in transactions. Reads are read-only and return plain
dataclass instances (no SQLite objects leak out).
"""

from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional

from ..models import (
    AuthorityTier,
    ChunkKind,
    ChunkRecord,
    CorpusManifest,
    CorpusRoot,
    CorpusSlice,
)

_SCHEMA_VERSION = "1.0"

_DDL = """
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS manifest (
    id                  INTEGER PRIMARY KEY CHECK (id = 1),
    schema_version      TEXT    NOT NULL,
    built_at            TEXT,
    embedding_backend   TEXT    NOT NULL DEFAULT 'tfidf_lexical',
    embedding_model     TEXT,
    embedding_dim       INTEGER,
    total_chunks        INTEGER NOT NULL DEFAULT 0,
    total_files         INTEGER NOT NULL DEFAULT 0,
    index_path          TEXT
);

CREATE TABLE IF NOT EXISTS corpus_roots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    abs_path        TEXT    NOT NULL UNIQUE,
    corpus_slice    TEXT    NOT NULL,
    file_count      INTEGER NOT NULL DEFAULT 0,
    chunk_count     INTEGER NOT NULL DEFAULT 0,
    indexed_at      TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id        TEXT    PRIMARY KEY,
    corpus_root     TEXT    NOT NULL,
    rel_path        TEXT    NOT NULL,
    kind            TEXT    NOT NULL,
    authority       INTEGER NOT NULL,
    corpus_slice    TEXT    NOT NULL,
    start_line      INTEGER NOT NULL,
    end_line        INTEGER NOT NULL,
    text            TEXT    NOT NULL,
    component       TEXT,
    symbol          TEXT,
    parent_symbol   TEXT,
    keywords        TEXT    NOT NULL DEFAULT '[]'
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    chunk_id UNINDEXED,
    text,
    symbol,
    component,
    keywords,
    content='chunks',
    content_rowid='rowid'
);

CREATE TABLE IF NOT EXISTS embeddings (
    chunk_id    TEXT    PRIMARY KEY REFERENCES chunks(chunk_id) ON DELETE CASCADE,
    vector_json TEXT    NOT NULL
);
"""

_FTS_TRIGGERS = """
CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
    INSERT INTO chunks_fts(rowid, chunk_id, text, symbol, component, keywords)
    VALUES (new.rowid, new.chunk_id, new.text, new.symbol, new.component, new.keywords);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, chunk_id, text, symbol, component, keywords)
    VALUES ('delete', old.rowid, old.chunk_id, old.text, old.symbol, old.component, old.keywords);
END;

CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, chunk_id, text, symbol, component, keywords)
    VALUES ('delete', old.rowid, old.chunk_id, old.text, old.symbol, old.component, old.keywords);
    INSERT INTO chunks_fts(rowid, chunk_id, text, symbol, component, keywords)
    VALUES (new.rowid, new.chunk_id, new.text, new.symbol, new.component, new.keywords);
END;
"""


class ChunkStore:
    """
    Persistent chunk storage backed by SQLite.

    Typical lifecycle:
      store = ChunkStore(path)
      store.open()
      store.clear()  # on full rebuild
      for chunk in chunks:
          store.insert_chunk(chunk)
      store.save_manifest(manifest)
      store.close()

    For incremental refresh, use upsert_chunk() instead of insert_chunk().
    """

    def __init__(self, db_path: Path) -> None:
        self._path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def open(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_DDL)
        try:
            self._conn.executescript(_FTS_TRIGGERS)
        except sqlite3.OperationalError:
            pass  # triggers already exist
        self._conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        assert self._conn is not None, "ChunkStore is not open"
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    # ------------------------------------------------------------------
    # Chunk writes
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Drop all chunks and embeddings (full rebuild)."""
        with self.transaction() as conn:
            conn.execute("DELETE FROM embeddings")
            conn.execute("DELETE FROM chunks")
            conn.execute("DELETE FROM chunks_fts")
            conn.execute("DELETE FROM corpus_roots")
            conn.execute("DELETE FROM manifest")

    def insert_chunk(self, chunk: ChunkRecord) -> None:
        with self.transaction() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO chunks
                (chunk_id, corpus_root, rel_path, kind, authority, corpus_slice,
                 start_line, end_line, text, component, symbol, parent_symbol, keywords)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    chunk.chunk_id, chunk.corpus_root, chunk.rel_path,
                    chunk.kind.value, chunk.authority.value, chunk.corpus_slice.value,
                    chunk.start_line, chunk.end_line, chunk.text,
                    chunk.component, chunk.symbol, chunk.parent_symbol,
                    json.dumps(chunk.keywords),
                ),
            )

    def insert_chunks_bulk(self, chunks: list[ChunkRecord]) -> None:
        if not chunks:
            return
        rows = [
            (
                c.chunk_id, c.corpus_root, c.rel_path,
                c.kind.value, c.authority.value, c.corpus_slice.value,
                c.start_line, c.end_line, c.text,
                c.component, c.symbol, c.parent_symbol,
                json.dumps(c.keywords),
            )
            for c in chunks
        ]
        with self.transaction() as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO chunks
                (chunk_id, corpus_root, rel_path, kind, authority, corpus_slice,
                 start_line, end_line, text, component, symbol, parent_symbol, keywords)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                rows,
            )

    # ------------------------------------------------------------------
    # Manifest writes
    # ------------------------------------------------------------------

    def save_manifest(self, manifest: CorpusManifest) -> None:
        with self.transaction() as conn:
            conn.execute("DELETE FROM manifest")
            conn.execute(
                """
                INSERT INTO manifest
                (id, schema_version, built_at, embedding_backend, embedding_model,
                 embedding_dim, total_chunks, total_files, index_path)
                VALUES (1,?,?,?,?,?,?,?,?)
                """,
                (
                    manifest.schema_version,
                    manifest.built_at.isoformat() if manifest.built_at else None,
                    manifest.embedding_backend,
                    manifest.embedding_model,
                    manifest.embedding_dim,
                    manifest.total_chunks,
                    manifest.total_files,
                    manifest.index_path,
                ),
            )
            conn.execute("DELETE FROM corpus_roots")
            for root in manifest.roots:
                conn.execute(
                    """
                    INSERT INTO corpus_roots
                    (abs_path, corpus_slice, file_count, chunk_count, indexed_at)
                    VALUES (?,?,?,?,?)
                    """,
                    (
                        root.abs_path, root.corpus_slice.value,
                        root.file_count, root.chunk_count,
                        root.indexed_at.isoformat() if root.indexed_at else None,
                    ),
                )

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def load_manifest(self) -> Optional[CorpusManifest]:
        assert self._conn is not None
        row = self._conn.execute("SELECT * FROM manifest WHERE id=1").fetchone()
        if row is None:
            return None

        roots_rows = self._conn.execute("SELECT * FROM corpus_roots").fetchall()
        roots = [
            CorpusRoot(
                abs_path=r["abs_path"],
                corpus_slice=CorpusSlice(r["corpus_slice"]),
                file_count=r["file_count"],
                chunk_count=r["chunk_count"],
                indexed_at=datetime.fromisoformat(r["indexed_at"]) if r["indexed_at"] else None,
            )
            for r in roots_rows
        ]
        return CorpusManifest(
            schema_version=row["schema_version"],
            built_at=datetime.fromisoformat(row["built_at"]) if row["built_at"] else None,
            embedding_backend=row["embedding_backend"],
            embedding_model=row["embedding_model"],
            embedding_dim=row["embedding_dim"],
            total_chunks=row["total_chunks"],
            total_files=row["total_files"],
            index_path=row["index_path"],
            roots=roots,
        )

    def fts_search(
        self,
        query: str,
        limit: int = 20,
        component: Optional[str] = None,
        corpus_slice: Optional[CorpusSlice] = None,
    ) -> list[ChunkRecord]:
        """Full-text search via FTS5. Returns ChunkRecord list (no embeddings)."""
        assert self._conn is not None

        # Sanitize query for FTS5 (avoid syntax errors on special chars)
        safe_query = re.sub(r'[^\w\s]', ' ', query)
        safe_query = safe_query.strip()
        if not safe_query:
            return []

        filters = []
        params: list = [safe_query]

        base_sql = """
            SELECT c.* FROM chunks c
            JOIN chunks_fts f ON c.rowid = f.rowid
            WHERE chunks_fts MATCH ?
        """

        if component:
            base_sql += " AND c.component = ?"
            params.append(component.upper())
        if corpus_slice:
            base_sql += " AND c.corpus_slice = ?"
            params.append(corpus_slice.value)

        base_sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        rows = self._conn.execute(base_sql, params).fetchall()
        return [_row_to_chunk(r) for r in rows]

    def get_chunk(self, chunk_id: str) -> Optional[ChunkRecord]:
        assert self._conn is not None
        row = self._conn.execute("SELECT * FROM chunks WHERE chunk_id=?", (chunk_id,)).fetchone()
        return _row_to_chunk(row) if row else None

    def count_chunks(self) -> int:
        assert self._conn is not None
        return self._conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]


# ---------------------------------------------------------------------------
# Row → dataclass conversion
# ---------------------------------------------------------------------------

# re already imported at top of module


def _row_to_chunk(row: sqlite3.Row) -> ChunkRecord:
    return ChunkRecord(
        chunk_id=row["chunk_id"],
        corpus_root=row["corpus_root"],
        rel_path=row["rel_path"],
        kind=ChunkKind(row["kind"]),
        authority=AuthorityTier(row["authority"]),
        corpus_slice=CorpusSlice(row["corpus_slice"]),
        start_line=row["start_line"],
        end_line=row["end_line"],
        text=row["text"],
        component=row["component"],
        symbol=row["symbol"],
        parent_symbol=row["parent_symbol"],
        keywords=json.loads(row["keywords"]) if row["keywords"] else [],
    )
