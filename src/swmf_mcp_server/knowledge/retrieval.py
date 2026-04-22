from __future__ import annotations

from typing import Any, Sequence

from ..catalog.source_index_catalog import SourceIndexCatalog
from .embeddings import TextEmbedder, cosine_similarity

_SEMANTIC_CHUNK_EMBEDDINGS_BY_ROOT: dict[str, dict[int, list[float]]] = {}


def reset_semantic_chunk_cache() -> None:
    _SEMANTIC_CHUNK_EMBEDDINGS_BY_ROOT.clear()


def search_semantic_chunks(
    catalog: SourceIndexCatalog,
    query: str,
    component: str | None = None,
    corpus_slice: str | None = None,
    max_results: int = 20,
    similarity_threshold: float | None = None,
    *,
    embedder: TextEmbedder,
) -> list[dict[str, Any]]:
    if not embedder.is_available:
        return []

    query_vector = embedder.embed_query(query)
    if not query_vector:
        return []

    candidates = catalog.list_chunks(component=component, corpus_slice=corpus_slice)
    if not candidates:
        return []

    cache = _SEMANTIC_CHUNK_EMBEDDINGS_BY_ROOT.setdefault(str(catalog.swmf_root), {})
    _populate_semantic_chunk_embeddings(candidates, embedder, cache)

    scored: list[dict[str, Any]] = []
    for candidate in candidates:
        chunk_id = int(candidate["id"])
        vector = cache.get(chunk_id, [])
        score = cosine_similarity(query_vector, vector)
        if similarity_threshold is not None and score < similarity_threshold:
            continue
        scored.append(_chunk_candidate_to_semantic_result(candidate, score))

    scored.sort(key=lambda item: float(item.get("search_score", 0.0)), reverse=True)
    return scored[:max_results]


def merge_search_results(
    primary: list[dict[str, Any]],
    secondary: list[dict[str, Any]],
    *,
    max_results: int,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()

    for record in [*primary, *secondary]:
        key = (
            record.get("file_path"),
            record.get("start_line"),
            record.get("name"),
            record.get("kind"),
        )
        if key in seen:
            continue
        seen.add(key)
        merged.append(record)
        if len(merged) >= max_results:
            break
    return merged


def _chunk_candidate_to_semantic_result(candidate: dict[str, Any], score: float) -> dict[str, Any]:
    return {
        "result_kind": "chunk",
        "name": candidate["label"],
        "kind": candidate["chunk_kind"],
        "start_line": candidate["start_line"],
        "end_line": candidate["end_line"],
        "component": candidate["component"],
        "docstring": candidate["chunk_text"],
        "source_kind": candidate["source_kind"],
        "authority": candidate["authority"],
        "uses": candidate["uses"],
        "file_path": candidate["file_path"],
        "corpus_root": candidate["corpus_root"],
        "corpus_slice": candidate["corpus_slice"],
        "symbol_name": candidate["symbol_name"],
        "chunk_kind": candidate["chunk_kind"],
        "chunk_text": candidate["chunk_text"],
        "param_refs": candidate["param_refs"],
        "search_score": score,
    }


def _populate_semantic_chunk_embeddings(
    candidates: Sequence[dict[str, Any]],
    embedder: TextEmbedder,
    cache: dict[int, list[float]],
) -> None:
    missing: list[tuple[int, str]] = []
    for candidate in candidates:
        chunk_id = int(candidate["id"])
        if chunk_id in cache:
            continue
        missing.append((chunk_id, str(candidate.get("chunk_text", ""))))

    if not missing:
        return

    vectors = embedder.embed_documents([text for _, text in missing])
    for (chunk_id, _), vector in zip(missing, vectors):
        cache[chunk_id] = vector