from __future__ import annotations

import os
from pathlib import Path

from .config import SWMF_ROOT_ENV, swmf_root_markers
from .models import SwmfRootResolution


def looks_like_swmf_root(path: Path) -> bool:
    markers = [path / marker for marker in swmf_root_markers()]
    return all(marker.is_file() for marker in markers)


def _dedupe(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    deduped: list[Path] = []
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return deduped


def _candidate_roots_from_run_dir(run_path: Path) -> list[Path]:
    candidates: list[Path] = []
    for parent in [run_path] + list(run_path.parents[:6]):
        candidates.append(parent)
        candidates.append(parent / "SWMF")
    return candidates


def _workspace_symlink_candidates(workspace_root: Path) -> list[Path]:
    candidates: list[Path] = []
    for child in workspace_root.iterdir():
        if child.name.startswith("."):
            continue
        try:
            if child.is_symlink() or child.is_dir():
                candidates.append(child.resolve())
                candidates.append(child.resolve() / "SWMF")
        except OSError:
            continue
    return candidates


def resolve_swmf_root(
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> SwmfRootResolution:
    notes: list[str] = []

    if swmf_root:
        explicit = Path(swmf_root).expanduser().resolve()
        notes.append(f"Checked explicit swmf_root: {explicit}")
        if looks_like_swmf_root(explicit):
            notes.append("Resolved from explicit swmf_root argument.")
            return SwmfRootResolution(True, str(explicit), notes)
        notes.append("Explicit swmf_root did not match SWMF markers.")

    env_root = os.environ.get(SWMF_ROOT_ENV)
    if env_root:
        env_path = Path(env_root).expanduser().resolve()
        notes.append(f"Checked environment {SWMF_ROOT_ENV}: {env_path}")
        if looks_like_swmf_root(env_path):
            notes.append(f"Resolved from {SWMF_ROOT_ENV} environment variable.")
            return SwmfRootResolution(True, str(env_path), notes)
        notes.append(f"{SWMF_ROOT_ENV} did not match SWMF markers.")

    candidates: list[Path] = []
    if run_dir:
        run_path = Path(run_dir).expanduser().resolve()
        notes.append(f"Using run_dir heuristics from: {run_path}")
        candidates.extend(_candidate_roots_from_run_dir(run_path))

    cwd = Path.cwd().resolve()
    workspace_root = Path(__file__).resolve().parents[3]
    candidates.extend([cwd, cwd / "SWMF", workspace_root / "SWMF", workspace_root])

    try:
        candidates.extend(_workspace_symlink_candidates(workspace_root))
    except OSError:
        pass

    for candidate in _dedupe(candidates):
        notes.append(f"Checked heuristic candidate: {candidate}")
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if looks_like_swmf_root(resolved):
            notes.append("Resolved from heuristic search (cwd/workspace/run_dir/symlink-aware).")
            return SwmfRootResolution(True, str(resolved), notes)

    return SwmfRootResolution(False, None, notes, "Could not resolve SWMF source directory.")
