from __future__ import annotations

from pathlib import Path
from typing import Iterable


def iter_files(root: Path, pattern: str) -> Iterable[Path]:
    if not root.exists():
        return []
    return root.rglob(pattern)


def safe_read_text(path: Path, encoding: str = "utf-8") -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding=encoding, errors="ignore"), None
    except OSError as exc:
        return None, f"Failed to read file {path}: {exc}"


def file_mtime_map(paths: list[str]) -> dict[str, float]:
    mtimes: dict[str, float] = {}
    for path_text in paths:
        path = Path(path_text)
        try:
            mtimes[path_text] = path.stat().st_mtime
        except OSError:
            mtimes[path_text] = -1.0
    return mtimes
