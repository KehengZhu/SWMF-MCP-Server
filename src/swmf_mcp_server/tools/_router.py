"""Private internal router for the Phase 2 MCP public API tools.

This module is NOT part of the public API surface.  It owns:
  - evidence type classification
  - raw-search-result → EvidenceItem conversion
  - shared index-readiness helpers
  - shared search dispatch

Callers should never be exposed to the choice of backend made here.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..knowledge import service as ks

# ---------------------------------------------------------------------------
# Evidence type classifier
# ---------------------------------------------------------------------------

_PARAM_XML_RE = re.compile(r"PARAM\.XML$", re.IGNORECASE)
_IDL_RE = re.compile(r"\.pro$", re.IGNORECASE)
_SCRIPT_RE = re.compile(r"\.(pl|pm)$", re.IGNORECASE)
_EXAMPLE_RE = re.compile(
    r"(?:Examples|example|Param|param).*PARAM\.in$",
    re.IGNORECASE,
)

_SOURCE_KIND_TO_EVIDENCE_TYPE: dict[str, str] = {
    "fortran_source": "code",
    "perl_source": "code",
    "idl_source": "idl",
    "manual_doc": "doc",
}


def _classify_evidence_type(record: dict[str, Any]) -> str:
    path_str = record.get("file_path", "")
    source_kind = record.get("source_kind", "")

    if _PARAM_XML_RE.search(path_str):
        return "param_spec"
    if _EXAMPLE_RE.search(path_str):
        return "example"
    if _IDL_RE.search(path_str):
        return "idl"
    if _SCRIPT_RE.search(path_str):
        return "code"
    mapped = _SOURCE_KIND_TO_EVIDENCE_TYPE.get(source_kind)
    if mapped:
        return mapped
    kind = record.get("kind", "")
    if kind == "doc_section":
        return "doc"
    return "code"


# ---------------------------------------------------------------------------
# Raw result → EvidenceItem
# ---------------------------------------------------------------------------

_SNIPPET_MAX = 300


def _truncate(text: str, max_chars: int = _SNIPPET_MAX) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "…"


def raw_result_to_evidence_item(record: dict[str, Any]) -> dict[str, Any]:
    """Convert a raw search/symbol record to the canonical EvidenceItem shape."""
    path_str = record.get("file_path", "")
    name = record.get("name", "")
    # Prefer chunk_text, then docstring, then excerpt
    snippet_raw = (
        record.get("chunk_text")
        or record.get("docstring")
        or record.get("excerpt")
        or ""
    )
    snippet_text = snippet_raw.strip()
    if name and snippet_text and not any(char.isalnum() for char in snippet_text):
        snippet_raw = f"{name}\n{snippet_raw}"
    score_raw = record.get("score")
    score: float | None = float(score_raw) if score_raw is not None else None

    return {
        "type": _classify_evidence_type(record),
        "path": path_str,
        "snippet": _truncate(snippet_raw),
        "score": score,
        "name": record.get("name", ""),
        "kind": record.get("kind", ""),
        "component": record.get("component") or "",
        "start_line": record.get("start_line"),
    }


# ---------------------------------------------------------------------------
# Index readiness helper (non-fatal)
# ---------------------------------------------------------------------------

def _check_index(swmf_root: str) -> tuple[bool, str | None]:
    """Return (ready, degraded_reason_or_None)."""
    try:
        status = ks.get_index_status(swmf_root)
        if status.ok and not status.is_stale:
            return True, None
        # Try to build automatically (fast path)
        status = ks.ensure_index_ready(swmf_root)
        if status.ok and not status.is_stale:
            return True, None
        return False, "Knowledge index not ready; results may be empty."
    except Exception as exc:
        return False, f"Index check failed: {exc}"


# ---------------------------------------------------------------------------
# Search dispatch — the core routing logic
# ---------------------------------------------------------------------------

def run_evidence_search(
    swmf_root: str,
    query: str,
    mode: str,
    scope: list[str],
    top_k: int,
    goal: str,
) -> tuple[list[dict[str, Any]], str, str, str | None]:
    """Run keyword search and return (evidence_items, mode_used, summary, degraded_reason).

    Semantic / hybrid retrieval has been removed; the `mode` argument is kept
    for backward compatibility with skill prompts but every search now uses
    the catalog's keyword (BM25) backend. Scope is honoured by passing
    component= to the backend when exactly one component is given, or by
    post-filtering when multiple are given.
    """
    query_analysis = ks.understand_source_query(query)
    index_ready, degraded_reason = _check_index(swmf_root)

    component_filter: str | None = scope[0] if len(scope) == 1 else None

    raw_payload = ks.search_source(
        swmf_root,
        query=query,
        component=component_filter,
        max_results=top_k,
        ensure_ready=False,
    )

    results: list[dict[str, Any]] = raw_payload.get("results", [])
    mode_used: str = raw_payload.get("search_method", "keyword")

    # If no results, try focus terms from query analysis
    if not results:
        for term in query_analysis.get("focus_terms", []):
            if term == query:
                continue
            fallback = ks.search_source(
                swmf_root,
                query=term,
                component=component_filter,
                max_results=top_k,
                ensure_ready=False,
            )
            if fallback.get("results"):
                results = fallback["results"]
                mode_used = "keyword_fallback"
                break

    # Post-filter to scope if multiple components specified
    if len(scope) > 1:
        scope_set = {s.upper() for s in scope}
        results = [r for r in results if (r.get("component") or "").upper() in scope_set or not r.get("component")]

    evidence = [raw_result_to_evidence_item(r) for r in results[:top_k]]

    if not index_ready and degraded_reason and not evidence:
        summary = f"No evidence found (index not ready: {degraded_reason})"
    elif evidence:
        summary = f"{len(evidence)} evidence item(s) found for '{query}'"
    else:
        summary = f"No evidence found for '{query}'"

    return evidence, mode_used, summary, degraded_reason


# ---------------------------------------------------------------------------
# Entities extraction from query analysis
# ---------------------------------------------------------------------------

def extract_entities_from_analysis(query_analysis: dict[str, Any]) -> dict[str, list[str]]:
    """Return the entities dict in the v2 contract shape."""
    entities = query_analysis.get("entities", {})
    return {
        "components": list(entities.get("components", [])),
        "files": [],
        "params": [
            cmd.lstrip("#") for cmd in entities.get("param_commands", [])
        ],
        "symbols": list(entities.get("symbol_hints", [])),
    }


# ---------------------------------------------------------------------------
# Enrich entities from evidence
# ---------------------------------------------------------------------------

def enrich_entities_from_evidence(
    entities: dict[str, list[str]],
    evidence: list[dict[str, Any]],
) -> dict[str, list[str]]:
    """Add file paths and additional components seen in evidence."""
    files_seen: set[str] = set()
    components_seen: set[str] = {c.upper() for c in entities["components"]}

    for item in evidence:
        path_str = item.get("path", "")
        if path_str and path_str not in files_seen:
            files_seen.add(path_str)
            entities["files"].append(path_str)
        comp = (item.get("component") or "").upper()
        if comp and len(comp) == 2 and comp not in components_seen:
            components_seen.add(comp)
            entities["components"].append(comp)

    return entities
