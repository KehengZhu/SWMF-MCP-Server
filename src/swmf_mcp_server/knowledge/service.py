"""Primary knowledge-domain service surface.

This module owns source-index orchestration and semantic retrieval for the
knowledge domain. Callers should import this module directly rather than the
legacy core shim.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from ..catalog.source_index_catalog import (
    SEARCH_MODE_HYBRID,
    SEARCH_MODE_KEYWORD,
    SEARCH_MODE_SEMANTIC,
    SLICE_SWMF_SOURCE,
    SLICE_ANALYST_CONTEXT,
    SLICE_SWMFSOLAR_SOURCE,
    SourceIndexCatalog,
)
from ..core.models import KnowledgeIndexStatus
from ..reference.service import (
    swmf_explain_idl_procedure,
    swmf_find_param_command,
    swmf_get_component_versions,
    swmf_trace_param_command,
)
from .agent_context import build_agent_context_pack
from .embeddings import get_text_embedder, get_text_embedder_runtime_payload
from .query_understanding import analyze_query
from .retrieval import merge_search_results, search_semantic_chunks

_INDEX_BY_ROOT: dict[str, SourceIndexCatalog] = {}
_EXTRA_ROOTS_KEY_BY_ROOT: dict[str, tuple[tuple[str, str], ...]] = {}


def _looks_like_swmfsolar_root(path: Path) -> bool:
    return (path / "Makefile").is_file() and (path / "Scripts").is_dir()


def _looks_like_mcp_repo_root(path: Path) -> bool:
    return (path / "pyproject.toml").is_file() and (path / "src" / "swmf_mcp_server").is_dir()


def _dedupe_extra_roots(roots: list[tuple[str, str]]) -> list[tuple[str, str]]:
    deduped: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for raw_path, slice_name in roots:
        key = (str(Path(raw_path).resolve()), slice_name)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(key)
    return deduped


def _discover_default_swmfsolar_root(swmf_root: str) -> str | None:
    primary_root = Path(swmf_root).resolve()
    candidate = primary_root.parent / "SWMFSOLAR"
    if _looks_like_swmfsolar_root(candidate):
        return str(candidate.resolve())
    return None


def _discover_default_mcp_repo_root(swmf_root: str) -> str | None:
    primary_root = Path(swmf_root).resolve()
    repo_root = Path(__file__).resolve().parents[3]
    if primary_root.parent != repo_root.parent:
        return None
    if _looks_like_mcp_repo_root(repo_root):
        return str(repo_root.resolve())
    return None


def _extra_roots_cache_key(
    extra_roots: list[tuple[str, str]] | None,
) -> tuple[tuple[str, str], ...]:
    if not extra_roots:
        return ()
    return tuple((str(Path(path).resolve()), slice_name) for path, slice_name in extra_roots)


def _get_catalog(
    swmf_root: str,
    extra_roots: list[tuple[str, str]] | None = None,
) -> SourceIndexCatalog:
    key = str(Path(swmf_root).resolve())
    extra_key = _extra_roots_cache_key(extra_roots)
    if extra_roots is not None:
        cached = _INDEX_BY_ROOT.get(key)
        if cached is not None and _EXTRA_ROOTS_KEY_BY_ROOT.get(key) == extra_key:
            return cached
        inst = SourceIndexCatalog(key, extra_roots=extra_roots)
        _INDEX_BY_ROOT[key] = inst
        _EXTRA_ROOTS_KEY_BY_ROOT[key] = extra_key
        return inst
    if key not in _INDEX_BY_ROOT:
        _INDEX_BY_ROOT[key] = SourceIndexCatalog(key)
        _EXTRA_ROOTS_KEY_BY_ROOT[key] = ()
    return _INDEX_BY_ROOT[key]


def _build_extra_roots(
    swmf_root: str,
    swmfsolar_root: str | None,
    mcp_repo_root: str | None,
) -> list[tuple[str, str]] | None:
    roots: list[tuple[str, str]] = []
    if swmfsolar_root:
        roots.append((swmfsolar_root, SLICE_SWMFSOLAR_SOURCE))
    else:
        auto_swmfsolar_root = _discover_default_swmfsolar_root(swmf_root)
        if auto_swmfsolar_root:
            roots.append((auto_swmfsolar_root, SLICE_SWMFSOLAR_SOURCE))
    if mcp_repo_root:
        roots.append((mcp_repo_root, SLICE_ANALYST_CONTEXT))
    else:
        auto_mcp_repo_root = _discover_default_mcp_repo_root(swmf_root)
        if auto_mcp_repo_root:
            roots.append((auto_mcp_repo_root, SLICE_ANALYST_CONTEXT))
    deduped = _dedupe_extra_roots(roots)
    return deduped if deduped else None


def _search_source_with_catalog(
    catalog: SourceIndexCatalog,
    query: str,
    component: str | None = None,
    kind: str | None = None,
    corpus_slice: str | None = None,
    max_results: int = 20,
    *,
    search_mode: str = SEARCH_MODE_KEYWORD,
    similarity_threshold: float | None = None,
) -> dict[str, Any]:
    normalized = (search_mode or SEARCH_MODE_KEYWORD).strip().lower()
    if normalized not in {SEARCH_MODE_KEYWORD, SEARCH_MODE_SEMANTIC, SEARCH_MODE_HYBRID}:
        normalized = SEARCH_MODE_KEYWORD

    effective_mode = SEARCH_MODE_KEYWORD
    semantic_available = False
    degraded_reason: str | None = None
    embedder = get_text_embedder()
    semantic_runtime = get_text_embedder_runtime_payload(embedder)

    if normalized != SEARCH_MODE_KEYWORD and kind is not None:
        degraded_reason = "Semantic retrieval does not support kind filtering yet; fell back to keyword search."
    else:
        semantic_available = embedder.is_available
        if normalized != SEARCH_MODE_KEYWORD and semantic_available:
            effective_mode = normalized
        elif normalized != SEARCH_MODE_KEYWORD:
            degraded_reason = embedder.availability_message or (
                "Semantic retrieval backend unavailable; fell back to keyword search."
            )

    keyword_results = catalog.search_symbols(
        query=query,
        component=component,
        kind=kind,
        corpus_slice=corpus_slice,
        max_results=max_results,
    )

    if effective_mode == SEARCH_MODE_KEYWORD:
        results = keyword_results
    else:
        semantic_results = search_semantic_chunks(
            catalog,
            query=query,
            component=component,
            corpus_slice=corpus_slice,
            max_results=max_results,
            similarity_threshold=similarity_threshold,
            embedder=embedder,
        )
        if effective_mode == SEARCH_MODE_SEMANTIC:
            results = semantic_results
        else:
            results = merge_search_results(semantic_results, keyword_results, max_results=max_results)

    return {
        "results": results,
        "search_mode_requested": normalized,
        "search_method": effective_mode,
        "semantic_available": semantic_available,
        "semantic_degraded_reason": degraded_reason,
        "semantic_runtime": semantic_runtime,
        "similarity_threshold": similarity_threshold,
    }


def get_index_status(swmf_root: str) -> KnowledgeIndexStatus:
    return _get_catalog(swmf_root).get_status()


def build_index(
    swmf_root: str,
    force: bool = False,
    *,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> KnowledgeIndexStatus:
    extra = _build_extra_roots(swmf_root, swmfsolar_root, mcp_repo_root)
    return _get_catalog(swmf_root, extra_roots=extra).build(force=force)


def refresh_index(
    swmf_root: str,
    *,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> KnowledgeIndexStatus:
    extra = _build_extra_roots(swmf_root, swmfsolar_root, mcp_repo_root)
    return _get_catalog(swmf_root, extra_roots=extra).refresh()


def ensure_index_ready(
    swmf_root: str,
    *,
    swmfsolar_root: str | None = None,
    mcp_repo_root: str | None = None,
) -> KnowledgeIndexStatus:
    extra = _build_extra_roots(swmf_root, swmfsolar_root, mcp_repo_root)
    catalog = _get_catalog(swmf_root, extra_roots=extra)
    status = catalog.get_status()
    if not status.ok or status.is_stale:
        return catalog.refresh()
    return status


def search_symbols(
    swmf_root: str,
    query: str,
    component: str | None = None,
    kind: str | None = None,
    corpus_slice: str | None = None,
    max_results: int = 20,
    *,
    ensure_ready: bool = True,
) -> list[dict[str, Any]]:
    if ensure_ready:
        ensure_index_ready(swmf_root)
    return _get_catalog(swmf_root).search_symbols(
        query=query,
        component=component,
        kind=kind,
        corpus_slice=corpus_slice,
        max_results=max_results,
    )


def search_source(
    swmf_root: str,
    query: str,
    component: str | None = None,
    kind: str | None = None,
    corpus_slice: str | None = None,
    max_results: int = 20,
    *,
    search_mode: str = SEARCH_MODE_KEYWORD,
    similarity_threshold: float | None = None,
    ensure_ready: bool = True,
) -> dict[str, Any]:
    if ensure_ready:
        ensure_index_ready(swmf_root)
    return _search_source_with_catalog(
        _get_catalog(swmf_root),
        query=query,
        component=component,
        kind=kind,
        corpus_slice=corpus_slice,
        max_results=max_results,
        search_mode=search_mode,
        similarity_threshold=similarity_threshold,
    )


def search_chunks(
    swmf_root: str,
    query: str,
    component: str | None = None,
    chunk_kind: str | None = None,
    corpus_slice: str | None = None,
    max_results: int = 20,
    *,
    ensure_ready: bool = True,
) -> list[dict[str, Any]]:
    if ensure_ready:
        ensure_index_ready(swmf_root)
    return _get_catalog(swmf_root).search_chunks(
        query=query,
        component=component,
        chunk_kind=chunk_kind,
        corpus_slice=corpus_slice,
        max_results=max_results,
    )


def lookup_symbol(
    swmf_root: str,
    name: str,
    kind: str | None = None,
    *,
    ensure_ready: bool = True,
) -> list[dict[str, Any]]:
    if ensure_ready:
        ensure_index_ready(swmf_root)
    return _get_catalog(swmf_root).lookup_symbol(name=name, kind=kind)


def get_param_evidence(
    swmf_root: str,
    command_normalized: str,
    max_results: int = 10,
    *,
    ensure_ready: bool = True,
) -> list[dict[str, Any]]:
    if ensure_ready:
        ensure_index_ready(swmf_root)
    return _get_catalog(swmf_root).get_param_evidence(
        command_normalized=command_normalized.upper(),
        max_results=max_results,
    )


def get_file_symbols(
    swmf_root: str,
    file_path: str,
    *,
    ensure_ready: bool = True,
) -> list[dict[str, Any]]:
    if ensure_ready:
        ensure_index_ready(swmf_root)
    return _get_catalog(swmf_root).get_file_symbols(file_path=file_path)


def status_as_payload(status: KnowledgeIndexStatus) -> dict[str, Any]:
    semantic_runtime = get_text_embedder_runtime_payload()
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
        "corpus_roots": status.corpus_roots,
        "semantic_runtime": semantic_runtime,
    }


def understand_source_query(query: str) -> dict[str, Any]:
    return analyze_query(query).as_payload()


def get_agent_context_pack(
    swmf_root: str,
    query: str,
    max_results: int = 8,
    *,
    search_mode: str | None = None,
    similarity_threshold: float | None = None,
    ensure_ready: bool = True,
) -> dict[str, Any]:
    status = ensure_index_ready(swmf_root) if ensure_ready else get_index_status(swmf_root)
    if not status.ok or status.is_stale:
        return {
            "ok": False,
            "error_code": "KNOWLEDGE_INDEX_PREP_FAILED",
            "message": "Knowledge index could not be prepared automatically.",
            "index_status": status_as_payload(status),
        }

    catalog = _get_catalog(swmf_root)
    analysis = analyze_query(query)
    analysis_payload = analysis.as_payload()
    requested_mode = (search_mode or analysis.preferred_search_mode or SEARCH_MODE_KEYWORD).strip().lower()
    component_filter = analysis.components[0] if len(analysis.components) == 1 else None

    search_payload, query_attempts = _collect_grounding_search_results(
        catalog,
        query=query,
        analysis=analysis,
        component=component_filter,
        max_results=max_results,
        search_mode=requested_mode,
        similarity_threshold=similarity_threshold,
    )
    reference_context = _collect_reference_context(swmf_root, analysis_payload)

    return build_agent_context_pack(
        query=query,
        query_analysis=analysis_payload,
        index_status=status_as_payload(status),
        search_results=search_payload["results"],
        reference_context=reference_context,
        search_mode_requested=search_payload["search_mode_requested"],
        search_method=search_payload["search_method"],
        semantic_available=search_payload["semantic_available"],
        semantic_degraded_reason=search_payload["semantic_degraded_reason"],
        semantic_runtime=search_payload["semantic_runtime"],
        similarity_threshold=search_payload["similarity_threshold"],
        query_attempts=query_attempts,
    )


def _collect_grounding_search_results(
    catalog: SourceIndexCatalog,
    *,
    query: str,
    analysis: Any,
    component: str | None,
    max_results: int,
    search_mode: str,
    similarity_threshold: float | None,
) -> tuple[dict[str, Any], list[dict[str, str | None]]]:
    merged_results: list[dict[str, Any]] = []
    query_attempts: list[dict[str, str | None]] = []
    search_payload: dict[str, Any] | None = None

    slices = analysis.recommended_corpus_slices or [SLICE_SWMF_SOURCE]
    terms = analysis.focus_terms[:5] if analysis.focus_terms else [query]

    for corpus_slice in slices:
        for term in terms:
            component_filters = [component]
            if component is not None:
                component_filters.append(None)

            for component_filter in component_filters:
                current_payload = _search_source_with_catalog(
                    catalog,
                    query=term,
                    component=component_filter,
                    corpus_slice=corpus_slice,
                    max_results=max_results,
                    search_mode=search_mode,
                    similarity_threshold=similarity_threshold,
                )
                query_attempts.append(
                    {
                        "query": term,
                        "corpus_slice": corpus_slice,
                        "component": component_filter,
                    }
                )
                merged_results = _merge_grounding_results(
                    merged_results,
                    current_payload["results"],
                    max_results=max_results,
                )
                search_payload = _merge_search_payload(search_payload, current_payload, merged_results)
                if current_payload["results"] or component_filter is None:
                    break

            if len(merged_results) >= max_results:
                return search_payload, query_attempts

    if search_payload is None or not merged_results:
        fallback_payload = _search_source_with_catalog(
            catalog,
            query=query,
            component=component,
            corpus_slice=None,
            max_results=max_results,
            search_mode=search_mode,
            similarity_threshold=similarity_threshold,
        )
        query_attempts.append({"query": query, "corpus_slice": None, "component": None})
        merged_results = _merge_grounding_results(merged_results, fallback_payload["results"], max_results=max_results)
        search_payload = _merge_search_payload(search_payload, fallback_payload, merged_results)

    assert search_payload is not None
    return search_payload, query_attempts


def _merge_grounding_results(
    existing: list[dict[str, Any]],
    new_records: list[dict[str, Any]],
    *,
    max_results: int,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for record in [*existing, *new_records]:
        key = (
            record.get("file_path"),
            record.get("start_line"),
            record.get("end_line"),
            record.get("name"),
            record.get("kind"),
            record.get("label"),
        )
        if key in seen:
            continue
        seen.add(key)
        merged.append(record)
        if len(merged) >= max_results:
            break
    return merged


def _merge_search_payload(
    existing: dict[str, Any] | None,
    current: dict[str, Any],
    merged_results: list[dict[str, Any]],
) -> dict[str, Any]:
    if existing is None:
        merged = dict(current)
        merged["results"] = list(merged_results)
        return merged

    merged = dict(existing)
    merged["results"] = list(merged_results)
    merged["semantic_available"] = existing["semantic_available"] or current["semantic_available"]
    merged["semantic_degraded_reason"] = existing["semantic_degraded_reason"] or current["semantic_degraded_reason"]
    if not merged["semantic_available"] and current["semantic_available"]:
        merged["semantic_runtime"] = current["semantic_runtime"]
    if existing["search_method"] == SEARCH_MODE_KEYWORD and current["search_method"] != SEARCH_MODE_KEYWORD:
        merged["search_method"] = current["search_method"]
    return merged


def _collect_reference_context(swmf_root: str, analysis_payload: dict[str, Any]) -> dict[str, Any]:
    entities = analysis_payload.get("entities", {})

    param_context = []
    for command in entities.get("param_commands", [])[:3]:
        param_context.append(
            {
                "command": command,
                "definition": swmf_find_param_command(name=command, swmf_root=swmf_root),
                "trace": swmf_trace_param_command(name=command, swmf_root=swmf_root),
            }
        )

    component_context = [
        swmf_get_component_versions(component=component, swmf_root=swmf_root)
        for component in entities.get("components", [])[:3]
    ]

    idl_context = []
    for name in entities.get("idl_procedure_hints", [])[:3]:
        payload = swmf_explain_idl_procedure(name=name, swmf_root=swmf_root)
        if payload.get("ok"):
            idl_context.append(payload)
            break

    return {
        "param_commands": param_context,
        "components": component_context,
        "idl_procedures": idl_context,
    }


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
