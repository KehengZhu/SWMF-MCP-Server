from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path
from typing import Any

from ..core.common import build_path_search_guidance as _build_path_search_guidance, resolve_run_dir
from ..parsing.job_layout import find_likely_job_scripts, infer_job_layout_from_script
from ._helpers import resolve_root_or_failure, with_root


_ALLOWED_SCHEDULER_HINTS = {"auto", "slurm", "pbs"}
_ALLOWED_RESTART_MODES = {"auto", "framework", "standalone", "a", "f", "s"}
_ALLOWED_POSTPROCESS_SCHEDULER_HINTS = {"auto", "slurm", "pbs"}

_CURATED_RELATED_SCRIPTS = {
    "restart": "Restart.pl",
    "postproc": "PostProc.pl",
    "resubmit": "Resubmit.pl",
    "testparam": "Scripts/TestParam.pl",
    "preplot": "Preplot.pl",
    "convert2vtk": "convert2vtk.jl",
}

_RESTART_OPTION_KEYWORDS = {
    "-h",
    "-help",
    "-o",
    "-output",
    "-i",
    "-input",
    "-c",
    "-check",
    "-v",
    "-verbose",
    "-W",
    "-warn",
    "-t",
    "-u",
    "-timeunit",
    "-unit",
    "-r",
    "-repeat",
    "-k",
    "-keep",
    "-l",
    "-linkorig",
    "-w",
    "-wait",
    "-m",
    "-mode",
}

_POSTPROC_OPTION_KEYWORDS = {
    "-h",
    "-help",
    "-v",
    "-verbose",
    "-c",
    "-cat",
    "-g",
    "-gzip",
    "-m",
    "-movie",
    "-M",
    "-MOVIE",
    "-t",
    "-tar",
    "-T",
    "-TAR",
    "-noptec",
    "-vtu",
    "-vtk",
    "-n",
    "-p",
    "-q",
    "-r",
    "-repeat",
    "-replace",
    "-s",
    "-stop",
    "-allparam",
    "-rsync",
    "-sync",
    "-l",
    "-link",
    "-f",
    "-format",
}


def _read_text_if_file(path: Path | None) -> str | None:
    if path is None or not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def _dedupe_preserve(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _resolve_related_script(run_dir: Path, swmf_root: Path, script_ref: str) -> Path | None:
    script_path = Path(script_ref)
    basename = script_path.name

    candidates: list[Path] = []
    if script_path.parts and len(script_path.parts) > 1:
        candidates.extend(
            [
                run_dir / script_path,
                swmf_root / script_path,
                swmf_root / "share" / script_path,
            ]
        )
    else:
        candidates.extend(
            [
                run_dir / basename,
                run_dir / "Scripts" / basename,
                run_dir / "share" / "Scripts" / basename,
                run_dir / "share" / "scripts" / basename,
                swmf_root / basename,
                swmf_root / "Scripts" / basename,
                swmf_root / "share" / "Scripts" / basename,
            ]
        )

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    if len(script_path.parts) == 1:
        for search_root in [run_dir, swmf_root / "Scripts", swmf_root / "share" / "Scripts"]:
            if not search_root.exists():
                continue
            discovered: list[Path] = []
            try:
                for candidate in search_root.rglob(basename):
                    if not candidate.is_file():
                        continue
                    try:
                        rel_parts = candidate.resolve().relative_to(search_root.resolve()).parts
                    except ValueError:
                        rel_parts = ()
                    if len(rel_parts) <= 6:
                        discovered.append(candidate.resolve())
            except OSError:
                discovered = []
            if discovered:
                discovered.sort(key=lambda p: (len(p.parts), str(p)))
                return discovered[0]

    return None


def _discover_related_scripts(run_dir: Path, swmf_root: Path) -> dict[str, Any]:
    scripts: dict[str, str | None] = {}
    source_paths: list[str] = []
    warnings: list[str] = []

    for key, ref in _CURATED_RELATED_SCRIPTS.items():
        resolved = _resolve_related_script(run_dir, swmf_root, ref)
        scripts[key] = str(resolved) if resolved is not None else None
        if resolved is not None:
            source_paths.append(str(resolved))
        elif key in {"restart", "postproc", "resubmit"}:
            warnings.append(f"Curated script was not found for {key}: {ref}")

    return {
        "scripts": scripts,
        "source_paths": _dedupe_preserve(source_paths),
        "warnings": warnings,
    }


def _extract_perl_help_options(script_text: str) -> list[dict[str, Any]]:
    in_usage = False
    in_examples = False
    options: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw_line in script_text.splitlines():
        line = raw_line.rstrip()

        if line.strip() == "Usage:":
            in_usage = True
            in_examples = False
            continue
        if line.strip().startswith("Examples"):
            in_examples = True
            continue
        if in_examples:
            continue
        if not in_usage:
            continue

        option_line = re.match(r"^\s+(-\S(?:.*?))(?:\s{2,}|\t+)(.+)$", line)
        if option_line:
            option_text = option_line.group(1).strip()
            description = option_line.group(2).strip()
            aliases = re.findall(r"-[A-Za-z][A-Za-z0-9]*(?:=[A-Za-z0-9_]+)?", option_text)
            if not aliases:
                continue

            current = {
                "aliases": aliases,
                "description": description,
                "takes_value": any("=" in alias for alias in aliases),
            }
            options.append(current)
            continue

        if current is not None:
            stripped = line.strip()
            if stripped and not stripped.startswith("-"):
                current["description"] = f"{current['description']} {stripped}".strip()

    deduped: list[dict[str, Any]] = []
    seen_alias_key: set[str] = set()
    for item in options:
        alias_key = ",".join(item.get("aliases", []))
        if alias_key in seen_alias_key:
            continue
        seen_alias_key.add(alias_key)
        deduped.append(item)
    return deduped


def _extract_perl_hash_map(script_text: str, hash_name: str) -> dict[str, str]:
    block_match = re.search(rf"%{re.escape(hash_name)}\s*=\s*\((.*?)\);", script_text, flags=re.S)
    if block_match is None:
        return {}
    body = block_match.group(1)
    pairs = re.findall(r'"?([A-Za-z0-9_]+)"?\s*=>\s*"([^\"]+)"', body)
    return {str(key): str(value) for key, value in pairs}


def _extract_perl_string_scalars(script_text: str) -> dict[str, str]:
    pairs = re.findall(r"my\s+\$(\w+)\s*=\s*\"([^\"]+)\"", script_text)
    return {str(key): str(value) for key, value in pairs}


def _filter_option_reference(
    options: list[dict[str, Any]],
    allowed_aliases: set[str],
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for item in options:
        aliases = [str(alias) for alias in item.get("aliases", [])]
        if not aliases:
            continue
        if not any(alias.split("=", 1)[0] in allowed_aliases for alias in aliases):
            continue
        filtered.append(
            {
                "aliases": aliases,
                "description": str(item.get("description", "")).strip(),
                "takes_value": bool(item.get("takes_value", False)),
            }
        )
    return filtered


def _extract_restart_knowledge(script_path: Path | None) -> dict[str, Any]:
    script_text = _read_text_if_file(script_path)
    if script_text is None:
        return {
            "detected": False,
            "option_reference": [],
            "time_unit_reference": [],
            "component_mappings": [],
            "control_files": {},
            "warnings": ["Restart.pl content could not be read for source-grounded guidance."],
        }

    options = _extract_perl_help_options(script_text)
    filtered_options = _filter_option_reference(options, _RESTART_OPTION_KEYWORDS)
    unit_map = _extract_perl_hash_map(script_text, "UnitSecond")
    out_dir = _extract_perl_hash_map(script_text, "RestartOutDir")
    in_dir = _extract_perl_hash_map(script_text, "RestartInDir")
    scalars = _extract_perl_string_scalars(script_text)

    component_mappings: list[dict[str, str]] = []
    components = sorted(set(out_dir.keys()) | set(in_dir.keys()))
    for comp in components:
        component_mappings.append(
            {
                "component": comp,
                "restart_out_dir": out_dir.get(comp, ""),
                "restart_in_dir": in_dir.get(comp, ""),
            }
        )

    time_unit_reference = [
        {
            "unit": unit,
            "seconds": seconds,
        }
        for unit, seconds in unit_map.items()
    ]

    control_files: dict[str, str] = {}
    for key in ["RestartOutFile", "RestartInFile"]:
        if key in scalars:
            control_files[key] = scalars[key]

    return {
        "detected": True,
        "option_reference": filtered_options,
        "time_unit_reference": time_unit_reference,
        "component_mappings": component_mappings,
        "control_files": control_files,
        "warnings": [],
    }


def _extract_postproc_knowledge(script_path: Path | None) -> dict[str, Any]:
    script_text = _read_text_if_file(script_path)
    if script_text is None:
        return {
            "detected": False,
            "option_reference": [],
            "plot_dir_mappings": {},
            "control_files": {},
            "warnings": ["PostProc.pl content could not be read for source-grounded guidance."],
        }

    options = _extract_perl_help_options(script_text)
    filtered_options = _filter_option_reference(options, _POSTPROC_OPTION_KEYWORDS)
    plot_dir_mappings = _extract_perl_hash_map(script_text, "PlotDir")
    scalars = _extract_perl_string_scalars(script_text)

    control_files: dict[str, str] = {}
    for key in ["StopFile", "ParamIn", "ParamInOrig", "RunLog"]:
        if key in scalars:
            control_files[key] = scalars[key]

    return {
        "detected": True,
        "option_reference": filtered_options,
        "plot_dir_mappings": plot_dir_mappings,
        "control_files": control_files,
        "warnings": [],
    }


def _extract_resubmit_knowledge(script_path: Path | None) -> dict[str, Any]:
    script_text = _read_text_if_file(script_path)
    if script_text is None:
        return {
            "detected": False,
            "control_files": {},
            "scheduler_branches": [],
            "warnings": ["Resubmit.pl content could not be read for source-grounded guidance."],
        }

    scalars = _extract_perl_string_scalars(script_text)
    control_files: dict[str, str] = {}
    for key in ["Success1", "Success2", "Done1", "Done2"]:
        if key in scalars:
            control_files[key] = scalars[key]

    scheduler_branches: list[dict[str, str]] = []
    if "qsub" in script_text:
        scheduler_branches.append(
            {
                "scheduler": "pbs",
                "detection": "#PBS in job script",
                "submit_command": "qsub <JOBFILE>",
            }
        )
    if "sbatch" in script_text:
        scheduler_branches.append(
            {
                "scheduler": "slurm",
                "detection": "#SBATCH in job script",
                "submit_command": "sbatch <JOBFILE>",
            }
        )

    return {
        "detected": True,
        "control_files": control_files,
        "scheduler_branches": scheduler_branches,
        "warnings": [],
    }


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
    related_discovery = _discover_related_scripts(resolved_run_dir, resolved_root)
    restart_knowledge = _extract_restart_knowledge(script if restart_script_detected else None)

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

    warnings: list[str] = [
        *list(related_discovery.get("warnings", [])),
        *list(restart_knowledge.get("warnings", [])),
    ]
    if not run_dir_exists:
        path_guidance = _build_path_search_guidance(
            path_role="run_dir",
            search_roots=[resolved_run_dir, resolved_run_dir.parent],
            expected_entries=["PARAM.in", "RESTART.in", "RESTART", "job.long"],
            keyword_hints=[resolved_run_dir.name, "run", "restart", "param", "job"],
        )
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "PATH_NOT_FOUND",
                "message": f"run_dir does not exist: {resolved_run_dir}",
                "run_dir_resolved": str(resolved_run_dir),
                "background_restart_resolved": str(resolved_background_restart),
                "preflight_checks": preflight,
                "requires_manual_execution": True,
                "authority": "authoritative",
                "source_kind": "script",
                "source_paths": [str(script)],
                "warnings": warnings,
                **path_guidance,
            },
            root,
        )

    if not restart_script_detected:
        path_guidance = _build_path_search_guidance(
            path_role="run_dir/swmf_root for Restart.pl",
            search_roots=[resolved_run_dir, resolved_root, resolved_run_dir.parent],
            expected_entries=["Restart.pl", "Scripts", "share"],
            keyword_hints=["restart", "scripts", "swmf", resolved_run_dir.name],
        )
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "RESTART_SCRIPT_NOT_FOUND",
                "message": f"Could not locate Restart.pl under run_dir or SWMF root: {script}",
                "run_dir_resolved": str(resolved_run_dir),
                "background_restart_resolved": str(resolved_background_restart),
                "preflight_checks": preflight,
                "requires_manual_execution": True,
                "authority": "authoritative",
                "source_kind": "script",
                "source_paths": [str(script)],
                "warnings": warnings,
                **path_guidance,
            },
            root,
        )

    if not restart_source_exists:
        path_guidance = _build_path_search_guidance(
            path_role="background_results_dir/restart_subdir",
            search_roots=[resolved_background_dir, resolved_background_dir.parent, resolved_run_dir],
            expected_entries=[restart_subdir, "RESTART", "restart"],
            keyword_hints=[restart_subdir, "restart", "results", "background"],
        )
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "RESTART_SOURCE_NOT_FOUND",
                "message": f"Restart source folder was not found: {resolved_background_restart}",
                "run_dir_resolved": str(resolved_run_dir),
                "background_restart_resolved": str(resolved_background_restart),
                "preflight_checks": preflight,
                "requires_manual_execution": True,
                "authority": "authoritative",
                "source_kind": "script",
                "source_paths": [str(script)],
                "warnings": warnings,
                **path_guidance,
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
                    f"cd {str(resolved_root)} && perl ./Scripts/TestParam.pl -n=<YOUR_NPROC> {shlex.quote(str(resolved_param))}"
                )
            else:
                validate_group.append(
                    f"cd {str(resolved_root)} && perl ./Scripts/TestParam.pl -n={nproc_used} {shlex.quote(str(resolved_param))}"
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
    workflow_guidance = [
        "Treat command outputs as optional examples and validate Restart.pl behavior in your local script copy.",
        "Use restart_check before restart_link to verify tree structure and header metadata alignment.",
        "Prefer explicit restart_mode when environment detection is ambiguous; auto mode is heuristic.",
    ]
    decision_branches = [
        {
            "name": "restart_check_then_link",
            "when": "include_restart_check=True and Restart.pl is available.",
            "action": "Run restart_check then restart_link command templates.",
            "status": "available" if include_restart_check else "disabled",
        },
        {
            "name": "scheduler_submit_preview",
            "when": "include_submit_preview=True.",
            "action": "Use submit_preview examples matching scheduler_resolved.",
            "status": "available" if include_submit_preview else "disabled",
            "scheduler": scheduler_resolved,
        },
        {
            "name": "validation_with_testparam",
            "when": "include_validation_commands=True and PARAM path exists.",
            "action": "Run TestParam.pl from SWMF root using nproc_used value.",
            "status": "available" if validate_group else "unavailable",
        },
    ]
    variable_guidance = {
        "RESTART_MODE": {
            "selected": restart_mode_effective,
            "source": "input_or_auto_detection",
            "description": "Restart.pl mode controls framework vs standalone directory assumptions.",
            "how_to_override": "Set restart_mode to framework or standalone explicitly.",
        },
        "SCHEDULER": {
            "selected": scheduler_resolved,
            "source": "scheduler_hint_or_job_script_detection",
            "description": "Submit preview branch uses scheduler-specific command examples.",
            "how_to_override": "Set scheduler_hint to slurm or pbs for deterministic submit preview.",
        },
        "NPROC": {
            "selected": nproc_used,
            "source": "explicit_or_job_layout_inference",
            "description": "MPI rank count used by TestParam validation example.",
            "how_to_override": "Pass nproc explicitly when preparing restart guidance.",
        },
        "WARN_ONLY": {
            "selected": warn_only,
            "source": "input_flag",
            "description": "When true, Restart.pl warning mode (-W) is included in command examples.",
            "how_to_override": "Set warn_only to False for strict failure behavior.",
        },
    }

    environment_prerequisites = [
        "Restart source directory must exist and contain restart tree content.",
        "Restart.pl must be available in run directory or SWMF script paths.",
    ]
    if include_validation_commands:
        environment_prerequisites.append("Scripts/TestParam.pl should be available under SWMF root for validation commands.")

    assumptions: list[str] = []
    if scheduler_resolved == "unknown":
        assumptions.append("Scheduler inference is heuristic because job script directives were not detected.")
    if restart_mode == "auto":
        assumptions.append("restart_mode was auto-detected from run-directory context and may require manual override.")
    if include_validation_commands and nproc_used is None:
        assumptions.append("nproc could not be inferred; validation uses placeholder and requires manual value.")

    script_source_paths = [
        str(script),
        *[str(path) for path in related_discovery.get("source_paths", []) if isinstance(path, str)],
    ]
    source_paths = sorted(set(script_source_paths))

    authority_by_field = {
        "restart_option_reference": "authoritative" if bool(restart_knowledge.get("option_reference")) else "heuristic",
        "restart_time_unit_reference": "authoritative" if bool(restart_knowledge.get("time_unit_reference")) else "heuristic",
        "restart_component_mappings": "authoritative" if bool(restart_knowledge.get("component_mappings")) else "heuristic",
        "optional_command_examples": "derived",
        "scheduler_resolved": "heuristic" if hint == "auto" else "input",
        "nproc_used": "heuristic" if nproc is None else "input",
    }

    payload = {
        "ok": True,
        "hard_error": False,
        "error_code": None,
        "guidance_mode": "instruction_first",
        "message": "Generated restart/validation/submit preview commands. Nothing was executed.",
        "run_dir_resolved": str(resolved_run_dir),
        "background_restart_resolved": str(resolved_background_restart),
        "testparam_constraint": "TestParam.pl validation commands must be run from SWMF_ROOT directory.",
        "testparam_execution_note": f"Run TestParam.pl from within SWMF_ROOT: cd {str(resolved_root)} && ./Scripts/TestParam.pl -n=<nproc> <PARAM.in>",
        "preflight_checks": preflight,
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
        "workflow_guidance": workflow_guidance,
        "decision_branches": decision_branches,
        "variable_guidance": variable_guidance,
        "environment_prerequisites": environment_prerequisites,
        "assumptions": assumptions,
        "restart_option_reference": list(restart_knowledge.get("option_reference", [])),
        "restart_time_unit_reference": list(restart_knowledge.get("time_unit_reference", [])),
        "restart_component_mappings": list(restart_knowledge.get("component_mappings", [])),
        "restart_control_files": dict(restart_knowledge.get("control_files", {})),
        "authority_by_field": authority_by_field,
        "optional_command_examples": {
            "full_sequence": command_preview,
            "restart_check": restart_check_group,
            "restart_link": restart_link_group,
            "validate": validate_group,
            "submit_preview": submit_group,
        },
        "requires_manual_execution": True,
        "authority": "authoritative",
        "source_kind": "script",
        "source_paths": source_paths,
        "warnings": warnings,
    }

    if include_validation_commands and not param_exists:
        payload["ok"] = False
        payload["hard_error"] = True
        payload["error_code"] = "PARAM_NOT_FOUND"
        payload["message"] = f"param_path does not point to a file: {resolved_param}"
        payload.update(
            _build_path_search_guidance(
                path_role="param_path",
                search_roots=[resolved_run_dir, resolved_run_dir.parent],
                expected_entries=[Path(param_input).name, "PARAM.in", "PARAM.in.start", "PARAM.in.restart"],
                keyword_hints=[Path(param_input).name, "param", "restart", "input"],
            )
        )

    return with_root(payload, root)


def _infer_scheduler_from_job_script(job_script: Path) -> str | None:
    if not job_script.is_file():
        return None
    try:
        text = job_script.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    if "#SBATCH" in text:
        return "slurm"
    if "#PBS" in text:
        return "pbs"
    return None


def plan_postprocess(
    run_dir: str,
    output_dir: str | None = None,
    repeat_seconds: int | None = None,
    stop_days: int | None = None,
    rsync_target: str | None = None,
    include_concat: bool = False,
    include_gzip: bool = False,
    swmf_root: str | None = None,
) -> dict[str, Any]:
    resolved_run_dir = resolve_run_dir(run_dir)
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    if repeat_seconds is not None and repeat_seconds <= 0:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "INPUT_INVALID",
                "message": "repeat_seconds must be positive when provided.",
            },
            root,
        )
    if stop_days is not None and stop_days <= 0:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "INPUT_INVALID",
                "message": "stop_days must be positive when provided.",
            },
            root,
        )
    if repeat_seconds is not None and output_dir is not None:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "INPUT_INVALID",
                "message": "PostProc.pl repeat mode (-r) cannot be combined with output collection directory.",
            },
            root,
        )

    resolved_root = Path(root.swmf_root_resolved or str(Path.cwd())).resolve()
    script = _resolve_script(resolved_run_dir, resolved_root, "PostProc.pl")
    if not script.is_file():
        path_guidance = _build_path_search_guidance(
            path_role="run_dir/swmf_root for PostProc.pl",
            search_roots=[resolved_run_dir, resolved_root, resolved_run_dir.parent],
            expected_entries=["PostProc.pl", "Scripts", "share"],
            keyword_hints=["postproc", "postprocess", "scripts", resolved_run_dir.name],
        )
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "POSTPROC_NOT_FOUND",
                "message": f"Could not locate PostProc.pl under run_dir or SWMF root: {script}",
                **path_guidance,
            },
            root,
        )

    related_discovery = _discover_related_scripts(resolved_run_dir, resolved_root)
    postproc_knowledge = _extract_postproc_knowledge(script)
    warnings: list[str] = [
        *list(related_discovery.get("warnings", [])),
        *list(postproc_knowledge.get("warnings", [])),
    ]

    cmd_parts = [f"perl {shlex.quote(str(script))}"]
    if include_concat:
        cmd_parts.append("-c")
    if include_gzip:
        cmd_parts.append("-g")
    if repeat_seconds is not None:
        cmd_parts.append(f"-r={repeat_seconds}")
    if stop_days is not None:
        cmd_parts.append(f"-s={stop_days}")
    if rsync_target:
        cmd_parts.append(f"-rsync={shlex.quote(rsync_target)}")
    if output_dir is not None:
        cmd_parts.append(shlex.quote(output_dir))

    planned_command = " ".join(cmd_parts)
    command_preview = [f"cd {shlex.quote(str(resolved_run_dir))}", planned_command]

    workflow_guidance = [
        "Treat PostProc.pl command previews as templates and verify component plot directories in your run tree.",
        "Use repeat mode only for background post-processing loops; use output_dir for one-time output collection.",
        "Enable rsync only after validating remote target access and expected transfer scope.",
    ]
    decision_branches = [
        {
            "name": "repeat_loop_mode",
            "when": "repeat_seconds is provided.",
            "action": "Run PostProc.pl with -r and optional -s stop_days control.",
            "status": "available" if repeat_seconds is not None else "disabled",
        },
        {
            "name": "collect_output_tree",
            "when": "output_dir is provided and repeat mode is disabled.",
            "action": "Collect processed outputs and restart tree into output_dir.",
            "status": "available" if output_dir is not None else "disabled",
        },
        {
            "name": "rsync_branch",
            "when": "rsync_target is provided.",
            "action": "Include -rsync target for local/remote synchronization.",
            "status": "available" if bool(rsync_target) else "disabled",
        },
    ]
    variable_guidance = {
        "REPEAT_SECONDS": {
            "selected": repeat_seconds,
            "source": "input",
            "description": "Controls repeat-loop cadence for background post-processing.",
            "how_to_override": "Set repeat_seconds to enable or disable repeat mode.",
        },
        "STOP_DAYS": {
            "selected": stop_days,
            "source": "input",
            "description": "Upper bound for repeat mode duration in days.",
            "how_to_override": "Set stop_days explicitly when repeat mode is active.",
        },
        "OUTPUT_DIR": {
            "selected": output_dir,
            "source": "input",
            "description": "Optional output tree destination used in non-repeat mode.",
            "how_to_override": "Provide output_dir to collect processed outputs into a directory tree.",
        },
        "RSYNC_TARGET": {
            "selected": rsync_target,
            "source": "input",
            "description": "Optional rsync destination passed through -rsync.",
            "how_to_override": "Set rsync_target to enable synchronization after processing.",
        },
    }

    environment_prerequisites = [
        "PostProc.pl must be available from run directory or SWMF script paths.",
        "Run directory should contain component output directories expected by PostProc.pl.",
    ]
    if rsync_target:
        environment_prerequisites.append("rsync transport must be configured for the target destination.")

    assumptions: list[str] = []
    if repeat_seconds is None:
        assumptions.append("Plan assumes one-pass post-processing because repeat_seconds was not provided.")
    if output_dir is None:
        assumptions.append("No output collection directory was provided; outputs remain in-place.")

    source_paths = sorted(
        set(
            [
                str(script),
                *[str(path) for path in related_discovery.get("source_paths", []) if isinstance(path, str)],
            ]
        )
    )
    return with_root(
        {
            "ok": True,
            "hard_error": False,
            "error_code": None,
            "guidance_mode": "instruction_first",
            "message": "Generated PostProc.pl guidance and command preview. Nothing was executed.",
            "run_dir_resolved": str(resolved_run_dir),
            "workflow_guidance": workflow_guidance,
            "decision_branches": decision_branches,
            "variable_guidance": variable_guidance,
            "environment_prerequisites": environment_prerequisites,
            "assumptions": assumptions,
            "postproc_option_reference": list(postproc_knowledge.get("option_reference", [])),
            "postproc_plot_dir_mappings": dict(postproc_knowledge.get("plot_dir_mappings", {})),
            "postproc_control_files": dict(postproc_knowledge.get("control_files", {})),
            "optional_command_examples": {
                "full_sequence": command_preview,
                "postprocess": [planned_command],
            },
            "requires_manual_execution": True,
            "execute_supported": False,
            "authority": "authoritative",
            "source_kind": "script",
            "source_paths": source_paths,
            "warnings": warnings,
        },
        root,
    )


def plan_resubmit(
    run_dir: str,
    job_script: str = "job.long",
    sleep_seconds: int = 10,
    scheduler_hint: str = "auto",
    swmf_root: str | None = None,
) -> dict[str, Any]:
    resolved_run_dir = resolve_run_dir(run_dir)
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    if sleep_seconds <= 0:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "INPUT_INVALID",
                "message": "sleep_seconds must be positive.",
            },
            root,
        )

    hint = scheduler_hint.strip().lower()
    if hint not in _ALLOWED_POSTPROCESS_SCHEDULER_HINTS:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "INPUT_INVALID",
                "message": f"Unsupported scheduler_hint '{scheduler_hint}'. Use one of: auto, slurm, pbs.",
            },
            root,
        )

    resolved_root = Path(root.swmf_root_resolved or str(Path.cwd())).resolve()
    script = _resolve_script(resolved_run_dir, resolved_root, "Resubmit.pl")
    if not script.is_file():
        path_guidance = _build_path_search_guidance(
            path_role="run_dir/swmf_root for Resubmit.pl",
            search_roots=[resolved_run_dir, resolved_root, resolved_run_dir.parent],
            expected_entries=["Resubmit.pl", "Scripts", "share"],
            keyword_hints=["resubmit", "scripts", "job", resolved_run_dir.name],
        )
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "RESUBMIT_SCRIPT_NOT_FOUND",
                "message": f"Could not locate Resubmit.pl under run_dir or SWMF root: {script}",
                **path_guidance,
            },
            root,
        )

    related_discovery = _discover_related_scripts(resolved_run_dir, resolved_root)
    resubmit_knowledge = _extract_resubmit_knowledge(script)
    warnings: list[str] = [
        *list(related_discovery.get("warnings", [])),
        *list(resubmit_knowledge.get("warnings", [])),
    ]

    resolved_job_script = _resolve_from_run_dir(job_script, resolved_run_dir)
    if not resolved_job_script.is_file():
        path_guidance = _build_path_search_guidance(
            path_role="job_script",
            search_roots=[resolved_run_dir, resolved_run_dir.parent],
            expected_entries=[Path(job_script).name, "job.long", "job.slurm", "job.pbs", "job.frontera"],
            keyword_hints=[Path(job_script).name, "job", "scheduler", "submit"],
        )
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "JOB_SCRIPT_NOT_FOUND",
                "message": f"Job script was not found: {resolved_job_script}",
                "run_dir_resolved": str(resolved_run_dir),
                "source_paths": sorted(set([str(script)])),
                **path_guidance,
            },
            root,
        )

    scheduler_resolved = hint
    if hint == "auto":
        scheduler_resolved = _infer_scheduler_from_job_script(resolved_job_script) or "unknown"
    if scheduler_resolved == "unknown":
        warnings.append("Could not detect scheduler from job script directives; review submit command branch manually.")

    relative_job_script = resolved_job_script.name
    resubmit_command = (
        f"perl {shlex.quote(str(script))} -s={sleep_seconds} {shlex.quote(relative_job_script)} >& Resubmit.log &"
    )
    command_preview = [f"cd {shlex.quote(str(resolved_run_dir))}", resubmit_command]
    scheduler_submit_preview = [
        "sbatch <JOBFILE>" if scheduler_resolved == "slurm" else "qsub <JOBFILE>"
        if scheduler_resolved == "pbs"
        else "# submit manually with site scheduler"
    ]

    param_restart_exists = (resolved_run_dir / "PARAM.in.restart").is_file()
    param_start_exists = (resolved_run_dir / "PARAM.in.start").is_file()

    workflow_guidance = [
        "Treat Resubmit.pl command output as optional execution template and confirm scheduler directives in job script.",
        "Resubmit loop relies on SUCCESS and DONE control files; verify these are produced by your runtime workflow.",
        "Restart.pl handoff is expected between iterations, so keep restart script available in the run context.",
    ]
    decision_branches = [
        {
            "name": "scheduler_branch",
            "when": "scheduler_hint or job script directive resolves scheduler.",
            "action": "Use scheduler-specific submit behavior inside Resubmit.pl.",
            "status": "available" if scheduler_resolved in {"slurm", "pbs"} else "unknown",
            "scheduler": scheduler_resolved,
        },
        {
            "name": "param_restart_swap",
            "when": "PARAM.in.restart exists and PARAM.in.start is absent.",
            "action": "Resubmit.pl will move PARAM.in to PARAM.in.start and copy PARAM.in.restart into PARAM.in.",
            "status": "active" if (param_restart_exists and not param_start_exists) else "inactive",
        },
    ]
    variable_guidance = {
        "JOB_SCRIPT": {
            "selected": relative_job_script,
            "source": "input",
            "description": "Job script used by Resubmit.pl for scheduler submissions.",
            "how_to_override": "Pass job_script path when preparing resubmit guidance.",
        },
        "SLEEP_SECONDS": {
            "selected": sleep_seconds,
            "source": "input",
            "description": "Polling interval for SUCCESS file checks between submissions.",
            "how_to_override": "Set sleep_seconds to tune polling cadence.",
        },
        "SCHEDULER": {
            "selected": scheduler_resolved,
            "source": "hint_or_script_detection",
            "description": "Scheduler branch inferred from directives or explicit scheduler_hint.",
            "how_to_override": "Set scheduler_hint to slurm or pbs for deterministic branch selection.",
        },
    }

    environment_prerequisites = [
        "Resubmit.pl must be available in run directory or SWMF script paths.",
        "Job script should include scheduler directives (#SBATCH or #PBS) for reliable scheduler detection.",
        "Restart.pl should be available because Resubmit.pl invokes it between job iterations.",
    ]
    assumptions: list[str] = []
    if scheduler_resolved == "unknown":
        assumptions.append("Scheduler could not be detected from job script, so submit behavior may need manual adjustment.")
    if param_start_exists:
        assumptions.append("PARAM.in.start already exists; PARAM.in.restart swap path in Resubmit.pl may remain inactive.")

    source_paths = sorted(
        set(
            [
                str(script),
                *[str(path) for path in related_discovery.get("source_paths", []) if isinstance(path, str)],
            ]
        )
    )

    return with_root(
        {
            "ok": True,
            "hard_error": False,
            "error_code": None,
            "guidance_mode": "instruction_first",
            "message": "Generated Resubmit.pl guidance and command preview. Nothing was executed.",
            "run_dir_resolved": str(resolved_run_dir),
            "job_script_resolved": str(resolved_job_script),
            "scheduler_hint": hint,
            "scheduler_resolved": scheduler_resolved,
            "workflow_guidance": workflow_guidance,
            "decision_branches": decision_branches,
            "variable_guidance": variable_guidance,
            "environment_prerequisites": environment_prerequisites,
            "assumptions": assumptions,
            "resubmit_control_files": dict(resubmit_knowledge.get("control_files", {})),
            "resubmit_scheduler_branches": list(resubmit_knowledge.get("scheduler_branches", [])),
            "optional_command_examples": {
                "full_sequence": command_preview,
                "resubmit": [resubmit_command],
                "scheduler_submit_preview": scheduler_submit_preview,
            },
            "requires_manual_execution": True,
            "execute_supported": False,
            "authority": "authoritative",
            "source_kind": "script",
            "source_paths": source_paths,
            "warnings": warnings,
        },
        root,
    )


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
        path_guidance = _build_path_search_guidance(
            path_role="run_dir/swmf_root for PostProc.pl",
            search_roots=[resolved_run_dir, resolved_root, resolved_run_dir.parent],
            expected_entries=["PostProc.pl", "Scripts", "share"],
            keyword_hints=["postproc", "postprocess", "scripts", resolved_run_dir.name],
        )
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "POSTPROC_NOT_FOUND",
                "message": f"Could not locate PostProc.pl under run_dir or SWMF root: {script}",
                **path_guidance,
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
        path_guidance = _build_path_search_guidance(
            path_role="run_dir/swmf_root for Restart.pl",
            search_roots=[resolved_run_dir, resolved_root, resolved_run_dir.parent],
            expected_entries=["Restart.pl", "Scripts", "share"],
            keyword_hints=["restart", "scripts", "job", resolved_run_dir.name],
        )
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "RESTART_SCRIPT_NOT_FOUND",
                "message": f"Could not locate Restart.pl under run_dir or SWMF root: {script}",
                **path_guidance,
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


def swmf_plan_postprocess(
    run_dir: str,
    output_dir: str | None = None,
    repeat_seconds: int | None = None,
    stop_days: int | None = None,
    rsync_target: str | None = None,
    include_concat: bool = False,
    include_gzip: bool = False,
    swmf_root: str | None = None,
) -> dict[str, Any]:
    return plan_postprocess(
        run_dir=run_dir,
        output_dir=output_dir,
        repeat_seconds=repeat_seconds,
        stop_days=stop_days,
        rsync_target=rsync_target,
        include_concat=include_concat,
        include_gzip=include_gzip,
        swmf_root=swmf_root,
    )


def swmf_plan_resubmit(
    run_dir: str,
    job_script: str = "job.long",
    sleep_seconds: int = 10,
    scheduler_hint: str = "auto",
    swmf_root: str | None = None,
) -> dict[str, Any]:
    return plan_resubmit(
        run_dir=run_dir,
        job_script=job_script,
        sleep_seconds=sleep_seconds,
        scheduler_hint=scheduler_hint,
        swmf_root=swmf_root,
    )


def register(app: Any) -> None:
    app.tool(description="Run or preview SWMF PostProc.pl in the target run directory.")(swmf_postprocess)
    app.tool(description="Run or preview SWMF Restart.pl for restart file management.")(swmf_manage_restart)
    app.tool(description="Plan guidance-first Restart.pl linking/validation workflow from background results without execution.")(swmf_plan_restart_from_background)
    app.tool(description="Plan guidance-first PostProc.pl workflow options and command templates without execution.")(swmf_plan_postprocess)
    app.tool(description="Plan guidance-first Resubmit.pl loop strategy and command templates without execution.")(swmf_plan_resubmit)
