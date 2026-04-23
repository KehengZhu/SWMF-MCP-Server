"""Meaning-bearing Fortran chunk extraction for SWMF source files.

This module extracts retrieval-oriented chunks from Fortran routines. It is
lighter-weight than a full parser and intentionally builds on the existing
symbol extraction logic.

Current chunk types
-------------------
* ``symbol_body``: whole subroutine/function body when no finer branch chunk is emitted
* ``case_branch``: one ``case(...)`` branch from a ``select case`` block
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .fortran_parser import FortranSymbol, parse_fortran_file

_CASE_RE = re.compile(r"^\s*case\s*(?:\(\s*(['\"][^'\"]+['\"])\s*\)|default)\s*$", re.IGNORECASE)
_SELECT_CASE_RE = re.compile(r"^\s*select\s+case\b", re.IGNORECASE)
_END_SELECT_RE = re.compile(r"^\s*end\s*select\b", re.IGNORECASE)
_END_SUBROUTINE_RE = re.compile(r"^\s*end\s+subroutine\b", re.IGNORECASE)
_END_FUNCTION_RE = re.compile(r"^\s*end\s+function\b", re.IGNORECASE)
_PARAM_REF_RE = re.compile(r"['\"]#([A-Z][A-Z0-9_]+)['\"]")


@dataclass
class FortranCodeChunk:
    chunk_kind: str
    symbol_name: str
    label: str
    file_path: str
    start_line: int
    end_line: int
    component: str | None
    text: str
    uses: list[str] = field(default_factory=list)
    param_refs: list[str] = field(default_factory=list)


def _collect_param_refs(text: str) -> list[str]:
    refs = {match.group(1) for match in _PARAM_REF_RE.finditer(text)}
    return sorted(refs)


def _find_symbol_end(lines: list[str], start_index: int, kind: str) -> int:
    end_pattern = _END_SUBROUTINE_RE if kind == "subroutine" else _END_FUNCTION_RE
    for index in range(start_index + 1, len(lines)):
        if end_pattern.match(lines[index]):
            return index
    return len(lines) - 1


def _make_symbol_body_chunk(
    path: Path,
    symbol: FortranSymbol,
    lines: list[str],
    start_index: int,
    end_index: int,
) -> FortranCodeChunk:
    text = "\n".join(lines[start_index:end_index + 1]).strip()
    return FortranCodeChunk(
        chunk_kind="symbol_body",
        symbol_name=symbol.name,
        label=symbol.name,
        file_path=str(path),
        start_line=start_index + 1,
        end_line=end_index + 1,
        component=symbol.component,
        text=text,
        uses=list(symbol.uses),
        param_refs=_collect_param_refs(text) or list(symbol.param_refs),
    )


def _extract_case_branch_chunks(
    path: Path,
    symbol: FortranSymbol,
    lines: list[str],
    start_index: int,
    end_index: int,
) -> list[FortranCodeChunk]:
    results: list[FortranCodeChunk] = []
    cursor = start_index

    while cursor <= end_index:
        if not _SELECT_CASE_RE.match(lines[cursor]):
            cursor += 1
            continue

        cursor += 1
        while cursor <= end_index:
            if _END_SELECT_RE.match(lines[cursor]):
                break

            case_match = _CASE_RE.match(lines[cursor])
            if case_match is None:
                cursor += 1
                continue

            branch_start = cursor
            raw_label = case_match.group(1)
            case_label = raw_label.strip("'\"") if raw_label else "default"

            cursor += 1
            while cursor <= end_index:
                if _CASE_RE.match(lines[cursor]) or _END_SELECT_RE.match(lines[cursor]):
                    break
                cursor += 1

            branch_end = cursor - 1
            if branch_end < branch_start:
                branch_end = branch_start

            text = "\n".join(lines[branch_start:branch_end + 1]).strip()
            results.append(
                FortranCodeChunk(
                    chunk_kind="case_branch",
                    symbol_name=symbol.name,
                    label=f"{symbol.name} {case_label}",
                    file_path=str(path),
                    start_line=branch_start + 1,
                    end_line=branch_end + 1,
                    component=symbol.component,
                    text=text,
                    uses=list(symbol.uses),
                    param_refs=_collect_param_refs(text) or list(symbol.param_refs),
                )
            )

        cursor += 1

    return results


def parse_fortran_chunks(path: str | Path, text: str | None = None) -> list[FortranCodeChunk]:
    path = Path(path)
    if text is None:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

    lines = text.splitlines()
    chunks: list[FortranCodeChunk] = []

    for symbol in parse_fortran_file(path, text=text):
        if symbol.kind not in {"subroutine", "function"}:
            continue

        start_index = symbol.start_line - 1
        end_index = _find_symbol_end(lines, start_index, symbol.kind)
        if end_index < start_index:
            continue

        branch_chunks = _extract_case_branch_chunks(path, symbol, lines, start_index, end_index)
        if branch_chunks:
            chunks.extend(branch_chunks)
            continue

        chunks.append(_make_symbol_body_chunk(path, symbol, lines, start_index, end_index))

    return chunks