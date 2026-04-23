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
        # v2 public API (primary agent-facing surface)
        "get_context",
        "get_evidence",
        "inspect_artifact",
        "compare_artifacts",
    }

    assert tool_names == expected
    assert not any(name.startswith("swmf_") for name in tool_names)


def test_server_registers_no_mcp_resources() -> None:
    """Resources have been fully replaced by named tools. Assert no URIs are registered."""
    app_runtime: Any = app
    resource_payload = asyncio.run(app_runtime.list_resources())
    template_payload = asyncio.run(app_runtime.list_resource_templates())

    resource_uris = {str(getattr(item, "uri", "")) for item in _normalize_resources(resource_payload)}
    template_uris = {
        str(getattr(item, "uriTemplate", getattr(item, "uri_template", "")))
        for item in _normalize_templates(template_payload)
    }

    assert not resource_uris, f"Unexpected resources registered: {resource_uris}"
    assert not template_uris, f"Unexpected resource templates registered: {template_uris}"
