from __future__ import annotations

from typing import Any

from ..catalog import get_source_catalog
from ..core.swmf_root import resolve_swmf_root
from ..tools.retrieve import find_param_command, get_component_versions, list_available_components, trace_param_command


def _load_catalog(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> tuple[dict[str, Any] | None, Any | None]:
    root = resolve_swmf_root(swmf_root=swmf_root, run_dir=run_dir)
    if not root.ok:
        return {
            "ok": False,
            "error_code": "SWMF_ROOT_RESOLUTION_FAILED",
            "message": root.message,
            "resolution_notes": root.resolution_notes,
        }, None

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None or catalog is None:
        return catalog_error or {"ok": False, "message": "Failed to load source catalog."}, None

    return None, catalog


def get_components_resource(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _load_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {"ok": False, "message": "Catalog unavailable."}
    return list_available_components(catalog)


def get_component_resource(
    component: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _load_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {"ok": False, "message": "Catalog unavailable."}
    return get_component_versions(catalog, component=component)


def get_param_command_resource(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _load_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {"ok": False, "message": "Catalog unavailable."}
    return find_param_command(catalog, name=name)


def get_param_trace_resource(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _load_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {"ok": False, "message": "Catalog unavailable."}
    return trace_param_command(catalog, name=name)


def register(app: Any) -> None:
    if not hasattr(app, "resource"):
        return

    @app.resource(
        "swmf://components",
        name="swmf_components",
        description="List SWMF components discovered from authoritative PARAM.XML catalogs.",
        mime_type="application/json",
    )
    def components_resource() -> dict[str, Any]:
        return get_components_resource()

    @app.resource(
        "swmf://component/{component}",
        name="swmf_component",
        description="Return available versions for one SWMF component from authoritative PARAM.XML catalogs.",
        mime_type="application/json",
    )
    def component_resource(component: str) -> dict[str, Any]:
        return get_component_resource(component)

    @app.resource(
        "swmf://param-command/{name}",
        name="swmf_param_command",
        description="Return authoritative PARAM command definitions and metadata for a command name.",
        mime_type="application/json",
    )
    def param_command_resource(name: str) -> dict[str, Any]:
        return get_param_command_resource(name)

    @app.resource(
        "swmf://param-trace/{name}",
        name="swmf_param_trace",
        description="Trace a PARAM command to authoritative definitions and example PARAM usage files.",
        mime_type="application/json",
    )
    def param_trace_resource(name: str) -> dict[str, Any]:
        return get_param_trace_resource(name)