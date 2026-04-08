from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def resolve_run_dir(run_dir: str | None) -> Path:
    if run_dir:
        return Path(run_dir).expanduser().resolve()
    return Path.cwd().resolve()


def load_param_text(
    param_text: str | None,
    param_path: str | None,
    run_dir: str | None,
) -> tuple[str | None, str | None, str | None]:
    if param_text is not None:
        return param_text, None, None

    if param_path is None:
        return None, None, "Provide param_text or param_path."

    try:
        path = Path(param_path).expanduser()
        if not path.is_absolute():
            base_dir = resolve_run_dir(run_dir)
            path = base_dir / path
        resolved = path.resolve()
        if not resolved.is_file():
            return None, str(resolved), f"param_path does not point to a file: {resolved}"
        return resolved.read_text(encoding="utf-8"), str(resolved), None
    except OSError as exc:
        return None, None, f"Failed to read param_path: {exc}"


def resolve_input_path(path_text: str, run_dir: str | None = None) -> tuple[Path | None, str | None]:
    try:
        path = Path(path_text).expanduser()
        if not path.is_absolute():
            path = resolve_run_dir(run_dir) / path
        resolved = path.resolve()
        if not resolved.is_file():
            return None, f"Input path does not point to a file: {resolved}"
        return resolved, None
    except OSError as exc:
        return None, f"Failed to resolve path '{path_text}': {exc}"


def resolve_reference_path(raw_ref: str, base_dir: Path) -> Path:
    path = Path(raw_ref).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def find_path_search_candidates(
    search_roots: list[Path],
    expected_entries: list[str],
    max_depth: int = 2,
    max_results: int = 12,
) -> list[str]:
    expected = {item for item in expected_entries if item}
    if not expected:
        return []

    candidates: list[str] = []
    seen_candidates: set[str] = set()

    for raw_root in search_roots:
        root = raw_root if raw_root.is_dir() else raw_root.parent
        if not root.exists() or not root.is_dir():
            continue

        queue: list[tuple[Path, int]] = [(root.resolve(), 0)]
        seen_dirs: set[Path] = set()

        while queue and len(candidates) < max_results:
            current, depth = queue.pop(0)
            if current in seen_dirs:
                continue
            seen_dirs.add(current)

            try:
                children = list(current.iterdir())
            except OSError:
                continue

            child_names = {item.name for item in children}
            if child_names.intersection(expected):
                current_text = str(current)
                if current_text not in seen_candidates:
                    seen_candidates.add(current_text)
                    candidates.append(current_text)

            if depth >= max_depth:
                continue

            subdirs = sorted((item for item in children if item.is_dir()), key=lambda item: item.name)
            for subdir in subdirs:
                queue.append((subdir.resolve(), depth + 1))

            if len(candidates) >= max_results:
                break

    return candidates


def _extract_keyword_tokens(values: list[str]) -> list[str]:
    stopwords = {
        "a",
        "an",
        "and",
        "dir",
        "directory",
        "file",
        "for",
        "in",
        "input",
        "of",
        "or",
        "path",
        "run",
        "the",
        "to",
    }
    tokens: list[str] = []
    seen: set[str] = set()
    for value in values:
        for raw in re.split(r"[^A-Za-z0-9]+", value.lower()):
            token = raw.strip()
            if len(token) < 3 or token in stopwords:
                continue
            if token in seen:
                continue
            seen.add(token)
            tokens.append(token)
    return tokens


def find_keyword_path_candidates(
    search_roots: list[Path],
    keywords: list[str],
    max_depth: int = 3,
    max_results: int = 8,
) -> list[str]:
    keywords_norm = [item.lower() for item in keywords if item]
    if not keywords_norm:
        return []

    ranked: list[tuple[int, int, str]] = []
    seen_paths: set[str] = set()

    for raw_root in search_roots:
        root = raw_root if raw_root.is_dir() else raw_root.parent
        if not root.exists() or not root.is_dir():
            continue

        queue: list[tuple[Path, int]] = [(root.resolve(), 0)]
        seen_dirs: set[Path] = set()

        while queue:
            current, depth = queue.pop(0)
            if current in seen_dirs:
                continue
            seen_dirs.add(current)

            current_name = current.name.lower()
            name_matches = [kw for kw in keywords_norm if kw in current_name]
            score = len(name_matches) * 2

            children: list[Path] = []
            try:
                children = list(current.iterdir())
            except OSError:
                children = []

            if children:
                child_names = " ".join(item.name.lower() for item in children)
                score += sum(1 for kw in keywords_norm if kw in child_names)

            if score > 0:
                current_text = str(current)
                if current_text not in seen_paths:
                    seen_paths.add(current_text)
                    ranked.append((score, depth, current_text))

            if depth >= max_depth:
                continue

            subdirs = sorted((item for item in children if item.is_dir()), key=lambda item: item.name)
            for subdir in subdirs:
                queue.append((subdir.resolve(), depth + 1))

    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [item[2] for item in ranked[:max_results]]


def build_path_search_guidance(
    path_role: str,
    search_roots: list[Path],
    expected_entries: list[str],
    keyword_hints: list[str] | None = None,
) -> dict[str, Any]:
    expected = [entry for entry in expected_entries if entry]
    expected_text = ", ".join(expected) if expected else "the expected run artifacts"
    roots = []
    seen_roots: set[str] = set()
    for root in search_roots:
        normalized = root if root.is_dir() else root.parent
        if not normalized.exists():
            continue
        normalized_text = str(normalized.resolve())
        if normalized_text in seen_roots:
            continue
        seen_roots.add(normalized_text)
        roots.append(normalized_text)

    keyword_sources = list(keyword_hints) if keyword_hints else [path_role, *expected]
    keyword_tokens = _extract_keyword_tokens(keyword_sources)
    keyword_candidates = find_keyword_path_candidates(
        search_roots=search_roots,
        keywords=keyword_tokens,
    )

    fallback_candidates = find_path_search_candidates(search_roots=search_roots, expected_entries=expected)

    candidates: list[str] = []
    seen_candidates: set[str] = set()
    for item in [*keyword_candidates, *fallback_candidates]:
        if item in seen_candidates:
            continue
        seen_candidates.add(item)
        candidates.append(item)

    hints = [
        f"Verify {path_role} points to the directory that directly contains {expected_text}.",
        "If lookup fails, inspect child directories first, then parent and sibling directories, and retry with the corrected path.",
        "When uncertain, run a file search for marker files/directories and pass the discovered path back into the tool input.",
    ]
    if keyword_candidates:
        hints.insert(1, "Keyword-matched directories were found; try those candidate paths first.")

    return {
        "path_search_hints": hints,
        "path_search_roots": roots,
        "path_search_keyword_candidates": keyword_candidates,
        "path_search_candidates": candidates,
    }
