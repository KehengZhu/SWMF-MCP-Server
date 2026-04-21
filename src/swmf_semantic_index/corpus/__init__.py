"""
Corpus discovery for the SWMF semantic index.

Walks SWMF and SWMFSOLAR directory trees and classifies files into corpus slices.
Returns lists of (abs_path, rel_path, CorpusSlice) tuples that the chunking layer
can consume.

Design notes:
- No dependency on swmf_mcp_server. Root validation is self-contained.
- Skips generated files, build artifacts, binaries, and very large files.
- File classification is heuristic but deterministic: same tree → same file list.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..models import CorpusSlice


# ---------------------------------------------------------------------------
# File classification rules
# ---------------------------------------------------------------------------

# Extensions that are worth indexing, mapped to their corpus slice hint.
# The final slice assignment also depends on directory position.
_INDEXABLE_EXTENSIONS: dict[str, CorpusSlice] = {
    ".f90": CorpusSlice.SWMF_SOURCE,
    ".f": CorpusSlice.SWMF_SOURCE,
    ".F90": CorpusSlice.SWMF_SOURCE,
    ".F": CorpusSlice.SWMF_SOURCE,
    ".pl": CorpusSlice.SWMF_SCRIPTS,
    ".pm": CorpusSlice.SWMF_SCRIPTS,
    ".tex": CorpusSlice.SWMF_MANUALS,
    ".xml": CorpusSlice.SWMF_PARAM_XML,
    ".XML": CorpusSlice.SWMF_PARAM_XML,
    ".md": CorpusSlice.ANALYST_CONTEXT,
    ".rst": CorpusSlice.ANALYST_CONTEXT,
}

# Directory name fragments that indicate generated or build output.
_SKIP_DIR_FRAGMENTS = frozenset([
    "build", "Build", "obj", "Obj", ".git", "__pycache__",
    "node_modules", ".cache", "dist", "CVS",
])

# Max file size to index (bytes). Files larger than this are skipped with a note.
_MAX_FILE_BYTES = 500_000

# Files whose names match these patterns are skipped.
_SKIP_FILE_PATTERNS = frozenset([
    "Makefile", "makefile", "GNUmakefile",
])


# ---------------------------------------------------------------------------
# Discovery result
# ---------------------------------------------------------------------------


@dataclass
class DiscoveredFile:
    abs_path: Path
    rel_path: str          # relative to corpus_root
    corpus_slice: CorpusSlice
    file_size: int


# ---------------------------------------------------------------------------
# Root detection helpers
# ---------------------------------------------------------------------------


def _is_swmf_root(path: Path) -> bool:
    """Quick heuristic: a directory is an SWMF root if Config.pl exists there."""
    return (path / "Config.pl").is_file()


def _is_swmfsolar_root(path: Path) -> bool:
    """A directory is an SWMFSOLAR root if it has an Idl/ or Solar/ sub-dir."""
    return (path / "Idl").is_dir() or (path / "Solar").is_dir()


def _refine_slice(default_slice: CorpusSlice, rel_path: str, corpus_root_slice: CorpusSlice) -> CorpusSlice:
    """
    Override the extension-based default slice based on path context.
    e.g. a .xml file under doc/ is a manual, not a PARAM file.
    """
    parts = rel_path.lower().split(os.sep)
    if "test" in parts or "tests" in parts:
        return CorpusSlice.SWMF_TESTS
    if any(p in ("doc", "docs", "tex") for p in parts):
        if default_slice == CorpusSlice.SWMF_PARAM_XML:
            return CorpusSlice.SWMF_MANUALS
        if default_slice == CorpusSlice.ANALYST_CONTEXT:
            return CorpusSlice.SWMF_MANUALS
    if default_slice == CorpusSlice.SWMF_SOURCE and corpus_root_slice == CorpusSlice.SWMFSOLAR_SOURCE:
        return CorpusSlice.SWMFSOLAR_SOURCE
    if default_slice == CorpusSlice.SWMF_PARAM_XML:
        # Only files named PARAM.XML or matching *PARAM*.xml count as param xml.
        filename = parts[-1]
        if "param" in filename:
            return CorpusSlice.SWMF_PARAM_XML
        return CorpusSlice.SWMF_MANUALS
    return corpus_root_slice if default_slice == CorpusSlice.SWMF_SOURCE else default_slice


# ---------------------------------------------------------------------------
# Main discovery functions
# ---------------------------------------------------------------------------


def discover_corpus_root(
    root: Path,
    corpus_root_slice: CorpusSlice,
    max_file_bytes: int = _MAX_FILE_BYTES,
) -> list[DiscoveredFile]:
    """
    Walk *root* and return DiscoveredFile records for all indexable files.

    Parameters
    ----------
    root:
        Absolute path to the corpus root (SWMF or SWMFSOLAR).
    corpus_root_slice:
        The primary CorpusSlice for this root (used when refining source files).
    max_file_bytes:
        Files larger than this are skipped.
    """
    root = root.resolve()
    results: list[DiscoveredFile] = []

    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # Prune directories in-place so os.walk does not descend into them.
        dirnames[:] = [
            d for d in dirnames
            if not any(frag in d for frag in _SKIP_DIR_FRAGMENTS)
        ]

        dir_path = Path(dirpath)
        for fname in filenames:
            if fname in _SKIP_FILE_PATTERNS:
                continue
            fpath = dir_path / fname
            ext = fpath.suffix

            if ext not in _INDEXABLE_EXTENSIONS:
                continue

            try:
                fsize = fpath.stat().st_size
            except OSError:
                continue

            if fsize == 0 or fsize > max_file_bytes:
                continue

            rel = str(fpath.relative_to(root))
            default_slice = _INDEXABLE_EXTENSIONS[ext]
            final_slice = _refine_slice(default_slice, rel, corpus_root_slice)

            results.append(DiscoveredFile(
                abs_path=fpath,
                rel_path=rel,
                corpus_slice=final_slice,
                file_size=fsize,
            ))

    return results


def discover_swmf(swmf_root: Path, max_file_bytes: int = _MAX_FILE_BYTES) -> list[DiscoveredFile]:
    """Discover all indexable files under an SWMF root."""
    return discover_corpus_root(swmf_root, CorpusSlice.SWMF_SOURCE, max_file_bytes)


def discover_swmfsolar(solar_root: Path, max_file_bytes: int = _MAX_FILE_BYTES) -> list[DiscoveredFile]:
    """Discover all indexable files under an SWMFSOLAR root."""
    return discover_corpus_root(solar_root, CorpusSlice.SWMFSOLAR_SOURCE, max_file_bytes)


def discover_roots(
    roots: list[tuple[Path, CorpusSlice]],
    max_file_bytes: int = _MAX_FILE_BYTES,
) -> list[DiscoveredFile]:
    """
    Discover files across multiple roots.

    Parameters
    ----------
    roots:
        List of (path, corpus_slice) pairs. Typically:
        [(swmf_path, SWMF_SOURCE), (solar_path, SWMFSOLAR_SOURCE)]
    """
    all_files: list[DiscoveredFile] = []
    for path, slice_ in roots:
        all_files.extend(discover_corpus_root(path, slice_, max_file_bytes))
    return all_files


def validate_root(path: Path) -> Optional[str]:
    """
    Return None if path is a usable corpus root, or an error string if not.
    Checks existence and at least one known root marker.
    """
    if not path.exists():
        return f"path does not exist: {path}"
    if not path.is_dir():
        return f"not a directory: {path}"
    if not _is_swmf_root(path) and not _is_swmfsolar_root(path):
        # Soft warning — we still index it, but warn that no root marker was found.
        return None  # allow any directory; caller may warn separately
    return None
