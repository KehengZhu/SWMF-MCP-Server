from __future__ import annotations

import re


_PATH_TOKEN_RE = re.compile(
    r"([A-Za-z0-9_./~-]+\.(?:fits|fit|dat|out|outs|hdf|hdf5|nc|cdf|txt|bin|xml|ini))",
    flags=re.IGNORECASE,
)


def extract_external_references_from_param_text(param_text: str) -> tuple[list[str], list[str], list[str]]:
    refs: list[str] = []
    include_refs: list[str] = []
    ambiguous: list[str] = []

    lines = param_text.splitlines()
    for idx, raw in enumerate(lines):
        line = raw.strip()
        if not line or line.startswith("!"):
            continue

        if line.upper() == "#INCLUDE":
            next_line = ""
            if idx + 1 < len(lines):
                next_line = lines[idx + 1].strip()
            if next_line and (not next_line.startswith("#")):
                include_refs.append(next_line.split()[0])
            continue

        refs.extend(_PATH_TOKEN_RE.findall(line))
        if any(char in line for char in ["$", "*", "?", "{"]):
            ambiguous.append(line)

    return refs, include_refs, ambiguous
