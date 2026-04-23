from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from ..core.swmf_root import resolve_swmf_root

_PAIR_PATTERNS = [
    re.compile(r"COUPLE[_A-Z0-9]*\b([A-Z]{2})\b[_ ]*TO[_ ]*\b([A-Z]{2})\b", flags=re.IGNORECASE),
    re.compile(r"\bUSECOUPLE([A-Z]{2})([A-Z]{2})\b", flags=re.IGNORECASE),
    re.compile(r"\b([A-Z]{2})\s*2\s*([A-Z]{2})\b", flags=re.IGNORECASE),
]

# CON_stop call pattern — presence near subroutine top indicates a stub
_CON_STOP_RE = re.compile(r"\bCON_stop\b", re.IGNORECASE)
# Mechanism detection patterns
_MECHANISM_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("buffer_grid", re.compile(r"\bbuffer.grid\b|\bbuffer_grid\b|\bBufferToGM\b|\bGMtoBuffer\b", re.IGNORECASE)),
    ("field_line", re.compile(r"\bfield.line\b|\bfield_line\b|\bfieldline\b", re.IGNORECASE)),
    ("point_coupling", re.compile(r"\bpoint.coupl\b|\binterpolat\b|\bput_from\b|\bget_from\b", re.IGNORECASE)),
]


def _find_coupler_file(interface_src: Path, a: str, b: str) -> Optional[Path]:
    """
    Find the coupler implementation file for a (source, target) pair.
    SWMF naming convention: CON_couple_{a_lower}_{b_lower}.f90.
    Tries both orderings.
    """
    al, bl = a.lower(), b.lower()
    for fname in (f"CON_couple_{al}_{bl}.f90", f"CON_couple_{bl}_{al}.f90"):
        candidate = interface_src / fname
        if candidate.is_file():
            return candidate
    return None


def _check_coupler_implementation(
    coupler_file: Path,
) -> tuple[str, str, Optional[str], Optional[int]]:
    """
    Read a coupler file and determine:
      - status: "implemented" | "stubbed"
      - mechanism: "buffer_grid" | "field_line" | "point_coupling" | "unknown"
      - stub_evidence: the CON_stop line text (if stubbed)
      - stub_line: line number of CON_stop (if stubbed)

    A coupler is considered stubbed if CON_stop appears in the first 30 lines
    of any subroutine whose name starts with 'couple_'.
    """
    try:
        lines = coupler_file.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return "unknown", "unknown", None, None

    full_text = "\n".join(lines)

    # Detect mechanism from full file
    mechanism = "unknown"
    for mech_name, pattern in _MECHANISM_PATTERNS:
        if pattern.search(full_text):
            mechanism = mech_name
            break

    # Detect stub: find CON_stop within first N lines of a couple_ subroutine
    in_couple_sub = False
    sub_line_count = 0
    _SUB_START = re.compile(r"^\s*SUBROUTINE\s+(couple_\w+)", re.IGNORECASE)
    _SUB_END = re.compile(r"^\s*END\s+SUBROUTINE", re.IGNORECASE)

    for lineno, line in enumerate(lines, start=1):
        if not in_couple_sub:
            if _SUB_START.match(line):
                in_couple_sub = True
                sub_line_count = 0
        else:
            sub_line_count += 1
            if _CON_STOP_RE.search(line) and sub_line_count <= 30:
                return "stubbed", mechanism, line.strip(), lineno
            if _SUB_END.match(line):
                in_couple_sub = False

    return "implemented", mechanism, None, None


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

    interface_src = Path(root.swmf_root_resolved) / "CON" / "Interface" / "src"
    source = interface_src / "CON_couple_all.f90"
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

    payload_pairs = []
    for a, b in sorted(pairs):
        coupler_file = _find_coupler_file(interface_src, a, b)
        if coupler_file is None:
            entry: dict[str, Any] = {
                "source": a,
                "target": b,
                "status": "in_registry_only",
                "mechanism": "unknown",
                "implementation_file": None,
                "implementation_line": None,
                "stub_evidence": None,
                "note": "Pair found in CON_couple_all.f90 but no coupler file located.",
            }
        else:
            status, mechanism, stub_evidence, stub_line = _check_coupler_implementation(coupler_file)
            entry = {
                "source": a,
                "target": b,
                "status": status,
                "mechanism": mechanism,
                "implementation_file": str(coupler_file.relative_to(root.swmf_root_resolved)),
                "implementation_line": stub_line,
                "stub_evidence": stub_evidence,
                "note": (
                    f"Stub detected at line {stub_line}: {stub_evidence}"
                    if status == "stubbed"
                    else None
                ),
            }
        payload_pairs.append(entry)

    implemented = [p for p in payload_pairs if p["status"] == "implemented"]
    stubbed = [p for p in payload_pairs if p["status"] == "stubbed"]
    registry_only = [p for p in payload_pairs if p["status"] == "in_registry_only"]

    return {
        "ok": True,
        "swmf_root_resolved": root.swmf_root_resolved,
        "source_path": str(source),
        "pairs": payload_pairs,
        "count": len(payload_pairs),
        "summary": {
            "implemented": len(implemented),
            "stubbed": len(stubbed),
            "in_registry_only": len(registry_only),
        },
        "authority_note": (
            "status field distinguishes registry entries from implemented couplings. "
            "Stubbed couplings call CON_stop in the coupler subroutine and are NOT operational."
        ),
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
