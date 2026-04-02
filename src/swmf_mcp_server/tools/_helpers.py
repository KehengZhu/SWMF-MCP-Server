from __future__ import annotations

from typing import Any

from ..core.errors import resolution_failure_payload
from ..core.models import SwmfRootResolution
from ..core.swmf_root import resolve_swmf_root


def resolve_root_or_failure(
    swmf_root: str | None,
    run_dir: str | None,
) -> tuple[dict[str, Any] | None, SwmfRootResolution | None]:
    root = resolve_swmf_root(swmf_root=swmf_root, run_dir=run_dir)
    if not root.ok:
        return resolution_failure_payload(root.message or "Could not resolve SWMF root.", root.resolution_notes), None
    return None, root


def with_root(payload: dict[str, Any], root: SwmfRootResolution) -> dict[str, Any]:
    payload.setdefault("swmf_root_resolved", root.swmf_root_resolved)
    payload.setdefault("resolution_notes", root.resolution_notes)
    return payload
