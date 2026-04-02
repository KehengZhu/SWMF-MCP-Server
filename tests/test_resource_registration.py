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
    assert "swmf://idl/procedures" in resource_uris

    assert "swmf://param-schema/{component}" in template_uris
    assert "swmf://examples/{name}" in template_uris
    assert "swmf://idl/{procedure}" in template_uris
