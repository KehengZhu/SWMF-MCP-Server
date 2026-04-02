from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..core.swmf_root import resolve_swmf_root

_PAIR_PATTERNS = [
    re.compile(r"COUPLE[_A-Z0-9]*\b([A-Z]{2})\b[_ ]*TO[_ ]*\b([A-Z]{2})\b", flags=re.IGNORECASE),
    re.compile(r"\bUSECOUPLE([A-Z]{2})([A-Z]{2})\b", flags=re.IGNORECASE),
    re.compile(r"\b([A-Z]{2})\s*2\s*([A-Z]{2})\b", flags=re.IGNORECASE),
]


def get_coupling_pairs_resource() -> dict[str, Any]:
    root = resolve_swmf_root()
    if not root.ok or root.swmf_root_resolved is None:
        return {
            "ok": False,
            "error_code": "SWMF_ROOT_RESOLUTION_FAILED",
            "message": root.message,
            "resolution_notes": root.resolution_notes,
            "pairs": [],
        }

    source = Path(root.swmf_root_resolved) / "CON" / "Interface" / "src" / "CON_couple_all.f90"
    if not source.is_file():
        return {
            "ok": False,
            "error_code": "COUPLING_SOURCE_NOT_FOUND",
            "message": f"Could not find coupling source file: {source}",
            "pairs": [],
            "swmf_root_resolved": root.swmf_root_resolved,
        }

    try:
        text = source.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return {
            "ok": False,
            "error_code": "COUPLING_SOURCE_READ_FAILED",
            "message": f"Failed to read coupling source file: {exc}",
            "pairs": [],
            "swmf_root_resolved": root.swmf_root_resolved,
        }

    pairs: set[tuple[str, str]] = set()
    for pattern in _PAIR_PATTERNS:
        for match in pattern.finditer(text):
            a = match.group(1).upper()
            b = match.group(2).upper()
            if len(a) == 2 and len(b) == 2 and a != b:
                pairs.add((a, b))

    payload_pairs = [
        {"source": a, "target": b}
        for a, b in sorted(pairs)
    ]

    return {
        "ok": True,
        "swmf_root_resolved": root.swmf_root_resolved,
        "source_path": str(source),
        "pairs": payload_pairs,
        "count": len(payload_pairs),
    }


def register(app: Any) -> None:
    if not hasattr(app, "resource"):
        return

    @app.resource(
        "swmf://coupling-pairs",
        name="swmf_coupling_pairs",
        description="Extract detected SWMF component coupling pairs from CON coupling source.",
        mime_type="application/json",
    )
    def coupling_resource() -> dict[str, Any]:
        return get_coupling_pairs_resource()
