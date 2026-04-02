from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any

from ..core.common import resolve_run_dir
from ._helpers import resolve_root_or_failure, with_root


def _resolve_script(run_dir: Path, swmf_root: Path, script_name: str) -> Path:
    local = run_dir / script_name
    if local.is_file():
        return local
    root_level = swmf_root / script_name
    if root_level.is_file():
        return root_level
    scripts_dir = swmf_root / "Scripts" / script_name
    return scripts_dir


def _execute_optional(command: list[str], cwd: Path, execute: bool, timeout_s: int) -> dict[str, Any]:
    if not execute:
        return {
            "ok": True,
            "executed": False,
            "command": " ".join(shlex.quote(part) for part in command),
            "cwd": str(cwd),
        }

    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=max(1, timeout_s),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "executed": True,
            "error_code": "COMMAND_TIMEOUT",
            "message": f"Command timed out after {timeout_s}s.",
            "command": " ".join(shlex.quote(part) for part in command),
            "cwd": str(cwd),
        }
    except OSError as exc:
        return {
            "ok": False,
            "executed": True,
            "error_code": "COMMAND_EXEC_FAILED",
            "message": f"Failed to execute command: {exc}",
            "command": " ".join(shlex.quote(part) for part in command),
            "cwd": str(cwd),
        }

    return {
        "ok": proc.returncode == 0,
        "executed": True,
        "command": " ".join(shlex.quote(part) for part in command),
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def postprocess(
    run_dir: str,
    args: list[str] | None = None,
    swmf_root: str | None = None,
    execute: bool = False,
    timeout_s: int = 600,
) -> dict[str, Any]:
    resolved_run_dir = resolve_run_dir(run_dir)
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    resolved_root = Path(root.swmf_root_resolved or str(Path.cwd())).resolve()
    script = _resolve_script(resolved_run_dir, resolved_root, "PostProc.pl")
    if not script.is_file():
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "POSTPROC_NOT_FOUND",
                "message": f"Could not locate PostProc.pl under run_dir or SWMF root: {script}",
            },
            root,
        )

    command = ["perl", str(script)] + list(args or [])
    payload = _execute_optional(command=command, cwd=resolved_run_dir, execute=execute, timeout_s=timeout_s)
    payload.update(
        {
            "script_path": str(script),
            "run_dir_resolved": str(resolved_run_dir),
            "authority": "authoritative",
            "source_kind": "script",
            "source_paths": [str(script)],
        }
    )
    return with_root(payload, root)


def manage_restart(
    run_dir: str,
    args: list[str] | None = None,
    swmf_root: str | None = None,
    execute: bool = False,
    timeout_s: int = 600,
) -> dict[str, Any]:
    resolved_run_dir = resolve_run_dir(run_dir)
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    resolved_root = Path(root.swmf_root_resolved or str(Path.cwd())).resolve()
    script = _resolve_script(resolved_run_dir, resolved_root, "Restart.pl")
    if not script.is_file():
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "RESTART_SCRIPT_NOT_FOUND",
                "message": f"Could not locate Restart.pl under run_dir or SWMF root: {script}",
            },
            root,
        )

    command = ["perl", str(script)] + list(args or [])
    payload = _execute_optional(command=command, cwd=resolved_run_dir, execute=execute, timeout_s=timeout_s)
    payload.update(
        {
            "script_path": str(script),
            "run_dir_resolved": str(resolved_run_dir),
            "authority": "authoritative",
            "source_kind": "script",
            "source_paths": [str(script)],
        }
    )
    return with_root(payload, root)


def swmf_postprocess(
    run_dir: str,
    args: list[str] | None = None,
    swmf_root: str | None = None,
    execute: bool = False,
    timeout_s: int = 600,
) -> dict[str, Any]:
    return postprocess(
        run_dir=run_dir,
        args=args,
        swmf_root=swmf_root,
        execute=execute,
        timeout_s=timeout_s,
    )


def swmf_manage_restart(
    run_dir: str,
    args: list[str] | None = None,
    swmf_root: str | None = None,
    execute: bool = False,
    timeout_s: int = 600,
) -> dict[str, Any]:
    return manage_restart(
        run_dir=run_dir,
        args=args,
        swmf_root=swmf_root,
        execute=execute,
        timeout_s=timeout_s,
    )


def swmf_list_postprocess_tool_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "hard_error": False,
        "authority": "authoritative",
        "source_kind": "implementation",
        "source_paths": ["src/swmf_mcp_server/tools/postprocess.py"],
        "domain": "postprocess",
        "tools": {
            "swmf_postprocess": {"description": "Run or preview SWMF PostProc.pl in the target run directory."},
            "swmf_manage_restart": {"description": "Run or preview SWMF Restart.pl for restart file management."},
        },
    }


def register(app: Any) -> None:
    app.tool(description="Run or preview SWMF PostProc.pl in the target run directory.")(swmf_postprocess)
    app.tool(description="Run or preview SWMF Restart.pl for restart file management.")(swmf_manage_restart)
    app.tool(description="List MCP tool capability contracts for SWMF postprocess tooling.")(swmf_list_postprocess_tool_capabilities)
