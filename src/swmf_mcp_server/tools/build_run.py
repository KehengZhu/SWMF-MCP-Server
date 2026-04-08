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
_SWMF_MAKEFILE_BUILD_TARGET_CANDIDATES = (
    "SWMF",
    "ALL",
    "LIB",
    "NOMPI",
    "PIDL",
    "PIONO",
    "PGITM",
    "SNAPSHOT",
    "INTERPOLATE",
    "EARTH_TRAJ",
)
_SWMF_MAKEFILE_RUN_TARGET_CANDIDATES = ("rundir", "rundir_code", "parallelrun", "serialrun")
_SWMF_MAKEFILE_DEFAULT_VARIABLES = ("CONFIG_PL", "SHELL", "NP", "RUNDIR")


def _extract_makefile_assignment(makefile_text: str, variable: str) -> str | None:
    pattern = rf"(?m)^\s*{re.escape(variable)}\s*[:+?]?=\s*(.+?)\s*$"
    match = re.search(pattern, makefile_text)
    if match is None:
        return None
    value = match.group(1).split("#", 1)[0].strip()
    return value or None


def _extract_makefile_targets(makefile_text: str) -> list[str]:
    targets: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"(?m)^([A-Za-z][A-Za-z0-9_]*)\s*:", makefile_text):
        target = match.group(1)
        if target in seen:
            continue
        seen.add(target)
        targets.append(target)
    return targets


def _extract_makefile_target_recipe(makefile_text: str, target: str) -> list[str]:
    lines = makefile_text.splitlines()
    start_index: int | None = None
    for index, line in enumerate(lines):
        if re.match(rf"^\s*{re.escape(target)}\s*:", line):
            start_index = index + 1
            break

    if start_index is None:
        return []

    recipe: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"^[A-Za-z][A-Za-z0-9_]*\s*:", line):
            break
        if line.startswith("\t") or line.startswith(" "):
            recipe.append(stripped)
            continue
        if stripped.startswith("#"):
            continue
        break
    return recipe


def _extract_config_help_block(config_text: str) -> str | None:
    marker = "Additional options for SWMF/Config.pl:"
    start = config_text.find(marker)
    if start < 0:
        return None

    end_marker = "#EOC"
    end = config_text.find(end_marker, start)
    if end < 0:
        end = len(config_text)
    return config_text[start:end]


def _extract_config_options(help_block: str) -> list[dict[str, str]]:
    options: list[dict[str, str]] = []
    lines = help_block.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        parts = stripped.split(None, 1)
        name = parts[0]
        summary = parts[1].strip() if len(parts) > 1 else ""
        detail = []
        for follow in lines[index + 1 :]:
            follow_stripped = follow.strip()
            if not follow_stripped:
                break
            if follow_stripped.startswith("-"):
                break
            detail.append(follow_stripped)
        options.append(
            {
                "name": name,
                "summary": summary,
                "details": " ".join(detail).strip(),
            }
        )
    return options


def _extract_config_examples(help_block: str) -> list[str]:
    examples: list[str] = []
    seen: set[str] = set()
    for line in help_block.splitlines():
        stripped = line.strip()
        if stripped.startswith("Config.pl "):
            if stripped not in seen:
                seen.add(stripped)
                examples.append(stripped)
    return examples


def _discover_swmf_config_guidance(swmf_root_resolved: str | None) -> dict[str, Any]:
    if swmf_root_resolved is None:
        return {
            "detected": False,
            "config_path": None,
            "options": [],
            "examples": [],
            "warnings": ["SWMF root was not provided for Config.pl guidance discovery."],
        }

    config_path = Path(swmf_root_resolved).expanduser().resolve() / "Config.pl"
    if not config_path.is_file():
        return {
            "detected": False,
            "config_path": str(config_path),
            "options": [],
            "examples": [],
            "warnings": [f"Config.pl was not found at {config_path}."],
        }

    try:
        config_text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "detected": False,
            "config_path": str(config_path),
            "options": [],
            "examples": [],
            "warnings": [f"Failed to read Config.pl: {exc}"],
        }

    help_block = _extract_config_help_block(config_text)
    if help_block is None:
        return {
            "detected": False,
            "config_path": str(config_path),
            "options": [],
            "examples": [],
            "warnings": ["Could not locate Config.pl help block for option guidance."],
        }

    return {
        "detected": True,
        "config_path": str(config_path),
        "options": _extract_config_options(help_block),
        "examples": _extract_config_examples(help_block),
        "warnings": [],
    }


def _discover_swmf_makefile_capabilities(swmf_root_resolved: str | None) -> dict[str, Any]:
    if swmf_root_resolved is None:
        return {
            "detected": False,
            "makefile_path": None,
            "capabilities": None,
            "warnings": ["SWMF root was not provided for Makefile capability discovery."],
        }

    makefile_path = Path(swmf_root_resolved).expanduser().resolve() / "Makefile"
    if not makefile_path.is_file():
        return {
            "detected": False,
            "makefile_path": str(makefile_path),
            "capabilities": None,
            "warnings": [f"SWMF Makefile was not found at {makefile_path}."],
        }

    try:
        makefile_text = makefile_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "detected": False,
            "makefile_path": str(makefile_path),
            "capabilities": None,
            "warnings": [f"Failed to read SWMF Makefile: {exc}"],
        }

    targets = _extract_makefile_targets(makefile_text)
    target_set = set(targets)
    default_variables: dict[str, str] = {}
    for key in _SWMF_MAKEFILE_DEFAULT_VARIABLES:
        value = _extract_makefile_assignment(makefile_text, key)
        if value is not None:
            default_variables[key.lower()] = value

    build_targets = [target for target in _SWMF_MAKEFILE_BUILD_TARGET_CANDIDATES if target in target_set]
    run_targets = [target for target in _SWMF_MAKEFILE_RUN_TARGET_CANDIDATES if target in target_set]
    recipe_targets = ["SWMF", "ALL", "rundir", "parallelrun", "serialrun", "rundir_code"]
    target_recipes = {
        target: _extract_makefile_target_recipe(makefile_text, target)
        for target in recipe_targets
        if _extract_makefile_target_recipe(makefile_text, target)
    }

    environment_prerequisites: list[str] = []
    if "include Makefile.def" in makefile_text:
        environment_prerequisites.append("SWMF Makefile includes Makefile.def; installation/configuration must provide it.")
    if "ENV_CHECK" in makefile_text:
        environment_prerequisites.append("ENV_CHECK target validates DIR/OS consistency before major build and run operations.")

    capabilities = {
        "targets": targets,
        "build_targets": build_targets,
        "run_targets": run_targets,
        "default_variables": default_variables,
        "is_notparallel": ".NOTPARALLEL" in makefile_text,
        "supports_machine_variable": "${MACHINE}" in makefile_text,
        "supports_np_variable": ("np" in default_variables) or ("${NP}" in makefile_text),
        "supports_rundir_variable": ("rundir" in default_variables) or ("${RUNDIR}" in makefile_text),
        "has_testparam_reference": "TestParam.pl" in makefile_text,
        "target_recipes": target_recipes,
        "environment_prerequisites": environment_prerequisites,
    }

    warnings: list[str] = []
    if "SWMF" not in target_set:
        warnings.append("SWMF Makefile does not expose the 'SWMF' build target; build recommendation may be incomplete.")
    if "rundir" not in target_set:
        warnings.append("SWMF Makefile does not expose 'rundir'; run directory setup suggestions may be generic.")

    return {
        "detected": True,
        "makefile_path": str(makefile_path),
        "capabilities": capabilities,
        "warnings": warnings,
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
    swmf_root_resolved: str | None = None,
) -> dict[str, Any]:
    makefile_discovery = _discover_swmf_makefile_capabilities(swmf_root_resolved=swmf_root_resolved)
    config_discovery = _discover_swmf_config_guidance(swmf_root_resolved=swmf_root_resolved)

    requested = _normalize_component_list(components_csv)
    if not requested:
        return {
            "ok": False,
            "message": "Provide at least one component version, e.g. GM/BATSRUS,IE/Ridley_serial",
        }

    version_list = ["Empty"] + [item for item in requested if item.lower() != "empty"]
    version_arg = ",".join(version_list)

    configure_commands: list[str] = []
    configure_commands.append(f"./Config.pl -install -compiler={compiler}" if compiler else "./Config.pl -install")
    configure_commands.append(f"Config.pl -v={version_arg}")

    if optimization is None:
        optimization = 0 if debug else 4

    configure_commands.append(f"Config.pl {'-debug' if debug else '-nodebug'} -O{optimization}")
    configure_commands.append("Config.pl -show")

    capabilities = makefile_discovery.get("capabilities")
    build_targets: list[str] = []
    if isinstance(capabilities, dict):
        build_targets = [str(item) for item in capabilities.get("build_targets", [])]

    recommended_make_build_target = "SWMF" if "SWMF" in build_targets else (build_targets[0] if build_targets else None)
    build_commands = [f"make {recommended_make_build_target}"] if recommended_make_build_target else ["make -j"]

    optional_make_targets: list[str] = []
    for target in ["ALL", "PIDL", "EARTH_TRAJ", "SNAPSHOT", "INTERPOLATE", "PIONO", "PGITM", "NOMPI"]:
        if target in build_targets and target != recommended_make_build_target:
            optional_make_targets.append(f"make {target}")

    commands = [*configure_commands, *build_commands]
    source_paths: list[str] = []
    makefile_path = makefile_discovery.get("makefile_path")
    if isinstance(makefile_path, str) and makefile_path:
        source_paths.append(makefile_path)
    config_path = config_discovery.get("config_path")
    if isinstance(config_path, str) and config_path:
        source_paths.append(config_path)

    notes = [
        "The prototype returns suggested commands only. It does not execute them.",
        "Putting Empty first follows standard SWMF usage for 'all empty except selected components'.",
        "After changing compiler flags, a real workflow may also need make clean before recompiling.",
    ]
    if isinstance(capabilities, dict) and bool(capabilities.get("is_notparallel")):
        notes.append("SWMF Makefile declares .NOTPARALLEL, so target-based make invocations are preferred over generic parallel make calls.")

    variable_guidance = {
        "COMPONENTS": {
            "selected": requested,
            "description": "Component versions passed to Config.pl -v. Keep Empty plus explicitly required non-empty components.",
            "how_to_override": "Set components_csv with authoritative component/version pairs for your build.",
        },
        "COMPILER": {
            "selected": compiler,
            "description": "Compiler selection influences module/toolchain compatibility and MPI wrappers.",
            "how_to_override": "Pass compiler explicitly to swmf_prepare_build or run Config.pl manually.",
        },
        "OPTIMIZATION": {
            "selected": optimization,
            "description": "Optimization level is a heuristic default when not explicitly provided.",
            "how_to_override": "Set optimization directly when preparing build guidance.",
        },
        "DEBUG": {
            "selected": debug,
            "description": "Debug mode toggles Config.pl debug flags and can change runtime behavior/performance.",
            "how_to_override": "Set debug=True for diagnostic builds.",
        },
    }

    makefile_target_recipes: dict[str, list[str]] = {}
    environment_prerequisites: list[str] = []
    if isinstance(capabilities, dict):
        makefile_target_recipes = {
            str(key): [str(item) for item in value]
            for key, value in dict(capabilities.get("target_recipes", {})).items()
            if isinstance(value, list)
        }
        environment_prerequisites = [str(item) for item in capabilities.get("environment_prerequisites", [])]

    config_option_reference = [
        {
            "name": str(item.get("name", "")),
            "summary": str(item.get("summary", "")),
            "details": str(item.get("details", "")),
        }
        for item in config_discovery.get("options", [])
        if isinstance(item, dict)
    ]
    config_examples = [str(item) for item in config_discovery.get("examples", [])]

    target_detection = "detected" if bool(makefile_discovery.get("detected", False)) else "not_detected"
    decision_branches = [
        {
            "name": "makefile_target_build",
            "when": "SWMF Makefile capabilities are detected and a preferred build target is available.",
            "action": "Use recommended_make_build_target and optional_command_examples.build as optional examples.",
            "status": "available" if recommended_make_build_target is not None else "unavailable",
            "target_detection": target_detection,
        },
        {
            "name": "generic_parallel_build",
            "when": "No authoritative build target is detected.",
            "action": "Use make -j style examples and adapt for local compiler/MPI environment.",
            "status": "fallback",
            "target_detection": target_detection,
        },
    ]

    workflow_guidance = [
        "Treat command outputs as optional examples and validate SWMF Makefile targets/variables in your environment first.",
        "Confirm component version selections satisfy PARAM-inferred active components before rebuilding.",
        "Use decision_branches to choose target-based or generic build strategy, then run validation checks in your local workflow.",
    ]

    assumptions: list[str] = []
    if not bool(makefile_discovery.get("detected", False)):
        assumptions.append("SWMF Makefile capability discovery was unavailable; build recommendations may rely on generic defaults.")
    if compiler is None:
        assumptions.append("Compiler was not explicitly provided; install/config commands use Config.pl defaults.")
    if not bool(config_discovery.get("detected", False)):
        assumptions.append("Config.pl help guidance could not be fully extracted; option/exemplar teaching may be limited.")

    return {
        "ok": True,
        "guidance_mode": "instruction_first",
        "selected_components": requested,
        "config_pl_v_argument": version_arg,
        "recommended_make_build_target": recommended_make_build_target,
        "swmf_makefile_detected": bool(makefile_discovery.get("detected", False)),
        "swmf_makefile_path": makefile_path,
        "swmf_makefile_capabilities": capabilities,
        "swmf_config_guidance_detected": bool(config_discovery.get("detected", False)),
        "swmf_config_path": config_path,
        "warnings": [
            *list(makefile_discovery.get("warnings", [])),
            *list(config_discovery.get("warnings", [])),
        ],
        "workflow_guidance": workflow_guidance,
        "decision_branches": decision_branches,
        "variable_guidance": variable_guidance,
        "makefile_target_recipes": makefile_target_recipes,
        "config_option_reference": config_option_reference,
        "config_examples": config_examples,
        "environment_prerequisites": environment_prerequisites,
        "assumptions": assumptions,
        "optional_command_examples": {
            "full_sequence": commands,
            "configure": configure_commands,
            "build": build_commands,
            "optional_targets": optional_make_targets,
        },
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": source_paths,
        "notes": notes,
    }


def prepare_component_config(
    param_text: str,
) -> dict[str, Any]:
    parsed = parse_param_text(param_text)
    recommendation = _build_component_config_recommendation(_infer_required_components_from_sessions(parsed.sessions))
    workflow_guidance = [
        "Use required_components as a discovery result, then reconcile with component catalogs and site-specific build availability.",
        "Treat recommended_config_command as an optional template before executing in your SWMF root.",
    ]
    return {
        "ok": True,
        "guidance_mode": "instruction_first",
        "authority": "heuristic",
        "source_kind": "lightweight_parser",
        "source_paths": [],
        "required_components": recommendation["required_components"],
        "recommended_component_versions": recommendation["recommended_component_versions"],
        "components_without_default_mapping": recommendation["components_without_default_mapping"],
        "recommended_config_command": recommendation["recommended_config_command"],
        "rebuild_commands": recommendation["rebuild_commands"],
        "workflow_guidance": workflow_guidance,
        "optional_command_examples": {
            "recommended_config_command": recommendation["recommended_config_command"],
            "rebuild_commands": recommendation["rebuild_commands"],
        },
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
    swmf_root_resolved: str | None = None,
) -> dict[str, Any]:
    makefile_discovery = _discover_swmf_makefile_capabilities(swmf_root_resolved=swmf_root_resolved)
    config_discovery = _discover_swmf_config_guidance(swmf_root_resolved=swmf_root_resolved)

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

    capabilities = makefile_discovery.get("capabilities")
    has_rundir = bool(isinstance(capabilities, dict) and ("rundir" in set(capabilities.get("run_targets", []))))
    has_serialrun = bool(isinstance(capabilities, dict) and ("serialrun" in set(capabilities.get("run_targets", []))))
    has_parallelrun = bool(isinstance(capabilities, dict) and ("parallelrun" in set(capabilities.get("run_targets", []))))
    supports_machine = bool(isinstance(capabilities, dict) and capabilities.get("supports_machine_variable"))

    run_dir_command = "make rundir"
    if has_rundir and run_name != "run":
        run_dir_command = f"make rundir RUNDIR={shlex.quote(run_name)}"

    run_param_path = f"{run_name}/PARAM.in"
    run_sequence = [
        run_dir_command,
        f"# From SWMF_ROOT: ./Scripts/TestParam.pl -n={nproc} {run_param_path}",
        f"cd {run_name}",
    ]

    if not has_rundir and run_name != "run":
        run_sequence.insert(1, f"mv run {run_name}")
    elif has_rundir and run_name == "run":
        run_param_path = "run/PARAM.in"
        run_sequence[1] = f"# From SWMF_ROOT: ./Scripts/TestParam.pl -n={nproc} {run_param_path}"
        run_sequence[2] = "cd run"

    local_execution_commands: list[str] = []
    if has_serialrun:
        local_execution_commands.append(f"make serialrun RUNDIR={shlex.quote(run_name)}")
    if has_parallelrun:
        local_execution_commands.append(f"make parallelrun NP={nproc} RUNDIR={shlex.quote(run_name)}")

    run_warnings = list(makefile_discovery.get("warnings", []))
    if has_rundir and not has_serialrun and not has_parallelrun:
        run_warnings.append("SWMF Makefile provides rundir but not serialrun/parallelrun targets; scheduler execution guidance remains manual.")

    source_paths: list[str] = []
    makefile_path = makefile_discovery.get("makefile_path")
    if isinstance(makefile_path, str) and makefile_path:
        source_paths.append(makefile_path)
    config_path = config_discovery.get("config_path")
    if isinstance(config_path, str) and config_path:
        source_paths.append(config_path)

    target_detection = "detected" if bool(makefile_discovery.get("detected", False)) else "not_detected"
    workflow_guidance = [
        "Treat suggested run commands as optional examples and verify run directory naming/paths in your deployment context.",
        "Always run TestParam.pl from SWMF root before submission; do not assume planner output is authoritative runtime validation.",
        "Use local_execution command examples only when they match your available Makefile run targets.",
    ]
    decision_branches = [
        {
            "name": "makefile_rundir_path",
            "when": "Makefile exposes rundir target.",
            "action": "Use make rundir (optionally with RUNDIR override) before validation and execution.",
            "status": "available" if has_rundir else "unavailable",
            "target_detection": target_detection,
        },
        {
            "name": "manual_run_directory_path",
            "when": "rundir target is unavailable.",
            "action": "Create/rename run directory manually and update PARAM path used by TestParam.pl.",
            "status": "fallback" if not has_rundir else "available",
            "target_detection": target_detection,
        },
    ]
    variable_guidance = {
        "NPROC": {
            "selected": nproc,
            "source": nproc_source,
            "description": "MPI process count used by TestParam and parallel run examples.",
            "how_to_override": "Provide nproc explicitly or update job-script inference inputs.",
        },
        "RUN_NAME": {
            "selected": run_name,
            "description": "Run directory stem used to place PARAM.in and execution artifacts.",
            "how_to_override": "Pass run_name explicitly and confirm directory layout in your filesystem.",
        },
        "TIME_ACCURATE": {
            "selected": time_accurate,
            "description": "Switches STOP block semantics between simulation time and iteration-count control.",
            "how_to_override": "Set time_accurate according to scenario requirements.",
        },
    }

    makefile_target_recipes: dict[str, list[str]] = {}
    environment_prerequisites: list[str] = []
    if isinstance(capabilities, dict):
        makefile_target_recipes = {
            str(key): [str(item) for item in value]
            for key, value in dict(capabilities.get("target_recipes", {})).items()
            if isinstance(value, list)
        }
        environment_prerequisites = [str(item) for item in capabilities.get("environment_prerequisites", [])]

    config_option_reference = [
        {
            "name": str(item.get("name", "")),
            "summary": str(item.get("summary", "")),
            "details": str(item.get("details", "")),
        }
        for item in config_discovery.get("options", [])
        if isinstance(item, dict)
    ]
    config_examples = [str(item) for item in config_discovery.get("examples", [])]

    assumptions: list[str] = []
    if nproc_source == "heuristic_default":
        assumptions.append("nproc used a heuristic fallback; validate MPI layout with scheduler/job script before execution.")
    if not has_rundir:
        assumptions.append("Makefile rundir target is unavailable; command examples include manual directory handling fallback.")
    if not bool(config_discovery.get("detected", False)):
        assumptions.append("Config.pl guidance was not fully discoverable; verify configuration options with local Config.pl -help output.")

    return {
        "ok": True,
        "guidance_mode": "instruction_first",
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": [],
        "nproc": nproc,
        "nproc_source": nproc_source,
        "job_layout": inferred_layout,
        "run_name": run_name,
        "time_accurate": time_accurate,
        "starter_param_in": param_in,
        "testparam_constraint": "TestParam.pl must be run from SWMF_ROOT, not from the run directory.",
        "swmf_makefile_detected": bool(makefile_discovery.get("detected", False)),
        "swmf_makefile_path": makefile_path,
        "swmf_makefile_capabilities": capabilities,
        "swmf_config_guidance_detected": bool(config_discovery.get("detected", False)),
        "swmf_config_path": config_path,
        "warnings": [*run_warnings, *list(config_discovery.get("warnings", []))],
        "workflow_guidance": workflow_guidance,
        "decision_branches": decision_branches,
        "variable_guidance": variable_guidance,
        "makefile_target_recipes": makefile_target_recipes,
        "config_option_reference": config_option_reference,
        "config_examples": config_examples,
        "environment_prerequisites": environment_prerequisites,
        "assumptions": assumptions,
        "optional_command_examples": {
            "full_sequence": run_sequence,
            "prepare": [run_sequence[0]],
            "validate": [run_sequence[1]],
            "enter_run_dir": [run_sequence[-1]],
            "local_execution": local_execution_commands,
        },
        "testparam_full_command_example": f"cd SWMF_ROOT && ./Scripts/TestParam.pl -n={nproc} $(pwd)/{run_name}/PARAM.in",
        "requires_manual_submission": True,
        "auto_submit_permitted": False,
        "suggested_manual_submission": [
            "Edit your scheduler job script (for example job.frontera) for this run directory.",
            "Ensure the script uses SWMF.exe and the intended MPI layout.",
            "Submit manually (example): sbatch job.frontera",
        ],
        "source_paths": source_paths,
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
            swmf_root_resolved=root.swmf_root_resolved,
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
            swmf_root_resolved=root.swmf_root_resolved,
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


def register(app: Any) -> None:
    app.tool(description="Prepare guidance-first SWMF build planning from component and compiler selections.")(swmf_prepare_build)
    app.tool(description="Prepare component configuration guidance from PARAM content.")(swmf_prepare_component_config)
    app.tool(description="Explain recommended fixes for component-configuration mismatches.")(swmf_explain_component_config_fix)
    app.tool(description="Infer MPI/job layout settings from job scripts or run context.")(swmf_infer_job_layout)
    app.tool(description="Prepare guidance-first SWMF run planning and PARAM snippets from component map inputs.")(swmf_prepare_run)
    app.tool(description="Detect allowed setup commands embedded in PARAM content.")(swmf_detect_setup_commands)
    app.tool(description="Apply allowed setup commands within the resolved SWMF root.")(swmf_apply_setup_commands)
