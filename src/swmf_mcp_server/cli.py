"""Local command-line surface for the SWMF AI tools.

This is the agent-facing interface that replaces the MCP server. Each
subcommand maps directly to one of the four tool functions (plus index
management) and prints the tool's result dict as JSON to stdout.

Usage (invoked by skills via Bash)::

    swmf get-context  --question "How does GM couple to IE?" --task-type architecture
    swmf get-evidence --query DoCoupleGMIE --mode keyword --goal "code grounding"
    swmf inspect      --type param --path PARAM.in --check-rules
    swmf compare      --left a/PARAM.in --right b/PARAM.in
    swmf index        build|refresh|status

Conventions
-----------
* Output: the tool's result dict is printed to stdout as indented JSON.
* Exit code: 0 on success; 1 when the result reports ``ok: False`` or
  ``hard_error: True`` (e.g. SWMF root could not be resolved). This lets a
  skill detect failure without parsing the payload.
* Root resolution: every subcommand accepts ``--swmf-root`` / ``--run-dir``;
  the ``SWMF_ROOT`` environment variable and the usual heuristics still apply,
  so those flags are normally unnecessary.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .core.errors import resolution_failure_payload
from .core.swmf_root import resolve_swmf_root
from .knowledge import service as ks
from .tools import compare_artifacts, get_context, get_evidence, inspect_artifact


def _emit(result: dict[str, Any]) -> int:
    """Print a tool result as JSON and return the process exit code."""
    print(json.dumps(result, indent=2, default=str))
    if not isinstance(result, dict):
        return 0
    ok = result.get("ok", True)
    hard_error = result.get("hard_error", False)
    return 0 if (ok and not hard_error) else 1


# --------------------------------------------------------------------------- #
# Tool subcommands
# --------------------------------------------------------------------------- #
def _cmd_get_context(args: argparse.Namespace) -> int:
    return _emit(
        get_context.get_context(
            question=args.question,
            scope=args.scope,
            task_type=args.task_type,
            detail=args.detail,
            swmf_root=args.swmf_root,
            run_dir=args.run_dir,
        )
    )


def _cmd_get_evidence(args: argparse.Namespace) -> int:
    return _emit(
        get_evidence.get_evidence(
            query=args.query,
            mode=args.mode,
            scope=args.scope,
            top_k=args.top_k,
            goal=args.goal,
            task_type=args.task_type,
            module=args.module,
            swmf_root=args.swmf_root,
            run_dir=args.run_dir,
        )
    )


def _cmd_inspect(args: argparse.Namespace) -> int:
    return _emit(
        inspect_artifact.inspect_artifact(
            artifact_type=args.artifact_type,
            path=args.path,
            question=args.question,
            swmf_root=args.swmf_root,
            run_dir=args.run_dir,
            check_rules=args.check_rules,
            xml_scope=args.xml_scope,
            check_xml_audit=args.check_xml_audit,
        )
    )


def _cmd_compare(args: argparse.Namespace) -> int:
    return _emit(
        compare_artifacts.compare_artifacts(
            left=args.left,
            right=args.right,
            comparison_type=args.comparison_type,
            question=args.question,
            swmf_root=args.swmf_root,
            run_dir=args.run_dir,
        )
    )


# --------------------------------------------------------------------------- #
# Index management subcommands
# --------------------------------------------------------------------------- #
def _resolve_root_for_index(args: argparse.Namespace) -> tuple[dict[str, Any] | None, str | None]:
    resolved = resolve_swmf_root(swmf_root=args.swmf_root, run_dir=getattr(args, "run_dir", None))
    if not resolved.ok or not resolved.swmf_root_resolved:
        failure = resolution_failure_payload(
            resolved.message or "Could not resolve SWMF root.",
            resolved.resolution_notes,
        )
        return failure, None
    return None, resolved.swmf_root_resolved


def _cmd_index(args: argparse.Namespace) -> int:
    failure, root = _resolve_root_for_index(args)
    if failure is not None or root is None:
        return _emit(failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."})

    action = args.index_action
    if action == "status":
        status = ks.get_index_status(root)
    elif action == "refresh":
        status = ks.refresh_index(
            root,
            swmfsolar_root=args.swmfsolar_root,
            mcp_repo_root=args.mcp_repo_root,
        )
    elif action == "build":
        status = ks.build_index(
            root,
            force=args.force,
            swmfsolar_root=args.swmfsolar_root,
            mcp_repo_root=args.mcp_repo_root,
        )
    else:  # pragma: no cover - argparse enforces choices
        return _emit({"ok": False, "hard_error": True, "message": f"Unknown index action: {action}"})

    payload = ks.status_as_payload(status)
    # A stale index after a build/refresh is a failure; for status it is informational.
    if action != "status" and payload.get("is_stale"):
        payload.setdefault("hard_error", True)
    return _emit(payload)


# --------------------------------------------------------------------------- #
# Argument parser
# --------------------------------------------------------------------------- #
def _add_root_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--swmf-root", help="Explicit SWMF source root path.")
    parser.add_argument("--run-dir", help="Run directory hint used for root resolution.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="swmf",
        description="Local CLI surface for SWMF AI tools (replaces the MCP server).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # get-context
    p = sub.add_parser("get-context", help="Compact repo/task orientation for a question.")
    p.add_argument("--question", required=True, help="The question or topic to orient around.")
    p.add_argument("--scope", nargs="*", help="SWMF component IDs to restrict orientation (e.g. GM IE).")
    p.add_argument(
        "--task-type",
        choices=["architecture", "debug", "lookup", "workflow", "compare"],
        help="Backend router hint (default architecture).",
    )
    p.add_argument("--detail", choices=["brief", "normal", "deep"], help="Verbosity (default normal).")
    _add_root_args(p)
    p.set_defaults(func=_cmd_get_context)

    # get-evidence
    p = sub.add_parser("get-evidence", help="Symbol/param/file lookup and code grounding.")
    p.add_argument("--query", required=True, help="The search query.")
    p.add_argument("--mode", help="Search mode (keyword).")
    p.add_argument("--scope", nargs="*", help="SWMF component IDs to restrict the search.")
    p.add_argument("--top-k", type=int, help="Max evidence items to return.")
    p.add_argument("--goal", help="Free-text goal describing why evidence is needed.")
    p.add_argument("--task-type", help="Task-type hint for the backend router.")
    p.add_argument("--module", help="Restrict evidence to a specific module/component.")
    _add_root_args(p)
    p.set_defaults(func=_cmd_get_evidence)

    # inspect
    p = sub.add_parser("inspect", help="Inspect one local SWMF artifact deeply.")
    p.add_argument(
        "--type",
        "--artifact-type",
        dest="artifact_type",
        required=True,
        help="log|param|xml|run_dir|build_output|result|jobscript|magnetogram|ccmc_spec|paper_spec (runlog=log alias).",
    )
    p.add_argument("--path", required=True, help="Path to the artifact.")
    p.add_argument("--question", help="Optional focusing question for the inspector.")
    p.add_argument("--check-rules", action="store_true", help="With --type param, evaluate physical_constraints.yaml.")
    p.add_argument("--xml-scope", help="e.g. commandgroup:<name> — the PARAM-authoring channel.")
    p.add_argument("--check-xml-audit", action="store_true", help="With --type param, run the XML audit gate.")
    _add_root_args(p)
    p.set_defaults(func=_cmd_inspect)

    # compare
    p = sub.add_parser("compare", help="Deterministic diff between two artifacts.")
    p.add_argument("--left", required=True, help="Left artifact path.")
    p.add_argument("--right", required=True, help="Right artifact path.")
    p.add_argument("--comparison-type", help="Optional comparison-type hint.")
    p.add_argument("--question", help="Optional focusing question.")
    _add_root_args(p)
    p.set_defaults(func=_cmd_compare)

    # index
    p = sub.add_parser("index", help="Build, refresh, or report status of the knowledge index.")
    isub = p.add_subparsers(dest="index_action", required=True)
    for action, helptext in (
        ("build", "Build the knowledge index (use --force to rebuild from scratch)."),
        ("refresh", "Refresh the knowledge index incrementally."),
        ("status", "Report knowledge index status without modifying it."),
    ):
        ip = isub.add_parser(action, help=helptext)
        _add_root_args(ip)
        if action in ("build", "refresh"):
            ip.add_argument("--swmfsolar-root", help="Optional SWMFSOLAR root to co-index.")
            ip.add_argument("--mcp-repo-root", help="Optional repo root to co-index.")
        if action == "build":
            ip.add_argument("--force", action="store_true", help="Force a full rebuild.")
        ip.set_defaults(func=_cmd_index)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
