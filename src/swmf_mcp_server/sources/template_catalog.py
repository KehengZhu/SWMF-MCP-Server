from __future__ import annotations

import fnmatch
from pathlib import Path


_ROOT_TEMPLATE_DIRS = ["Param", "PARAM", "Examples", "example"]
_ROOT_PATTERNS = ["PARAM.in*", "*.PARAM.in", "*.param.in"]


def discover_example_params(swmf_root: Path, max_results: int = 800) -> list[str]:
    matches: list[str] = []
    seen: set[str] = set()

    for dirname in _ROOT_TEMPLATE_DIRS:
        path = swmf_root / dirname
        if not path.is_dir():
            continue
        for child in path.iterdir():
            name = child.name
            if any(fnmatch.fnmatch(name, pattern) for pattern in _ROOT_PATTERNS):
                resolved = str(child.resolve())
                if resolved not in seen:
                    matches.append(resolved)
                    seen.add(resolved)
                    if len(matches) >= max_results:
                        return sorted(matches)

    # Recursive fallback for common PARAM.in files in component trees.
    for path in swmf_root.rglob("PARAM.in"):
        resolved = str(path.resolve())
        if resolved in seen:
            continue
        matches.append(resolved)
        seen.add(resolved)
        if len(matches) >= max_results:
            break

    return sorted(matches)


def find_examples_using_text(paths: list[str], query: str, max_results: int = 50) -> list[str]:
    query_norm = query.lower().strip()
    if not query_norm:
        return []

    results: list[str] = []
    for path_text in paths:
        path = Path(path_text)
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if query_norm in text.lower():
            results.append(path_text)
            if len(results) >= max_results:
                break
    return results
