from __future__ import annotations

import argparse
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

from .core.swmf_root import resolve_swmf_root
from .knowledge import service as ks
from .tools import catalog, configure, debug_protocol, knowledge, param, reference

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
catalog.register(app)
reference.register(app)
knowledge.register(app)

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
swmf_build_catalog_index = catalog.swmf_build_catalog_index
swmf_refresh_catalog_index = catalog.swmf_refresh_catalog_index
swmf_get_catalog_status = catalog.swmf_get_catalog_status
swmf_search_catalog = catalog.swmf_search_catalog
swmf_lookup_catalog_symbol = catalog.swmf_lookup_catalog_symbol
swmf_list_components = reference.swmf_list_components
swmf_get_component = reference.swmf_get_component
swmf_get_param_command = reference.swmf_get_param_command
swmf_get_param_trace = reference.swmf_get_param_trace
swmf_get_param_schema = reference.swmf_get_param_schema
swmf_find_examples = reference.swmf_find_examples
swmf_get_coupling_info = reference.swmf_get_coupling_info
swmf_list_idl_procedures = reference.swmf_list_idl_procedures
swmf_explain_idl_procedure = reference.swmf_explain_idl_procedure
swmf_build_knowledge_index = knowledge.swmf_build_knowledge_index
swmf_get_knowledge_status = knowledge.swmf_get_knowledge_status
swmf_search_knowledge = knowledge.swmf_search_knowledge
swmf_get_agent_context_pack = knowledge.swmf_get_agent_context_pack


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="swmf-mcp-server",
        description="Run the SWMF MCP prototype server.",
    )
    parser.add_argument(
        "--preindex-knowledge",
        action="store_true",
        help="Prepare the SQLite knowledge index before serving requests.",
    )
    parser.add_argument(
        "--force-rebuild-knowledge",
        action="store_true",
        help="Force a full knowledge-index rebuild when preindexing at startup.",
    )
    parser.add_argument(
        "--swmf-root",
        help="Explicit SWMF source root to use for startup knowledge preindexing.",
    )
    parser.add_argument(
        "--run-dir",
        help="Optional run directory hint used during SWMF root resolution for startup preindexing.",
    )
    parser.add_argument(
        "--swmfsolar-root",
        help="Optional SWMFSOLAR root to co-index during startup preindexing.",
    )
    parser.add_argument(
        "--mcp-repo-root",
        help="Optional MCP repository root to co-index during startup preindexing.",
    )
    return parser.parse_args(argv)


def _maybe_preindex_knowledge(args: argparse.Namespace) -> None:
    if not args.preindex_knowledge:
        return

    resolved = resolve_swmf_root(swmf_root=args.swmf_root, run_dir=args.run_dir)
    if not resolved.ok or not resolved.swmf_root_resolved:
        logger.warning(
            "Skipping startup knowledge preindex: %s",
            resolved.message or "Could not resolve SWMF root.",
        )
        return

    root = resolved.swmf_root_resolved
    try:
        if args.force_rebuild_knowledge:
            status = ks.build_index(
                root,
                force=True,
                swmfsolar_root=args.swmfsolar_root,
                mcp_repo_root=args.mcp_repo_root,
            )
            action = "rebuilt"
        else:
            status = ks.refresh_index(
                root,
                swmfsolar_root=args.swmfsolar_root,
                mcp_repo_root=args.mcp_repo_root,
            )
            action = "prepared"
    except Exception as exc:  # pragma: no cover - defensive logging path
        logger.warning("Startup knowledge preindex failed for %s: %s", root, exc)
        return

    if status.ok and not status.is_stale:
        logger.info(
            "Knowledge index %s at startup for %s (%s symbols across %s files)",
            action,
            root,
            status.symbol_count,
            status.file_count,
        )
        return

    logger.warning(
        "Startup knowledge preindex finished without a ready index for %s: %s",
        root,
        status.message or "index status remained stale",
    )


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    logger.info("Starting SWMF MCP prototype server on stdio")
    _maybe_preindex_knowledge(args)
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
