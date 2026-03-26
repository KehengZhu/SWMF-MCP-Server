from __future__ import annotations

import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from .core.errors import resolution_failure_payload
from .discovery.swmf_root import resolve_swmf_root
from .services import (
    apply_setup_commands,
    detect_setup_commands,
    diagnose_param,
    explain_component_config_fix,
    explain_param,
    find_example_params,
    find_param_command,
    generate_param_from_template,
    get_component_versions,
    get_source_catalog,
    infer_job_layout,
    inspect_fits_magnetogram,
    list_available_components,
    prepare_build,
    prepare_component_config,
    prepare_idl_workflow,
    prepare_run,
    prepare_sc_quickrun_from_magnetogram,
    run_testparam,
    trace_param_command,
    validate_external_inputs,
    validate_param,
)
from .services.common import load_param_text
from .services.idl_service import IDL_OUTPUT_FORMATS, IDL_TASKS, _try_import_astropy_fits


logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("swmf-mcp")

mcp = FastMCP("swmf-prototype", json_response=True)


def _resolve_root_or_failure(swmf_root: str | None, run_dir: str | None) -> tuple[dict[str, Any] | None, Any | None]:
    root = resolve_swmf_root(swmf_root=swmf_root, run_dir=run_dir)
    if not root.ok:
        return resolution_failure_payload(root.message or "Could not resolve SWMF root.", root.resolution_notes), None
    return None, root


def _with_root(payload: dict[str, Any], root: Any) -> dict[str, Any]:
    payload.setdefault("swmf_root_resolved", root.swmf_root_resolved)
    payload.setdefault("resolution_notes", root.resolution_notes)
    return payload


@mcp.tool()
def swmf_explain_param(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        fallback = explain_param(name=name, catalog=None)
        fallback["swmf_root_resolved"] = None
        fallback["resolution_failure"] = failure
        return fallback

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None:
        fallback = explain_param(name=name, catalog=None)
        fallback["swmf_root_resolved"] = None
        fallback["resolution_failure"] = catalog_error
        return fallback

    return _with_root(explain_param(name=name, catalog=catalog), root)


@mcp.tool()
def swmf_validate_param(
    param_text: str | None = None,
    nproc: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    param_path: str | None = None,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    return _with_root(
        validate_param(
            param_text=param_text,
            nproc=nproc,
            run_dir=run_dir,
            param_path=param_path,
        ),
        root,
    )


@mcp.tool()
def swmf_run_testparam(
    param_path: str,
    nproc: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    return _with_root(
        run_testparam(
            param_path=param_path,
            swmf_root_resolved=root.swmf_root_resolved,
            nproc=nproc,
            run_dir=run_dir,
            job_script_path=job_script_path,
        ),
        root,
    )


@mcp.tool()
def swmf_prepare_build(
    components_csv: str,
    compiler: str | None = None,
    debug: bool = False,
    optimization: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure
    return _with_root(
        prepare_build(
            components_csv=components_csv,
            compiler=compiler,
            debug=debug,
            optimization=optimization,
        ),
        root,
    )


@mcp.tool()
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
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure
    return _with_root(
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


@mcp.tool()
def swmf_prepare_idl_workflow(
    request: str | None = None,
    task: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    output_pattern: str | None = None,
    input_file: str | None = None,
    artifact_name: str | None = None,
    output_format: str | None = None,
    frame_rate: int = 10,
    preview: bool = False,
    frame_indices: list[int] | None = None,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    root_resolved = root.swmf_root_resolved if root is not None else None

    payload = prepare_idl_workflow(
        request=request,
        swmf_root_resolved=root_resolved,
        run_dir=run_dir,
        output_pattern=output_pattern,
        input_file=input_file,
        artifact_name=artifact_name,
        output_format=output_format,
        frame_rate=frame_rate,
        preview=preview,
        frame_indices=frame_indices,
        task=task,
    )
    if failure is not None:
        payload["resolution_failure"] = failure
        payload["swmf_root_resolved"] = None
        return payload
    assert root is not None
    return _with_root(payload, root)


@mcp.tool()
def swmf_list_tool_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "hard_error": False,
        "authority": "authoritative",
        "source_kind": "implementation",
        "source_paths": ["src/swmf_mcp_server/server.py", "src/swmf_mcp_server/services/idl_service.py"],
        "tools": {
            "swmf_prepare_idl_workflow": {
                "description": "Prepare an IDL workflow script and shell command sequence for SWMF data operations.",
                "notes": [
                    "For task='plot', set_device uses PostScript output; non-PS formats are generated by converting .ps.",
                    "For task='animate', video formats use videofile/videorate and image formats use moviedir.",
                ],
                "requires_one_of": ["task", "request"],
                "task_enum": list(IDL_TASKS),
                "output_format_enum": list(IDL_OUTPUT_FORMATS),
                "inputs": {
                    "request": {"type": "string", "required": False},
                    "task": {"type": "string", "required": False, "enum": list(IDL_TASKS)},
                    "swmf_root": {"type": "string", "required": False},
                    "run_dir": {"type": "string", "required": False},
                    "output_pattern": {"type": "string", "required": False},
                    "input_file": {"type": "string", "required": False},
                    "artifact_name": {"type": "string", "required": False},
                    "output_format": {"type": "string", "required": False, "enum": list(IDL_OUTPUT_FORMATS)},
                    "frame_rate": {"type": "integer", "required": False, "default": 10, "minimum": 1},
                    "preview": {"type": "boolean", "required": False, "default": False},
                    "frame_indices": {"type": "array", "required": False, "items": {"type": "integer", "minimum": 1}},
                },
                "response_shape": [
                    "ok",
                    "hard_error",
                    "authority",
                    "source_kind",
                    "request",
                    "capability",
                    "normalized_inputs",
                    "inferred",
                    "idl_script_filename",
                    "idl_script",
                    "shell_commands",
                    "warnings",
                    "assumptions",
                ],
            }
        },
    }


@mcp.tool()
def swmf_prepare_component_config(
    param_text: str | None = None,
    param_path: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    loaded_text, resolved_param_path, load_error = load_param_text(param_text=param_text, param_path=param_path, run_dir=run_dir)
    if load_error is not None or loaded_text is None:
        return _with_root(
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
    return _with_root(payload, root)


@mcp.tool()
def swmf_detect_setup_commands(
    param_text: str | None = None,
    param_path: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    loaded_text, resolved_param_path, load_error = load_param_text(param_text=param_text, param_path=param_path, run_dir=run_dir)
    if load_error is not None or loaded_text is None:
        return _with_root(
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
    return _with_root(payload, root)


@mcp.tool()
def swmf_apply_setup_commands(
    commands: list[str] | None = None,
    param_text: str | None = None,
    param_path: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    continue_on_error: bool = False,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    detected_payload: dict[str, Any] | None = None
    source = "explicit_commands"
    effective_commands = commands

    if effective_commands is None:
        loaded_text, _resolved_param_path, load_error = load_param_text(param_text=param_text, param_path=param_path, run_dir=run_dir)
        if load_error is not None or loaded_text is None:
            return _with_root(
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
        return _with_root(
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
        swmf_root=root.swmf_root_resolved,
        commands=effective_commands,
        continue_on_error=continue_on_error,
    )
    payload["source"] = source
    payload["detection"] = detected_payload
    return _with_root(payload, root)


@mcp.tool()
def swmf_infer_job_layout(
    job_script_path: str | None = None,
    run_dir: str | None = None,
    swmf_root: str | None = None,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure
    return _with_root(infer_job_layout(job_script_path=job_script_path, run_dir=run_dir), root)


@mcp.tool()
def swmf_inspect_fits_magnetogram(
    fits_path: str,
    run_dir: str | None = None,
    swmf_root: str | None = None,
    read_data: bool = False,
) -> dict[str, Any]:
    _ = swmf_root
    payload = inspect_fits_magnetogram(
        fits_path=fits_path,
        run_dir=run_dir,
        read_data=read_data,
        importer=_try_import_astropy_fits,
    )
    payload.setdefault("suggested_next_tool", "swmf_prepare_sc_quickrun_from_magnetogram")
    return payload


@mcp.tool()
def swmf_generate_param_from_template(
    template_kind: str,
    fits_path: str | None = None,
    run_dir: str | None = None,
    swmf_root: str | None = None,
    nproc: int | None = None,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    return _with_root(
        generate_param_from_template(
            template_kind=template_kind,
            fits_path=fits_path,
            run_dir=run_dir,
            swmf_root_resolved=root.swmf_root_resolved,
            nproc=nproc,
        ),
        root,
    )


@mcp.tool()
def swmf_prepare_sc_quickrun_from_magnetogram(
    fits_path: str,
    run_dir: str | None = None,
    swmf_root: str | None = None,
    mode: str = "sc_steady",
    nproc: int | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    return _with_root(
        prepare_sc_quickrun_from_magnetogram(
            fits_path=fits_path,
            swmf_root_resolved=root.swmf_root_resolved,
            run_dir=run_dir,
            mode=mode,
            nproc=nproc,
            job_script_path=job_script_path,
        ),
        root,
    )


@mcp.tool()
def swmf_validate_external_inputs(
    param_text: str | None = None,
    param_path: str | None = None,
    run_dir: str | None = None,
    swmf_root: str | None = None,
) -> dict[str, Any]:
    _ = swmf_root
    return validate_external_inputs(
        param_text=param_text,
        param_path=param_path,
        run_dir=run_dir,
    )


@mcp.tool()
def swmf_explain_component_config_fix() -> dict[str, Any]:
    payload = explain_component_config_fix()
    payload.setdefault("swmf_root_resolved", None)
    return payload


@mcp.tool()
def swmf_list_available_components(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None or catalog is None:
        return catalog_error or failure
    return _with_root(list_available_components(catalog), root)


@mcp.tool()
def swmf_find_param_command(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None or catalog is None:
        return catalog_error or failure
    return _with_root(find_param_command(catalog, name=name), root)


@mcp.tool()
def swmf_get_component_versions(
    component: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None or catalog is None:
        return catalog_error or failure
    return _with_root(get_component_versions(catalog, component=component), root)


@mcp.tool()
def swmf_find_example_params(
    query: str,
    max_results: int = 30,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None or catalog is None:
        return catalog_error or failure
    return _with_root(find_example_params(catalog, query=query, max_results=max_results), root)


@mcp.tool()
def swmf_trace_param_command(
    name: str,
    max_examples: int = 20,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None or catalog is None:
        return catalog_error or failure
    return _with_root(trace_param_command(catalog, name=name, max_examples=max_examples), root)


@mcp.tool()
def swmf_diagnose_param(
    param_path: str | None = None,
    param_text: str | None = None,
    nproc: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    """
    Fast diagnosis path: preflight + authoritative TestParam + fix synthesis in one call.

    Returns likely root cause, fastest likely fix, authoritative result, and recommended commands.
    """
    failure, root = _resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None:
        return failure

    if param_path is None and param_text is None:
        return _with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "PARAM_INPUT_MISSING",
                "message": "Provide param_path or param_text.",
            },
            root,
        )

    payload = diagnose_param(
        swmf_root_resolved=root.swmf_root_resolved,
        param_path=param_path,
        param_text=param_text,
        run_dir=run_dir,
        nproc=nproc,
        job_script_path=job_script_path,
    )
    return _with_root(payload, root)


def main() -> None:
    logger.info("Starting SWMF MCP prototype server on stdio")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
