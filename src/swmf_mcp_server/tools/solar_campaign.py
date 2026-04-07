from __future__ import annotations

import shlex
from collections import OrderedDict
from pathlib import Path
from typing import Any

from ..core.common import resolve_run_dir


_SUPPORTED_MODELS = {"AWSoM", "AWSoM2T", "AWSoMR", "AWSoMR_SOFIE"}


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


def _plan_single_run(entry: dict[str, Any], include_submit_commands: bool) -> dict[str, Any]:
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
        submit_vars["JOBNAME"] = f"r{run_id:02d}_"
        submit_shell.append("make run " + " ".join(f"{key}={value}" for key, value in submit_vars.items()))

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
        "command_groups": {
            "prepare_shell": prepare_shell,
            "submit_shell": submit_shell,
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

    run_plans = [_plan_single_run(entry=item, include_submit_commands=include_submit_commands) for item in selected_runs]

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
    warnings: list[str] = list(parsed.get("warnings", []))
    for run_plan in run_plans:
        prepare_commands.extend(run_plan["command_groups"]["prepare_shell"])
        submit_commands.extend(run_plan["command_groups"]["submit_shell"])
        warnings.extend(run_plan.get("warnings", []))

    command_preview = [*compile_commands, *prepare_commands, *submit_commands]
    if swmfsolar_root_resolved:
        command_preview = [f"cd {swmfsolar_root_resolved}", *command_preview]

    source_paths = list(parsed.get("source_paths", []))
    if swmfsolar_root_resolved:
        makefile = Path(swmfsolar_root_resolved) / "Makefile"
        if makefile.is_file():
            source_paths.append(str(makefile.resolve()))

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
        "command_preview": command_preview,
        "command_groups": {
            "compile": compile_commands,
            "prepare": prepare_commands,
            "submit": submit_commands,
        },
        "warnings": sorted(set(warnings)),
        "authority": "derived",
        "source_kind": "script",
        "source_paths": sorted(set(source_paths)),
        "recommended_next_steps": [
            "Review command_preview and planned_non_shell_steps for each run.",
            "Run swmf_generate_param_from_template or swmf_validate_param for additional preflight checks.",
            "Execute commands manually in SWMFSOLAR after validation.",
        ],
    }


def _prepare_sc_quickrun_from_magnetogram(
    fits_path: str,
    swmf_root_resolved: str,
    run_dir: str | None,
    mode: str = "sc_steady",
    nproc: int | None = None,
    job_script_path: str | None = None,
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
        ),
        root,
    )


def register(app: Any) -> None:
    app.tool(description="Parse SWMFSOLAR event-list entries into normalized campaign run specs.")(swmf_parse_solar_event_list)
    app.tool(description="Prepare a dry-run SWMFSOLAR campaign plan (compile/prepare/submit command preview only).")(
        swmf_plan_solar_campaign
    )
    app.tool(description="Prepare a heuristic solar quickrun plan from a magnetogram FITS file.")(
        swmf_prepare_solar_quickrun_from_magnetogram
    )
