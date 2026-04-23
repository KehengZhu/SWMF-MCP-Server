"""Public API tool: compare_artifacts.

Purpose
-------
Compare two local SWMF artifacts and return structured differences.
Supports PARAM files, run outputs, logs, and generated artifacts.
Returns a diff summary, evidence from both sides, and provenance.

Internal backends (hidden from caller)
---------------------------------------
- param diff (structured PARAM.in comparison)
- log diff (side-by-side error/warning extraction)
- run directory diff (file inventory, output comparison)
- text diff (generic fallback)

Output contract
---------------
{
  "summary": str,
  "differences": list[DiffItem],
  "evidence": list[EvidenceItem],
  "provenance": {"left": str, "right": str, "comparison_type": str},
  "uncertainty": {"known_unknowns": list[str]}
}

DiffItem shape
--------------
{
  "kind": "added" | "removed" | "changed" | "structural",
  "location": str,
  "left_value": str | None,
  "right_value": str | None,
  "description": str
}

EvidenceItem shape
------------------
{
  "path": str,
  "snippet": str,
  "score": float | None
}

Example request (two PARAM.in files)
--------------------------------------
{
  "left": "run_baseline/PARAM.in",
  "right": "run_modified/PARAM.in",
  "comparison_type": "param",
  "question": "what changed between the two runs?"
}

Example request (two logs)
---------------------------
{
  "left": "run_baseline/log.stdout",
  "right": "run_modified/log.stdout",
  "comparison_type": "log"
}

Example response
----------------
{
  "summary": "2 structural differences found between PARAM.in files.",
  "differences": [
    {
      "kind": "changed",
      "location": "#DTCOUPLE",
      "left_value": "10.0",
      "right_value": "5.0",
      "description": "DtCouple value changed"
    }
  ],
  "evidence": [
    {"path": "run_baseline/PARAM.in", "snippet": "#DTCOUPLE\\n10.0 ...", "score": null},
    {"path": "run_modified/PARAM.in",  "snippet": "#DTCOUPLE\\n5.0 ...",  "score": null}
  ],
  "provenance": {
    "left": "run_baseline/PARAM.in",
    "right": "run_modified/PARAM.in",
    "comparison_type": "param"
  },
  "uncertainty": {"known_unknowns": ["semantic impact not evaluated"]}
}

Field semantics
---------------
left             : Required. Path to the left (baseline) artifact.
right            : Required. Path to the right (modified) artifact.
comparison_type  : Optional. Hint for which diff strategy to use.
                   One of "param", "log", "run_dir", "result", "text".
                   Inferred from file extension if omitted.
question         : Optional. Freeform question to focus the comparison.
swmf_root        : Optional explicit SWMF source root path.
run_dir          : Optional run directory used for root resolution.
"""

from __future__ import annotations

import difflib
from pathlib import Path
from typing import Any

from ._helpers import resolve_root_or_failure, with_root
from .debug_protocol import _extract_first_error_payload, _stable_file_hash
from ..core.common import read_text_file
from ..parsing.param_parser import parse_param_text

_VALID_COMPARISON_TYPES = frozenset({"param", "log", "run_dir", "result", "text"})

_EXTENSION_TYPE_MAP: dict[str, str] = {
    ".in": "param",
    ".xml": "text",
    ".log": "log",
    ".out": "log",
    ".stdout": "log",
    ".stderr": "log",
}


def _infer_comparison_type(left: str, right: str) -> str:
    left_ext = Path(left).suffix.lower()
    right_ext = Path(right).suffix.lower()
    if left_ext in _EXTENSION_TYPE_MAP:
        return _EXTENSION_TYPE_MAP[left_ext]
    if right_ext in _EXTENSION_TYPE_MAP:
        return _EXTENSION_TYPE_MAP[right_ext]
    if Path(left).is_dir() or Path(right).is_dir():
        return "run_dir"
    return "text"


def _diff_text_files(
    left_path: Path,
    right_path: Path,
    max_diff_lines: int = 80,
) -> tuple[list[dict[str, Any]], bool]:
    """Return (DiffItem list, changed_flag) from a unified diff."""
    left_text = read_text_file(left_path)
    right_text = read_text_file(right_path)
    diff_lines = list(
        difflib.unified_diff(
            left_text.splitlines(),
            right_text.splitlines(),
            fromfile=str(left_path),
            tofile=str(right_path),
            lineterm="",
            n=2,
        )
    )
    changed = left_text != right_text
    differences: list[dict[str, Any]] = []
    if diff_lines:
        differences.append({
            "kind": "unified_diff",
            "location": f"{left_path.name} vs {right_path.name}",
            "left_value": str(left_path),
            "right_value": str(right_path),
            "description": f"{len(diff_lines)} diff line(s)",
            "diff_lines": diff_lines[:max_diff_lines],
        })
    return differences, changed


def _diff_dirs(
    left_path: Path,
    right_path: Path,
    max_files: int = 300,
) -> tuple[list[dict[str, Any]], bool]:
    """Return (DiffItem list, changed_flag) for directory comparison."""
    def scan(p: Path) -> set[str]:
        items: set[str] = set()
        for entry in p.rglob("*"):
            if len(items) >= max_files:
                break
            if entry.is_file():
                try:
                    items.add(str(entry.resolve().relative_to(p.resolve())))
                except ValueError:
                    pass
        return items

    left_files = scan(left_path)
    right_files = scan(right_path)
    only_left = sorted(left_files - right_files)
    only_right = sorted(right_files - left_files)
    changed = bool(only_left or only_right)

    differences: list[dict[str, Any]] = []
    if only_left:
        differences.append({
            "kind": "files_only_in_left",
            "location": str(left_path),
            "left_value": only_left,
            "right_value": [],
            "description": f"{len(only_left)} file(s) only in left directory",
        })
    if only_right:
        differences.append({
            "kind": "files_only_in_right",
            "location": str(right_path),
            "left_value": [],
            "right_value": only_right,
            "description": f"{len(only_right)} file(s) only in right directory",
        })
    if not differences:
        differences.append({
            "kind": "identical",
            "location": "directories",
            "left_value": str(left_path),
            "right_value": str(right_path),
            "description": f"Directory contents identical ({len(left_files & right_files)} files).",
        })
    return differences, changed


def _diff_logs(
    left_path: Path,
    right_path: Path,
) -> tuple[list[dict[str, Any]], bool]:
    """Compare two log files: first error comparison + unified diff snippet."""
    left_text = read_text_file(left_path)
    right_text = read_text_file(right_path)
    left_err = _extract_first_error_payload(left_text)
    right_err = _extract_first_error_payload(right_text)
    differences: list[dict[str, Any]] = []

    if left_err.get("found") or right_err.get("found"):
        differences.append({
            "kind": "first_error_comparison",
            "location": "log comparison",
            "left_value": left_err.get("line") if left_err.get("found") else None,
            "right_value": right_err.get("line") if right_err.get("found") else None,
            "description": "First error lines in left vs right logs.",
        })

    text_diffs, changed = _diff_text_files(left_path, right_path, max_diff_lines=40)
    differences.extend(text_diffs)
    return differences, (left_text != right_text)


def _diff_params(
    left_path: Path,
    right_path: Path,
) -> tuple[list[dict[str, Any]], bool]:
    """Compare two PARAM.in files at section level, then unified diff."""
    left_text = read_text_file(left_path)
    right_text = read_text_file(right_path)
    left_parsed = parse_param_text(left_text)
    right_parsed = parse_param_text(right_text)

    left_names = [s.name for s in left_parsed.sections] if hasattr(left_parsed, "sections") else [s.name for s in left_parsed.sessions]
    right_names = [s.name for s in right_parsed.sections] if hasattr(right_parsed, "sections") else [s.name for s in right_parsed.sessions]

    differences: list[dict[str, Any]] = []
    if left_names != right_names:
        differences.append({
            "kind": "section_names",
            "location": "PARAM.in sections",
            "left_value": left_names,
            "right_value": right_names,
            "description": "Section/session names differ between the two PARAM.in files.",
        })

    text_diffs, changed = _diff_text_files(left_path, right_path)
    differences.extend(text_diffs)
    return differences, (left_text != right_text)


def compare_artifacts(
    left: str,
    right: str,
    comparison_type: str | None = None,
    question: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Compare two local SWMF artifacts and return structured differences.

    Use for comparing two PARAM files, two run outputs, two logs, or two
    generated artifacts. Returns a diff summary and evidence from both sides.
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    if comparison_type and comparison_type in _VALID_COMPARISON_TYPES:
        resolved_type = comparison_type
    else:
        resolved_type = _infer_comparison_type(left, right)

    left_path = Path(left)
    right_path = Path(right)

    # Existence checks
    missing: list[str] = []
    if not left_path.exists():
        missing.append(left)
    if not right_path.exists():
        missing.append(right)
    if missing:
        payload: dict[str, Any] = {
            "ok": False,
            "hard_error": True,
            "left": left,
            "right": right,
            "comparison_type": resolved_type,
            "question": question or "",
            "summary": f"Artifact(s) not found: {', '.join(missing)}",
            "differences": [],
            "evidence": [],
            "provenance": {"left": left, "right": right, "comparison_type": resolved_type},
            "uncertainty": {"known_unknowns": ["Paths provided do not exist."]},
        }
        return with_root(payload, root)

    # Route to comparison strategy
    differences: list[dict[str, Any]] = []
    changed = False

    try:
        if resolved_type == "run_dir":
            differences, changed = _diff_dirs(left_path, right_path)
        elif resolved_type == "log":
            differences, changed = _diff_logs(left_path, right_path)
        elif resolved_type == "param":
            differences, changed = _diff_params(left_path, right_path)
        else:  # "text", "result", or fallback
            if left_path.is_dir() and right_path.is_dir():
                differences, changed = _diff_dirs(left_path, right_path)
            else:
                differences, changed = _diff_text_files(left_path, right_path)
    except Exception as exc:
        differences = [{"kind": "error", "location": "comparison", "description": str(exc)}]
        changed = True

    n_diffs = len([d for d in differences if d.get("kind") not in ("identical",)])
    if not changed:
        summary = f"Artifacts are identical (comparison_type='{resolved_type}')."
    else:
        summary = f"{n_diffs} difference(s) found between left and right artifacts ({resolved_type})."

    payload = {
        "ok": True,
        "left": left,
        "right": right,
        "comparison_type": resolved_type,
        "question": question or "",
        "summary": summary,
        "differences": differences,
        "evidence": [],
        "provenance": {"left": left, "right": right, "comparison_type": resolved_type},
        "uncertainty": {
            "known_unknowns": [
                "Semantic impact of differences not evaluated.",
                "Only static diff performed; no runtime context consulted.",
            ]
        },
    }
    return with_root(payload, root)


def register(app: Any) -> None:
    app.tool(
        description=(
            "Compare two local SWMF artifacts and return structured differences. "
            "Supports PARAM.in files, run outputs, logs, and generated artifacts. "
            "comparison_type must be one of: 'param', 'log', 'run_dir', 'result', 'text'. "
            "If omitted, the type is inferred from file extensions."
        )
    )(compare_artifacts)
