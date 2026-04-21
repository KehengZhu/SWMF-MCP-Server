"""Lightweight Perl symbol extractor for SWMF script files.

Extracts subroutine declarations from Perl scripts using simple regex
patterns suitable for the SWMF Scripts/ style. Authority is always
heuristic — no full Perl AST is involved.

Key capabilities
----------------
- Subroutine declarations (``sub Name { ...}``)
- Comment blocks (``#``) collected above each declaration as docstrings
- Inline PARAM command references (#COMMANDNAME) found in the subroutine body
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

# sub Name { or sub Name($args) { or sub Name\n{
_SUB_RE = re.compile(r"^\s*sub\s+(\w+)\s*(?:\{|(?:\(|;|$))", re.IGNORECASE)

# Perl comment line
_COMMENT_RE = re.compile(r"^\s*#\s?(.*)")

# PARAM command literals in source: '#STOP', '#MAGNETOGRAM', etc.
_PARAM_REF_RE = re.compile(r"['\"]#([A-Z][A-Z0-9_]+)['\"]")

# Maximum body lines scanned for PARAM refs
_BODY_SCAN_LINES = 100


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class PerlSymbol:
    """A subroutine extracted from a Perl file."""

    kind: str           # always "sub"
    name: str
    file_path: str
    start_line: int     # 1-based
    docstring: str | None
    param_refs: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _collect_comment_above(lines: list[str], index: int, max_lines: int = 8) -> str | None:
    """Return the # comment block immediately above *index* as a single string."""
    block: list[str] = []
    cursor = index - 1
    while cursor >= 0 and (index - cursor) <= max_lines:
        m = _COMMENT_RE.match(lines[cursor])
        if m:
            block.append(m.group(1))
            cursor -= 1
        elif not lines[cursor].strip():
            if block:
                break
            cursor -= 1
        else:
            break
    if not block:
        return None
    block.reverse()
    return " ".join(line for line in block if line)


def _collect_param_refs(lines: list[str], start: int, max_scan: int = _BODY_SCAN_LINES) -> list[str]:
    """Return PARAM command names referenced in lines[start:start+max_scan]."""
    refs: set[str] = set()
    end = min(start + max_scan, len(lines))
    for line in lines[start:end]:
        for m in _PARAM_REF_RE.finditer(line):
            refs.add(m.group(1))
    return sorted(refs)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_perl_file(path: str | Path, text: str | None = None) -> list[PerlSymbol]:
    """Extract subroutines from a Perl source file.

    Parameters
    ----------
    path:
        File path (used for metadata and as a fallback reader).
    text:
        Pre-loaded file content; if *None* the file is read from *path*.

    Returns a list of :class:`PerlSymbol` items in declaration order.
    """
    path = Path(path)
    if text is None:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

    lines = text.splitlines()
    symbols: list[PerlSymbol] = []

    for i, line in enumerate(lines):
        m = _SUB_RE.match(line)
        if m:
            name = m.group(1)
            docstring = _collect_comment_above(lines, i)
            param_refs = _collect_param_refs(lines, i + 1)
            symbols.append(PerlSymbol(
                kind="sub",
                name=name,
                file_path=str(path),
                start_line=i + 1,
                docstring=docstring,
                param_refs=param_refs,
            ))

    return symbols
