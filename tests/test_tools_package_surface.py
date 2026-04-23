from __future__ import annotations

import swmf_mcp_server.tools as tools


def test_tools_package_exports_only_active_public_modules() -> None:
    assert tools.__all__ == [
        "get_context",
        "get_evidence",
        "get_workflow_guidance",
        "inspect_artifact",
        "compare_artifacts",
    ]


def test_tools_package_does_not_advertise_legacy_workflow_modules() -> None:
    for module_name in [
        "build_run",
        "catalog",
        "configure",
        "debug_protocol",
        "diagnose",
        "idl",
        "knowledge",
        "lookup",
        "param",
        "postprocess",
        "reference",
        "retrieve",
        "solar_campaign",
    ]:
        assert module_name not in tools.__all__
