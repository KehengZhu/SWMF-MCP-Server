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

from .resources import catalog_reference, coupling_info, examples, idl_reference, param_schema, source_knowledge
from .tools import configure, debug_protocol, knowledge, param

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("swmf-mcp")

app = FastMCP("swmf-prototype", json_response=True)

# Register tool modules by workflow domain.
configure.register(app)
param.register(app)
debug_protocol.register(app)
knowledge.register(app)

# Register MCP resources.
catalog_reference.register(app)
param_schema.register(app)
examples.register(app)
coupling_info.register(app)
idl_reference.register(app)
source_knowledge.register(app)

# Primary app alias used by callers/tests.
mcp = app

# Convenience exports for integration tests and scripts.
swmf_show_config = configure.swmf_show_config
swmf_explain_param = param.swmf_explain_param
swmf_validate_param = param.swmf_validate_param
swmf_run_testparam = param.swmf_run_testparam
swmf_validate_external_inputs = param.swmf_validate_external_inputs
swmf_collect_param_context = debug_protocol.swmf_collect_param_context
swmf_resolve_param_includes = debug_protocol.swmf_resolve_param_includes
swmf_extract_component_map = debug_protocol.swmf_extract_component_map
swmf_collect_build_context = debug_protocol.swmf_collect_build_context
swmf_collect_run_context = debug_protocol.swmf_collect_run_context
swmf_extract_first_error = debug_protocol.swmf_extract_first_error
swmf_extract_stacktrace = debug_protocol.swmf_extract_stacktrace
swmf_collect_source_context = debug_protocol.swmf_collect_source_context
swmf_collect_invariant_context = debug_protocol.swmf_collect_invariant_context
swmf_compare_run_artifacts = debug_protocol.swmf_compare_run_artifacts
swmf_search_source = knowledge.swmf_search_source


def main() -> None:
    logger.info("Starting SWMF MCP prototype server on stdio")
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
