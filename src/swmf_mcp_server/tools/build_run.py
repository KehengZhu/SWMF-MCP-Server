from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path
from typing import Any

from ..core.common import load_param_text, resolve_run_dir
from ..parsing.component_map import COMPONENTMAP_ROW
from ..parsing.job_layout import find_likely_job_scripts, infer_job_layout_from_script
from ..parsing.param_parser import parse_param_text
from ._helpers import resolve_root_or_failure, with_root

COMPONENT_VERSION_DEFAULTS: dict[str, str] = {
    "GM": "GM/BATSRUS",
    "SC": "SC/BATSRUS",
    "IE": "IE/Ridley_serial",
    "IM": "IM/RCM2",
    "IH": "IH/BATSRUS",
    "OH": "OH/BATSRUS",
    "UA": "UA/GITM",
    "EE": "EE/Empty",
}


def _normalize_component_list(components_csv: str) -> list[str]:
    items = [item.strip() for item in components_csv.split(",") if item.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return deduped


def _infer_required_components_from_sessions(sessions: list) -> list[str]:
    required: list[str] = []
    seen: set[str] = set()

    def add_component(comp: str) -> None:
        comp_id = comp.strip().upper()
        if len(comp_id) != 2:
            return
        if comp_id not in seen:
            seen.add(comp_id)
            required.append(comp_id)

    for session in sessions:
        for row in session.component_map_rows:
            add_component(str(row.get("component", "")))
        for comp in session.component_blocks:
            add_component(comp)
        for comp, _ in session.switched_components:
            add_component(comp)

    return required


def _build_component_config_recommendation(required_components: list[str]) -> dict[str, Any]:
    versions: list[str] = []
    missing_defaults: list[str] = []

    for comp in required_components:
        version = COMPONENT_VERSION_DEFAULTS.get(comp)
        if version is None:
            missing_defaults.append(comp)
        else:
            versions.append(version)

    config_command = f"./Config.pl -v={','.join(['Empty'] + versions)}"
    warnings = [f"No prototype default version mapping is defined for component {comp}." for comp in missing_defaults]

    return {
        "required_components": required_components,
        "recommended_component_versions": versions,
        "components_without_default_mapping": missing_defaults,
        "recommended_config_command": config_command,
        "rebuild_commands": ["make clean", "make -j"],
        "warnings": warnings,
    }


def prepare_build(
    components_csv: str,
    compiler: str | None = None,
    debug: bool = False,
    optimization: int | None = None,
) -> dict[str, Any]:
    requested = _normalize_component_list(components_csv)
    if not requested:
        return {
            "ok": False,
            "message": "Provide at least one component version, e.g. GM/BATSRUS,IE/Ridley_serial",
        }

    version_list = ["Empty"] + [item for item in requested if item.lower() != "empty"]
    version_arg = ",".join(version_list)

    commands: list[str] = []
    commands.append(f"./Config.pl -install -compiler={compiler}" if compiler else "./Config.pl -install")
    commands.append(f"Config.pl -v={version_arg}")

    if optimization is None:
        optimization = 0 if debug else 4

    commands.append(f"Config.pl {'-debug' if debug else '-nodebug'} -O{optimization}")
    commands.append("Config.pl -show")
    commands.append("make -j")

    return {
        "ok": True,
        "selected_components": requested,
        "config_pl_v_argument": version_arg,
        "suggested_commands": commands,
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": [],
        "notes": [
            "The prototype returns suggested commands only. It does not execute them.",
            "Putting Empty first follows standard SWMF usage for 'all empty except selected components'.",
            "After changing compiler flags, a real workflow may also need make clean before recompiling.",
        ],
    }


def prepare_component_config(
    param_text: str,
) -> dict[str, Any]:
    parsed = parse_param_text(param_text)
    recommendation = _build_component_config_recommendation(_infer_required_components_from_sessions(parsed.sessions))
    return {
        "ok": True,
        "authority": "heuristic",
        "source_kind": "lightweight_parser",
        "source_paths": [],
        "required_components": recommendation["required_components"],
        "recommended_component_versions": recommendation["recommended_component_versions"],
        "components_without_default_mapping": recommendation["components_without_default_mapping"],
        "recommended_config_command": recommendation["recommended_config_command"],
        "rebuild_commands": recommendation["rebuild_commands"],
        "warnings": recommendation["warnings"],
    }


def explain_component_config_fix() -> dict[str, Any]:
    return {
        "ok": True,
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": [],
        "title": "Why Config.pl -v is needed for real components",
        "explanation": [
            "#COMPONENTMAP and component blocks reference active SWMF components such as SC or GM.",
            "If SWMF is compiled with only Empty versions for those components, validation and runtime checks can fail for missing component versions.",
            "Use Config.pl -v=Empty,<non-empty component versions...> to compile the component implementations required by PARAM.in.",
            "After changing component selections, rebuild with make clean and make -j.",
        ],
        "example": {
            "required_components": ["SC"],
            "recommended_config_command": "./Config.pl -v=Empty,SC/BATSRUS",
            "rebuild_commands": ["make clean", "make -j"],
        },
    }


def infer_job_layout(job_script_path: str | None = None, run_dir: str | None = None) -> dict[str, Any]:
    resolved_run_dir = resolve_run_dir(run_dir)

    if job_script_path:
        script_path = Path(job_script_path).expanduser()
        if not script_path.is_absolute():
            script_path = resolved_run_dir / script_path
        script_path = script_path.resolve()
        if not script_path.is_file():
            return {
                "ok": False,
                "hard_error": True,
                "error_code": "JOB_SCRIPT_NOT_FOUND",
                "message": f"Job script does not exist: {script_path}",
            }
    else:
        candidates = find_likely_job_scripts(resolved_run_dir)
        if not candidates:
            return {
                "ok": False,
                "hard_error": True,
                "error_code": "JOB_SCRIPT_NOT_FOUND",
                "message": f"No likely job script found under run_dir: {resolved_run_dir}",
            }
        script_path = candidates[0]

    try:
        script_text = script_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "JOB_SCRIPT_READ_FAILED",
            "message": f"Could not read job script: {exc}",
        }

    payload = infer_job_layout_from_script(script_path=script_path, script_text=script_text)
    payload.update(
        {
            "ok": True,
            "run_dir_resolved": str(resolved_run_dir),
            "authority": "derived",
            "source_kind": "script",
            "source_paths": [str(script_path)],
        }
    )
    return payload


def prepare_run(
    component_map_text: str,
    nproc: int | None = None,
    description: str = "Prototype SWMF run",
    time_accurate: bool = True,
    stop_value: str = "3600.0",
    include_restart: bool = False,
    run_name: str = "run_demo",
    run_dir: str | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    map_rows: list[str] = []
    map_errors: list[str] = []

    for raw in component_map_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if not COMPONENTMAP_ROW.match(line):
            map_errors.append(f"Could not parse component map row: {line}")
        else:
            map_rows.append(line)

    if not map_rows:
        return {"ok": False, "message": "Provide at least one valid component map row.", "errors": map_errors}
    if map_errors:
        return {"ok": False, "message": "Component map rows contain parse errors.", "errors": map_errors}

    nproc_source = "explicit"
    inferred_layout: dict[str, Any] | None = None
    if nproc is None:
        layout_result = infer_job_layout(job_script_path=job_script_path, run_dir=run_dir)
        if layout_result.get("ok") and layout_result.get("swmf_nproc") is not None:
            nproc = int(layout_result["swmf_nproc"])
            nproc_source = "job_script_inference"
            inferred_layout = layout_result
        else:
            return {
                "ok": False,
                "hard_error": True,
                "error_code": "NPROC_INFERENCE_FAILED",
                "message": "nproc was not provided and could not be inferred from a job script.",
                "how_to_fix": [
                    "Provide nproc explicitly.",
                    "Or provide run_dir/job_script_path and call swmf_infer_job_layout.",
                ],
                "job_layout": layout_result,
            }

    assert nproc is not None
    stop_block = (
        "#STOP\n" + (f"{stop_value} tSimulationMax\n-1 MaxIteration" if time_accurate else f"-1.0 tSimulationMax\n{stop_value} MaxIteration")
    )
    include_block = "#INCLUDE\nRESTART.in\n\n" if include_restart else ""
    time_flag = "T" if time_accurate else "F"

    param_in = (
        "#DESCRIPTION\n"
        f"{description}\n\n"
        f"{include_block}"
        "#TIMEACCURATE\n"
        f"{time_flag} DoTimeAccurate\n\n"
        "ID Proc0 ProcEnd Stride nThread\n"
        "#COMPONENTMAP\n"
        + "\n".join(map_rows)
        + "\n\n"
        + stop_block
        + "\n\n#END\n"
    )

    return {
        "ok": True,
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": [],
        "nproc": nproc,
        "nproc_source": nproc_source,
        "job_layout": inferred_layout,
        "run_name": run_name,
        "time_accurate": time_accurate,
        "starter_param_in": param_in,
        "suggested_commands": [
            "make rundir",
            f"mv run {run_name}",
            f"Scripts/TestParam.pl -n={nproc} {run_name}/PARAM.in",
            f"cd {run_name}",
        ],
        "requires_manual_submission": True,
        "auto_submit_permitted": False,
        "suggested_manual_submission": [
            "Edit your scheduler job script (for example job.frontera) for this run directory.",
            "Ensure the script uses SWMF.exe and the intended MPI layout.",
            "Submit manually (example): sbatch job.frontera",
        ],
    }


def _extract_candidate_setup_command_lines(param_text: str) -> list[str]:
    candidates: list[str] = []
    for raw_line in param_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        cleaned = re.sub(r"^\s*(?:[#;!]+|//|\*|-)+\s*", "", raw_line).strip()
        if not cleaned:
            continue

        match = re.search(r"((?:\./)?Config\.pl\s+.+)$", cleaned)
        if match:
            candidates.append(match.group(1).strip())
            continue

        if re.match(r"^make\s+", cleaned):
            candidates.append(cleaned)

    return candidates


def _parse_setup_command(command: str) -> tuple[dict[str, Any] | None, str | None]:
    forbidden_chars = {"|", "&", ">", "<", "`"}
    if any(ch in command for ch in forbidden_chars):
        return None, "Command contains forbidden shell control characters."

    try:
        argv = shlex.split(command, posix=True)
    except ValueError as exc:
        return None, f"Failed to parse command: {exc}"

    if not argv:
        return None, "Empty command."

    program = argv[0]
    if program in {"Config.pl", "./Config.pl"}:
        normalized_argv = ["./Config.pl"] + argv[1:]
        return {"kind": "config", "program": "./Config.pl", "argv": normalized_argv, "normalized": " ".join(normalized_argv)}, None

    if program == "make":
        if argv == ["make", "clean"]:
            return {"kind": "make-clean", "program": "make", "argv": argv, "normalized": "make clean"}, None
        if len(argv) == 2 and re.match(r"^-j\d*$", argv[1]):
            normalized = argv[1] if argv[1] != "-j" else "-j"
            return {"kind": "make-parallel", "program": "make", "argv": ["make", normalized], "normalized": f"make {normalized}"}, None
        return None, "Only 'make clean' and 'make -j' (or -jN) are allowed."

    return None, "Command is not in the allowed SWMF setup whitelist."


def detect_setup_commands(param_text: str) -> dict[str, Any]:
    parsed_commands: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    seen: set[str] = set()

    for candidate in _extract_candidate_setup_command_lines(param_text):
        parsed, error = _parse_setup_command(candidate)
        if parsed is None:
            rejected.append({"command": candidate, "reason": error or "Rejected."})
            continue
        normalized = parsed["normalized"]
        if normalized in seen:
            continue
        seen.add(normalized)
        parsed_commands.append(parsed)

    return {
        "ok": True,
        "found": len(parsed_commands) > 0,
        "commands": [entry["normalized"] for entry in parsed_commands],
        "commands_structured": parsed_commands,
        "rejected_candidates": rejected,
        "warnings": [item["reason"] for item in rejected],
        "authority": "derived",
        "source_kind": "lightweight_parser",
        "source_paths": [],
    }


def apply_setup_commands(
    swmf_root: str,
    commands: list[str],
    continue_on_error: bool = False,
) -> dict[str, Any]:
    execution_results: list[dict[str, Any]] = []
    all_ok = True

    for command in commands:
        parsed, parse_error = _parse_setup_command(command)
        if parsed is None:
            all_ok = False
            execution_results.append({"ok": False, "command": command, "error": parse_error or "Rejected command.", "cwd": swmf_root})
            if not continue_on_error:
                break
            continue

        argv = parsed["argv"]
        try:
            proc = subprocess.run(
                argv,
                cwd=swmf_root,
                capture_output=True,
                text=True,
                check=False,
                shell=False,
            )
        except OSError as exc:
            all_ok = False
            execution_results.append({"ok": False, "command": parsed["normalized"], "argv": argv, "cwd": swmf_root, "error": f"Execution failed: {exc}"})
            if not continue_on_error:
                break
            continue

        cmd_ok = proc.returncode == 0
        all_ok = all_ok and cmd_ok
        execution_results.append(
            {
                "ok": cmd_ok,
                "command": parsed["normalized"],
                "argv": argv,
                "cwd": swmf_root,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        )
        if (not cmd_ok) and (not continue_on_error):
            break

    return {
        "ok": all_ok,
        "continue_on_error": continue_on_error,
        "results": execution_results,
        "authority": "authoritative",
        "source_kind": "script",
        "source_paths": [str(Path(swmf_root) / "Config.pl")],
    }


_QUICKRUN_MODES: set[str] = {"sc_steady", "sc_ih_steady", "sc_ih_timeaccurate"}


def _quickrun_mode_to_components(mode: str) -> list[str]:
    if mode == "sc_steady":
        return ["SC/BATSRUS"]
    if mode in {"sc_ih_steady", "sc_ih_timeaccurate"}:
        return ["SC/BATSRUS", "IH/BATSRUS"]
    return ["SC/BATSRUS"]


def _quickrun_component_map(mode: str, nproc: int) -> str:
    if mode == "sc_steady" or nproc <= 1:
        return "SC 0 -1 1"
    sc_end = max(nproc - 2, 0)
    return "\n".join([f"SC 0 {sc_end} 1", "IH -1 -1 1"])


def prepare_sc_quickrun_from_magnetogram(
    fits_path: str,
    swmf_root_resolved: str,
    run_dir: str | None,
    mode: str = "sc_steady",
    nproc: int | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    from .idl import inspect_fits_magnetogram
    from .param import generate_param_from_template

    if mode not in _QUICKRUN_MODES:
        return {
            "ok": False,
            "hard_error": True,
            "message": f"Unsupported mode: {mode}",
            "how_to_fix": ["Use one of: sc_steady, sc_ih_steady, sc_ih_timeaccurate."],
        }

    inspect_result = inspect_fits_magnetogram(fits_path=fits_path, run_dir=run_dir, read_data=False)
    if not inspect_result.get("ok"):
        return {
            "ok": False,
            "hard_error": bool(inspect_result.get("hard_error", False)),
            "message": "FITS inspection failed; quickrun preparation aborted.",
            "fits_inspection": inspect_result,
            "recommended_next_tool": "swmf_inspect_fits_magnetogram",
        }

    inferred_nproc = nproc
    inferred_nproc_source = "explicit" if nproc is not None else "heuristic_default"
    layout_payload: dict[str, Any] | None = None
    nproc_warnings: list[str] = []

    if inferred_nproc is None:
        layout_result = infer_job_layout(job_script_path=job_script_path, run_dir=run_dir)
        if layout_result.get("ok") and layout_result.get("swmf_nproc") is not None:
            inferred_nproc = int(layout_result["swmf_nproc"])
            inferred_nproc_source = "job_script_inference"
            layout_payload = layout_result
        else:
            inferred_nproc = 64
            inferred_nproc_source = "heuristic_default"
            nproc_warnings.append("Could not infer nproc from job script; using heuristic default nproc=64.")

    assert inferred_nproc is not None

    recommended_components = _quickrun_mode_to_components(mode)
    build_plan = prepare_build(components_csv=",".join(recommended_components))

    prepare_run_plan = prepare_run(
        component_map_text=_quickrun_component_map(mode, inferred_nproc),
        nproc=inferred_nproc,
        description="MCP heuristic solar quickrun from GONG FITS metadata (non-authoritative; validate with Scripts/TestParam.pl)",
        time_accurate=(mode == "sc_ih_timeaccurate"),
        stop_value="7200.0" if mode == "sc_ih_timeaccurate" else "4000",
        include_restart=False,
        run_name=f"quick_{mode}",
        run_dir=run_dir,
        job_script_path=job_script_path,
    )

    template_kind = "solar_sc_ih" if mode in {"sc_ih_steady", "sc_ih_timeaccurate"} else "solar_sc"
    template_payload = generate_param_from_template(
        template_kind=template_kind,
        fits_path=fits_path,
        run_dir=run_dir,
        swmf_root_resolved=swmf_root_resolved,
        nproc=inferred_nproc,
    )

    minimal_component_map_param = str(prepare_run_plan.get("starter_param_in", "")) if prepare_run_plan.get("ok") else ""
    config_hint = prepare_component_config(param_text=minimal_component_map_param)

    from .param import default_quickrun_param_skeleton

    suggested_param_template_text = template_payload.get("suggested_param_text") or default_quickrun_param_skeleton(
        mode=mode,
        fits_path_resolved=inspect_result.get("fits_path_resolved"),
        nproc=inferred_nproc,
    )

    external_input_warnings: list[str] = []
    external_input_warnings.extend(list(inspect_result.get("warnings", [])))
    external_input_warnings.extend(nproc_warnings)
    if template_payload.get("template_found") is False:
        external_input_warnings.append("No solar PARAM template was found; returned a heuristic skeleton for manual review.")

    return {
        "ok": True,
        "heuristic": True,
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": template_payload.get("source_paths", []),
        "heuristic_fields": [
            "recommended_components",
            "inferred_nproc_when_not_explicit",
            "suggested_param_template_text",
            "solar_alignment_hints",
        ],
        "fits_inspection": inspect_result,
        "recommended_components": recommended_components,
        "recommended_config_pl_command": config_hint.get("recommended_config_command") or build_plan.get("suggested_commands", [None])[1],
        "recommended_build_steps": build_plan.get("suggested_commands", []),
        "recommended_run_steps": prepare_run_plan.get("suggested_commands", []),
        "inferred_nproc": inferred_nproc,
        "inferred_nproc_source": inferred_nproc_source,
        "job_layout": layout_payload,
        "suggested_param_template_text": suggested_param_template_text,
        "suggested_param_patch_summary": template_payload.get("suggested_param_patch_summary", []),
        "solar_alignment_hints": [
            "Heuristic: verify magnetogram coordinate convention (Carrington vs Stonyhurst) against SC setup.",
            "Heuristic: ensure map timestamp/carrington rotation matches your intended simulation window.",
            "Heuristic: confirm magnetogram polarity/sign conventions and units used by your SC component input parser.",
            "Authoritative checks still require Scripts/TestParam.pl and component documentation.",
        ],
        "external_input_warnings": external_input_warnings,
        "validation_plan": [
            "Run swmf_validate_external_inputs on the suggested PARAM text/path.",
            "Run swmf_validate_param for lightweight structure checks.",
            "Run swmf_run_testparam for authoritative SWMF validation.",
        ],
        "recommended_next_tool": "swmf_validate_external_inputs",
        "physics_authority_note": "This output is a deterministic heuristic preparation aid, not authoritative solar-physics validation.",
    }


def swmf_prepare_build(
    components_csv: str,
    compiler: str | None = None,
    debug: bool = False,
    optimization: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}
    return with_root(
        prepare_build(
            components_csv=components_csv,
            compiler=compiler,
            debug=debug,
            optimization=optimization,
        ),
        root,
    )


def swmf_prepare_component_config(
    param_text: str | None = None,
    param_path: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    loaded_text, resolved_param_path, load_error = load_param_text(param_text=param_text, param_path=param_path, run_dir=run_dir)
    if load_error is not None or loaded_text is None:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "message": load_error,
                "param_path_resolved": resolved_param_path,
            },
            root,
        )

    payload = prepare_component_config(param_text=loaded_text)
    payload["param_source"] = "param_text" if param_text is not None else "param_path"
    payload["param_path_resolved"] = resolved_param_path
    return with_root(payload, root)


def swmf_explain_component_config_fix() -> dict[str, Any]:
    payload = explain_component_config_fix()
    payload.setdefault("swmf_root_resolved", None)
    return payload


def swmf_infer_job_layout(
    job_script_path: str | None = None,
    run_dir: str | None = None,
    swmf_root: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}
    return with_root(infer_job_layout(job_script_path=job_script_path, run_dir=run_dir), root)


def swmf_prepare_run(
    component_map_text: str,
    nproc: int | None = None,
    description: str = "Prototype SWMF run",
    time_accurate: bool = True,
    stop_value: str = "3600.0",
    include_restart: bool = False,
    run_name: str = "run_demo",
    swmf_root: str | None = None,
    run_dir: str | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}
    return with_root(
        prepare_run(
            component_map_text=component_map_text,
            nproc=nproc,
            description=description,
            time_accurate=time_accurate,
            stop_value=stop_value,
            include_restart=include_restart,
            run_name=run_name,
            run_dir=run_dir,
            job_script_path=job_script_path,
        ),
        root,
    )


def swmf_detect_setup_commands(
    param_text: str | None = None,
    param_path: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    loaded_text, resolved_param_path, load_error = load_param_text(param_text=param_text, param_path=param_path, run_dir=run_dir)
    if load_error is not None or loaded_text is None:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "PARAM_LOAD_FAILED",
                "message": load_error,
            },
            root,
        )

    payload = detect_setup_commands(param_text=loaded_text)
    payload["param_source"] = "param_text" if param_text is not None else "param_path"
    payload["param_path_resolved"] = resolved_param_path
    return with_root(payload, root)


def swmf_apply_setup_commands(
    commands: list[str] | None = None,
    param_text: str | None = None,
    param_path: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    continue_on_error: bool = False,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    detected_payload: dict[str, Any] | None = None
    source = "explicit_commands"
    effective_commands = commands

    if effective_commands is None:
        loaded_text, _resolved_param_path, load_error = load_param_text(param_text=param_text, param_path=param_path, run_dir=run_dir)
        if load_error is not None or loaded_text is None:
            return with_root(
                {
                    "ok": False,
                    "hard_error": True,
                    "error_code": "PARAM_LOAD_FAILED",
                    "message": load_error,
                },
                root,
            )
        detected_payload = detect_setup_commands(param_text=loaded_text)
        effective_commands = list(detected_payload.get("commands", []))
        source = "detected_from_param"

    if not effective_commands:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "NO_SETUP_COMMANDS",
                "message": "No allowed setup commands were provided or detected.",
                "detection": detected_payload,
            },
            root,
        )

    payload = apply_setup_commands(
        swmf_root=root.swmf_root_resolved or str(Path.cwd()),
        commands=effective_commands,
        continue_on_error=continue_on_error,
    )
    payload["source"] = source
    payload["detection"] = detected_payload
    return with_root(payload, root)


def swmf_prepare_sc_quickrun_from_magnetogram(
    fits_path: str,
    run_dir: str | None = None,
    swmf_root: str | None = None,
    mode: str = "sc_steady",
    nproc: int | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    return with_root(
        prepare_sc_quickrun_from_magnetogram(
            fits_path=fits_path,
            swmf_root_resolved=root.swmf_root_resolved or str(Path.cwd()),
            run_dir=run_dir,
            mode=mode,
            nproc=nproc,
            job_script_path=job_script_path,
        ),
        root,
    )


def swmf_list_build_run_tool_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "hard_error": False,
        "authority": "authoritative",
        "source_kind": "implementation",
        "source_paths": ["src/swmf_mcp_server/tools/build_run.py"],
        "domain": "build_run",
        "tools": {
            "swmf_prepare_build": {
                "description": "Prepare SWMF build commands from component and compiler selections."
            },
            "swmf_prepare_component_config": {
                "description": "Prepare component configuration guidance from PARAM content."
            },
            "swmf_explain_component_config_fix": {
                "description": "Explain recommended fixes for component-configuration mismatches."
            },
            "swmf_infer_job_layout": {
                "description": "Infer MPI/job layout settings from job scripts or run context."
            },
            "swmf_prepare_run": {
                "description": "Prepare SWMF run commands and PARAM snippets from component map inputs."
            },
            "swmf_detect_setup_commands": {
                "description": "Detect allowed setup commands embedded in PARAM content."
            },
            "swmf_apply_setup_commands": {
                "description": "Apply allowed setup commands within the resolved SWMF root."
            },
            "swmf_prepare_sc_quickrun_from_magnetogram": {
                "description": "Prepare a heuristic SC quickrun plan from a magnetogram FITS file."
            },
        },
    }


def register(app: Any) -> None:
    app.tool(description="Prepare SWMF build commands from component and compiler selections.")(swmf_prepare_build)
    app.tool(description="Prepare component configuration guidance from PARAM content.")(swmf_prepare_component_config)
    app.tool(description="Explain recommended fixes for component-configuration mismatches.")(swmf_explain_component_config_fix)
    app.tool(description="Infer MPI/job layout settings from job scripts or run context.")(swmf_infer_job_layout)
    app.tool(description="Prepare SWMF run commands and PARAM snippets from component map inputs.")(swmf_prepare_run)
    app.tool(description="Detect allowed setup commands embedded in PARAM content.")(swmf_detect_setup_commands)
    app.tool(description="Apply allowed setup commands within the resolved SWMF root.")(swmf_apply_setup_commands)
    app.tool(description="Prepare a heuristic SC quickrun plan from a magnetogram FITS file.")(swmf_prepare_sc_quickrun_from_magnetogram)
    app.tool(description="List MCP tool capability contracts for SWMF build/run tooling.")(swmf_list_build_run_tool_capabilities)
