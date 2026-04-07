from __future__ import annotations

import logging
import sys
from typing import Any, Callable

try:
    from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - fallback for environments without mcp installed
    class FastMCP:  # type: ignore[no-redef]
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                return func

            return _decorator

        def resource(self, *_args: Any, **_kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
            def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
                return func

            return _decorator

        def run(self, *_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError("mcp package is required to run the MCP server.")

from .resources import coupling_info, examples, idl_reference, param_schema
from .tools import build_run, configure, diagnose, idl, param, postprocess, retrieve, solar_campaign

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("swmf-mcp")

app = FastMCP("swmf-prototype", json_response=True)

# Register tool modules by workflow domain.
configure.register(app)
diagnose.register(app)
param.register(app)
build_run.register(app)
postprocess.register(app)
retrieve.register(app)
idl.register(app)
solar_campaign.register(app)

# Register MCP resources.
param_schema.register(app)
examples.register(app)
coupling_info.register(app)
idl_reference.register(app)

# Primary app alias used by callers/tests.
mcp = app

# Convenience exports for integration tests and scripts.
swmf_explain_param = param.swmf_explain_param
swmf_validate_param = param.swmf_validate_param
swmf_run_testparam = param.swmf_run_testparam
swmf_prepare_build = build_run.swmf_prepare_build
swmf_prepare_run = build_run.swmf_prepare_run
swmf_prepare_idl_workflow = idl.swmf_prepare_idl_workflow
swmf_list_idl_procedures = idl.swmf_list_idl_procedures
swmf_explain_idl_procedure = idl.swmf_explain_idl_procedure
swmf_generate_idl_script = idl.swmf_generate_idl_script
swmf_run_idl_batch = idl.swmf_run_idl_batch
swmf_prepare_component_config = build_run.swmf_prepare_component_config
swmf_detect_setup_commands = build_run.swmf_detect_setup_commands
swmf_apply_setup_commands = build_run.swmf_apply_setup_commands
swmf_infer_job_layout = build_run.swmf_infer_job_layout
swmf_inspect_fits_magnetogram = idl.swmf_inspect_fits_magnetogram
swmf_generate_param_from_template = param.swmf_generate_param_from_template
swmf_prepare_sc_quickrun_from_magnetogram = solar_campaign.swmf_prepare_solar_quickrun_from_magnetogram
swmf_validate_external_inputs = param.swmf_validate_external_inputs
swmf_explain_component_config_fix = build_run.swmf_explain_component_config_fix
swmf_list_available_components = retrieve.swmf_list_available_components
swmf_find_param_command = retrieve.swmf_find_param_command
swmf_get_component_versions = retrieve.swmf_get_component_versions
swmf_find_example_params = retrieve.swmf_find_example_params
swmf_trace_param_command = retrieve.swmf_trace_param_command
swmf_diagnose_param = param.swmf_diagnose_param
swmf_diagnose_error = diagnose.swmf_diagnose_error
swmf_plan_restart_from_background = postprocess.swmf_plan_restart_from_background
swmf_parse_solar_event_list = solar_campaign.swmf_parse_solar_event_list
swmf_plan_solar_campaign = solar_campaign.swmf_plan_solar_campaign


def main() -> None:
    logger.info("Starting SWMF MCP prototype server on stdio")
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
