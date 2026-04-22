"""Named MCP tools for reference-domain lookups."""

from .lookup import (
    register,
    swmf_explain_idl_procedure,
    swmf_find_examples,
    swmf_get_component,
    swmf_get_coupling_info,
    swmf_get_param_command,
    swmf_get_param_schema,
    swmf_get_param_trace,
    swmf_list_components,
    swmf_list_idl_procedures,
)

__all__ = [
    "register",
    "swmf_explain_idl_procedure",
    "swmf_find_examples",
    "swmf_get_component",
    "swmf_get_coupling_info",
    "swmf_get_param_command",
    "swmf_get_param_schema",
    "swmf_get_param_trace",
    "swmf_list_components",
    "swmf_list_idl_procedures",
]