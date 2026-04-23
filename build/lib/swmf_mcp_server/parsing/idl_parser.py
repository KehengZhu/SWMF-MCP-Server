from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_DECLARATION_RE = re.compile(
    r"^\s*(pro|function)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:,\s*(.*))?$",
    flags=re.IGNORECASE,
)


@dataclass
class IdlProcedureSignature:
    kind: str
    name: str
    params: list[str]
    keywords: list[str]
    signature: str
    docstring: str | None
    line_number: int


def _parse_declared_parameters(raw: str | None) -> tuple[list[str], list[str]]:
    if not raw:
        return [], []

    # IDL declarations are comma-separated. This lightweight split is sufficient
    # for SWMF's procedure headers where nested expressions are uncommon.
    tokens = [item.strip() for item in raw.split(",") if item.strip()]
    params: list[str] = []
    keywords: list[str] = []

    for token in tokens:
        if token.startswith("/"):
            keywords.append(token[1:].strip())
            continue

        if "=" in token:
            key = token.split("=", 1)[0].strip()
            if key:
                keywords.append(key)
            continue

        params.append(token)

    return params, keywords


def _is_comment_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(";")


def _clean_comment_line(line: str) -> str:
    stripped = line.strip()
    return stripped.lstrip(";").strip()


def _collect_comment_block_above(lines: list[str], index: int) -> list[str]:
    comments: list[str] = []
    cursor = index - 1

    while cursor >= 0:
        line = lines[cursor]
        if _is_comment_line(line):
            comments.append(_clean_comment_line(line))
            cursor -= 1
            continue

        if not line.strip():
            if comments:
                break
            cursor -= 1
            continue

        break

    comments.reverse()
    return [item for item in comments if item]


def _collect_comment_block_below(lines: list[str], index: int) -> list[str]:
    comments: list[str] = []
    cursor = index + 1

    while cursor < len(lines):
        line = lines[cursor]
        if _is_comment_line(line):
            comments.append(_clean_comment_line(line))
            cursor += 1
            continue

        if not line.strip():
            if comments:
                break
            cursor += 1
            continue

        break

    return [item for item in comments if item]


def parse_idl_procedures(text: str) -> list[IdlProcedureSignature]:
    lines = text.splitlines()
    procedures: list[IdlProcedureSignature] = []

    for index, line in enumerate(lines):
        match = _DECLARATION_RE.match(line)
        if match is None:
            continue

        kind = match.group(1).lower()
        name = match.group(2)
        raw_params = match.group(3)
        params, keywords = _parse_declared_parameters(raw_params)

        comment_lines = _collect_comment_block_above(lines, index)
        if not comment_lines:
            comment_lines = _collect_comment_block_below(lines, index)
        docstring = "\n".join(comment_lines) if comment_lines else None

        procedures.append(
            IdlProcedureSignature(
                kind=kind,
                name=name,
                params=params,
                keywords=keywords,
                signature=line.strip(),
                docstring=docstring,
                line_number=index + 1,
            )
        )

    return procedures


def parse_idl_file(path: Path) -> list[IdlProcedureSignature]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    return parse_idl_procedures(text)
