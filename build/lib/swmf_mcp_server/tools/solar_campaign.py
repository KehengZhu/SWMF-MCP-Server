from __future__ import annotations

import re
import shlex
from collections import OrderedDict
from pathlib import Path
from typing import Any

from ..core.common import build_path_search_guidance, resolve_run_dir


_SUPPORTED_MODELS = {"AWSoM", "AWSoM2T", "AWSoMR", "AWSoMR_SOFIE"}
_SWMFSOLAR_QUICKRUN_TARGETS = [
    "adapt_run",
    "compile",
    "backup_run",
    "copy_param",
    "rundir_realizations",
    "clean_rundir_tmp",
    "run",
]
_SWMFSOLAR_DEFAULT_VARIABLES = (
    "MODEL",
    "MACHINE",
    "PFSS",
    "TIME",
    "MAP",
    "PARAM",
    "REALIZATIONS",
    "POYNTINGFLUX",
    "JOBNAME",
    "DOINSTALL",
)


def _parse_int_list_expression(expr: str) -> tuple[list[int], str | None]:
    values: list[int] = []
    seen: set[int] = set()

    for part in [item.strip() for item in expr.split(",") if item.strip()]:
        if "-" in part:
            bounds = [item.strip() for item in part.split("-", 1)]
            if len(bounds) != 2:
                return [], f"Invalid range token '{part}'."
            try:
                start = int(bounds[0])
                end = int(bounds[1])
            except ValueError:
                return [], f"Range token '{part}' must contain integers."
            if end < start:
                return [], f"Range token '{part}' has end < start."
            for value in range(start, end + 1):
                if value not in seen:
                    seen.add(value)
                    values.append(value)
            continue

        try:
            value = int(part)
        except ValueError:
            return [], f"Token '{part}' must be an integer or range."
        if value not in seen:
            seen.add(value)
            values.append(value)

    if not values:
        return [], "No integer IDs were parsed from the expression."
    return values, None


def _parse_realization_value(value: str) -> tuple[list[int], str | None]:
    local = value.strip()
    if local.startswith("[") and local.endswith("]"):
        local = local[1:-1]
    return _parse_int_list_expression(local)


def _infer_default_realizations(map_name: str) -> tuple[list[int], str]:
    lowered = map_name.strip().lower()
    if lowered == "nomap":
        return list(range(1, 13)), "nomap_default_adapt"
    if "adapt" in lowered:
        return list(range(1, 13)), "map_type_adapt"
    if "gong" in lowered:
        return [1], "map_type_gong"
    return [1], "fallback_single_realization"


def _normalize_event_run(run_id: int, tokens: list[str], raw_line: str) -> dict[str, Any]:
    map_value = "NoMap"
    pfss = "HARMONICS"
    time_value = "MapTime"
    model = "AWSoM"
    param = "Default"
    scheme = 2
    restartdir: str | None = None
    realization_list: list[int] | None = None

    add: list[str] = []
    rm: list[str] = []
    replace: dict[str, str] = {}
    change: dict[str, str] = {}
    warnings: list[str] = []

    for token in tokens:
        if "=" not in token:
            warnings.append(f"Ignored malformed token without '=': {token}")
            continue

        name, value = token.split("=", 1)
        key = name.strip()
        key_lower = key.lower()
        value = value.strip()

        if key_lower == "map":
            map_value = value
            continue
        if key_lower == "pfss":
            pfss = value
            continue
        if key_lower == "time":
            time_value = value
            continue
        if key_lower == "model":
            model = value
            continue
        if key_lower == "param":
            param = value
            continue
        if key_lower == "scheme":
            try:
                scheme = int(value)
            except ValueError:
                warnings.append(f"Could not parse scheme as integer: {value}")
            continue
        if key_lower == "restartdir":
            restartdir = value
            continue
        if key_lower in {"realization", "realizations"}:
            parsed_realizations, parse_error = _parse_realization_value(value)
            if parse_error is not None:
                warnings.append(f"Could not parse realization list '{value}': {parse_error}")
            else:
                realization_list = parsed_realizations
            continue

        if key == "add":
            add.extend([item.strip() for item in value.split(",") if item.strip()])
            continue
        if key == "rm":
            rm.extend([item.strip() for item in value.split(",") if item.strip()])
            continue

        if value.startswith("[") and value.endswith("]"):
            replace[key] = value[1:-1]
            continue

        if key == "GridResolution":
            continue

        change[key] = value

    if realization_list is None:
        realization_list, realization_source = _infer_default_realizations(map_value)
    else:
        realization_source = "explicit"

    if model not in _SUPPORTED_MODELS:
        warnings.append(
            f"Model '{model}' is not in the SWMFSOLAR supported list: {', '.join(sorted(_SUPPORTED_MODELS))}."
        )

    if map_value != "NoMap" and ("adapt" not in map_value.lower()) and ("gong" not in map_value.lower()):
        warnings.append(
            "Map name is neither ADAPT nor GONG. SWMFSOLAR event-list workflows usually expect these map families."
        )

    return {
        "run_id": run_id,
        "model": model,
        "map": map_value,
        "pfss": pfss,
        "time": time_value,
        "param": param,
        "scheme": scheme,
        "restartdir": restartdir,
        "realizations": realization_list,
        "realizations_source": realization_source,
        "realizations_expression": ",".join(str(value) for value in realization_list),
        "param_mutations": {
            "add": add,
            "rm": rm,
            "replace": replace,
            "change": change,
        },
        "raw_tokens": tokens,
        "raw_line": raw_line,
        "warnings": warnings,
    }


def _extract_selected_ids(lines: list[str], selected_run_ids: str | None) -> tuple[list[int], str | None, str, str | None]:
    if selected_run_ids is not None and selected_run_ids.strip():
        parsed, error = _parse_int_list_expression(selected_run_ids.strip())
        return parsed, selected_run_ids.strip(), "override", error

    for line in lines:
        if line.strip().lower().startswith("selected run ids") and "=" in line:
            expression = line.split("=", 1)[1].strip()
            parsed, error = _parse_int_list_expression(expression)
            return parsed, expression, "event_list", error

    return [], None, "event_list", "Could not find 'selected run IDs = ...' in event list."


def _find_start_index(lines: list[str]) -> int | None:
    for index, line in enumerate(lines):
        if line.strip().lower().startswith("#start"):
            return index + 1
    return None


def _parse_event_list_text(
    event_list_text: str,
    selected_run_ids: str | None,
    source_path: str | None,
) -> dict[str, Any]:
    lines = event_list_text.splitlines()
    selected_ids, selected_expression, selected_source, selected_error = _extract_selected_ids(lines, selected_run_ids)
    if selected_error is not None:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "SELECTED_RUN_IDS_PARSE_FAILED",
            "message": selected_error,
            "event_list_path_resolved": source_path,
            "selected_run_ids_expression": selected_expression,
            "selected_run_ids_source": selected_source,
        }

    start_index = _find_start_index(lines)
    if start_index is None:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "EVENT_LIST_START_MARKER_NOT_FOUND",
            "message": "Could not find '#START' marker in event list.",
            "event_list_path_resolved": source_path,
            "selected_run_ids": selected_ids,
        }

    parsed_runs: list[dict[str, Any]] = []
    warnings: list[str] = []

    for line in lines[start_index:]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue

        tokens = shlex.split(stripped, comments=False, posix=True)
        if not tokens:
            continue
        if tokens[0].lower() in {"id", "runid", "run_id"}:
            continue

        try:
            run_id = int(tokens[0])
        except ValueError:
            warnings.append(f"Skipped line because first token is not an integer run ID: {stripped}")
            continue

        normalized = _normalize_event_run(run_id=run_id, tokens=tokens[1:], raw_line=stripped)
        parsed_runs.append(normalized)

    run_by_id = {entry["run_id"]: entry for entry in parsed_runs}
    selected_entries: list[dict[str, Any]] = []
    missing_selected_ids: list[int] = []
    for run_id in selected_ids:
        if run_id in run_by_id:
            selected_entries.append(run_by_id[run_id])
        else:
            missing_selected_ids.append(run_id)

    if missing_selected_ids:
        warnings.append(
            "Selected run IDs were not found in the event table: "
            + ",".join(str(value) for value in missing_selected_ids)
        )

    for item in selected_entries:
        warnings.extend(item.get("warnings", []))

    return {
        "ok": True,
        "phase": "parse",
        "event_list_path_resolved": source_path,
        "selected_run_ids": selected_ids,
        "selected_run_ids_expression": selected_expression,
        "selected_run_ids_source": selected_source,
        "all_run_ids": sorted(run_by_id),
        "available_run_count": len(run_by_id),
        "selected_run_count": len(selected_entries),
        "selected_runs": selected_entries,
        "warnings": warnings,
        "authority": "derived",
        "source_kind": "script",
        "source_paths": [source_path] if source_path else [],
    }


def _load_event_list_text(
    event_list_path: str | None,
    event_list_text: str | None,
    run_dir: str | None,
) -> tuple[str | None, str | None, str | None]:
    if event_list_text is not None:
        return event_list_text, None, None

    base_dir = resolve_run_dir(run_dir)
    candidates: list[Path] = []
    if event_list_path is not None:
        candidate = Path(event_list_path).expanduser()
        if not candidate.is_absolute():
            candidate = base_dir / candidate
        candidates.append(candidate.resolve())
    else:
        candidates.extend(
            [
                (base_dir / "param_list.txt").resolve(),
                (base_dir / "Events" / "param_list.txt").resolve(),
                (base_dir / "SWMFSOLAR" / "Events" / "param_list.txt").resolve(),
            ]
        )

    for candidate in candidates:
        if candidate.is_file():
            try:
                return candidate.read_text(encoding="utf-8"), str(candidate), None
            except OSError as exc:
                return None, str(candidate), f"Failed to read event list file: {exc}"

    if event_list_path is not None:
        return None, str(candidates[0]), f"Event list path does not point to a file: {candidates[0]}"
    return None, None, "Could not find a default event list. Pass event_list_text or event_list_path."


def _resolve_swmfsolar_root(event_list_path_resolved: str | None, run_dir: str | None) -> str | None:
    if event_list_path_resolved:
        event_path = Path(event_list_path_resolved)
        parent = event_path.parent
        if (parent / "Makefile").is_file() and (parent / "Scripts").is_dir():
            return str(parent.resolve())
        if parent.name == "Events":
            candidate = parent.parent
            if (candidate / "Makefile").is_file() and (candidate / "Scripts").is_dir():
                return str(candidate.resolve())

    base_dir = resolve_run_dir(run_dir)
    candidates = [base_dir / "SWMFSOLAR", base_dir]
    for candidate in candidates:
        if (candidate / "Makefile").is_file() and (candidate / "Scripts").is_dir():
            return str(candidate.resolve())
    return None


def parse_solar_event_list(
    event_list_path: str | None = None,
    event_list_text: str | None = None,
    selected_run_ids: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    loaded_text, resolved_path, load_error = _load_event_list_text(
        event_list_path=event_list_path,
        event_list_text=event_list_text,
        run_dir=run_dir,
    )
    if load_error is not None or loaded_text is None:
        search_roots = [resolve_run_dir(run_dir), resolve_run_dir(run_dir).parent]
        expected_entries = ["param_list.txt", "Events", "SWMFSOLAR"]
        if event_list_path is not None:
            requested = Path(event_list_path).expanduser()
            requested_name = requested.name
            if requested_name:
                expected_entries.insert(0, requested_name)
            if requested.is_absolute():
                search_roots.append(requested.parent)
        if resolved_path is not None:
            resolved = Path(resolved_path)
            search_roots.append(resolved.parent)

        path_guidance = build_path_search_guidance(
            path_role="event_list_path",
            search_roots=search_roots,
            expected_entries=expected_entries,
            keyword_hints=["event", "events", "param_list", "swmfsolar", *( [requested_name] if event_list_path is not None and requested_name else [] )],
        )
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "EVENT_LIST_LOAD_FAILED",
            "message": load_error,
            "event_list_path_resolved": resolved_path,
            "how_to_fix": [
                "Pass event_list_text directly.",
                "Or pass event_list_path to an existing event list file.",
            ],
            **path_guidance,
        }

    payload = _parse_event_list_text(
        event_list_text=loaded_text,
        selected_run_ids=selected_run_ids,
        source_path=resolved_path,
    )
    payload.setdefault("run_dir_resolved", str(resolve_run_dir(run_dir)))
    return payload


def _build_simdir(run_id: int, model: str, restartdir: str | None) -> str:
    simdir = f"run{run_id:03d}_{model}"
    if restartdir:
        simdir = f"{simdir}_restart_{restartdir.replace('/', '_')}"
    return simdir


def _extract_named_token_value(raw_tokens: list[str], key: str) -> str | None:
    key_lower = key.lower()
    for token in raw_tokens:
        if "=" not in token:
            continue
        name, value = token.split("=", 1)
        if name.strip().lower() != key_lower:
            continue

        local = value.strip()
        if local.startswith("[") and local.endswith("]"):
            local = local[1:-1].strip()
        return local or None
    return None


def _token_has_named_value(raw_tokens: list[str], key: str) -> bool:
    key_lower = key.lower()
    for token in raw_tokens:
        if "=" not in token:
            continue
        name, _value = token.split("=", 1)
        if name.strip().lower() == key_lower:
            return True
    return False


def _plan_single_run(
    entry: dict[str, Any],
    include_submit_commands: bool,
    makefile_default_variables: dict[str, str] | None = None,
    include_adapt_run_commands: bool = False,
    adapt_run_target_detected: bool | None = None,
) -> dict[str, Any]:
    run_id = int(entry["run_id"])
    model = str(entry["model"])
    pfss = str(entry["pfss"])
    map_value = str(entry["map"])
    time_value = str(entry["time"])
    param = str(entry["param"])
    restartdir = entry.get("restartdir")

    realizations = [int(value) for value in entry.get("realizations", [])]
    realization_expr = ",".join(str(value) for value in realizations)
    simdir = _build_simdir(run_id=run_id, model=model, restartdir=restartdir)

    make_vars: OrderedDict[str, str] = OrderedDict()
    make_vars["SIMDIR"] = simdir
    make_vars["MODEL"] = model
    make_vars["PARAM"] = param
    make_vars["PFSS"] = pfss
    make_vars["MAP"] = map_value
    make_vars["TIME"] = time_value
    if realization_expr:
        make_vars["REALIZATIONS"] = realization_expr

    raw_tokens = [str(token) for token in entry.get("raw_tokens", [])]
    default_variables = makefile_default_variables or {}
    poyntingflux = _extract_named_token_value(raw_tokens, "POYNTINGFLUX") or default_variables.get("poyntingflux", "-1.0")
    machine = _extract_named_token_value(raw_tokens, "MACHINE") or default_variables.get("machine")
    jobname = _extract_named_token_value(raw_tokens, "JOBNAME") or default_variables.get("jobname", f"r{run_id:02d}_")

    prepare_shell = [
        "make backup_run " + " ".join(f"{key}={value}" for key, value in make_vars.items() if key == "SIMDIR"),
        "make copy_param " + " ".join(f"{key}={value}" for key, value in make_vars.items() if key in {"MODEL", "PARAM"}),
        "make rundir_realizations "
        + " ".join(
            f"{key}={value}" for key, value in make_vars.items() if key in {"SIMDIR", "REALIZATIONS", "PFSS", "MODEL"}
        ),
        "make clean_rundir_tmp",
    ]

    submit_shell: list[str] = []
    if include_submit_commands:
        submit_vars: OrderedDict[str, str] = OrderedDict()
        submit_vars["SIMDIR"] = simdir
        submit_vars["PFSS"] = pfss
        if realization_expr:
            submit_vars["REALIZATIONS"] = realization_expr
        submit_vars["JOBNAME"] = jobname
        submit_shell.append("make run " + " ".join(f"{key}={value}" for key, value in submit_vars.items()))

    adapt_run_shell: list[str] = []
    if include_adapt_run_commands and include_submit_commands:
        adapt_run_vars: OrderedDict[str, str] = OrderedDict()
        adapt_run_vars["MODEL"] = model
        adapt_run_vars["SIMDIR"] = simdir
        adapt_run_vars["REALIZATIONS"] = realization_expr or "1"
        adapt_run_vars["MAP"] = map_value
        adapt_run_vars["TIME"] = time_value
        adapt_run_vars["PFSS"] = pfss
        adapt_run_vars["POYNTINGFLUX"] = poyntingflux
        if machine:
            adapt_run_vars["MACHINE"] = machine
        adapt_run_vars["JOBNAME"] = jobname
        adapt_run_shell.append(
            "make adapt_run " + " ".join(f"{key}={shlex.quote(value)}" for key, value in adapt_run_vars.items())
        )

    non_shell_steps = [
        {
            "kind": "change_awsom_param",
            "summary": "Apply SWMFSOLAR param mutation semantics (add/rm/replace/change) before rundir generation.",
            "inputs": {
                "time": time_value,
                "map": map_value,
                "pfss": pfss,
                "scheme": entry.get("scheme"),
                "do_restart": bool(restartdir),
                "param_mutations": entry.get("param_mutations", {}),
            },
        }
    ]

    key_params_preview = [
        f"model={model}",
        f"map={map_value}",
        f"pfss={pfss}",
        f"time={time_value}",
        f"param={param}",
        f"realizations={realization_expr or '1'}",
    ]
    if restartdir:
        key_params_preview.append(f"restartdir={restartdir}")

    variable_guidance = {
        "MODEL": {
            "selected": model,
            "source": "event_list_token" if _token_has_named_value(raw_tokens, "model") else "default_or_inferred",
            "description": "Selects the SWMFSOLAR model family used by make targets and copied PARAM defaults.",
            "how_to_override": "Set model=<value> in event list or pass a model hint at tool entry points that support overrides.",
        },
        "MAP": {
            "selected": map_value,
            "source": "event_list_token" if _token_has_named_value(raw_tokens, "map") else "default_or_inferred",
            "description": "Magnetogram/map path or selector consumed by change_awsom_param workflow.",
            "how_to_override": "Set map=<value> in event list; ensure the path resolves in SWMFSOLAR runtime context.",
        },
        "PFSS": {
            "selected": pfss,
            "source": "event_list_token" if _token_has_named_value(raw_tokens, "pfss") else "makefile_or_tool_default",
            "description": "Coronal field extrapolation selector (typically HARMONICS or FDIPS).",
            "how_to_override": "Set pfss=<value> in event list or override via Makefile variables during make invocation.",
        },
        "REALIZATIONS": {
            "selected": realization_expr or "1",
            "source": str(entry.get("realizations_source", "default_or_inferred")),
            "description": "Realization IDs to expand into run directories.",
            "how_to_override": "Set realizations=<csv_or_ranges> in event list, for example realization=[1,2-4].",
        },
        "SIMDIR": {
            "selected": simdir,
            "source": "derived_from_run_id_and_model",
            "description": "Per-run output directory stem used by backup/rundir/run targets.",
            "how_to_override": "Adjust run naming conventions upstream or post-process generated plans before execution.",
        },
        "JOBNAME": {
            "selected": jobname,
            "source": "event_list_token"
            if _token_has_named_value(raw_tokens, "jobname")
            else ("makefile_default" if "jobname" in default_variables else "tool_default"),
            "description": "Scheduler-visible job label passed to make run/adapt_run paths.",
            "how_to_override": "Set JOBNAME=<value> in event list tokens or SWMFSOLAR Makefile defaults.",
        },
    }

    adapt_detection = "unknown"
    if adapt_run_target_detected is True:
        adapt_detection = "detected"
    elif adapt_run_target_detected is False:
        adapt_detection = "not_detected"

    decision_branches = [
        {
            "name": "prefer_adapt_run",
            "when": "Makefile target adapt_run exists and submit commands are enabled.",
            "action": "Use make adapt_run as a compact orchestration path.",
            "status": "available" if (include_submit_commands and include_adapt_run_commands) else "disabled",
            "target_detection": adapt_detection,
        },
        {
            "name": "manual_prepare_then_submit",
            "when": "adapt_run is unavailable or you need step-by-step debugging.",
            "action": "Run backup_run -> copy_param -> rundir_realizations -> clean_rundir_tmp, then run.",
            "status": "available" if include_submit_commands else "prepare_only",
            "target_detection": adapt_detection,
        },
    ]

    workflow_guidance = [
        "Interpret this run plan as guidance-first: validate variables and target availability before shell execution.",
        "Choose between adapt_run and manual prepare/submit branches using decision_branches and Makefile capabilities.",
        "Apply planned_non_shell_steps before or alongside shell steps to keep PARAM mutations consistent.",
    ]

    return {
        "run_id": run_id,
        "simdir": simdir,
        "model": model,
        "pfss": pfss,
        "map": map_value,
        "time": time_value,
        "param": param,
        "restartdir": restartdir,
        "realizations": realizations,
        "realizations_expression": realization_expr,
        "param_mutations": entry.get("param_mutations", {}),
        "make_variables": dict(make_vars),
        "key_params_preview": key_params_preview,
        "workflow_guidance": workflow_guidance,
        "decision_branches": decision_branches,
        "variable_guidance": variable_guidance,
        "optional_command_examples": {
            "full_sequence": [*prepare_shell, *submit_shell],
            "prepare_shell": prepare_shell,
            "submit_shell": submit_shell,
            "adapt_run_shell": adapt_run_shell,
        },
        "planned_non_shell_steps": non_shell_steps,
        "warnings": entry.get("warnings", []),
    }


def plan_solar_campaign(
    event_list_path: str | None = None,
    event_list_text: str | None = None,
    selected_run_ids: str | None = None,
    run_dir: str | None = None,
    include_submit_commands: bool = True,
    include_compile_commands: bool = True,
) -> dict[str, Any]:
    parsed = parse_solar_event_list(
        event_list_path=event_list_path,
        event_list_text=event_list_text,
        selected_run_ids=selected_run_ids,
        run_dir=run_dir,
    )
    if not parsed.get("ok"):
        return parsed

    selected_runs = list(parsed.get("selected_runs", []))
    if not selected_runs:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "NO_SELECTED_RUNS",
            "message": "No selected runs were found to plan.",
            "event_list_path_resolved": parsed.get("event_list_path_resolved"),
            "selected_run_ids": parsed.get("selected_run_ids", []),
            "warnings": parsed.get("warnings", []),
        }

    swmfsolar_root_resolved = _resolve_swmfsolar_root(
        event_list_path_resolved=parsed.get("event_list_path_resolved"),
        run_dir=run_dir,
    )

    makefile_defaults: dict[str, str] = {}
    makefile_targets: set[str] = set()
    warnings: list[str] = list(parsed.get("warnings", []))
    makefile_discovery: dict[str, Any] = {
        "detected": False,
        "swmfsolar_root_resolved": swmfsolar_root_resolved,
        "makefile_path": None,
        "capabilities": None,
        "warnings": [],
    }

    if swmfsolar_root_resolved:
        makefile_discovery = _discover_swmfsolar_makefile(
            run_dir=run_dir,
            swmf_root_resolved=swmfsolar_root_resolved,
        )
        warnings.extend([str(item) for item in makefile_discovery.get("warnings", [])])

        capabilities = makefile_discovery.get("capabilities")
        if isinstance(capabilities, dict):
            makefile_defaults = {
                str(key): str(value)
                for key, value in dict(capabilities.get("default_variables", {})).items()
                if isinstance(key, str)
            }
            makefile_targets = {str(item) for item in capabilities.get("targets", [])}

    include_adapt_run_commands = include_submit_commands
    adapt_run_target_detected: bool | None = None
    if swmfsolar_root_resolved and makefile_targets:
        adapt_run_target_detected = "adapt_run" in makefile_targets

    if include_adapt_run_commands and swmfsolar_root_resolved and makefile_targets and "adapt_run" not in makefile_targets:
        warnings.append("SWMFSOLAR Makefile does not expose target 'adapt_run'; adapt_run command group may not execute as-is.")

    run_plans = [
        _plan_single_run(
            entry=item,
            include_submit_commands=include_submit_commands,
            makefile_default_variables=makefile_defaults,
            include_adapt_run_commands=include_adapt_run_commands,
            adapt_run_target_detected=adapt_run_target_detected,
        )
        for item in selected_runs
    ]

    compile_commands: list[str] = []
    if include_compile_commands:
        seen_models: list[str] = []
        for item in run_plans:
            model = str(item["model"])
            if model not in seen_models:
                seen_models.append(model)
        for index, model in enumerate(seen_models):
            doinstall = "T" if index == 0 else "F"
            compile_commands.append(f"make compile DOINSTALL={doinstall} MODEL={model}")

    prepare_commands: list[str] = []
    submit_commands: list[str] = []
    adapt_run_commands: list[str] = []
    for run_plan in run_plans:
        run_examples = dict(run_plan.get("optional_command_examples", {}))
        prepare_commands.extend([str(item) for item in run_examples.get("prepare_shell", [])])
        submit_commands.extend([str(item) for item in run_examples.get("submit_shell", [])])
        adapt_run_commands.extend([str(item) for item in run_examples.get("adapt_run_shell", [])])
        warnings.extend(run_plan.get("warnings", []))

    command_preview = [*compile_commands, *prepare_commands, *submit_commands]
    if swmfsolar_root_resolved:
        command_preview = [f"cd {swmfsolar_root_resolved}", *command_preview]

    source_paths = list(parsed.get("source_paths", []))
    discovered_capabilities: dict[str, Any] = {}
    if swmfsolar_root_resolved and isinstance(makefile_discovery.get("capabilities"), dict):
        discovered_capabilities = dict(makefile_discovery["capabilities"])

    if swmfsolar_root_resolved:
        makefile = Path(swmfsolar_root_resolved) / "Makefile"
        if makefile.is_file():
            source_paths.append(str(makefile.resolve()))
    readme_path = discovered_capabilities.get("readme_path")
    if isinstance(readme_path, str) and readme_path:
        source_paths.append(readme_path)

    variable_guidance = {
        "MODEL": {
            "description": "Model selection should be reconciled between event list entries, Makefile supported models, and compile target usage.",
            "default_hint": makefile_defaults.get("model"),
        },
        "PFSS": {
            "description": "PFSS choice influences map preprocessing and run preparation paths.",
            "default_hint": makefile_defaults.get("pfss"),
        },
        "REALIZATIONS": {
            "description": "Realization expansion should follow map family and campaign goals; ADAPT often uses multiple realizations.",
            "default_hint": makefile_defaults.get("realizations"),
        },
        "JOBNAME": {
            "description": "Job names are environment-dependent and should encode run identifiers meaningful to your scheduler queue.",
            "default_hint": makefile_defaults.get("jobname"),
        },
        "MACHINE": {
            "description": "Machine value should match cluster-specific presets consumed by your Makefile and scripts.",
            "default_hint": makefile_defaults.get("machine"),
        },
    }

    target_recipes = dict(discovered_capabilities.get("target_recipes", {}))
    scheduler_branches = list(discovered_capabilities.get("scheduler_branches", []))
    environment_prerequisites = [str(item) for item in discovered_capabilities.get("environment_prerequisites", [])]
    help_variable_descriptions = dict(discovered_capabilities.get("help_variable_descriptions", {}))

    for key in ["MODEL", "PFSS", "REALIZATIONS", "JOBNAME", "MACHINE", "TIME", "MAP", "PARAM", "POYNTINGFLUX", "DOINSTALL"]:
        if key in variable_guidance and key in help_variable_descriptions:
            variable_guidance[key]["source_description"] = help_variable_descriptions[key]

    workflow_guidance = [
        "Treat command outputs as optional examples; validate Makefile targets and defaults in your active SWMFSOLAR tree first.",
        "Use per-run variable_guidance and decision_branches to adapt commands for your scheduler, filesystem layout, and campaign needs.",
        "Prefer adapt_run when available for robust directory-context handling; otherwise use manual prepare and submit stages.",
    ]

    decision_branches = [
        {
            "name": "use_adapt_run",
            "when": "Makefile target adapt_run is available and include_submit_commands=True.",
            "action": "Use optional_command_examples.adapt_run as a compact workflow example.",
            "status": "available" if include_submit_commands else "disabled",
            "target_detection": "detected"
            if adapt_run_target_detected is True
            else ("not_detected" if adapt_run_target_detected is False else "unknown"),
        },
        {
            "name": "manual_prepare_submit",
            "when": "adapt_run target is unavailable or debugging requires split steps.",
            "action": "Use optional_command_examples.prepare and optional_command_examples.submit examples with environment-specific edits.",
            "status": "available" if include_submit_commands else "prepare_only",
            "target_detection": "detected"
            if adapt_run_target_detected is True
            else ("not_detected" if adapt_run_target_detected is False else "unknown"),
        },
    ]

    assumptions: list[str] = []
    if not swmfsolar_root_resolved:
        assumptions.append("SWMFSOLAR root could not be resolved from run_dir/event list path; guidance may rely on generic defaults.")
    if adapt_run_target_detected is None:
        assumptions.append("adapt_run target detection was not authoritative because Makefile capabilities were not fully discoverable.")
    if include_submit_commands is False:
        assumptions.append("Submit-stage guidance is intentionally disabled by include_submit_commands=False.")

    return {
        "ok": True,
        "phase": "plan_only",
        "requires_manual_execution": True,
        "execute_supported": False,
        "event_list_path_resolved": parsed.get("event_list_path_resolved"),
        "run_dir_resolved": parsed.get("run_dir_resolved"),
        "swmfsolar_root_resolved": swmfsolar_root_resolved,
        "selected_run_ids": parsed.get("selected_run_ids", []),
        "selected_run_ids_expression": parsed.get("selected_run_ids_expression"),
        "selected_run_count": len(run_plans),
        "runs": run_plans,
        "guidance_mode": "instruction_first",
        "workflow_guidance": workflow_guidance,
        "decision_branches": decision_branches,
        "variable_guidance": variable_guidance,
        "target_recipes": target_recipes,
        "scheduler_branches": scheduler_branches,
        "environment_prerequisites": environment_prerequisites,
        "assumptions": assumptions,
        "optional_command_examples": {
            "full_sequence": command_preview,
            "compile": compile_commands,
            "prepare": prepare_commands,
            "submit": submit_commands,
            "adapt_run": adapt_run_commands,
        },
        "warnings": sorted(set(warnings)),
        "authority": "derived",
        "source_kind": "script",
        "source_paths": sorted(set(source_paths)),
        "guided_next_steps": [
            "Review optional command examples and planned_non_shell_steps for each run.",
            "Run swmf_generate_param_from_template or swmf_validate_param for additional preflight checks.",
            "Execute commands manually in SWMFSOLAR after validation.",
        ],
    }


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
        if target not in seen:
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


def _extract_make_subtargets(recipe_lines: list[str]) -> list[str]:
    targets: list[str] = []
    seen: set[str] = set()
    for line in recipe_lines:
        for match in re.finditer(r"\bmake\s+([A-Za-z][A-Za-z0-9_]*)", line):
            target = match.group(1)
            if target not in seen:
                seen.add(target)
                targets.append(target)
    return targets


def _extract_help_variable_descriptions(makefile_text: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for line in makefile_text.splitlines():
        if "@echo" not in line or " - " not in line or "=" not in line:
            continue

        quote_match = re.search(r'@echo\s+"(.+?)"\s*$', line)
        if quote_match is None:
            continue

        message = quote_match.group(1).strip()
        if " - " not in message:
            continue

        left, description = message.split(" - ", 1)
        if "=" not in left:
            continue

        name, default_hint = left.split("=", 1)
        variable = name.strip()
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", variable):
            continue

        result[variable] = {
            "default_hint": default_hint.strip(),
            "description": description.strip(),
        }

    return result


def _extract_scheduler_branches(makefile_text: str) -> list[dict[str, str]]:
    run_recipe = "\n".join(_extract_makefile_target_recipe(makefile_text, "run"))
    if not run_recipe:
        return []

    branches: list[dict[str, str]] = []
    for machine in re.findall(r'MACHINE\}"\s*==\s*"([^"]+)"', run_recipe):
        submit_command = "unknown"
        if machine == "frontera" and "sbatch" in run_recipe:
            submit_command = "sbatch job.long"
        elif machine == "pfe" and "qsub.pfe.pbspl.pl" in run_recipe:
            submit_command = "./qsub.pfe.pbspl.pl job.long <jobname>"
        elif machine == "derecho" and "qsub job.long" in run_recipe:
            submit_command = "qsub job.long"

        branches.append(
            {
                "machine": machine,
                "submit_command": submit_command,
                "source": "run_target_recipe",
            }
        )

    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in branches:
        key = item["machine"]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _extract_readme_prerequisites(readme_text: str) -> list[str]:
    prerequisites: list[str] = []
    for raw in readme_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        lowered = line.lower()
        if "required" in lowered or "must" in lowered:
            prerequisites.append(line)
    return prerequisites


def _extract_makefile_supported_models(makefile_text: str) -> list[str]:
    models: list[str] = []
    seen: set[str] = set()

    def _add_model(token: str) -> None:
        normalized = token.strip().strip("\"'.,")
        if not normalized or normalized.startswith("${"):
            return
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", normalized):
            return
        if normalized not in seen:
            seen.add(normalized)
            models.append(normalized)

    for raw in re.findall(r"filter\s+\$\{MODEL\},([A-Za-z0-9_\s]+)\)", makefile_text):
        for token in raw.split():
            _add_model(token)

    for raw in re.findall(r"must be either ([^.\n]+)", makefile_text):
        normalized = raw.replace(" or ", ",")
        for token in normalized.split(","):
            _add_model(token)

    return models


def _discover_swmfsolar_makefile(run_dir: str | None, swmf_root_resolved: str) -> dict[str, Any]:
    base_dir = resolve_run_dir(run_dir)
    candidates = [
        base_dir / "SWMFSOLAR",
        base_dir,
        Path(swmf_root_resolved).expanduser().resolve() / "SWMFSOLAR",
        Path(swmf_root_resolved).expanduser().resolve().parent / "SWMFSOLAR",
    ]

    seen: set[str] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        marker = str(resolved)
        if marker in seen:
            continue
        seen.add(marker)

        makefile = resolved / "Makefile"
        scripts_dir = resolved / "Scripts"
        if not makefile.is_file() or not scripts_dir.is_dir():
            continue

        try:
            makefile_text = makefile.read_text(encoding="utf-8")
        except OSError as exc:
            return {
                "detected": False,
                "swmfsolar_root_resolved": str(resolved),
                "makefile_path": str(makefile),
                "capabilities": None,
                "warnings": [f"Failed to read SWMFSOLAR Makefile: {exc}"],
            }

        default_variables: dict[str, str] = {}
        for key in _SWMFSOLAR_DEFAULT_VARIABLES:
            value = _extract_makefile_assignment(makefile_text, key)
            if value is not None:
                default_variables[key.lower()] = value

        targets = _extract_makefile_targets(makefile_text)
        target_set = set(targets)

        supported_models = _extract_makefile_supported_models(makefile_text) or sorted(_SUPPORTED_MODELS)
        supported_pfss = [item for item in ["HARMONICS", "FDIPS"] if re.search(rf"\b{item}\b", makefile_text)]
        if not supported_pfss:
            supported_pfss = ["HARMONICS", "FDIPS"]

        recipe_targets = [
            "adapt_run_w_compile",
            "adapt_run",
            "rundir_local",
            "compile",
            "backup_run",
            "copy_param",
            "rundir_realizations",
            "clean_rundir_tmp",
            "run",
        ]
        target_recipes: dict[str, list[str]] = {}
        for target in recipe_targets:
            recipe = _extract_makefile_target_recipe(makefile_text, target)
            if recipe:
                target_recipes[target] = _extract_make_subtargets(recipe)

        help_variable_descriptions = _extract_help_variable_descriptions(makefile_text)
        scheduler_branches = _extract_scheduler_branches(makefile_text)

        readme_path = resolved / "README"
        readme_prerequisites: list[str] = []
        warnings: list[str] = []
        if readme_path.is_file():
            try:
                readme_text = readme_path.read_text(encoding="utf-8")
                readme_prerequisites = _extract_readme_prerequisites(readme_text)
            except OSError as exc:
                warnings.append(f"Failed to read SWMFSOLAR README: {exc}")
        else:
            warnings.append(f"SWMFSOLAR README was not found at {readme_path}.")

        capabilities = {
            "targets": targets,
            "workflow_targets": [target for target in _SWMFSOLAR_QUICKRUN_TARGETS if target in target_set],
            "missing_workflow_targets": [target for target in _SWMFSOLAR_QUICKRUN_TARGETS if target not in target_set],
            "default_variables": default_variables,
            "supported_models": supported_models,
            "supported_pfss": supported_pfss,
            "uses_change_awsom_param": "change_awsom_param.py" in makefile_text,
            "target_recipes": target_recipes,
            "scheduler_branches": scheduler_branches,
            "help_variable_descriptions": help_variable_descriptions,
            "environment_prerequisites": readme_prerequisites,
            "readme_path": str(readme_path) if readme_path.is_file() else None,
        }

        return {
            "detected": True,
            "swmfsolar_root_resolved": str(resolved),
            "makefile_path": str(makefile.resolve()),
            "capabilities": capabilities,
            "warnings": warnings,
        }

    return {
        "detected": False,
        "swmfsolar_root_resolved": None,
        "makefile_path": None,
        "capabilities": None,
        "warnings": [
            "SWMFSOLAR Makefile was not found in run_dir or alongside SWMF root; falling back to generic SWMF guidance."
        ],
    }


def _infer_swmfsolar_realizations_expression(
    inspect_result: dict[str, Any],
    default_variables: dict[str, str],
) -> tuple[str, str]:
    resolved_path = str(inspect_result.get("fits_path_resolved") or "")
    fits_name = Path(resolved_path).name.lower() if resolved_path else ""
    instrument = str(inspect_result.get("instrument") or "").lower()
    probable_map_type = str(inspect_result.get("probable_map_type") or "").lower()
    default_expression = default_variables.get("realizations")

    if "adapt" in fits_name or "adapt" in instrument:
        if default_expression:
            return default_expression, "makefile_default_adapt"
        return "1,2,3,4,5,6,7,8,9,10,11,12", "adapt_fallback_12"

    if "gong" in fits_name or "gong" in instrument or probable_map_type == "synoptic":
        return "1", "gong_or_synoptic_single"

    if default_expression:
        parsed, parse_error = _parse_int_list_expression(default_expression)
        if parse_error is None and parsed:
            return str(parsed[0]), "first_makefile_realization"

    return "1", "fallback_single_realization"


def _build_swmfsolar_make_quickrun_plan(
    discovery: dict[str, Any],
    inspect_result: dict[str, Any],
    mode: str,
    preferred_model: str | None = None,
    preferred_simdir: str | None = None,
    preferred_machine: str | None = None,
) -> dict[str, Any] | None:
    if not discovery.get("detected"):
        return None

    capabilities = discovery.get("capabilities")
    if not isinstance(capabilities, dict):
        return None

    default_variables = dict(capabilities.get("default_variables", {}))
    supported_models = [str(item) for item in capabilities.get("supported_models", [])]
    supported_pfss = [str(item) for item in capabilities.get("supported_pfss", [])]

    warnings: list[str] = []

    model = str((preferred_model or default_variables.get("model") or "AWSoM")).strip()
    if supported_models and model not in supported_models:
        warnings.append(
            f"Requested/default model '{model}' is not in discovered supported models; using '{supported_models[0]}' instead."
        )
        model = supported_models[0]

    pfss = str(default_variables.get("pfss", "HARMONICS"))
    if supported_pfss and pfss not in supported_pfss:
        warnings.append(
            f"Makefile default PFSS '{pfss}' is not in discovered supported PFSS options; using '{supported_pfss[0]}' instead."
        )
        pfss = supported_pfss[0]

    time_value = str(default_variables.get("time", "MapTime"))
    param = str(default_variables.get("param", "Default"))
    poyntingflux = str(default_variables.get("poyntingflux", "-1.0"))
    jobname = str(default_variables.get("jobname", "amap"))
    machine = str((preferred_machine or default_variables.get("machine") or "")).strip() or None
    doinstall = str(default_variables.get("doinstall", "T")).upper()
    if doinstall not in {"T", "F"}:
        warnings.append(f"Unexpected DOINSTALL value '{doinstall}' in Makefile; using 'T'.")
        doinstall = "T"

    map_value = str(inspect_result.get("fits_path_resolved") or default_variables.get("map", "NoMap"))
    realizations_expression, realizations_source = _infer_swmfsolar_realizations_expression(
        inspect_result=inspect_result,
        default_variables=default_variables,
    )
    simdir = str((preferred_simdir or f"quick_{mode}")).strip() or f"quick_{mode}"
    target_set = {str(item) for item in capabilities.get("targets", [])}

    missing_targets = [str(item) for item in capabilities.get("missing_workflow_targets", [])]
    if missing_targets:
        warnings.append(
            "SWMFSOLAR Makefile is missing quickrun targets used by the planner: " + ", ".join(missing_targets)
        )
    if not capabilities.get("uses_change_awsom_param", False):
        warnings.append("SWMFSOLAR Makefile does not reference change_awsom_param.py; map mutation command may need adjustment.")

    def _var(name: str, value: str) -> str:
        return f"{name}={shlex.quote(value)}"

    compile_commands = ["make compile " + " ".join([_var("DOINSTALL", doinstall), _var("MODEL", model)])]
    prepare_commands = [
        "make backup_run " + _var("SIMDIR", simdir),
        "make copy_param " + " ".join([_var("MODEL", model), _var("PARAM", param)]),
        "python Scripts/change_awsom_param.py "
        + " ".join(
            [
                f"--map {shlex.quote(map_value)}",
                f"-t {shlex.quote(time_value)}",
                f"-B0 {shlex.quote(pfss)}",
                f"-p {shlex.quote(poyntingflux)}",
            ]
        ),
        "make rundir_realizations "
        + " ".join(
            [
                _var("SIMDIR", simdir),
                _var("MODEL", model),
                _var("PFSS", pfss),
                _var("REALIZATIONS", realizations_expression),
            ]
        ),
        "make clean_rundir_tmp",
    ]
    submit_commands = [
        "make run "
        + " ".join(
            [
                _var("SIMDIR", simdir),
                _var("PFSS", pfss),
                _var("REALIZATIONS", realizations_expression),
                _var("JOBNAME", jobname),
            ]
        )
    ]

    adapt_run_commands: list[str] = []
    if "adapt_run" in target_set:
        adapt_vars: OrderedDict[str, str] = OrderedDict()
        adapt_vars["MODEL"] = model
        adapt_vars["SIMDIR"] = simdir
        adapt_vars["REALIZATIONS"] = realizations_expression
        adapt_vars["MAP"] = map_value
        adapt_vars["TIME"] = time_value
        adapt_vars["PFSS"] = pfss
        adapt_vars["POYNTINGFLUX"] = poyntingflux
        if machine:
            adapt_vars["MACHINE"] = machine
        adapt_vars["JOBNAME"] = jobname
        adapt_run_commands = [
            "make adapt_run " + " ".join(_var(name, value) for name, value in adapt_vars.items())
        ]

    command_preview = [*compile_commands, *(adapt_run_commands or [*prepare_commands, *submit_commands])]
    swmfsolar_root_resolved = str(discovery.get("swmfsolar_root_resolved") or "")
    if swmfsolar_root_resolved:
        command_preview = [f"cd {swmfsolar_root_resolved}", *command_preview]

    decision_branches = [
        {
            "name": "adapt_run_available",
            "when": "adapt_run target exists in SWMFSOLAR Makefile.",
            "action": "Use optional_command_examples.adapt_run optional example path.",
            "status": "available" if bool(adapt_run_commands) else "unavailable",
        },
        {
            "name": "split_prepare_submit",
            "when": "adapt_run is unavailable or stepwise debugging is preferred.",
            "action": "Use optional_command_examples.prepare then optional_command_examples.submit optional examples.",
            "status": "available",
        },
    ]

    variable_guidance = {
        "MODEL": {
            "selected": model,
            "supported_values": supported_models,
            "description": "Should be supported by Makefile model checks and aligned with selected quickrun mode.",
        },
        "PFSS": {
            "selected": pfss,
            "supported_values": supported_pfss,
            "description": "PFSS mode influences magnetic preprocessing route and matching script arguments.",
        },
        "REALIZATIONS": {
            "selected": realizations_expression,
            "source": realizations_source,
            "description": "Chosen from FITS/map hints or Makefile defaults; adjust for campaign breadth and resource limits.",
        },
        "SIMDIR": {
            "selected": simdir,
            "description": "Run directory stem used by backup, prepare, and submission targets.",
        },
        "MACHINE": {
            "selected": machine,
            "description": "Optional machine preset consumed by Makefile-specific scheduler wrappers.",
        },
        "JOBNAME": {
            "selected": jobname,
            "description": "Queue-visible label used by run/adapt_run submit flows.",
        },
    }

    target_recipes = dict(capabilities.get("target_recipes", {}))
    scheduler_branches = list(capabilities.get("scheduler_branches", []))
    environment_prerequisites = [str(item) for item in capabilities.get("environment_prerequisites", [])]
    help_variable_descriptions = dict(capabilities.get("help_variable_descriptions", {}))
    for key in ["MODEL", "PFSS", "TIME", "MAP", "PARAM", "REALIZATIONS", "JOBNAME", "POYNTINGFLUX", "MACHINE", "DOINSTALL"]:
        if key in variable_guidance and key in help_variable_descriptions:
            variable_guidance[key]["source_description"] = help_variable_descriptions[key]

    workflow_guidance = [
        "Inspect SWMFSOLAR Makefile targets and defaults before executing examples in a cluster environment.",
        "Select an execution branch using decision_branches and then customize variables for your scheduler/accounting policy.",
        "Treat command examples as templates; validate directories and file paths (MAP, PARAM, SIMDIR) in your runtime context.",
    ]

    return {
        "variables": {
            "model": model,
            "pfss": pfss,
            "time": time_value,
            "map": map_value,
            "param": param,
            "poyntingflux": poyntingflux,
            "realizations_expression": realizations_expression,
            "realizations_source": realizations_source,
            "simdir": simdir,
            "jobname": jobname,
            "machine": machine,
            "doinstall": doinstall,
        },
        "workflow_guidance": workflow_guidance,
        "decision_branches": decision_branches,
        "variable_guidance": variable_guidance,
        "target_recipes": target_recipes,
        "scheduler_branches": scheduler_branches,
        "environment_prerequisites": environment_prerequisites,
        "optional_command_examples": {
            "full_sequence": command_preview,
            "compile": compile_commands,
            "prepare": prepare_commands,
            "submit": submit_commands,
            "adapt_run": adapt_run_commands,
        },
        "warnings": warnings,
    }


def _prepare_sc_quickrun_from_magnetogram(
    fits_path: str,
    swmf_root_resolved: str,
    run_dir: str | None,
    mode: str = "sc_steady",
    nproc: int | None = None,
    job_script_path: str | None = None,
    model: str | None = None,
    simdir: str | None = None,
    machine: str | None = None,
) -> dict[str, Any]:
    from .idl import inspect_fits_magnetogram
    from .param import generate_param_from_template, default_quickrun_param_skeleton
    from .build_run import (
        prepare_build,
        prepare_run,
        prepare_component_config,
        infer_job_layout,
    )

    _QUICKRUN_MODES = {"sc_steady", "sc_ih_steady", "sc_ih_timeaccurate"}
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

    inferred_machine: str | None = machine
    if inferred_machine is None and isinstance(layout_payload, dict):
        machine_hint = layout_payload.get("machine_hint")
        if isinstance(machine_hint, str) and machine_hint.strip():
            inferred_machine = machine_hint.strip()

    inferred_simdir = str(simdir or "").strip()
    if not inferred_simdir and run_dir is not None:
        candidate_name = Path(run_dir).expanduser().name.strip()
        if candidate_name:
            inferred_simdir = candidate_name
    if not inferred_simdir:
        inferred_simdir = f"quick_{mode}"

    makefile_discovery = _discover_swmfsolar_makefile(run_dir=run_dir, swmf_root_resolved=swmf_root_resolved)
    swmfsolar_make_plan = _build_swmfsolar_make_quickrun_plan(
        discovery=makefile_discovery,
        inspect_result=inspect_result,
        mode=mode,
        preferred_model=model,
        preferred_simdir=inferred_simdir,
        preferred_machine=inferred_machine,
    )

    def _quickrun_mode_to_components(m: str) -> list[str]:
        if m == "sc_steady":
            return ["SC/BATSRUS"]
        if m in {"sc_ih_steady", "sc_ih_timeaccurate"}:
            return ["SC/BATSRUS", "IH/BATSRUS"]
        return ["SC/BATSRUS"]

    def _quickrun_component_map(m: str, n: int) -> str:
        if m == "sc_steady" or n <= 1:
            return "SC 0 -1 1"
        sc_end = max(n - 2, 0)
        return "\n".join([f"SC 0 {sc_end} 1", "IH -1 -1 1"])

    recommended_components = _quickrun_mode_to_components(mode)
    build_plan = prepare_build(
        components_csv=",".join(recommended_components),
        swmf_root_resolved=swmf_root_resolved,
    )

    prepare_run_plan = prepare_run(
        component_map_text=_quickrun_component_map(mode, inferred_nproc),
        nproc=inferred_nproc,
        description="MCP heuristic solar quickrun from GONG FITS metadata (non-authoritative; validate with Scripts/TestParam.pl)",
        time_accurate=(mode == "sc_ih_timeaccurate"),
        stop_value="7200.0" if mode == "sc_ih_timeaccurate" else "4000",
        include_restart=False,
        run_name=inferred_simdir,
        run_dir=run_dir,
        job_script_path=job_script_path,
        swmf_root_resolved=swmf_root_resolved,
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

    suggested_param_template_text = template_payload.get("suggested_param_text") or default_quickrun_param_skeleton(
        mode=mode,
        fits_path_resolved=inspect_result.get("fits_path_resolved"),
        nproc=inferred_nproc,
    )

    external_input_warnings: list[str] = []
    external_input_warnings.extend(list(inspect_result.get("warnings", [])))
    external_input_warnings.extend(nproc_warnings)
    external_input_warnings.extend(list(makefile_discovery.get("warnings", [])))
    if swmfsolar_make_plan is not None:
        external_input_warnings.extend(list(swmfsolar_make_plan.get("warnings", [])))
    if template_payload.get("template_found") is False:
        external_input_warnings.append("No solar PARAM template was found; returned a heuristic skeleton for manual review.")

    build_examples = dict(build_plan.get("optional_command_examples", {}))
    run_examples = dict(prepare_run_plan.get("optional_command_examples", {}))
    recommended_build_steps = [str(item) for item in build_examples.get("full_sequence", [])]
    recommended_run_steps = [str(item) for item in run_examples.get("full_sequence", [])]
    swmfsolar_command_examples: dict[str, list[str]] = {
        "compile": [],
        "prepare": [],
        "submit": [],
        "adapt_run": [],
        "full_sequence": [],
    }
    swmfsolar_recommended_variables: dict[str, Any] | None = None
    if swmfsolar_make_plan is not None:
        plan_examples = dict(swmfsolar_make_plan.get("optional_command_examples", {}))
        swmfsolar_command_examples = {
            "compile": [str(item) for item in plan_examples.get("compile", [])],
            "prepare": [str(item) for item in plan_examples.get("prepare", [])],
            "submit": [str(item) for item in plan_examples.get("submit", [])],
            "adapt_run": [str(item) for item in plan_examples.get("adapt_run", [])],
            "full_sequence": [str(item) for item in plan_examples.get("full_sequence", [])],
        }
        swmfsolar_recommended_variables = dict(swmfsolar_make_plan.get("variables", {}))
        recommended_build_steps = list(swmfsolar_command_examples.get("compile", [])) or recommended_build_steps
        recommended_run_steps = (
            list(swmfsolar_command_examples.get("adapt_run", []))
            or [
                *swmfsolar_command_examples.get("prepare", []),
                *swmfsolar_command_examples.get("submit", []),
            ]
            or recommended_run_steps
        )

    quickrun_workflow_guidance = [
        "Use this payload as guidance-first output: inspect capability fields and variable guidance before execution.",
        "Prioritize SWMFSOLAR Makefile-driven branches when detected; otherwise fall back to generic SWMF build/run guidance.",
        "Run validation_plan checks before submission and treat command examples as editable templates.",
    ]
    quickrun_decision_branches = [
        {
            "name": "swmfsolar_makefile_branch",
            "when": "SWMFSOLAR Makefile is detected and capability extraction succeeds.",
            "action": "Use optional_command_examples.swmfsolar_commands.adapt_run with variable overrides from swmfsolar_recommended_variables.",
            "status": "available" if swmfsolar_make_plan is not None else "unavailable",
        },
        {
            "name": "generic_swmf_branch",
            "when": "SWMFSOLAR Makefile is missing or incomplete.",
            "action": "Use optional_command_examples.generic_swmf commands and re-check paths/targets manually.",
            "status": "fallback",
        },
    ]

    variable_guidance: dict[str, Any] = {}
    target_recipes: dict[str, Any] = {}
    scheduler_branches: list[dict[str, Any]] = []
    environment_prerequisites: list[str] = []
    if swmfsolar_make_plan is not None:
        variable_guidance = dict(swmfsolar_make_plan.get("variable_guidance", {}))
        target_recipes = dict(swmfsolar_make_plan.get("target_recipes", {}))
        scheduler_branches = list(swmfsolar_make_plan.get("scheduler_branches", []))
        environment_prerequisites = [str(item) for item in swmfsolar_make_plan.get("environment_prerequisites", [])]
    else:
        variable_guidance = {
            "MODEL": {
                "description": "Model defaults to quickrun heuristics unless explicitly provided.",
                "selected": model,
            },
            "SIMDIR": {
                "description": "SIMDIR defaults to run_dir basename or quick_<mode>.",
                "selected": inferred_simdir,
            },
            "NPROC": {
                "description": "NP inferred from job script when possible; otherwise heuristic default may be used.",
                "selected": inferred_nproc,
                "source": inferred_nproc_source,
            },
        }

    source_paths = list(template_payload.get("source_paths", []))
    makefile_path = makefile_discovery.get("makefile_path")
    if isinstance(makefile_path, str) and makefile_path:
        source_paths.append(makefile_path)
    discovered_capabilities = makefile_discovery.get("capabilities")
    if isinstance(discovered_capabilities, dict):
        readme_path = discovered_capabilities.get("readme_path")
        if isinstance(readme_path, str) and readme_path:
            source_paths.append(readme_path)

    return {
        "ok": True,
        "heuristic": True,
        "guidance_mode": "instruction_first",
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": sorted(set(source_paths)),
        "heuristic_fields": [
            "recommended_components",
            "inferred_nproc_when_not_explicit",
            "suggested_param_template_text",
            "solar_alignment_hints",
            "swmfsolar_makefile_capabilities",
            "optional_command_examples",
        ],
        "fits_inspection": inspect_result,
        "recommended_components": recommended_components,
        "recommended_config_pl_command": config_hint.get("recommended_config_command"),
        "inferred_nproc": inferred_nproc,
        "inferred_nproc_source": inferred_nproc_source,
        "job_layout": layout_payload,
        "swmfsolar_makefile_detected": bool(makefile_discovery.get("detected", False)),
        "swmfsolar_root_resolved": makefile_discovery.get("swmfsolar_root_resolved"),
        "swmfsolar_makefile_path": makefile_path,
        "swmfsolar_makefile_capabilities": makefile_discovery.get("capabilities"),
        "swmfsolar_recommended_variables": swmfsolar_recommended_variables,
        "workflow_guidance": quickrun_workflow_guidance,
        "decision_branches": quickrun_decision_branches,
        "variable_guidance": variable_guidance,
        "target_recipes": target_recipes,
        "scheduler_branches": scheduler_branches,
        "environment_prerequisites": environment_prerequisites,
        "optional_command_examples": {
            "swmfsolar_commands": swmfsolar_command_examples,
            "selected_build_sequence": recommended_build_steps,
            "selected_run_sequence": recommended_run_steps,
            "generic_swmf": {
                "build": [str(item) for item in build_examples.get("full_sequence", [])],
                "run": [str(item) for item in run_examples.get("full_sequence", [])],
            },
        },
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


def swmf_parse_solar_event_list(
    event_list_path: str | None = None,
    event_list_text: str | None = None,
    selected_run_ids: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    return parse_solar_event_list(
        event_list_path=event_list_path,
        event_list_text=event_list_text,
        selected_run_ids=selected_run_ids,
        run_dir=run_dir,
    )


def swmf_plan_solar_campaign(
    event_list_path: str | None = None,
    event_list_text: str | None = None,
    selected_run_ids: str | None = None,
    run_dir: str | None = None,
    include_submit_commands: bool = True,
    include_compile_commands: bool = True,
) -> dict[str, Any]:
    return plan_solar_campaign(
        event_list_path=event_list_path,
        event_list_text=event_list_text,
        selected_run_ids=selected_run_ids,
        run_dir=run_dir,
        include_submit_commands=include_submit_commands,
        include_compile_commands=include_compile_commands,
    )


def swmf_prepare_solar_quickrun_from_magnetogram(
    fits_path: str,
    run_dir: str | None = None,
    swmf_root: str | None = None,
    mode: str = "sc_steady",
    nproc: int | None = None,
    job_script_path: str | None = None,
    model: str | None = None,
    simdir: str | None = None,
    machine: str | None = None,
) -> dict[str, Any]:
    from ._helpers import resolve_root_or_failure, with_root

    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    return with_root(
        _prepare_sc_quickrun_from_magnetogram(
            fits_path=fits_path,
            swmf_root_resolved=root.swmf_root_resolved or str(Path.cwd()),
            run_dir=run_dir,
            mode=mode,
            nproc=nproc,
            job_script_path=job_script_path,
            model=model,
            simdir=simdir,
            machine=machine,
        ),
        root,
    )


def register(app: Any) -> None:
    app.tool(description="Parse SWMFSOLAR event-list entries into normalized campaign run specs.")(swmf_parse_solar_event_list)
    app.tool(description="Prepare a guidance-first SWMFSOLAR campaign plan with optional command examples.")(
        swmf_plan_solar_campaign
    )
    app.tool(description="Prepare a guidance-first heuristic solar quickrun plan from a magnetogram FITS file.")(
        swmf_prepare_solar_quickrun_from_magnetogram
    )
