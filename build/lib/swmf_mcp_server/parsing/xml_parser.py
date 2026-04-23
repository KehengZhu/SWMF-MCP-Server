from __future__ import annotations

import re
from pathlib import Path

from ..core.authority import SOURCE_KIND_COMPONENT_PARAM_XML, SOURCE_KIND_PARAM_XML
from ..core.models import CommandMetadata

_COMMAND_OPEN_RE = re.compile(r"<command\b([^>]*)>", flags=re.IGNORECASE)
_COMMAND_SELF_CLOSING_RE = re.compile(r"<command\b([^>]*)/>", flags=re.IGNORECASE)
_NAME_ATTR_RE = re.compile(r"\bname\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_TYPE_ATTR_RE = re.compile(r"\btype\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_DEFAULT_ATTR_RE = re.compile(r"\bdefault\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_MIN_ATTR_RE = re.compile(r"\bmin\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_MAX_ATTR_RE = re.compile(r"\bmax\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
_VALUE_ATTR_RE = re.compile(r"\bvalue\s*=\s*\"([^\"]+)\"", flags=re.IGNORECASE)
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


def parse_param_xml_file(path: Path, component: str | None) -> list[CommandMetadata]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    commands: list[CommandMetadata] = []
    seen: set[tuple[str, str | None]] = set()

    source_kind = SOURCE_KIND_COMPONENT_PARAM_XML if component else SOURCE_KIND_PARAM_XML

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

        defaults, allowed_values, ranges = _metadata_from_attrs(attrs)
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
            )
        )

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
            )
        )

    for token_match in _HASH_TOKEN_RE.finditer(text):
        token = token_match.group(1).upper()
        key = (token, component)
        if key in seen:
            continue
        seen.add(key)
        commands.append(
            CommandMetadata(
                name=token,
                normalized=token,
                component=component,
                description=_extract_description_after(token_match.end(), text),
                source_kind=source_kind,
                source_path=str(path),
                authority="authoritative",
            )
        )

    return commands
