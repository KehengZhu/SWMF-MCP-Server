from __future__ import annotations

from typing import Any, Sequence

_MAX_EXCERPT_CHARS = 280


def build_agent_context_pack(
    *,
    query: str,
    query_analysis: dict[str, Any],
    index_status: dict[str, Any],
    search_results: Sequence[dict[str, Any]],
    reference_context: dict[str, Any],
    search_method: str,
    query_attempts: Sequence[dict[str, str | None]],
) -> dict[str, Any]:
    entities = query_analysis.get("entities", {})
    evidence = [_search_result_to_grounding_item(record) for record in search_results]

    return {
        "ok": True,
        "query": query,
        "query_analysis": query_analysis,
        "index_status": index_status,
        "search_strategy": {
            "search_method": search_method,
            "query_attempts": list(query_attempts),
        },
        "grounded_context": {
            "briefing": {
                "task_intent": query_analysis.get("intent"),
                "focus_components": list(entities.get("components", [])),
                "focus_commands": list(entities.get("param_commands", [])),
                "focus_symbols": list(entities.get("symbol_hints", [])),
                "focus_scripts": list(entities.get("script_hints", [])),
                "focus_idl_procedures": list(entities.get("idl_procedure_hints", [])),
                "recommended_corpus_slices": list(query_analysis.get("recommended_corpus_slices", [])),
                "focus_points": _build_focus_points(query_analysis, evidence, reference_context),
            },
            "grounding_rules": [
                "Treat PARAM.XML and TestParam.pl outputs as authoritative when they are present.",
                "Use knowledge search results as heuristic grounding, not final truth.",
                "Prefer the cited files and line ranges before making broader architectural claims.",
            ],
            "evidence": evidence,
            "reference_context": reference_context,
            "reference_highlights": _summarize_reference_context(reference_context),
        },
    }


def _build_focus_points(
    query_analysis: dict[str, Any],
    evidence: Sequence[dict[str, Any]],
    reference_context: dict[str, Any],
) -> list[str]:
    entities = query_analysis.get("entities", {})
    focus_points: list[str] = []

    if entities.get("param_commands"):
        focus_points.append(
            f"Anchor the answer on PARAM command context for {', '.join(entities['param_commands'])}."
        )
    if entities.get("components"):
        focus_points.append(
            f"Keep component-specific grounding centered on {', '.join(entities['components'])}."
        )
    if entities.get("symbol_hints"):
        focus_points.append(
            f"Prioritize exact source matches for {', '.join(entities['symbol_hints'][:3])}."
        )
    if reference_context.get("idl_procedures"):
        first = reference_context["idl_procedures"][0]
        focus_points.append(f"Use authoritative IDL signature details from {first.get('name')}.")
    if evidence:
        first = evidence[0]
        focus_points.append(
            f"Start from {first.get('file_path')} at lines {first.get('line_span')} for concrete grounding."
        )
    return focus_points


def _summarize_reference_context(reference_context: dict[str, Any]) -> list[str]:
    notes: list[str] = []

    for item in reference_context.get("param_commands", []):
        command = item.get("command", "PARAM command")
        definition = item.get("definition", {})
        if definition.get("ok"):
            notes.append(f"Authoritative definition found for {command}.")

    for item in reference_context.get("components", []):
        if item.get("ok") and item.get("component"):
            versions = ", ".join(item.get("versions", []))
            notes.append(f"Component {item['component']} exposes versions: {versions}.")

    for item in reference_context.get("idl_procedures", []):
        if item.get("ok") and item.get("name"):
            notes.append(f"IDL procedure {item['name']} resolved with authoritative signature data.")

    return notes


def _search_result_to_grounding_item(record: dict[str, Any]) -> dict[str, Any]:
    start_line = record.get("start_line")
    end_line = record.get("end_line")
    if start_line and end_line and start_line != end_line:
        line_span = f"{start_line}-{end_line}"
    elif start_line:
        line_span = str(start_line)
    else:
        line_span = "unknown"

    excerpt_source = (
        record.get("chunk_text")
        or record.get("docstring")
        or record.get("label")
        or record.get("name")
        or ""
    )
    excerpt = " ".join(str(excerpt_source).split())[:_MAX_EXCERPT_CHARS]

    return {
        "result_kind": record.get("result_kind", "symbol"),
        "name": record.get("name"),
        "kind": record.get("kind"),
        "component": record.get("component"),
        "file_path": record.get("file_path"),
        "line_span": line_span,
        "corpus_slice": record.get("corpus_slice"),
        "authority": record.get("authority"),
        "search_score": record.get("search_score"),
        "excerpt": excerpt,
    }


__all__ = ["build_agent_context_pack"]
