from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from ..catalog.source_index_catalog import (
    SEARCH_MODE_KEYWORD,
    SLICE_ANALYST_CONTEXT,
    SLICE_SWMF_MANUALS,
    SLICE_SWMF_PARAM_XML,
    SLICE_SWMF_SCRIPTS,
    SLICE_SWMF_SOURCE,
    SLICE_SWMFSOLAR_SOURCE,
)

_PARAM_COMMAND_RE = re.compile(r"#([A-Za-z][A-Za-z0-9_]+)")
_COMPONENT_TOKEN_RE = re.compile(r"\b([A-Za-z]{2})\b")
_SCRIPT_NAME_RE = re.compile(r"\b([A-Za-z0-9_]+\.pl)\b", re.IGNORECASE)
_PROCEDURE_FILE_RE = re.compile(r"\b([A-Za-z0-9_]+)\.pro\b", re.IGNORECASE)
_SYMBOL_HINT_RE = re.compile(
    r"\b(?:Mod[A-Za-z0-9_]+|[A-Z][A-Za-z0-9_]{2,}|[a-z]+_[a-z0-9_]+|[A-Za-z0-9_]+::[A-Za-z0-9_]+)\b"
)

_KNOWN_COMPONENTS = frozenset({
    "EE",
    "GM",
    "IE",
    "IH",
    "IM",
    "OH",
    "PC",
    "PW",
    "RB",
    "SC",
    "SP",
    "UA",
})
_KNOWN_SCRIPT_NAMES = {
    "config.pl": "Config.pl",
    "postproc.pl": "PostProc.pl",
    "restart.pl": "Restart.pl",
    "resubmit.pl": "Resubmit.pl",
    "testparam.pl": "TestParam.pl",
}
_SYMBOL_STOPWORDS = frozenset({
    "agent",
    "command",
    "component",
    "coupling",
    "definition",
    "docs",
    "documentation",
    "evidence",
    "explain",
    "find",
    "guide",
    "how",
    "idl",
    "lookup",
    "manual",
    "mcp",
    "param",
    "parameter",
    "procedure",
    "script",
    "show",
    "source",
    "swmf",
    "swmfsolar",
    "tool",
    "trace",
    "what",
    "where",
    "why",
    "workflow",
})
_DOC_TERMS = ("doc", "docs", "documentation", "manual", "guide", "meaning")
_SCRIPT_TERMS = ("script", ".pl", "testparam", "config.pl", "restart.pl", "postproc.pl")
_SOLAR_TERMS = ("magnetogram", "swmfsolar", "cme", "pfss", "synoptic", "corona")
_ANALYST_TERMS = ("agent", "skill", "mcp", "prototype", "context pack")
_LOOKUP_TERMS = ("find", "lookup", "where", "definition", "defined", "symbol")
_EXPLAIN_TERMS = ("how", "why", "explain", "overview", "workflow", "what does", "meaning")


@dataclass(frozen=True)
class QueryUnderstanding:
    query: str
    normalized_query: str
    intent: str
    intent_reason: str
    preferred_search_mode: str
    recommended_corpus_slices: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    param_commands: list[str] = field(default_factory=list)
    symbol_hints: list[str] = field(default_factory=list)
    script_hints: list[str] = field(default_factory=list)
    idl_procedure_hints: list[str] = field(default_factory=list)
    focus_terms: list[str] = field(default_factory=list)

    def as_payload(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "normalized_query": self.normalized_query,
            "intent": self.intent,
            "intent_reason": self.intent_reason,
            "preferred_search_mode": self.preferred_search_mode,
            "recommended_corpus_slices": list(self.recommended_corpus_slices),
            "entities": {
                "components": list(self.components),
                "param_commands": [f"#{value}" for value in self.param_commands],
                "symbol_hints": list(self.symbol_hints),
                "script_hints": list(self.script_hints),
                "idl_procedure_hints": list(self.idl_procedure_hints),
            },
            "focus_terms": list(self.focus_terms),
        }


def analyze_query(query: str) -> QueryUnderstanding:
    normalized = " ".join(query.strip().split())
    lowered = normalized.lower()

    components = _extract_components(normalized)
    param_commands = _extract_param_commands(normalized, lowered)
    script_hints = _extract_script_hints(normalized, lowered)
    symbol_hints = _extract_symbol_hints(normalized, param_commands=param_commands, script_hints=script_hints)
    idl_procedure_hints = _extract_idl_procedure_hints(normalized, lowered, symbol_hints=symbol_hints)

    intent, reason = _classify_intent(
        lowered=lowered,
        components=components,
        param_commands=param_commands,
        script_hints=script_hints,
        symbol_hints=symbol_hints,
        idl_procedure_hints=idl_procedure_hints,
    )
    preferred_search_mode = _preferred_search_mode(intent)
    recommended_corpus_slices = _recommend_corpus_slices(
        lowered=lowered,
        intent=intent,
        components=components,
        param_commands=param_commands,
        script_hints=script_hints,
        idl_procedure_hints=idl_procedure_hints,
    )
    focus_terms = _build_focus_terms(
        query=normalized,
        components=components,
        param_commands=param_commands,
        symbol_hints=symbol_hints,
        script_hints=script_hints,
        idl_procedure_hints=idl_procedure_hints,
    )

    return QueryUnderstanding(
        query=query,
        normalized_query=normalized,
        intent=intent,
        intent_reason=reason,
        preferred_search_mode=preferred_search_mode,
        recommended_corpus_slices=recommended_corpus_slices,
        components=components,
        param_commands=param_commands,
        symbol_hints=symbol_hints,
        script_hints=script_hints,
        idl_procedure_hints=idl_procedure_hints,
        focus_terms=focus_terms,
    )


def understand_source_query(query: str) -> dict[str, Any]:
    return analyze_query(query).as_payload()


def _extract_components(query: str) -> list[str]:
    matches = []
    for token in _COMPONENT_TOKEN_RE.findall(query):
        candidate = token.upper()
        if candidate in _KNOWN_COMPONENTS:
            matches.append(candidate)
    return _dedupe(matches)


def _extract_param_commands(query: str, lowered: str) -> list[str]:
    commands = [match.upper() for match in _PARAM_COMMAND_RE.findall(query)]
    if re.search(r"\bparam(?:eter)?\b|\bcommand\b", lowered):
        for pattern in (
            r"\b(?:param(?:eter)?|command)\b\s+[#:]?([A-Za-z][A-Za-z0-9_]+)",
            r"[\"']#?([A-Za-z][A-Za-z0-9_]+)[\"']",
        ):
            for match in re.findall(pattern, query, flags=re.IGNORECASE):
                upper = match.upper()
                if upper not in {"PARAM", "PARAMETER", "COMMAND"}:
                    commands.append(upper)
    return _dedupe(commands)


def _extract_script_hints(query: str, lowered: str) -> list[str]:
    hints = [_KNOWN_SCRIPT_NAMES.get(match.lower(), match) for match in _SCRIPT_NAME_RE.findall(query)]
    for lower_name, canonical in _KNOWN_SCRIPT_NAMES.items():
        if lower_name in lowered:
            hints.append(canonical)
    return _dedupe(hints)


def _extract_symbol_hints(
    query: str,
    *,
    param_commands: list[str],
    script_hints: list[str],
) -> list[str]:
    script_stems = {script.rsplit(".", 1)[0].lower() for script in script_hints}
    hints: list[str] = []
    for match in _SYMBOL_HINT_RE.findall(query):
        candidate = match.strip()
        lowered = candidate.lower()
        if lowered in _SYMBOL_STOPWORDS:
            continue
        if lowered in script_stems:
            continue
        if candidate.upper() in param_commands:
            continue
        if candidate.upper() in _KNOWN_COMPONENTS:
            continue
        hints.append(candidate)
    return _dedupe(hints)


def _extract_idl_procedure_hints(
    query: str,
    lowered: str,
    *,
    symbol_hints: list[str],
) -> list[str]:
    hints = [match for match in _PROCEDURE_FILE_RE.findall(query)]
    if "idl" in lowered or ".pro" in lowered or "procedure" in lowered:
        hints.extend(symbol_hints)
    return _dedupe(hints)


def _classify_intent(
    *,
    lowered: str,
    components: list[str],
    param_commands: list[str],
    script_hints: list[str],
    symbol_hints: list[str],
    idl_procedure_hints: list[str],
) -> tuple[str, str]:
    if param_commands or "param.xml" in lowered or "param.in" in lowered:
        return "param_lookup", "The query names a PARAM command or explicit PARAM file target."
    if idl_procedure_hints and ("idl" in lowered or ".pro" in lowered or "procedure" in lowered):
        return "idl_lookup", "The query points to an IDL procedure or macro."
    if script_hints or _contains_any(lowered, _SCRIPT_TERMS):
        return "script_lookup", "The query is centered on Perl helper scripts or script behavior."
    if "coupling" in lowered or "couple" in lowered:
        return "coupling_analysis", "The query asks about interactions between SWMF components."
    if _contains_any(lowered, _DOC_TERMS) and not symbol_hints:
        return "documentation_lookup", "The query asks for explanatory documentation rather than a direct symbol match."
    if symbol_hints and _contains_any(lowered, _LOOKUP_TERMS):
        return "symbol_lookup", "The query includes likely source symbols and lookup language."
    if _contains_any(lowered, _EXPLAIN_TERMS) or len(components) > 1:
        return "concept_explanation", "The query asks for higher-level explanation across code or components."
    return "general_search", "The query is broad, so use general source grounding."


def _preferred_search_mode(intent: str) -> str:
    # Semantic / hybrid retrieval has been removed; only keyword mode remains.
    return SEARCH_MODE_KEYWORD


def _recommend_corpus_slices(
    *,
    lowered: str,
    intent: str,
    components: list[str],
    param_commands: list[str],
    script_hints: list[str],
    idl_procedure_hints: list[str],
) -> list[str]:
    slices: list[str] = []

    if intent == "param_lookup" or param_commands:
        _append_once(slices, SLICE_SWMF_PARAM_XML)
        _append_once(slices, SLICE_SWMF_SCRIPTS)
        _append_once(slices, SLICE_SWMF_SOURCE)
    if intent == "script_lookup" or script_hints:
        _append_once(slices, SLICE_SWMF_SCRIPTS)
    if intent in {"symbol_lookup", "concept_explanation", "coupling_analysis", "idl_lookup", "general_search"}:
        _append_once(slices, SLICE_SWMF_SOURCE)
    if intent in {"documentation_lookup", "concept_explanation", "coupling_analysis"}:
        _append_once(slices, SLICE_SWMF_MANUALS)
    if _contains_any(lowered, _SOLAR_TERMS) or "SC" in components:
        _append_once(slices, SLICE_SWMFSOLAR_SOURCE)
    if idl_procedure_hints:
        _append_once(slices, SLICE_SWMF_SOURCE)
    if _contains_any(lowered, _ANALYST_TERMS):
        _append_once(slices, SLICE_ANALYST_CONTEXT)
    if not slices:
        _append_once(slices, SLICE_SWMF_SOURCE)
    return slices


def _build_focus_terms(
    *,
    query: str,
    components: list[str],
    param_commands: list[str],
    symbol_hints: list[str],
    script_hints: list[str],
    idl_procedure_hints: list[str],
) -> list[str]:
    values: list[str] = [query]
    values.extend(f"#{value}" for value in param_commands)
    values.extend(symbol_hints)
    values.extend(script_hints)
    values.extend(idl_procedure_hints)
    values.extend(components)
    return _dedupe(values)


def _append_once(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _contains_any(text: str, values: Iterable[str]) -> bool:
    return any(value in text for value in values)


def _dedupe(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


__all__ = [
    "QueryUnderstanding",
    "analyze_query",
    "understand_source_query",
]
