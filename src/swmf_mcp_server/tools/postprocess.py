from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any

from ..core.common import resolve_run_dir
from ..parsing.job_layout import find_likely_job_scripts, infer_job_layout_from_script
from ._helpers import resolve_root_or_failure, with_root


_ALLOWED_SCHEDULER_HINTS = {"auto", "slurm", "pbs"}
_ALLOWED_RESTART_MODES = {"auto", "framework", "standalone", "a", "f", "s"}


def _resolve_script(run_dir: Path, swmf_root: Path, script_name: str) -> Path:
    local = run_dir / script_name
    if local.is_file():
        return local

    run_dir_candidates = [
        run_dir / "Scripts" / script_name,
        run_dir / "share" / "Scripts" / script_name,
        run_dir / "share" / "scripts" / script_name,
    ]
    for candidate in run_dir_candidates:
        if candidate.is_file():
            return candidate

    discovered: list[Path] = []
    try:
        for candidate in run_dir.rglob(script_name):
            if not candidate.is_file():
                continue
            rel_parts = candidate.resolve().relative_to(run_dir.resolve()).parts
            if len(rel_parts) <= 6:
                discovered.append(candidate.resolve())
    except OSError:
        discovered = []

    if discovered:
        discovered.sort(key=lambda p: (len(p.relative_to(run_dir.resolve()).parts), str(p)))
        return discovered[0]

    root_level = swmf_root / script_name
    if root_level.is_file():
        return root_level
    scripts_dir = swmf_root / "Scripts" / script_name
    if scripts_dir.is_file():
        return scripts_dir
    return swmf_root / "share" / "Scripts" / script_name


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


def _resolve_from_run_dir(path_text: str, run_dir: Path) -> Path:
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = run_dir / path
    return path.resolve()


def _infer_scheduler_for_preview(run_dir: Path) -> str | None:
    candidates = [run_dir / "job.long"]
    candidates.extend(find_likely_job_scripts(run_dir))

    seen: set[Path] = set()
    for path in candidates:
        resolved = path.resolve()
        if resolved in seen or not resolved.is_file():
            continue
        seen.add(resolved)

        if resolved.suffix in {".slurm", ".sbatch"}:
            return "slurm"
        if resolved.suffix in {".pbs"}:
            return "pbs"

        try:
            text = resolved.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "#SBATCH" in text:
            return "slurm"
        if "#PBS" in text:
            return "pbs"

    return None


def _infer_nproc_from_run_dir(run_dir: Path) -> tuple[int | None, dict[str, Any] | None]:
    for script in find_likely_job_scripts(run_dir):
        try:
            script_text = script.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        layout = infer_job_layout_from_script(script_path=script, script_text=script_text)
        nproc = layout.get("swmf_nproc")
        if isinstance(nproc, int) and nproc > 0:
            return nproc, layout
    return None, None


def _normalize_restart_mode(restart_mode: str) -> tuple[str | None, str | None]:
    mode = restart_mode.strip().lower()
    if mode not in _ALLOWED_RESTART_MODES:
        return None, f"Unsupported restart_mode '{restart_mode}'. Use one of: auto, framework, standalone."
    if mode in {"a", "f", "s"}:
        return {"a": "auto", "f": "framework", "s": "standalone"}[mode], None
    return mode, None


def _infer_restart_mode_hint(run_dir: Path) -> str:
    framework_component_dirs = {
        "EE",
        "IE",
        "GM",
        "SC",
        "IH",
        "OH",
        "IM",
        "PC",
        "PS",
        "PT",
        "PW",
        "RB",
        "UA",
        "SP",
    }
    if (run_dir / "RESTART.in").is_file() or (run_dir / "STDOUT").is_dir():
        return "framework"
    if any((run_dir / comp).is_dir() for comp in framework_component_dirs):
        return "framework"
    return "auto"


def plan_restart_from_background(
    run_dir: str,
    background_results_dir: str,
    restart_subdir: str = "RESTART",
    param_path: str | None = None,
    nproc: int | None = None,
    scheduler_hint: str = "auto",
    restart_mode: str = "auto",
    include_restart_check: bool = True,
    verbose: bool = True,
    warn_only: bool = False,
    include_validation_commands: bool = True,
    include_submit_preview: bool = True,
    swmf_root: str | None = None,
) -> dict[str, Any]:
    resolved_run_dir = resolve_run_dir(run_dir)
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    hint = scheduler_hint.strip().lower()
    if hint not in _ALLOWED_SCHEDULER_HINTS:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "INPUT_INVALID",
                "message": f"Unsupported scheduler_hint '{scheduler_hint}'. Use one of: auto, slurm, pbs.",
            },
            root,
        )

    mode_normalized, mode_error = _normalize_restart_mode(restart_mode)
    if mode_error is not None or mode_normalized is None:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "INPUT_INVALID",
                "message": mode_error,
            },
            root,
        )

    resolved_root = Path(root.swmf_root_resolved or str(Path.cwd())).resolve()
    run_dir_exists = resolved_run_dir.is_dir()
    script = _resolve_script(resolved_run_dir, resolved_root, "Restart.pl")
    restart_script_detected = script.is_file()

    resolved_background_dir = _resolve_from_run_dir(background_results_dir, resolved_run_dir)
    resolved_background_restart = (resolved_background_dir / restart_subdir).resolve()
    restart_source_exists = resolved_background_restart.is_dir()

    param_input = param_path if param_path is not None else "PARAM.in"
    resolved_param = _resolve_from_run_dir(param_input, resolved_run_dir)
    param_exists = resolved_param.is_file()

    preflight = {
        "run_dir_exists": run_dir_exists,
        "param_exists": param_exists,
        "restart_source_exists": restart_source_exists,
        "restart_script_detected": restart_script_detected,
    }

    warnings: list[str] = []
    if not run_dir_exists:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "PATH_NOT_FOUND",
                "message": f"run_dir does not exist: {resolved_run_dir}",
                "run_dir_resolved": str(resolved_run_dir),
                "background_restart_resolved": str(resolved_background_restart),
                "preflight_checks": preflight,
                "command_preview": [],
                "command_groups": {"restart_link": [], "validate": [], "submit_preview": []},
                "requires_manual_execution": True,
                "authority": "authoritative",
                "source_kind": "script",
                "source_paths": [str(script)],
                "warnings": warnings,
            },
            root,
        )

    if not restart_script_detected:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "RESTART_SCRIPT_NOT_FOUND",
                "message": f"Could not locate Restart.pl under run_dir or SWMF root: {script}",
                "run_dir_resolved": str(resolved_run_dir),
                "background_restart_resolved": str(resolved_background_restart),
                "preflight_checks": preflight,
                "command_preview": [],
                "command_groups": {"restart_link": [], "validate": [], "submit_preview": []},
                "requires_manual_execution": True,
                "authority": "authoritative",
                "source_kind": "script",
                "source_paths": [str(script)],
                "warnings": warnings,
            },
            root,
        )

    if not restart_source_exists:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "RESTART_SOURCE_NOT_FOUND",
                "message": f"Restart source folder was not found: {resolved_background_restart}",
                "run_dir_resolved": str(resolved_run_dir),
                "background_restart_resolved": str(resolved_background_restart),
                "preflight_checks": preflight,
                "command_preview": [],
                "command_groups": {"restart_link": [], "validate": [], "submit_preview": []},
                "requires_manual_execution": True,
                "authority": "authoritative",
                "source_kind": "script",
                "source_paths": [str(script)],
                "warnings": warnings,
            },
            root,
        )

    restart_mode_effective = mode_normalized
    if restart_mode_effective == "auto":
        restart_mode_effective = _infer_restart_mode_hint(resolved_run_dir)

    restart_base_args: list[str] = ["-i"]
    if verbose:
        restart_base_args.append("-v")
    if warn_only:
        restart_base_args.append("-W")
    if restart_mode_effective != "auto":
        restart_base_args.append(f"-m={restart_mode_effective}")

    restart_check_group: list[str] = []
    if include_restart_check:
        check_args = [*restart_base_args, "-c"]
        restart_check_group.append(
            " ".join(
                [
                    f"perl {shlex.quote(str(script))}",
                    *check_args,
                    shlex.quote(str(resolved_background_restart)),
                ]
            )
        )

    restart_link_group = [
        " ".join(
            [
                f"perl {shlex.quote(str(script))}",
                *restart_base_args,
                shlex.quote(str(resolved_background_restart)),
            ]
        )
    ]

    restart_group = [f"cd {shlex.quote(str(resolved_run_dir))}", *restart_check_group, *restart_link_group]

    validate_group: list[str] = []
    nproc_used = nproc
    job_layout: dict[str, Any] | None = None
    if include_validation_commands:
        if not param_exists:
            warnings.append(f"param_path does not point to a file: {resolved_param}")
        else:
            if nproc_used is None:
                nproc_used, job_layout = _infer_nproc_from_run_dir(resolved_run_dir)

            testparam_script = resolved_root / "Scripts" / "TestParam.pl"
            if not testparam_script.is_file():
                warnings.append(f"Could not locate Scripts/TestParam.pl under SWMF root: {testparam_script}")
            elif nproc_used is None:
                warnings.append("Could not infer nproc from job scripts; using placeholder in validation command.")
                validate_group.append(
                    f"perl {shlex.quote(str(testparam_script))} -n=<YOUR_NPROC> {shlex.quote(str(resolved_param))}"
                )
            else:
                validate_group.append(
                    f"perl {shlex.quote(str(testparam_script))} -n={nproc_used} {shlex.quote(str(resolved_param))}"
                )

    scheduler_resolved = hint
    if hint == "auto":
        scheduler_resolved = _infer_scheduler_for_preview(resolved_run_dir) or "unknown"

    submit_group: list[str] = []
    if include_submit_preview:
        if scheduler_resolved == "slurm":
            submit_group.append("sbatch job.long")
        elif scheduler_resolved == "pbs":
            submit_group.append("qsub job.long")
        else:
            submit_group.append("# submit manually with site scheduler (sbatch job.long or qsub job.long)")
            warnings.append("Could not infer scheduler from run directory; returned a manual submit placeholder.")

    command_preview = [*restart_group, *validate_group, *submit_group]
    payload = {
        "ok": True,
        "hard_error": False,
        "error_code": None,
        "message": "Generated restart/validation/submit preview commands. Nothing was executed.",
        "run_dir_resolved": str(resolved_run_dir),
        "background_restart_resolved": str(resolved_background_restart),
        "preflight_checks": preflight,
        "command_preview": command_preview,
        "command_groups": {
            "restart_link": restart_link_group,
            "restart_check": restart_check_group,
            "validate": validate_group,
            "submit_preview": submit_group,
        },
        "scheduler_hint": hint,
        "scheduler_resolved": scheduler_resolved,
        "restart_mode_requested": mode_normalized,
        "restart_mode_effective": restart_mode_effective,
        "restart_options": {
            "include_restart_check": include_restart_check,
            "verbose": verbose,
            "warn_only": warn_only,
        },
        "nproc_used": nproc_used,
        "job_layout": job_layout,
        "requires_manual_execution": True,
        "authority": "authoritative",
        "source_kind": "script",
        "source_paths": [str(script)],
        "warnings": warnings,
    }

    if include_validation_commands and not param_exists:
        payload["ok"] = False
        payload["hard_error"] = True
        payload["error_code"] = "PARAM_NOT_FOUND"
        payload["message"] = f"param_path does not point to a file: {resolved_param}"

    return with_root(payload, root)


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


def swmf_plan_restart_from_background(
    run_dir: str,
    background_results_dir: str,
    restart_subdir: str = "RESTART",
    param_path: str | None = None,
    nproc: int | None = None,
    scheduler_hint: str = "auto",
    restart_mode: str = "auto",
    include_restart_check: bool = True,
    verbose: bool = True,
    warn_only: bool = False,
    include_validation_commands: bool = True,
    include_submit_preview: bool = True,
    swmf_root: str | None = None,
) -> dict[str, Any]:
    return plan_restart_from_background(
        run_dir=run_dir,
        background_results_dir=background_results_dir,
        restart_subdir=restart_subdir,
        param_path=param_path,
        nproc=nproc,
        scheduler_hint=scheduler_hint,
        restart_mode=restart_mode,
        include_restart_check=include_restart_check,
        verbose=verbose,
        warn_only=warn_only,
        include_validation_commands=include_validation_commands,
        include_submit_preview=include_submit_preview,
        swmf_root=swmf_root,
    )


def register(app: Any) -> None:
    app.tool(description="Run or preview SWMF PostProc.pl in the target run directory.")(swmf_postprocess)
    app.tool(description="Run or preview SWMF Restart.pl for restart file management.")(swmf_manage_restart)
    app.tool(description="Plan Restart.pl commands for linking background solar wind results without execution.")(swmf_plan_restart_from_background)
