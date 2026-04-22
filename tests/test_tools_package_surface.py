from __future__ import annotations

import swmf_mcp_server.tools as tools


def test_tools_package_exports_only_active_public_modules() -> None:
    assert tools.__all__ == [
        "catalog",
        "configure",
        "debug_protocol",
        "knowledge",
        "param",
        "reference",
    ]


def test_tools_package_does_not_advertise_legacy_workflow_modules() -> None:
    for module_name in [
        "build_run",
        "diagnose",
        "idl",
        "lookup",
        "postprocess",
        "retrieve",
        "solar_campaign",
    ]:
        assert module_name not in tools.__all__