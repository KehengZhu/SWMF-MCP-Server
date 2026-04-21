"""Lightweight Fortran symbol extractor for SWMF source files.

Extracts modules, subroutines, and functions using regex patterns tuned for
the SWMF/BATSRUS coding style. This is intentionally heuristic (authority:
heuristic) — it does not implement a full Fortran parser or AST.

Key capabilities
----------------
- Module, subroutine, and function declarations
- Comment blocks (!) collected above each declaration as docstrings
- USE module_name statements listed per symbol
- Inline PARAM command references (#COMMANDNAME) found in the symbol body
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

# Module: "module ModName" — but NOT "submodule"
_MODULE_RE = re.compile(r"^\s*module\s+(\w+)\s*(?:!.*)?$", re.IGNORECASE)
_SUBMODULE_RE = re.compile(r"^\s*submodule\b", re.IGNORECASE)

# Subroutine: optional pure/elemental/recursive prefix
_SUBROUTINE_RE = re.compile(
    r"^\s*(?:(?:pure|elemental|recursive|impure)\s+)*subroutine\s+(\w+)\b",
    re.IGNORECASE,
)

# Function: optional type / attribute prefix, handles:
#   real function Foo(x)
#   logical, pure function Bar(x)
#   function Baz(x)
_FUNCTION_RE = re.compile(
    r"^\s*(?:(?:integer|real|double\s+precision|logical|complex|character|type\s*\(\w+\)|"
    r"pure|elemental|recursive|impure)\s+)*function\s+(\w+)\b",
    re.IGNORECASE,
)

# Lines that cannot be declarations (greedy false-positive filter)
_NOT_DECL_PREFIXES_RE = re.compile(r"^\s*(?:call|use|interface|end\s+function|end\s+subroutine)\b", re.IGNORECASE)

# USE statement: "use ModName" or "use ModName, ONLY: ..."
_USE_RE = re.compile(r"^\s*use\s+(\w+)", re.IGNORECASE)

# Fortran comment line
_COMMENT_RE = re.compile(r"^\s*!\s?(.*)")

# PARAM command literals in source: '#STOP', '#MAGNETOGRAM', case('#STOP'), etc.
_PARAM_REF_RE = re.compile(r"['\"]#([A-Z][A-Z0-9_]+)['\"]")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

# Maximum body lines scanned for USE statements and PARAM refs
_BODY_SCAN_LINES = 200


@dataclass
class FortranSymbol:
    """A module, subroutine, or function extracted from a Fortran file."""

    kind: str           # "module" | "subroutine" | "function"
    name: str
    file_path: str
    start_line: int     # 1-based
    docstring: str | None
    component: str | None = None
    uses: list[str] = field(default_factory=list)
    param_refs: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _collect_comment_above(lines: list[str], index: int, max_lines: int = 10) -> str | None:
    """Return the ! comment block immediately above *index* as a single string."""
    block: list[str] = []
    cursor = index - 1
    while cursor >= 0 and (index - cursor) <= max_lines:
        m = _COMMENT_RE.match(lines[cursor])
        if m:
            block.append(m.group(1))
            cursor -= 1
        elif not lines[cursor].strip():
            # Allow one blank line gap; stop if we already collected text
            if block:
                break
            cursor -= 1
        else:
            break
    if not block:
        return None
    block.reverse()
    return " ".join(line for line in block if line)


def _collect_uses(lines: list[str], start: int, max_scan: int = 40) -> list[str]:
    """Return module names from USE statements in the lines following *start*."""
    uses: list[str] = []
    end = min(start + max_scan, len(lines))
    for line in lines[start:end]:
        m = _USE_RE.match(line)
        if m:
            mod = m.group(1)
            if mod not in uses:
                uses.append(mod)
    return uses


def _collect_param_refs(lines: list[str], start: int, max_scan: int = _BODY_SCAN_LINES) -> list[str]:
    """Return PARAM command names (without #) referenced in lines[start:start+max_scan]."""
    refs: set[str] = set()
    end = min(start + max_scan, len(lines))
    for line in lines[start:end]:
        for m in _PARAM_REF_RE.finditer(line):
            refs.add(m.group(1))
    return sorted(refs)


def _infer_component_from_path(path: Path) -> str | None:
    """Guess the SWMF component (GM, SC, IE, …) from the file path."""
    parts = path.parts
    for i, part in enumerate(parts):
        if len(part) == 2 and part.isalpha() and part.isupper():
            # e.g.  SWMF/GM/BATSRUS/src/Mod...
            if i + 1 < len(parts) and parts[i + 1] not in ("src", "util", "share"):
                return part
    # Control layer: files directly under src/ at the root
    for i, part in enumerate(parts):
        if part == "src" and i > 0:
            parent_name = parts[i - 1]
            if parent_name.upper() in ("SWMF", "CON"):
                return "CON"
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_fortran_file(path: str | Path, text: str | None = None) -> list[FortranSymbol]:
    """Extract Fortran symbols from *path*.

    Parameters
    ----------
    path:
        File path (used for metadata and as a fallback reader).
    text:
        Pre-loaded file content; if *None* the file is read from *path*.

    Returns a list of :class:`FortranSymbol` items in declaration order.
    Symbols for which the declaration line could not be classified are omitted.
    """
    path = Path(path)
    if text is None:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

    component = _infer_component_from_path(path)
    lines = text.splitlines()
    symbols: list[FortranSymbol] = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip lines that are obviously not declarations
        if _NOT_DECL_PREFIXES_RE.match(line):
            i += 1
            continue

        # Skip submodule declarations (they start with "submodule")
        if _SUBMODULE_RE.match(line):
            i += 1
            continue

        # ---- Module ----
        mod_m = _MODULE_RE.match(line)
        if mod_m:
            name = mod_m.group(1)
            if name.lower() != "procedure":
                docstring = _collect_comment_above(lines, i)
                symbols.append(FortranSymbol(
                    kind="module",
                    name=name,
                    file_path=str(path),
                    start_line=i + 1,
                    docstring=docstring,
                    component=component,
                ))
            i += 1
            continue

        # ---- Subroutine ----
        sub_m = _SUBROUTINE_RE.match(line)
        if sub_m:
            name = sub_m.group(1)
            docstring = _collect_comment_above(lines, i)
            uses = _collect_uses(lines, i + 1)
            param_refs = _collect_param_refs(lines, i + 1)
            symbols.append(FortranSymbol(
                kind="subroutine",
                name=name,
                file_path=str(path),
                start_line=i + 1,
                docstring=docstring,
                component=component,
                uses=uses,
                param_refs=param_refs,
            ))
            i += 1
            continue

        # ---- Function ----
        fun_m = _FUNCTION_RE.match(line)
        if fun_m:
            name = fun_m.group(1)
            # Filter common false positives
            if name.lower() in ("result",):
                i += 1
                continue
            docstring = _collect_comment_above(lines, i)
            uses = _collect_uses(lines, i + 1)
            param_refs = _collect_param_refs(lines, i + 1)
            symbols.append(FortranSymbol(
                kind="function",
                name=name,
                file_path=str(path),
                start_line=i + 1,
                docstring=docstring,
                component=component,
                uses=uses,
                param_refs=param_refs,
            ))
            i += 1
            continue

        i += 1

    return symbols
