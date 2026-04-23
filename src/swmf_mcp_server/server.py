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

        def run(self, *_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError("mcp package is required to run the MCP server.")

from .core.swmf_root import resolve_swmf_root
from .knowledge import service as ks
from .tools import get_context, get_evidence, inspect_artifact, compare_artifacts

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("swmf-mcp")

app = FastMCP("swmf-prototype", json_response=True)

# Phase 3 v2 public API tools (primary agent-facing surface).
get_context.register(app)
get_evidence.register(app)
inspect_artifact.register(app)
compare_artifacts.register(app)

# Primary app alias used by callers/tests.
mcp = app


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
