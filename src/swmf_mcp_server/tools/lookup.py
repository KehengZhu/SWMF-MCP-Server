"""Named MCP tools for catalog-backed reference lookups.

Replaces resource URIs (swmf://...) with named tools that MCP clients
can discover and invoke reliably through standard tool routing.

Tools exposed
-------------
swmf_list_components          List SWMF components from PARAM.XML catalogs.
swmf_get_component            Get versions for one SWMF component.
swmf_get_param_command        Look up a PARAM command definition from PARAM.XML.
swmf_get_param_trace          Trace a PARAM command to definitions and examples.
swmf_get_param_schema         Get PARAM schema filtered by component or keyword.
swmf_find_examples            Find example PARAM.in files matching a name.
swmf_get_coupling_info        Get SWMF coupling pair information.
swmf_list_idl_procedures      List indexed IDL procedures with optional category filter.
swmf_explain_idl_procedure    Get signature and details for one IDL procedure.
"""

from __future__ import annotations

from typing import Any

from ..resources.coupling_info import get_coupling_pairs_resource
from ..resources.examples import get_examples_resource
from ..resources.param_schema import get_param_schema_resource
from .idl import swmf_explain_idl_procedure, swmf_list_idl_procedures
from .retrieve import (
    swmf_find_param_command,
    swmf_get_component_versions,
    swmf_list_available_components,
    swmf_trace_param_command,
)


def swmf_list_components(
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """List SWMF components discovered from authoritative PARAM.XML catalogs."""
    return swmf_list_available_components(swmf_root=swmf_root, run_dir=run_dir)


def swmf_get_component(
    component: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Return available versions for one SWMF component from PARAM.XML catalogs."""
    return swmf_get_component_versions(component=component, swmf_root=swmf_root, run_dir=run_dir)


def swmf_get_param_command(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Return authoritative PARAM command definitions and metadata from PARAM.XML."""
    return swmf_find_param_command(name=name, swmf_root=swmf_root, run_dir=run_dir)


def swmf_get_param_trace(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Trace a PARAM command to its authoritative definitions and example PARAM.in files."""
    return swmf_trace_param_command(name=name, swmf_root=swmf_root, run_dir=run_dir)


def swmf_get_param_schema(
    component: str,
) -> dict[str, Any]:
    """Get PARAM.XML schema metadata filtered by component or keyword, with manual doc snippets."""
    return get_param_schema_resource(component)


def swmf_find_examples(
    name: str,
) -> dict[str, Any]:
    """Find indexed SWMF example PARAM.in files matching a name or path fragment."""
    return get_examples_resource(name)


def swmf_get_coupling_info() -> dict[str, Any]:
    """Return SWMF component coupling pairs and implementation status from CON_couple_all.f90."""
    return get_coupling_pairs_resource()


def register(app: Any) -> None:
    app.tool(
        description="List SWMF components discovered from authoritative PARAM.XML catalogs."
    )(swmf_list_components)
    app.tool(
        description="Return available versions for one SWMF component from PARAM.XML catalogs."
    )(swmf_get_component)
    app.tool(
        description="Return authoritative PARAM command definitions and metadata from PARAM.XML."
    )(swmf_get_param_command)
    app.tool(
        description="Trace a PARAM command to its authoritative definitions and example PARAM.in files."
    )(swmf_get_param_trace)
    app.tool(
        description="Get PARAM.XML schema metadata for a component or keyword query, with TeX manual doc snippets."
    )(swmf_get_param_schema)
    app.tool(
        description="Find indexed SWMF example PARAM.in files matching a name or path fragment."
    )(swmf_find_examples)
    app.tool(
        description="Return SWMF component coupling pairs and implementation status from CON_couple_all.f90."
    )(swmf_get_coupling_info)
    app.tool(
        description="List indexed SWMF IDL procedures with optional category filter."
    )(swmf_list_idl_procedures)
    app.tool(
        description="Return signature and details for one indexed SWMF IDL procedure."
    )(swmf_explain_idl_procedure)
