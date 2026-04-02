from __future__ import annotations

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


def get_param_schema_resource(component: str) -> dict[str, Any]:
    error, catalog = _load_catalog()
    if error is not None or catalog is None:
        return error or {"ok": False, "message": "Catalog unavailable."}

    target = component.strip().upper()
    commands: list[dict[str, Any]] = []
    for _, entries in sorted(catalog.commands.items()):
        for item in entries:
            if target == "ALL" or (item.component or "CON") == target:
                commands.append(
                    {
                        "name": item.name,
                        "normalized": item.normalized,
                        "component": item.component,
                        "description": item.description,
                        "defaults": item.defaults,
                        "allowed_values": item.allowed_values,
                        "ranges": item.ranges,
                        "source_path": item.source_path,
                    }
                )

    return {
        "ok": True,
        "component": target,
        "count": len(commands),
        "commands": commands,
        "swmf_root_resolved": catalog.swmf_root,
    }


def register(app: Any) -> None:
    if not hasattr(app, "resource"):
        return

    @app.resource("swmf://param-schema/{component}")
    def _param_schema_resource(component: str) -> dict[str, Any]:
        return get_param_schema_resource(component)
