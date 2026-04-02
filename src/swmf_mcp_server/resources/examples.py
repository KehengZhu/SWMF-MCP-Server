from __future__ import annotations

from pathlib import Path
from typing import Any

from ..catalog import get_source_catalog
from ..core.swmf_root import resolve_swmf_root


def _load_catalog() -> tuple[dict[str, Any] | None, Any | None]:
    root = resolve_swmf_root()
    if not root.ok:
        return {
            "ok": False,
            "error_code": "SWMF_ROOT_RESOLUTION_FAILED",
            "message": root.message,
            "resolution_notes": root.resolution_notes,
        }, None

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=False)
    if catalog_error is not None or catalog is None:
        return catalog_error or {"ok": False, "message": "Failed to load source catalog."}, None

    return None, catalog


def get_examples_resource(name: str) -> dict[str, Any]:
    error, catalog = _load_catalog()
    if error is not None or catalog is None:
        return error or {"ok": False, "message": "Catalog unavailable."}

    query = name.strip().lower()
    templates = catalog.templates

    if query in {"", "all", "*"}:
        matches = templates
    else:
        matches = [path for path in templates if query in Path(path).name.lower() or query in path.lower()]

    return {
        "ok": True,
        "name": name,
        "count": len(matches),
        "examples": matches,
        "swmf_root_resolved": catalog.swmf_root,
    }


def register(app: Any) -> None:
    if not hasattr(app, "resource"):
        return

    @app.resource(
        "swmf://examples/{name}",
        name="swmf_examples",
        description="List indexed SWMF PARAM example files filtered by name.",
        mime_type="application/json",
    )
    def examples_resource(name: str) -> dict[str, Any]:
        return get_examples_resource(name)
