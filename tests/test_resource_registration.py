from __future__ import annotations

import asyncio
from typing import Any

from swmf_mcp_server.server import app


def _normalize_resources(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    resources = getattr(payload, "resources", None)
    return list(resources or [])


def _normalize_templates(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    templates = getattr(payload, "resourceTemplates", None)
    if templates is None:
        templates = getattr(payload, "resource_templates", None)
    return list(templates or [])


def _normalize_tools(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    tools = getattr(payload, "tools", None)
    return list(tools or [])


def test_server_registers_only_minimal_public_tools() -> None:
    app_runtime: Any = app
    tool_payload = asyncio.run(app_runtime.list_tools())
    tool_names = {str(getattr(item, "name", "")) for item in _normalize_tools(tool_payload)}

    expected = {
        "swmf_show_config",
        "swmf_explain_param",
        "swmf_validate_param",
        "swmf_run_testparam",
        "swmf_validate_external_inputs",
        "swmf_collect_param_context",
        "swmf_resolve_param_includes",
        "swmf_extract_component_map",
        "swmf_collect_build_context",
        "swmf_collect_run_context",
        "swmf_extract_first_error",
        "swmf_extract_stacktrace",
        "swmf_collect_source_context",
        "swmf_collect_invariant_context",
        "swmf_compare_run_artifacts",
        "swmf_search_source",
    }

    assert tool_names == expected
    assert not any(name.startswith(("swmf_prepare_", "swmf_plan_", "swmf_generate_", "swmf_diagnose_")) for name in tool_names)


def test_server_registers_mcp_resources_and_templates() -> None:
    app_runtime: Any = app
    resource_payload = asyncio.run(app_runtime.list_resources())
    template_payload = asyncio.run(app_runtime.list_resource_templates())

    resource_uris = {str(getattr(item, "uri", "")) for item in _normalize_resources(resource_payload)}
    template_uris = {
        str(getattr(item, "uriTemplate", getattr(item, "uri_template", "")))
        for item in _normalize_templates(template_payload)
    }

    assert "swmf://coupling-pairs" in resource_uris
    assert "swmf://components" in resource_uris
    assert "swmf://idl/procedures" in resource_uris
    assert "swmf://knowledge/index-status" in resource_uris

    assert "swmf://component/{component}" in template_uris
    assert "swmf://param-command/{name}" in template_uris
    assert "swmf://param-trace/{name}" in template_uris
    assert "swmf://param-schema/{component}" in template_uris
    assert "swmf://examples/{name}" in template_uris
    assert "swmf://idl/{procedure}" in template_uris
