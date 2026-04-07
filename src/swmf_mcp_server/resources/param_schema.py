from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..catalog import get_source_catalog
from ..core.swmf_root import resolve_swmf_root


def _load_catalog() -> tuple[dict[str, Any] | None, Any | None]:
    root = resolve_swmf_root()
    if not root.ok:
        return {
            "ok": False,
            "error_code": "SWMF_ROOT_RESOLUTION_FAILED",
            "message": root.message,
            "resolution_notes": root.resolution_notes,
        }, None

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=False)
    if catalog_error is not None or catalog is None:
        return catalog_error or {"ok": False, "message": "Failed to load source catalog."}, None

    return None, catalog


def _keyword_tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9_]+", text.lower()) if token]


def _command_blob(item: Any) -> str:
    defaults_flat = " ".join(f"{key} {value}" for key, value in sorted((item.defaults or {}).items()))
    allowed = " ".join(item.allowed_values or [])
    ranges = " ".join(item.ranges or [])
    aliases = " ".join(item.aliases or [])
    fields = [
        item.name or "",
        item.normalized or "",
        item.component or "",
        item.description or "",
        defaults_flat,
        allowed,
        ranges,
        aliases,
        item.source_path or "",
    ]
    return " ".join(fields).lower()


def _command_keyword_score(item: Any, query_norm: str, tokens: list[str]) -> int:
    blob = _command_blob(item)
    score = 0

    if query_norm and query_norm in blob:
        score += 25
    normalized = (item.normalized or "").lower()
    name = (item.name or "").lower()
    description = (item.description or "").lower()
    if query_norm and query_norm == normalized:
        score += 30
    if query_norm and query_norm in normalized:
        score += 15
    if query_norm and query_norm in name:
        score += 15
    if query_norm and query_norm in description:
        score += 10

    for token in tokens:
        if token in normalized:
            score += 10
        elif token in name:
            score += 8
        elif token in description:
            score += 6
        elif token in blob:
            score += 2

    return score


def _strip_tex_commands(text: str) -> str:
    # Remove TeX comments while preserving escaped percent signs.
    text = re.sub(r"(?<!\\)%.*", "", text)

    # Keep section-like titles as plain text for better snippet quality.
    text = re.sub(r"\\(?:sub)*section\*?\{([^}]*)\}", r"\n\1\n", text)
    text = re.sub(r"\\chapter\*?\{([^}]*)\}", r"\n\1\n", text)

    # Repeatedly unwrap simple commands with a single braced argument.
    for _ in range(4):
        text = re.sub(r"\\[a-zA-Z@]+(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", text)

    # Drop remaining begin/end and command tokens.
    text = re.sub(r"\\(?:begin|end)\{[^}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z@]+(?:\[[^\]]*\])?", " ", text)

    # Unescape common TeX escaped characters.
    text = (
        text.replace(r"\_", "_")
        .replace(r"\%", "%")
        .replace(r"\&", "&")
        .replace(r"\$", "$")
        .replace(r"\#", "#")
    )
    return text


def _prepare_manual_text(path: Path, raw_text: str) -> str:
    if path.suffix.lower() == ".tex":
        raw_text = _strip_tex_commands(raw_text)

    # Normalize whitespace for matching/snippets.
    lines = [re.sub(r"\s+", " ", line).strip() for line in raw_text.splitlines()]
    return "\n".join(line for line in lines if line)


def _read_manual_matches(swmf_root: str, query_norm: str, tokens: list[str], max_docs: int = 5) -> list[dict[str, Any]]:
    source_roots: list[tuple[Path, str, list[str]]] = [
        (Path(swmf_root) / "doc" / "Tex", "manual/tex", ["*.tex"]),
    ]

    matches: list[dict[str, Any]] = []
    for root_dir, source_kind, patterns in source_roots:
        if not root_dir.is_dir():
            continue

        files: list[Path] = []
        for pattern in patterns:
            files.extend(sorted(root_dir.rglob(pattern)))

        for path in files:
            try:
                raw_text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            prepared_text = _prepare_manual_text(path, raw_text)
            lowered = prepared_text.lower()

            if query_norm and query_norm in lowered:
                pass
            elif tokens and any(token in lowered for token in tokens):
                pass
            else:
                continue

            lines = prepared_text.splitlines()
            hit_indices: list[int] = []
            for idx, line in enumerate(lines):
                line_l = line.lower()
                if (query_norm and query_norm in line_l) or any(token in line_l for token in tokens):
                    hit_indices.append(idx)
                if len(hit_indices) >= 2:
                    break

            snippets: list[str] = []
            for idx in hit_indices:
                start = max(0, idx - 1)
                end = min(len(lines), idx + 2)
                snippet = "\n".join(lines[start:end]).strip()
                if snippet:
                    snippets.append(snippet)

            if not snippets and lines:
                snippets = ["\n".join(lines[:2]).strip()]

            matches.append(
                {
                    "path": str(path.resolve()),
                    "snippets": snippets[:2],
                    "source_kind": source_kind,
                    "authority": "derived",
                }
            )
            if len(matches) >= max_docs:
                return matches

    return matches


def get_param_schema_resource(component: str) -> dict[str, Any]:
    error, catalog = _load_catalog()
    if error is not None or catalog is None:
        return error or {"ok": False, "message": "Catalog unavailable."}

    raw_query = component.strip()
    query_norm = raw_query.lower()
    target = raw_query.upper()
    tokens = _keyword_tokens(raw_query)
    known_components = {comp.upper() for comp in catalog.components.keys()}

    if target in {"", "ALL", "*"}:
        query_mode = "all"
    elif target in known_components:
        query_mode = "component"
    else:
        query_mode = "keyword"

    commands: list[dict[str, Any]] = []
    ranked_matches: list[tuple[int, Any]] = []
    for _, entries in sorted(catalog.commands.items()):
        for item in entries:
            include = False
            score = 0
            if query_mode == "all":
                include = True
            elif query_mode == "component":
                include = (item.component or "CON") == target
            else:
                score = _command_keyword_score(item, query_norm=query_norm, tokens=tokens)
                include = score > 0

            if include:
                ranked_matches.append((score, item))

    if query_mode == "keyword":
        ranked_matches.sort(key=lambda pair: (-pair[0], (pair[1].normalized or "")))

    for score, item in ranked_matches:
        command_payload = {
            "name": item.name,
            "normalized": item.normalized,
            "component": item.component,
            "description": item.description,
            "defaults": item.defaults,
            "allowed_values": item.allowed_values,
            "ranges": item.ranges,
            "source_path": item.source_path,
        }
        if query_mode == "keyword":
            command_payload["match_score"] = score
        commands.append(command_payload)

    manual_context: list[dict[str, Any]] = []
    if query_mode == "keyword":
        manual_context = _read_manual_matches(catalog.swmf_root, query_norm=query_norm, tokens=tokens)

    source_path_set: set[str] = set()
    for item in commands:
        path_text = item.get("source_path")
        if isinstance(path_text, str) and path_text:
            source_path_set.add(path_text)
    for entry in manual_context:
        path_text = entry.get("path")
        if isinstance(path_text, str) and path_text:
            source_path_set.add(path_text)
    source_paths = sorted(source_path_set)

    source_kinds = {"PARAM.XML", "component PARAM.XML"}
    for entry in manual_context:
        source_kind = entry.get("source_kind")
        if isinstance(source_kind, str) and source_kind:
            source_kinds.add(source_kind)

    return {
        "ok": True,
        "component": target,
        "query": raw_query,
        "query_mode": query_mode,
        "keyword_tokens": tokens,
        "count": len(commands),
        "commands": commands,
        "manual_context_count": len(manual_context),
        "manual_context": manual_context,
        "source_paths": source_paths,
        "source_kinds": sorted(source_kinds),
        "swmf_root_resolved": catalog.swmf_root,
    }


def register(app: Any) -> None:
    if not hasattr(app, "resource"):
        return

    @app.resource(
        "swmf://param-schema/{component}",
        name="swmf_param_schema",
        description="Indexed PARAM.XML metadata filtered by component or keyword, enriched with manual docs snippets.",
        mime_type="application/json",
    )
    def param_schema_resource(component: str) -> dict[str, Any]:
        return get_param_schema_resource(component)
