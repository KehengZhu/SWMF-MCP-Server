from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..core.authority import SOURCE_KIND_COMPONENT_PARAM_XML, SOURCE_KIND_PARAM_XML
from ..core.models import CommandMetadata

_COMMAND_OPEN_RE = re.compile(r"<command\b([^>]*)>", flags=re.IGNORECASE)
_COMMAND_CLOSE_RE = re.compile(r"</command\s*>", flags=re.IGNORECASE)
_COMMAND_SELF_CLOSING_RE = re.compile(r"<command\b([^>]*)/>", flags=re.IGNORECASE)
_COMMANDGROUP_OPEN_RE = re.compile(r"<commandgroup\b([^>]*)>", flags=re.IGNORECASE)
_COMMANDGROUP_CLOSE_RE = re.compile(r"</commandgroup\s*>", flags=re.IGNORECASE)
_PARAMETER_RE = re.compile(r"<parameter\b([^>]*?)/?>", flags=re.IGNORECASE)
_NAME_ATTR_RE = re.compile(r"\bname\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_TYPE_ATTR_RE = re.compile(r"\btype\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_DEFAULT_ATTR_RE = re.compile(r"\bdefault\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_MIN_ATTR_RE = re.compile(r"\bmin\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_MAX_ATTR_RE = re.compile(r"\bmax\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_VALUE_ATTR_RE = re.compile(r"\bvalue\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_IF_ATTR_RE = re.compile(r"\bif\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_HASH_TOKEN_RE = re.compile(r"(?m)^\s*(#[A-Z0-9_]+)\s*$")


def normalize_command_name(raw: str) -> str:
    name = raw.strip()
    if not name:
        return name
    if name.startswith("#"):
        return name.upper()
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
        return f"#{name.upper()}"
    return name


def _extract_description_after(start: int, text: str) -> str | None:
    remainder = text[start : min(len(text), start + 700)]
    lines = [line.strip() for line in remainder.splitlines()]
    filtered = [line for line in lines if line and not line.startswith("<") and not line.startswith("!")]
    if not filtered:
        return None
    sentence = " ".join(filtered[:2]).strip()
    return sentence[:320] if sentence else None


def _metadata_from_attrs(attrs: str) -> tuple[dict[str, str], list[str], list[str]]:
    defaults: dict[str, str] = {}
    allowed_values: list[str] = []
    ranges: list[str] = []

    dtype = _TYPE_ATTR_RE.search(attrs)
    if dtype:
        allowed_values.append(f"type={dtype.group(1)}")

    default = _DEFAULT_ATTR_RE.search(attrs)
    if default:
        defaults["default"] = default.group(1)

    value = _VALUE_ATTR_RE.search(attrs)
    if value:
        allowed_values.append(value.group(1))

    min_match = _MIN_ATTR_RE.search(attrs)
    max_match = _MAX_ATTR_RE.search(attrs)
    if min_match or max_match:
        ranges.append(f"[{min_match.group(1) if min_match else '-inf'}, {max_match.group(1) if max_match else '+inf'}]")

    return defaults, allowed_values, ranges


def _extract_parameters(command_body: str) -> list[dict[str, Any]]:
    """Parse <parameter> children of a <command>...</command> block.

    Returns a list of structured dicts, one per parameter.
    """
    parameters: list[dict[str, Any]] = []
    for match in _PARAMETER_RE.finditer(command_body):
        attrs = match.group(1)
        name_match = _NAME_ATTR_RE.search(attrs)
        if not name_match:
            continue
        entry: dict[str, Any] = {"name": name_match.group(1)}
        type_match = _TYPE_ATTR_RE.search(attrs)
        if type_match:
            entry["type"] = type_match.group(1)
        default_match = _DEFAULT_ATTR_RE.search(attrs)
        if default_match:
            entry["default"] = default_match.group(1)
        min_match = _MIN_ATTR_RE.search(attrs)
        if min_match:
            entry["min"] = min_match.group(1)
        max_match = _MAX_ATTR_RE.search(attrs)
        if max_match:
            entry["max"] = max_match.group(1)
        if_match = _IF_ATTR_RE.search(attrs)
        if if_match:
            entry["if"] = if_match.group(1)
        parameters.append(entry)
    return parameters


def _build_commandgroup_spans(text: str) -> list[tuple[int, int, str]]:
    """Return non-nested (start, end, name) tuples for each <commandgroup>.

    PARAM.XML files in SWMF never nest commandgroups in practice; if a nested
    open is encountered we keep the outermost span and let the inner one be
    treated as orphan content (commandgroup=None for any commands inside).
    """
    spans: list[tuple[int, int, str]] = []
    cursor = 0
    while cursor < len(text):
        open_match = _COMMANDGROUP_OPEN_RE.search(text, cursor)
        if not open_match:
            break
        name_match = _NAME_ATTR_RE.search(open_match.group(1))
        name = name_match.group(1) if name_match else ""
        close_match = _COMMANDGROUP_CLOSE_RE.search(text, open_match.end())
        if not close_match:
            break
        spans.append((open_match.start(), close_match.end(), name))
        cursor = close_match.end()
    return spans


def _commandgroup_for_offset(spans: list[tuple[int, int, str]], offset: int) -> str | None:
    for start, end, name in spans:
        if start <= offset < end:
            return name or None
    return None


def parse_param_xml_file(path: Path, component: str | None) -> list[CommandMetadata]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    commands: list[CommandMetadata] = []
    seen: set[tuple[str, str | None]] = set()
    source_kind = SOURCE_KIND_COMPONENT_PARAM_XML if component else SOURCE_KIND_PARAM_XML
    commandgroup_spans = _build_commandgroup_spans(text)

    # Match <command ...>...</command> blocks first so we can capture <parameter> children.
    for match in _COMMAND_OPEN_RE.finditer(text):
        attrs = match.group(1)
        name_match = _NAME_ATTR_RE.search(attrs)
        if not name_match:
            continue
        raw_name = name_match.group(1)
        normalized = normalize_command_name(raw_name)
        key = (normalized, component)
        if key in seen:
            continue
        seen.add(key)

        # Find the matching </command> (non-nested in PARAM.XML).
        close_match = _COMMAND_CLOSE_RE.search(text, match.end())
        body_end = close_match.start() if close_match else min(len(text), match.end() + 4000)
        body = text[match.end():body_end]

        defaults, allowed_values, ranges = _metadata_from_attrs(attrs)
        parameters = _extract_parameters(body)
        commandgroup = _commandgroup_for_offset(commandgroup_spans, match.start())

        commands.append(
            CommandMetadata(
                name=raw_name,
                normalized=normalized,
                component=component,
                description=_extract_description_after(match.end(), text),
                defaults=defaults,
                allowed_values=allowed_values,
                ranges=ranges,
                source_kind=source_kind,
                source_path=str(path),
                authority="authoritative",
                commandgroup=commandgroup,
                parameters=parameters,
            )
        )

    # Self-closing <command ... /> entries (rare; no parameter children).
    for match in _COMMAND_SELF_CLOSING_RE.finditer(text):
        attrs = match.group(1)
        name_match = _NAME_ATTR_RE.search(attrs)
        if not name_match:
            continue
        raw_name = name_match.group(1)
        normalized = normalize_command_name(raw_name)
        key = (normalized, component)
        if key in seen:
            continue
        seen.add(key)
        defaults, allowed_values, ranges = _metadata_from_attrs(attrs)
        commandgroup = _commandgroup_for_offset(commandgroup_spans, match.start())
        commands.append(
            CommandMetadata(
                name=raw_name,
                normalized=normalized,
                component=component,
                description=None,
                defaults=defaults,
                allowed_values=allowed_values,
                ranges=ranges,
                source_kind=source_kind,
                source_path=str(path),
                authority="authoritative",
                commandgroup=commandgroup,
            )
        )

    # Bare #TOKEN lines (legacy convention; no parameter children, no group).
    for token_match in _HASH_TOKEN_RE.finditer(text):
        token = token_match.group(1).upper()
        key = (token, component)
        if key in seen:
            continue
        seen.add(key)
        commandgroup = _commandgroup_for_offset(commandgroup_spans, token_match.start())
        commands.append(
            CommandMetadata(
                name=token,
                normalized=token,
                component=component,
                description=_extract_description_after(token_match.end(), text),
                source_kind=source_kind,
                source_path=str(path),
                authority="authoritative",
                commandgroup=commandgroup,
            )
        )

    return commands
