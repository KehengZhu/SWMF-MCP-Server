"""
SWMF-aware text chunkers.

Each chunker takes a DiscoveredFile and returns a list of ChunkRecord objects,
one per semantic unit (module, subroutine, command block, section, etc.).

All chunkers are stateless and deterministic: same file → same chunks.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from ..corpus import DiscoveredFile
from ..models import AuthorityTier, ChunkKind, ChunkRecord, CorpusSlice


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> list[str]:
    """Read lines, tolerating encoding errors."""
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def _make_chunk(
    f: DiscoveredFile,
    kind: ChunkKind,
    start: int,
    end: int,
    lines: list[str],
    *,
    symbol: str | None = None,
    parent_symbol: str | None = None,
    component: str | None = None,
    keywords: list[str] | None = None,
    authority: AuthorityTier = AuthorityTier.SEMANTIC_RETRIEVAL,
) -> ChunkRecord:
    text = "\n".join(lines[start:end])
    chunk_id = ChunkRecord.make_id(f.abs_path.parent.as_posix(), f.rel_path, start + 1)
    return ChunkRecord(
        chunk_id=chunk_id,
        corpus_root=str(f.abs_path.parent),  # re-rooted at corpus root in index builder
        rel_path=f.rel_path,
        kind=kind,
        authority=authority,
        corpus_slice=f.corpus_slice,
        start_line=start + 1,
        end_line=end,
        text=text,
        component=component or _component_from_path(f.rel_path),
        symbol=symbol,
        parent_symbol=parent_symbol,
        keywords=keywords or [],
    )


_COMPONENT_RE = re.compile(
    r"(?:^|[/\\])(GM|IE|IM|IH|SC|OH|RB|UA|PS|SP|CON|BATS|RCM|RIM|ESMF|PWOM|CIE|CIMI|GITM|PWOM)(?:[/\\$])",
    re.IGNORECASE,
)


def _component_from_path(rel_path: str) -> str | None:
    m = _COMPONENT_RE.search(rel_path)
    return m.group(1).upper() if m else None


# ---------------------------------------------------------------------------
# Fortran chunker
# ---------------------------------------------------------------------------

_F90_MODULE_START = re.compile(r"^\s*MODULE\s+(\w+)", re.IGNORECASE)
_F90_MODULE_END = re.compile(r"^\s*END\s+MODULE(?:\s+\w+)?", re.IGNORECASE)
_F90_SUB_START = re.compile(r"^\s*(?:RECURSIVE\s+)?SUBROUTINE\s+(\w+)", re.IGNORECASE)
_F90_SUB_END = re.compile(r"^\s*END\s+SUBROUTINE(?:\s+\w+)?", re.IGNORECASE)
_F90_FUNC_START = re.compile(r"^\s*(?:PURE\s+|ELEMENTAL\s+)?(?:\w+\s+)?FUNCTION\s+(\w+)", re.IGNORECASE)
_F90_FUNC_END = re.compile(r"^\s*END\s+FUNCTION(?:\s+\w+)?", re.IGNORECASE)


def chunk_fortran(f: DiscoveredFile) -> list[ChunkRecord]:
    lines = _read(f.abs_path)
    if not lines:
        return []

    chunks: list[ChunkRecord] = []
    stack: list[tuple[str, str, int]] = []  # (kind, name, start_line_idx)

    for i, line in enumerate(lines):
        m = _F90_MODULE_START.match(line)
        if m:
            stack.append(("module", m.group(1), i))
            continue

        m = _F90_MODULE_END.match(line)
        if m and stack and stack[-1][0] == "module":
            kind_str, name, start = stack.pop()
            chunks.append(_make_chunk(
                f, ChunkKind.FORTRAN_MODULE, start, i + 1, lines,
                symbol=name, authority=AuthorityTier.SOURCE_VERBATIM,
                keywords=_extract_fortran_keywords(lines[start: i + 1]),
            ))
            continue

        m = _F90_SUB_START.match(line)
        if m:
            parent = stack[-1][1] if stack else None
            stack.append(("subroutine", m.group(1), i))
            continue

        m = _F90_SUB_END.match(line)
        if m and stack and stack[-1][0] == "subroutine":
            kind_str, name, start = stack.pop()
            parent = stack[-1][1] if stack else None
            chunks.append(_make_chunk(
                f, ChunkKind.FORTRAN_SUBROUTINE, start, i + 1, lines,
                symbol=name, parent_symbol=parent,
                authority=AuthorityTier.SOURCE_VERBATIM,
                keywords=_extract_fortran_keywords(lines[start: i + 1]),
            ))
            continue

        m = _F90_FUNC_START.match(line)
        if m and "END" not in line.upper():
            parent = stack[-1][1] if stack else None
            stack.append(("function", m.group(1), i))
            continue

        m = _F90_FUNC_END.match(line)
        if m and stack and stack[-1][0] == "function":
            kind_str, name, start = stack.pop()
            parent = stack[-1][1] if stack else None
            chunks.append(_make_chunk(
                f, ChunkKind.FORTRAN_FUNCTION, start, i + 1, lines,
                symbol=name, parent_symbol=parent,
                authority=AuthorityTier.SOURCE_VERBATIM,
                keywords=_extract_fortran_keywords(lines[start: i + 1]),
            ))

    # If stack is non-empty (malformed file), emit remaining spans as plain blocks.
    for kind_str, name, start in stack:
        kind_map = {
            "module": ChunkKind.FORTRAN_MODULE,
            "subroutine": ChunkKind.FORTRAN_SUBROUTINE,
            "function": ChunkKind.FORTRAN_FUNCTION,
        }
        chunks.append(_make_chunk(
            f, kind_map.get(kind_str, ChunkKind.PLAIN_TEXT_BLOCK),
            start, len(lines), lines,
            symbol=name, authority=AuthorityTier.SOURCE_VERBATIM,
        ))

    # Fallback: if no structured chunks found, emit the whole file as one block.
    if not chunks:
        chunks.append(_make_chunk(
            f, ChunkKind.PLAIN_TEXT_BLOCK, 0, len(lines), lines,
            authority=AuthorityTier.SOURCE_VERBATIM,
        ))

    return chunks


def _extract_fortran_keywords(lines: list[str]) -> list[str]:
    """Extract identifiers called or used — heuristic keyword set for lexical pass."""
    words: set[str] = set()
    call_re = re.compile(r"\bCALL\s+(\w+)", re.IGNORECASE)
    use_re = re.compile(r"\bUSE\s+(\w+)", re.IGNORECASE)
    for line in lines:
        for m in call_re.finditer(line):
            words.add(m.group(1).upper())
        for m in use_re.finditer(line):
            words.add(m.group(1).upper())
    return sorted(words)


# ---------------------------------------------------------------------------
# Perl chunker
# ---------------------------------------------------------------------------

_PERL_SUB_START = re.compile(r"^sub\s+(\w+)\s*\{?")
_PERL_SUB_END = re.compile(r"^\}$")


def chunk_perl(f: DiscoveredFile) -> list[ChunkRecord]:
    lines = _read(f.abs_path)
    if not lines:
        return []

    chunks: list[ChunkRecord] = []
    in_sub: bool = False
    sub_name: str = ""
    sub_start: int = 0
    brace_depth: int = 0

    for i, line in enumerate(lines):
        if not in_sub:
            m = _PERL_SUB_START.match(line)
            if m:
                in_sub = True
                sub_name = m.group(1)
                sub_start = i
                brace_depth = line.count("{") - line.count("}")
        else:
            brace_depth += line.count("{") - line.count("}")
            if brace_depth <= 0:
                chunks.append(_make_chunk(
                    f, ChunkKind.PERL_SUB, sub_start, i + 1, lines,
                    symbol=sub_name, authority=AuthorityTier.SOURCE_VERBATIM,
                ))
                in_sub = False
                brace_depth = 0

    if not chunks:
        chunks.append(_make_chunk(
            f, ChunkKind.PLAIN_TEXT_BLOCK, 0, len(lines), lines,
            authority=AuthorityTier.SOURCE_VERBATIM,
        ))

    return chunks


# ---------------------------------------------------------------------------
# PARAM XML chunker
# ---------------------------------------------------------------------------

_XML_COMMAND_RE = re.compile(r'<command\s+name="([^"]+)"', re.IGNORECASE)
_XML_COMMAND_END = re.compile(r"</command>", re.IGNORECASE)


def chunk_param_xml(f: DiscoveredFile) -> list[ChunkRecord]:
    lines = _read(f.abs_path)
    if not lines:
        return []

    chunks: list[ChunkRecord] = []
    in_cmd: bool = False
    cmd_name: str = ""
    cmd_start: int = 0

    for i, line in enumerate(lines):
        if not in_cmd:
            m = _XML_COMMAND_RE.search(line)
            if m:
                in_cmd = True
                cmd_name = m.group(1)
                cmd_start = i
        if in_cmd and _XML_COMMAND_END.search(line):
            chunks.append(_make_chunk(
                f, ChunkKind.XML_COMMAND, cmd_start, i + 1, lines,
                symbol=cmd_name, authority=AuthorityTier.SCHEMA_VALIDATED,
                keywords=[cmd_name],
            ))
            in_cmd = False

    if not chunks:
        chunks.append(_make_chunk(
            f, ChunkKind.PLAIN_TEXT_BLOCK, 0, len(lines), lines,
            authority=AuthorityTier.SCHEMA_VALIDATED,
        ))

    return chunks


# ---------------------------------------------------------------------------
# TeX chunker
# ---------------------------------------------------------------------------

_TEX_SUBSECTION_RE = re.compile(r"\\(?:sub)?section\*?\{([^}]+)\}")


def chunk_tex(f: DiscoveredFile) -> list[ChunkRecord]:
    lines = _read(f.abs_path)
    if not lines:
        return []

    sections: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        m = _TEX_SUBSECTION_RE.search(line)
        if m:
            sections.append((m.group(1), i))

    if not sections:
        return [_make_chunk(
            f, ChunkKind.TEX_SUBSECTION, 0, len(lines), lines,
            authority=AuthorityTier.DOCUMENTATION,
        )]

    chunks: list[ChunkRecord] = []
    for idx, (title, start) in enumerate(sections):
        end = sections[idx + 1][1] if idx + 1 < len(sections) else len(lines)
        chunks.append(_make_chunk(
            f, ChunkKind.TEX_SUBSECTION, start, end, lines,
            symbol=title, authority=AuthorityTier.DOCUMENTATION,
            keywords=[w.lower() for w in re.findall(r"\b\w{4,}\b", title)],
        ))

    return chunks


# ---------------------------------------------------------------------------
# Markdown / skill chunker
# ---------------------------------------------------------------------------

_MD_HEADER_RE = re.compile(r"^#{1,3}\s+(.+)")


def chunk_markdown(f: DiscoveredFile) -> list[ChunkRecord]:
    lines = _read(f.abs_path)
    if not lines:
        return []

    # Skill files get a different kind for authority purposes.
    is_skill = "skills" in f.rel_path.replace("\\", "/")
    kind = ChunkKind.SKILL_SECTION if is_skill else ChunkKind.MARKDOWN_SECTION
    authority = AuthorityTier.DOCUMENTATION

    sections: list[tuple[str, int]] = []
    for i, line in enumerate(lines):
        m = _MD_HEADER_RE.match(line)
        if m:
            sections.append((m.group(1).strip(), i))

    if not sections:
        return [_make_chunk(f, kind, 0, len(lines), lines, authority=authority)]

    chunks: list[ChunkRecord] = []
    for idx, (title, start) in enumerate(sections):
        end = sections[idx + 1][1] if idx + 1 < len(sections) else len(lines)
        chunks.append(_make_chunk(
            f, kind, start, end, lines,
            symbol=title, authority=authority,
            keywords=[w.lower() for w in re.findall(r"\b\w{4,}\b", title)],
        ))

    return chunks


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

ChunkerFn = Callable[[DiscoveredFile], list[ChunkRecord]]

_EXT_TO_CHUNKER: dict[str, ChunkerFn] = {
    ".f90": chunk_fortran,
    ".f": chunk_fortran,
    ".F90": chunk_fortran,
    ".F": chunk_fortran,
    ".pl": chunk_perl,
    ".pm": chunk_perl,
    ".xml": chunk_param_xml,
    ".tex": chunk_tex,
    ".md": chunk_markdown,
    ".rst": chunk_markdown,
}


def chunk_file(f: DiscoveredFile) -> list[ChunkRecord]:
    """
    Dispatch to the appropriate chunker based on file extension.
    Returns an empty list if no chunker handles this extension.
    """
    ext = f.abs_path.suffix
    chunker = _EXT_TO_CHUNKER.get(ext)
    if chunker is None:
        return []
    try:
        return chunker(f)
    except Exception:
        # Never crash the full build because one file is malformed.
        return []
