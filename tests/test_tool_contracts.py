from __future__ import annotations

from swmf_mcp_server.server import (
    swmf_list_build_run_tool_capabilities,
    swmf_list_configure_tool_capabilities,
    swmf_list_idl_tool_capabilities,
    swmf_list_param_tool_capabilities,
    swmf_list_postprocess_tool_capabilities,
    swmf_list_retrieve_tool_capabilities,
)


def test_capabilities_contract_has_idl_workflow_schema() -> None:
    payload = swmf_list_idl_tool_capabilities()

    assert payload["ok"] is True
    assert payload["authority"] == "authoritative"
    assert "tools" in payload

    idl = payload["tools"]["swmf_prepare_idl_workflow"]
    assert "requires_one_of" in idl
    assert idl["requires_one_of"] == ["task", "request"]
    assert "task_enum" in idl
    assert "output_format_enum" in idl
    assert "inputs" in idl
    assert "response_shape" in idl

    expected_keys = {
        "ok",
        "hard_error",
        "authority",
        "source_kind",
        "request",
        "capability",
        "normalized_inputs",
        "inferred",
        "idl_script_filename",
        "idl_script",
        "shell_commands",
        "warnings",
        "assumptions",
    }
    assert expected_keys.issubset(set(idl["response_shape"]))

    resources = payload["resources"]
    assert resources["swmf://param-schema/{component}"]["template"] is True
    assert resources["swmf://examples/{name}"]["template"] is True
    assert resources["swmf://coupling-pairs"]["template"] is False
    assert resources["swmf://idl/procedures"]["template"] is False
    assert resources["swmf://idl/{procedure}"]["template"] is True


def test_domain_capability_endpoints_are_available() -> None:
    payloads = [
        swmf_list_configure_tool_capabilities(),
        swmf_list_param_tool_capabilities(),
        swmf_list_build_run_tool_capabilities(),
        swmf_list_postprocess_tool_capabilities(),
        swmf_list_retrieve_tool_capabilities(),
    ]

    for payload in payloads:
        assert payload["ok"] is True
        assert payload["authority"] == "authoritative"
        assert payload["source_kind"] == "implementation"
        assert payload.get("domain")
        assert payload.get("tools")
