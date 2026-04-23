"""Private helpers for workflow-oriented evidence discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_TASK_SCRIPT_HINTS: dict[str, set[str]] = {
    "configuration": {"Config.pl"},
    "build": {"Config.pl", "Makefile"},
    "run": {"Scripts/TestParam.pl", "Restart.pl"},
    "analysis": {"PostProc.pl"},
}


def _relative_path(root: Path, candidate: Path) -> str:
    try:
        return str(candidate.resolve().relative_to(root.resolve()))
    except Exception:
        return str(candidate)


def _workflow_kind(candidate: Path) -> str:
    if candidate.name == "Makefile":
        return "makefile_target"
    if candidate.suffix.lower() == ".pl":
        return "script"
    if candidate.suffix.lower() == ".pm":
        return "module"
    return "config_file"


def _workflow_why_relevant(task_type: str, candidate: Path, module: str | None) -> str:
    if module and candidate.name == "Config.pl":
        return f"Component-level configuration for {module}"
    return f"Known {task_type} entrypoint: {candidate.name}"


def discover_workflow_entrypoints(
    swmf_root: str,
    module: str | None,
    task_type: str,
) -> list[dict[str, Any]]:
    """Return evidence items for likely workflow entrypoints."""

    root_path = Path(swmf_root)
    hint_names = _TASK_SCRIPT_HINTS.get(task_type, {"Config.pl"})
    module_upper = module.upper() if module else None
    entrypoints: list[dict[str, Any]] = []
    seen_relative_paths: set[str] = set()

    for candidate_path in root_path.rglob("*"):
        if not candidate_path.is_file():
            continue

        relative_path = _relative_path(root_path, candidate_path)
        if candidate_path.name not in hint_names and relative_path not in hint_names:
            continue

        if module_upper:
            parts = [part.upper() for part in candidate_path.parts]
            if module_upper not in parts:
                continue

        if relative_path in seen_relative_paths:
            continue

        seen_relative_paths.add(relative_path)
        why_relevant = _workflow_why_relevant(task_type, candidate_path, module_upper)
        entrypoints.append(
            {
                "type": "code",
                "path": str(candidate_path.resolve()),
                "snippet": why_relevant,
                "score": 1.0,
                "metadata": {
                    "kind": _workflow_kind(candidate_path),
                    "relative_path": relative_path,
                    "why_relevant": why_relevant,
                },
            }
        )

    return entrypoints[:12]
