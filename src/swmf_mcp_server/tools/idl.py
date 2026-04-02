from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..catalog import get_idl_procedure, get_source_catalog, list_idl_procedures as catalog_list_idl_procedures
from ..core.common import resolve_input_path, resolve_run_dir
from ._helpers import resolve_root_or_failure, with_root


def _try_import_astropy_fits() -> tuple[Any | None, str | None]:
    try:
        from astropy.io import fits as astropy_fits

        return astropy_fits, None
    except Exception as exc:
        return None, f"Optional dependency 'astropy' is required for FITS inspection: {exc}"


def _header_value(header: Any, keys: list[str]) -> str | None:
    for key in keys:
        value = header.get(key)
        if value is not None:
            text = str(value).strip()
            if text:
                return text
    return None


def _probable_map_type_from_header_and_name(header: Any, fits_name: str) -> str:
    stacked = " ".join(
        [
            fits_name.lower(),
            str(header.get("MAPTYPE", "")).lower(),
            str(header.get("CTYPE1", "")).lower(),
            str(header.get("CTYPE2", "")).lower(),
            str(header.get("CONTENT", "")).lower(),
            str(header.get("OBJECT", "")).lower(),
            str(header.get("COMMENT", "")).lower(),
        ]
    )
    if "synoptic" in stacked:
        return "synoptic"
    if "synchronic" in stacked or "diachronic" in stacked:
        return "synchronic"
    return "unknown"


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _summarize_fits_data_array(data: Any) -> tuple[list[int] | None, float | None, float | None, list[str]]:
    warnings: list[str] = []
    shape: list[int] | None = None
    value_min: float | None = None
    value_max: float | None = None

    data_shape = getattr(data, "shape", None)
    if isinstance(data_shape, tuple):
        shape = [int(item) for item in data_shape]

    if data is None:
        warnings.append("Selected FITS HDU has no data array.")
        return shape, value_min, value_max, warnings

    try:
        if hasattr(data, "min") and hasattr(data, "max"):
            value_min = _safe_float(data.min())
            value_max = _safe_float(data.max())
    except Exception:
        warnings.append("Could not compute data min/max from FITS array.")

    return shape, value_min, value_max, warnings


def inspect_fits_magnetogram(
    fits_path: str,
    run_dir: str | None,
    read_data: bool,
    importer: Any | None = None,
) -> dict:
    resolved, path_error = resolve_input_path(fits_path, run_dir=run_dir)
    if path_error is not None or resolved is None:
        return {
            "ok": False,
            "hard_error": True,
            "message": path_error or "Could not resolve fits_path.",
            "fits_path_resolved": str(resolved) if resolved else None,
            "warnings": [],
            "suggested_next_tool": None,
        }

    fits_mod, dep_error = importer() if importer is not None else _try_import_astropy_fits()
    if fits_mod is None:
        return {
            "ok": False,
            "hard_error": False,
            "message": dep_error,
            "fits_path_resolved": str(resolved),
            "warnings": ["Install astropy to enable FITS metadata inspection."],
            "how_to_fix": ["Install dependency: pip install astropy"],
            "suggested_next_tool": None,
        }

    warnings: list[str] = []
    try:
        with fits_mod.open(str(resolved), memmap=True) as hdul:
            if not hdul:
                return {
                    "ok": False,
                    "hard_error": True,
                    "message": "FITS file has no HDU entries.",
                    "fits_path_resolved": str(resolved),
                    "warnings": warnings,
                    "suggested_next_tool": None,
                }

            selected_hdu = hdul[0]
            if getattr(selected_hdu, "data", None) is None:
                for hdu in hdul:
                    if getattr(hdu, "data", None) is not None:
                        selected_hdu = hdu
                        break

            header = selected_hdu.header
            instrument = _header_value(header, ["INSTRUME", "TELESCOP", "OBSERVAT", "ORIGIN"])
            source = _header_value(header, ["ORIGIN", "PROVIDER", "MISSION", "OBSRVTRY"])
            observation_date = _header_value(header, ["DATE-OBS", "T_OBS", "OBS_DATE", "DATE_OBS"])
            map_date = _header_value(header, ["MAPDATE", "DATE", "DATE_MAP", "T_REC"])
            carrington_rotation = _header_value(header, ["CAR_ROT", "CARROT", "CRROT", "CARROTNO", "CRLN_OBS"])

            coordinate_hints = {
                "ctype1": _header_value(header, ["CTYPE1"]),
                "ctype2": _header_value(header, ["CTYPE2"]),
                "cunit1": _header_value(header, ["CUNIT1"]),
                "cunit2": _header_value(header, ["CUNIT2"]),
                "wcs_name": _header_value(header, ["WCSNAME", "WCSNAMEA", "WCSNAMEB"]),
            }

            dimensions = None
            if header.get("NAXIS", 0) >= 2:
                dimensions = {
                    "naxis": int(header.get("NAXIS", 0)),
                    "naxis1": _safe_float(header.get("NAXIS1")),
                    "naxis2": _safe_float(header.get("NAXIS2")),
                }

            data_summary: dict[str, Any] | None = None
            if read_data:
                shape, value_min, value_max, data_warnings = _summarize_fits_data_array(getattr(selected_hdu, "data", None))
                warnings.extend(data_warnings)
                data_summary = {"shape": shape, "min": value_min, "max": value_max}

            return {
                "ok": True,
                "hard_error": False,
                "authority": "derived",
                "source_kind": "file",
                "source_paths": [str(resolved)],
                "message": "FITS metadata inspection completed.",
                "fits_path_resolved": str(resolved),
                "instrument": instrument,
                "source": source,
                "observation_date": observation_date,
                "map_date": map_date,
                "carrington_rotation": carrington_rotation,
                "dimensions": dimensions,
                "coordinate_system_hints": coordinate_hints,
                "probable_map_type": _probable_map_type_from_header_and_name(header, resolved.name),
                "data_summary": data_summary,
                "warnings": warnings,
                "suggested_next_tool": "swmf_prepare_sc_quickrun_from_magnetogram",
            }
    except Exception as exc:
        return {
            "ok": False,
            "hard_error": True,
            "message": f"Failed to inspect FITS file: {exc}",
            "fits_path_resolved": str(resolved),
            "warnings": warnings,
            "suggested_next_tool": None,
        }


def _normalize_artifact_name(name: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")
    return sanitized or "swmf_output"


def _parse_visualization_request(request: str) -> dict:
    text = request.strip().lower()
    warnings: list[str] = []
    assumptions: list[str] = []

    variable = None
    for token, normalized in [("rho", "rho"), ("density", "rho"), ("bx", "bx"), ("u", "u"), ("p", "p"), ("pressure", "p")]:
        if re.search(rf"\b{re.escape(token)}\b", text):
            variable = normalized
            break

    if variable is None:
        variable = "u"
        warnings.append("Could not identify a supported variable from the request.")
        assumptions.append("Assumed variable/function is 'u'.")

    component = None
    component_match = re.search(r"\b(cz|ee|gm|ie|ih|im|oh|ps|pt|pw|rb|sc|sp|ua)\b", text)
    if component_match:
        component = component_match.group(1).upper()
    elif re.search(r"\bsolar\s*corona\b", text):
        component = "SC"
    if component is None:
        assumptions.append("No component keyword detected; using a generic output-file pattern.")

    cut_plane = None
    if re.search(r"\bz\s*=\s*0\b|\bz0\b", text):
        cut_plane = "z=0"
    elif re.search(r"\bx\s*=\s*0\b|\bx0\b", text):
        cut_plane = "x=0"
    elif re.search(r"\by\s*=\s*0\b|\by0\b", text):
        cut_plane = "y=0"

    if cut_plane is None:
        warnings.append("Could not identify a cut plane such as z=0.")
        assumptions.append("Assumed combined output filename 'combined.outs'.")

    return {"variable": variable, "component": component, "cut_plane": cut_plane, "warnings": warnings, "assumptions": assumptions}


_IDL_MANUAL_TOPICS = [
    "read_data and show_data",
    "plot_data / show_data with func and plotmode",
    "animate_data for snapshot animation and movie export",
    "transform modes (regular, polar, unpolar, sphere, my)",
    "compare for dataset comparisons",
    "read_log_data / plot_log_data for log files",
    "cuts with grid/triplet/quadruplet",
]

_IDL_TASKS = ["animate", "compare", "transform", "read_log", "plot_log", "plot", "read", "generic"]

_IDL_OUTPUT_FORMATS = ["none", "png", "jpeg", "bmp", "tiff", "ps", "mp4", "mov", "avi"]

# Exported for capability introspection in server tool responses.
IDL_TASKS = tuple(_IDL_TASKS)
IDL_OUTPUT_FORMATS = tuple(_IDL_OUTPUT_FORMATS)


_PLOT_MODE_TOKENS = [
    "contbar",
    "contfill",
    "contour",
    "contlabel",
    "surface",
    "shade",
    "tv",
    "tvbar",
    "stream",
    "vector",
    "velovect",
    "arrow",
]


def _extract_plotmode(text: str) -> str | None:
    for token in _PLOT_MODE_TOKENS:
        if re.search(rf"\b{re.escape(token)}\b", text):
            return token
    return None


def _extract_transform_mode(text: str) -> str | None:
    mode_map = {
        "regular": "r",
        "polar": "p",
        "unpolar": "u",
        "sphere": "s",
        "my": "m",
        "none": "n",
    }
    for key, code in mode_map.items():
        if re.search(rf"\b{re.escape(key)}\b", text):
            return code
    return None


def _infer_idl_task(request: str, preferred_task: str | None = None) -> dict[str, Any]:
    text = request.strip().lower()
    parsed = _parse_visualization_request(request)
    warnings = list(parsed["warnings"])
    assumptions = list(parsed["assumptions"])

    task = preferred_task
    if task is None:
        if re.search(r"\banimate\b|\banimation\b|\bmovie\b|\bvideo\b|\bmp4\b|\bmov\b|\bavi\b", text):
            task = "animate"
        elif re.search(r"\bcompare\b|\bdifference\b|\bw0\b|\bw1\b", text):
            task = "compare"
        elif re.search(r"\btransform\b|\bregular\b|\bpolar\b|\bunpolar\b|\bsphere\b|\bnxreg\b", text):
            task = "transform"
        elif re.search(r"\bread\s*log\b|\bread_log_data\b", text):
            task = "read_log"
        elif re.search(r"\bplot\s*log\b|\bshow\s*log\b|\bplot_log_data\b|\bshow_log_data\b", text):
            task = "plot_log"
        elif re.search(r"\bplot\b|\bshow\b|\bcontour\b|\bstream\b|\bvector\b|\bplotmode\b", text):
            task = "plot"
        elif re.search(r"\bread\s*data\b|\bread\s*snapshot\b|\bshow_data\b", text):
            task = "read"
        else:
            task = "generic"

    plotmode = _extract_plotmode(text)
    transform_mode = _extract_transform_mode(text)
    if task == "transform" and transform_mode is None:
        transform_mode = "r"
        assumptions.append("Assumed transform mode 'regular' (transform='r').")

    if task in {"plot", "animate"} and plotmode is None:
        plotmode = "contbar"
        assumptions.append("Assumed plotting mode is 'contbar'.")

    if task in {"plot", "animate", "compare"} and parsed["variable"] is None:
        warnings.append("No variable detected; plotting defaults may need manual adjustment.")

    return {
        "task": task,
        "variable": parsed["variable"],
        "component": parsed["component"],
        "cut_plane": parsed["cut_plane"],
        "plotmode": plotmode,
        "transform_mode": transform_mode,
        "warnings": warnings,
        "assumptions": assumptions,
    }


def _default_pattern_for_visualization(cut_plane: str | None, component: str | None) -> tuple[str, str | None]:
    if cut_plane == "z=0":
        return "*z=0*.out", "Heuristic pattern '*z=0*.out' may need manual adjustment for your filenames."
    if cut_plane == "x=0":
        return "*x=0*.out", "Heuristic pattern '*x=0*.out' may need manual adjustment for your filenames."
    if cut_plane == "y=0":
        return "*y=0*.out", "Heuristic pattern '*y=0*.out' may need manual adjustment for your filenames."
    if component == "SC":
        return "*.out", "Using broad pattern '*.out'; refine if your run directory has mixed outputs."
    return "*.out", "Using fallback pattern '*.out'; adjust to match your cut files."


def _idl_command_with_env(swmf_root_resolved: str | None, idl_script_filename: str, warnings: list[str]) -> str:
    if swmf_root_resolved:
        idl_general = str(Path(swmf_root_resolved) / "share" / "IDL" / "General")
        return f'IDL_PATH="{idl_general}:${{IDL_PATH:-}}" IDL_STARTUP=idlrc idl < {idl_script_filename}'
    warnings.append("Could not resolve SWMF root; IDL_PATH for SWMF macros may need manual setup.")
    return f"IDL_STARTUP=idlrc idl < {idl_script_filename}"


def prepare_idl_workflow(
    request: str | None,
    swmf_root_resolved: str | None,
    run_dir: str | None,
    output_pattern: str | None,
    input_file: str | None,
    artifact_name: str | None,
    output_format: str | None,
    frame_rate: int,
    preview: bool,
    frame_indices: list[int] | None,
    task: str | None = None,
) -> dict:
    normalized_request = (request or "").strip()
    normalized_task = (task or "").strip().lower() or None

    if normalized_task is None and not normalized_request:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "IDL_TASK_OR_REQUEST_REQUIRED",
            "message": "Provide task or request for IDL workflow planning.",
            "allowed_tasks": list(_IDL_TASKS),
            "warnings": [],
            "assumptions": [],
        }

    if normalized_task is not None and normalized_task not in _IDL_TASKS:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "IDL_TASK_INVALID",
            "message": f"Unsupported task '{normalized_task}'.",
            "allowed_tasks": list(_IDL_TASKS),
            "warnings": [],
            "assumptions": [],
        }

    parsed = _infer_idl_task(request=normalized_request, preferred_task=normalized_task)
    warnings = list(parsed["warnings"])
    assumptions = list(parsed["assumptions"])
    task = parsed["task"]

    resolved_run_dir = resolve_run_dir(run_dir)
    if output_pattern:
        pattern = output_pattern.strip()
    else:
        pattern, pattern_warning = _default_pattern_for_visualization(parsed["cut_plane"], parsed["component"])
        if pattern_warning:
            warnings.append(pattern_warning)

    outs_name = input_file.strip() if input_file else (f"{parsed['cut_plane']}.outs" if parsed["cut_plane"] else "combined.outs")
    data_file = input_file.strip() if input_file else "example.out"
    plotmode = parsed["plotmode"] or "contbar"
    variable = parsed["variable"] or "u"

    export_format = (output_format or "none").strip().lower()
    if export_format not in set(_IDL_OUTPUT_FORMATS):
        warnings.append(f"Unsupported output_format '{export_format}', defaulting to 'none'.")
        export_format = "none"

    export_name = _normalize_artifact_name(artifact_name) if artifact_name else _normalize_artifact_name(
        f"{(parsed['component'] or 'run').lower()}_{(parsed['cut_plane'] or 'cut').replace('=', '')}_{variable}_{task}"
    )

    if frame_rate <= 0:
        warnings.append("frame_rate must be positive; defaulting to 10.")
        frame_rate = 10

    idl_script_filename = f"idl_{task}_{export_name}.pro"
    idl_script_lines: list[str] = []
    shell_commands = [f"cd {resolved_run_dir}"]
    notes = [
        "This tool only prepares commands and script text; nothing is executed.",
        "Run from the directory containing your SWMF output files unless your script uses absolute paths.",
    ]

    raster_image_formats = {"png", "jpeg", "bmp", "tiff"}
    postscript_formats = {"ps"}
    plot_export_formats = raster_image_formats | postscript_formats

    if task == "animate":
        component_for_title = f" in {parsed['component']}" if parsed["component"] else ""
        plot_title = f"{variable.upper()}{component_for_title} {(parsed['cut_plane'] or 'requested cut')} cut"
        shell_commands.append(f"cat {pattern} > {outs_name}")
        notes.append("animate_data expects a combined multi-snapshot .outs file.")
        animate_export = "'n'" if export_format == "none" else f"'{export_format}'"
        is_video_export = export_format in {"mp4", "mov", "avi"}
        is_image_export = export_format in {"png", "jpeg", "bmp", "tiff", "ps"}
        animate_preview = "y" if preview else "n"
        firstpict_line = ""
        dpict_line = ""
        npictmax_line = ""
        if frame_indices:
            positive = [int(v) for v in frame_indices if int(v) > 0]
            if positive:
                first = min(positive)
                if len(positive) > 1:
                    sorted_values = sorted(set(positive))
                    step = sorted_values[1] - sorted_values[0]
                    if step <= 0:
                        step = 1
                    firstpict_line = f"firstpict={first}"
                    dpict_line = f"dpict={step}"
                    npictmax_line = f"npictmax={len(sorted_values)}"
                else:
                    firstpict_line = f"firstpict={first}"
                    npictmax_line = "npictmax=1"
        idl_script_lines = [
            f"filename='{outs_name}'",
            f"func='{variable}'",
            f"plotmode='{plotmode}'",
            f"plottitle='{plot_title}'",
            f"savemovie={animate_export}",
            f"showmovie='{animate_preview}'",
            f"videofile='{export_name}'" if is_video_export else "",
            f"videorate={frame_rate}" if is_video_export else "",
            f"moviedir='{export_name}'" if is_image_export else "",
            firstpict_line,
            dpict_line,
            npictmax_line,
            "animate_data",
        ]
        if is_video_export:
            notes.append("Video export optimization enabled: uses videofile/videorate for animate_data.")
    elif task == "plot":
        idl_script_lines = [
            f"filename='{data_file}'",
            "read_data",
            f"func='{variable}'",
            f"plotmode='{plotmode}'",
            "plot_data",
        ]
        if export_format in {"mp4", "mov", "avi"}:
            warnings.append("Video output_format applies to animate workflows. Ignoring video export for task='plot'.")

        if export_format in plot_export_formats:
            ps_file = f"{export_name}.ps"
            idl_script_lines.extend(
                [
                    f"set_device,'{ps_file}'",
                    "plot_data",
                    "close_device",
                ]
            )
            if export_format in raster_image_formats:
                warnings.append("SWMF IDL set_device uses a PostScript backend. Non-PS plot exports require conversion from .ps.")
                notes.append("For plot task, non-PS formats are produced by converting PostScript output.")
                shell_commands.append(
                    f"# convert PostScript to {export_format} (example with ImageMagick)"
                )
                shell_commands.append(
                    f"convert -density 300 {ps_file} {export_name}.{export_format}"
                )
            else:
                notes.append("Plot export for task='plot' writes PostScript output via set_device.")
        notes.append("Adjust func and plotmode as needed for scalar vs vector plotting in the IDL manual.")
    elif task == "read":
        idl_script_lines = [
            f"filename='{data_file}'",
            "read_data",
            "help, x, w",
        ]
        notes.append("read_data can prompt interactively for frame selection when multiple snapshots exist.")
    elif task == "transform":
        transform_mode = parsed["transform_mode"] or "r"
        idl_script_lines = [
            f"filename='{data_file}'",
            f"transform='{transform_mode}'",
            "nxreg=[100,100]",
            "read_data",
            f"func='{variable}'",
            f"plotmode='{plotmode}'",
            "plot_data",
        ]
        notes.append("For transform='my', compile your custom do_my_transform.pro before read_data.")
    elif task == "compare":
        idl_script_lines = [
            "filename='example1.out example2.out'",
            "read_data",
            "compare,w0,w1",
            "w=w1-w0",
            f"func='{variable}'",
            f"plotmode='{plotmode}'",
            "plot_data",
        ]
        notes.append("Update filename with the exact two datasets you want to compare.")
    elif task == "read_log":
        idl_script_lines = [
            "filename='run.log'",
            "read_log_data",
        ]
        notes.append("Update filename for your actual SWMF log file path.")
    elif task == "plot_log":
        idl_script_lines = [
            "filename='run.log'",
            "read_log_data",
            "plot_log_data",
        ]
        notes.append("Use plotmode variants for log plotting as described in the IDL manual.")
    else:
        idl_script_lines = [
            "; starter IDL session script",
            "set_default_values",
            "; choose one: read_data / show_data / animate_data / read_log_data",
        ]
        notes.append("Request was broad; generated a starter script. Add the specific macro sequence you want.")

    shell_commands.append("# save the returned idl_script text to the returned idl_script_filename")
    shell_commands.append(_idl_command_with_env(swmf_root_resolved, idl_script_filename, warnings))

    return {
        "ok": True,
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": [],
        "request": normalized_request,
        "run_dir_resolved": str(resolved_run_dir),
        "capability": task,
        "supported_manual_topics": list(_IDL_MANUAL_TOPICS),
        "normalized_inputs": {
            "task": task,
            "request": normalized_request,
            "output_pattern": pattern,
            "input_file": data_file,
            "artifact_name": export_name,
            "output_format": export_format,
            "frame_rate": frame_rate,
            "preview": preview,
            "frame_indices": frame_indices,
        },
        "inferred": {
            "task": task,
            "variable": variable,
            "component": parsed["component"],
            "cut_plane": parsed["cut_plane"],
            "plotmode": plotmode,
            "transform_mode": parsed["transform_mode"],
            "output_pattern": pattern,
            "input_file": data_file,
            "output_format": export_format,
            "artifact_name": export_name,
            "frame_indices": frame_indices,
        },
        "shell_commands": shell_commands,
        "idl_script_filename": idl_script_filename,
        "idl_script": "\n".join(line for line in idl_script_lines if line),
        "notes": notes,
        "assumptions": assumptions,
        "warnings": warnings,
    }


def swmf_list_idl_procedures(
    category: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None or catalog is None:
        return catalog_error or failure or {
            "ok": False,
            "hard_error": True,
            "message": "Could not load IDL source catalog.",
        }

    rows = catalog_list_idl_procedures(catalog.idl_procedures, category=category)
    payload = {
        "ok": True,
        "category": category,
        "procedures": rows,
        "count": len(rows),
        "authority": "authoritative",
        "source_kind": "idl_catalog",
        "source_paths": catalog.idl_macros,
    }
    return with_root(payload, root)


def swmf_explain_idl_procedure(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None or catalog is None:
        return catalog_error or failure or {
            "ok": False,
            "hard_error": True,
            "message": "Could not load IDL source catalog.",
        }

    payload = get_idl_procedure(catalog.idl_procedures, name=name)
    if payload is None:
        return with_root(
            {
                "ok": False,
                "hard_error": False,
                "message": f"IDL procedure not found: {name}",
                "name": name,
                "source_paths": catalog.idl_macros,
            },
            root,
        )

    response = {
        "ok": True,
        "name": payload["name"],
        "kind": payload["kind"],
        "signature": payload["signature"],
        "params": payload["params"],
        "keywords": payload["keywords"],
        "docstring": payload["docstring"],
        "category": payload["category"],
        "file_path": payload["file_path"],
        "line_number": payload["line_number"],
        "authority": "authoritative",
        "source_kind": "idl_catalog",
        "source_paths": [payload["file_path"]],
    }
    return with_root(response, root)


def swmf_generate_idl_script(
    task: str,
    data_files: list[str] | None = None,
    request: str | None = None,
    output_format: str | None = None,
    frame_rate: int = 10,
    preview: bool = False,
    artifact_name: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    root_resolved = root.swmf_root_resolved if root is not None else None

    input_file = data_files[0] if data_files else None
    output_pattern = data_files[0] if data_files and len(data_files) > 1 else None

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
        frame_indices=None,
        task=task,
    )

    if failure is not None:
        payload["resolution_failure"] = failure
        payload["swmf_root_resolved"] = None
        return payload

    assert root is not None
    return with_root(payload, root)


def swmf_run_idl_batch(
    script: str,
    working_dir: str,
    idl_command: str = "idl",
    timeout_s: int = 120,
) -> dict[str, Any]:
    work_dir = Path(working_dir).expanduser().resolve()
    if not work_dir.is_dir():
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "WORKING_DIR_NOT_FOUND",
            "message": f"working_dir is not a directory: {work_dir}",
        }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".pro", prefix="mcp_idl_", dir=str(work_dir), delete=False, encoding="utf-8") as handle:
        handle.write(script)
        script_path = Path(handle.name)

    command = f"{idl_command} < {script_path.name}"
    try:
        proc = subprocess.run(
            command,
            cwd=str(work_dir),
            shell=True,
            capture_output=True,
            text=True,
            timeout=max(1, timeout_s),
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "IDL_TIMEOUT",
            "message": f"IDL batch execution timed out after {timeout_s}s.",
            "working_dir": str(work_dir),
            "script_path": str(script_path),
            "command": command,
        }
    except OSError as exc:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "IDL_EXEC_FAILED",
            "message": f"Failed to execute IDL batch command: {exc}",
            "working_dir": str(work_dir),
            "script_path": str(script_path),
            "command": command,
        }

    return {
        "ok": proc.returncode == 0,
        "hard_error": proc.returncode != 0,
        "working_dir": str(work_dir),
        "script_path": str(script_path),
        "command": command,
        "exit_code": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


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
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
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
    return with_root(payload, root)


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


def swmf_list_tool_capabilities() -> dict[str, Any]:
    return {
        "ok": True,
        "hard_error": False,
        "authority": "authoritative",
        "source_kind": "implementation",
        "source_paths": ["src/swmf_mcp_server/server.py", "src/swmf_mcp_server/tools/idl.py"],
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


def register(app: Any) -> None:
    app.tool()(swmf_prepare_idl_workflow)
    app.tool()(swmf_inspect_fits_magnetogram)
    app.tool()(swmf_list_tool_capabilities)
    app.tool()(swmf_list_idl_procedures)
    app.tool()(swmf_explain_idl_procedure)
    app.tool()(swmf_generate_idl_script)
    app.tool()(swmf_run_idl_batch)
