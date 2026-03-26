from __future__ import annotations

import re
from pathlib import Path


_PATH_TOKEN_RE = re.compile(
    r"([A-Za-z0-9_./~-]+\.(?:fits|fit|dat|out|outs|hdf|hdf5|nc|cdf|txt|bin|xml|ini))",
    flags=re.IGNORECASE,
)


def classify_lightweight_findings(
    param_text: str,
    parser_errors: list[str],
    parser_warnings: list[str],
    param_path_resolved: str | None,
    run_dir: str | None,
) -> dict:
    syntax_or_structure_errors: list[str] = []
    inferred_issues: list[str] = []

    for err in parser_errors:
        lowered = err.lower()
        if any(token in lowered for token in ["parse", "mismatch", "missing", "unclosed", "nested"]):
            syntax_or_structure_errors.append(err)
        else:
            inferred_issues.append(err)

    for warn in parser_warnings:
        inferred_issues.append(warn)

    unresolved_references: list[str] = []
    base_dir = Path(param_path_resolved).resolve().parent if param_path_resolved else Path(run_dir or ".").resolve()

    for line in param_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("!"):
            continue
        for token in _PATH_TOKEN_RE.findall(stripped):
            if any(sym in token for sym in ["*", "?", "$"]):
                continue
            path = Path(token).expanduser()
            if not path.is_absolute():
                path = base_dir / path
            if not path.resolve().is_file():
                unresolved_references.append(str(path.resolve()))

    return {
        "syntax_or_structure_errors": sorted(set(syntax_or_structure_errors)),
        "inferred_issues": sorted(set(inferred_issues)),
        "unresolved_references": sorted(set(unresolved_references)),
        "requires_authoritative_validation": True,
        "authoritative_next_tool": "swmf_run_testparam",
    }
