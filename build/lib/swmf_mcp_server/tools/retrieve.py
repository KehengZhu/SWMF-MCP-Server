from __future__ import annotations

from typing import Any

from ..reference.service import (
    find_example_params,
    find_param_command,
    get_component_versions,
    list_available_components,
    swmf_find_example_params,
    swmf_find_param_command,
    swmf_get_component_versions,
    swmf_list_available_components,
    swmf_trace_param_command,
    trace_param_command,
)


def register(app: Any) -> None:
    app.tool(description="List SWMF components discovered from authoritative PARAM.XML catalogs.")(swmf_list_available_components)
    app.tool(description="Find command definitions and metadata for a PARAM command name.")(swmf_find_param_command)
    app.tool(description="Return available versions for one SWMF component or all components.")(swmf_get_component_versions)
    app.tool(description="Search indexed example PARAM files for matching query text.")(swmf_find_example_params)
    app.tool(description="Trace a PARAM command to definitions and example usages.")(swmf_trace_param_command)
