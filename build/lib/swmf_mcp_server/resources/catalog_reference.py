from __future__ import annotations

from typing import Any

from ..reference.service import (
    swmf_find_param_command,
    swmf_get_component_versions,
    swmf_list_available_components,
    swmf_trace_param_command,
)


def get_components_resource(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    return swmf_list_available_components(
        swmf_root=swmf_root,
        run_dir=run_dir,
        force_refresh=force_refresh,
    )


def get_component_resource(
    component: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    return swmf_get_component_versions(
        component=component,
        swmf_root=swmf_root,
        run_dir=run_dir,
        force_refresh=force_refresh,
    )


def get_param_command_resource(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    return swmf_find_param_command(
        name=name,
        swmf_root=swmf_root,
        run_dir=run_dir,
        force_refresh=force_refresh,
    )


def get_param_trace_resource(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    return swmf_trace_param_command(
        name=name,
        swmf_root=swmf_root,
        run_dir=run_dir,
        force_refresh=force_refresh,
    )


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