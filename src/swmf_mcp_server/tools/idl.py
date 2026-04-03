from __future__ import annotations

import os
import re
import shlex
import shutil
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
_IDL_EXEC_ENV = "SWMF_IDL_EXEC"

_IDL_BATCH_SHELL_RC_FILES: dict[str, tuple[str, ...]] = {
    "sh": ("~/.profile",),
    "bash": ("~/.bashrc", "~/.bash_profile", "~/.profile"),
    "zsh": ("~/.zshrc", "~/.zprofile", "~/.zshenv"),
    "csh": ("~/.cshrc", "~/.login"),
    "tcsh": ("~/.tcshrc", "~/.cshrc", "~/.login"),
}


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


def _normalize_idl_shell(shell: str | None) -> tuple[str | None, str | None]:
    explicit = shell is not None and shell.strip() != ""
    if explicit:
        normalized = Path(shell or "").name.lower()
    else:
        normalized = Path(os.environ.get("SHELL", "/bin/sh")).name.lower() or "sh"

    if normalized in _IDL_BATCH_SHELL_RC_FILES:
        return normalized, None

    if explicit:
        allowed = ", ".join(sorted(_IDL_BATCH_SHELL_RC_FILES))
        return None, f"Unsupported shell '{shell}'. Supported shells: {allowed}."

    return "sh", None


def _resolve_shell_executable(shell_name: str) -> str | None:
    shell_path = shutil.which(shell_name)
    if shell_path:
        return shell_path
    if shell_name == "sh" and Path("/bin/sh").is_file():
        return "/bin/sh"
    return None


def _build_shell_preamble(shell_name: str, load_shell_rc: bool) -> str:
    if not load_shell_rc:
        return ""

    rc_files = _IDL_BATCH_SHELL_RC_FILES.get(shell_name, ())
    if shell_name in {"sh", "bash", "zsh"}:
        bootstrap = [
            f'[ -f "{rc_file.replace("~", "$HOME", 1)}" ] && . "{rc_file.replace("~", "$HOME", 1)}"'
            for rc_file in rc_files
        ]
        return "; ".join(bootstrap)

    bootstrap = [
        f'if ( -f "{rc_file.replace("~", "$HOME", 1)}" ) source "{rc_file.replace("~", "$HOME", 1)}"'
        for rc_file in rc_files
    ]
    return "; ".join(bootstrap)


def _build_shell_command(run_part: str, shell_name: str, load_shell_rc: bool) -> str:
    preamble = _build_shell_preamble(shell_name=shell_name, load_shell_rc=load_shell_rc)
    if preamble:
        return f"{preamble}; {run_part}"
    return run_part


def _shell_invocation_prefix(shell_executable: str, shell_name: str) -> list[str]:
    if shell_name in {"bash", "zsh", "csh", "tcsh"}:
        return [shell_executable, "-i", "-c"]
    return [shell_executable, "-c"]


def _resolve_idl_command(idl_command: str | None) -> tuple[str, str]:
    env_command = os.environ.get(_IDL_EXEC_ENV, "").strip()
    if env_command:
        return env_command, f"env:{_IDL_EXEC_ENV}"

    requested = (idl_command or "").strip()
    if requested:
        return requested, "argument"
    return "idl", "default"


def _extract_lookup_target(command: str) -> str | None:
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None

    if not tokens:
        return None

    i = 0
    while i < len(tokens) and "=" in tokens[i] and not tokens[i].startswith("="):
        i += 1
    if i >= len(tokens):
        return None

    if tokens[i] == "env":
        i += 1
        while i < len(tokens):
            token = tokens[i]
            if token == "--":
                i += 1
                break
            if token.startswith("-"):
                i += 1
                continue
            if "=" in token and not token.startswith("="):
                i += 1
                continue
            break
        if i >= len(tokens):
            return None
    return tokens[i]


def _build_lookup_check_command(lookup_target: str, shell_name: str) -> str:
    quoted = shlex.quote(lookup_target)
    if "/" in lookup_target:
        return f"/bin/test -x {quoted}"
    if shell_name in {"csh", "tcsh"}:
        return f"which {quoted} >& /dev/null"
    return f"command -v {quoted} >/dev/null 2>&1"


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
        return (
            f"Try running the saved script '{idl_script_filename}' with your normal IDL command first. "
            "If SWMF routines are missing at runtime, retry with IDL_PATH including "
            f"'{idl_general}' and IDL_STARTUP=idlrc."
        )
    warnings.append("Could not resolve SWMF root; IDL_PATH for SWMF macros may need manual setup.")
    return (
        f"Try running the saved script '{idl_script_filename}' with your normal IDL command first. "
        "Only if SWMF routines are missing should you configure IDL_PATH/IDL_STARTUP manually."
    )


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
    workflow_hints = [f"Use run_dir_resolved ({resolved_run_dir}) as the working directory."]
    notes = [
        "This tool only prepares commands and script text; nothing is executed.",
        "Run from the directory containing your SWMF output files unless your script uses absolute paths.",
        "workflow_hints contains workflow guidance (not executable shell commands).",
    ]
    guidance: list[str] = []
    requires_clarification = False
    requires_file_resolution = False

    raster_image_formats = {"png", "jpeg", "bmp", "tiff"}
    postscript_formats = {"ps"}
    plot_export_formats = raster_image_formats | postscript_formats

    if task == "animate":
        component_for_title = f" in {parsed['component']}" if parsed["component"] else ""
        plot_title = f"{variable.upper()}{component_for_title} {(parsed['cut_plane'] or 'requested cut')} cut"
        workflow_hints.append(
            "Create a combined multi-snapshot .outs file from files matching output_pattern before running animate_data."
        )
        notes.append("animate_data expects a combined multi-snapshot .outs file.")
        if output_pattern is None and input_file is None:
            requires_file_resolution = True
            guidance.append("Provide output_pattern or input_file so the combined .outs source is explicit.")
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
        if input_file is None:
            requires_file_resolution = True
            guidance.append("Provide input_file to target a concrete dataset instead of the default template value.")

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
                workflow_hints.append(
                    f"After plotting, convert '{ps_file}' to '{export_name}.{export_format}' with your preferred PostScript conversion tool."
                )
            else:
                notes.append("Plot export for task='plot' writes PostScript output via set_device.")
        notes.append("Adjust func and plotmode as needed for scalar vs vector plotting in the IDL manual.")
    elif task == "read":
        if input_file is None:
            requires_file_resolution = True
            guidance.append("Provide input_file to avoid the default template filename 'example.out'.")
        idl_script_lines = [
            f"filename='{data_file}'",
            "read_data",
            "help, x, w",
        ]
        notes.append("read_data can prompt interactively for frame selection when multiple snapshots exist.")
    elif task == "transform":
        if input_file is None:
            requires_file_resolution = True
            guidance.append("Provide input_file to avoid the default template filename 'example.out'.")
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
        requires_file_resolution = True
        guidance.append("Replace the compare template filename with your two real data files before execution.")
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
        requires_file_resolution = True
        guidance.append("Update filename in the script to your actual log file path before execution.")
        idl_script_lines = [
            "filename='run.log'",
            "read_log_data",
        ]
        notes.append("Update filename for your actual SWMF log file path.")
    elif task == "plot_log":
        requires_file_resolution = True
        guidance.append("Update filename in the script to your actual log file path before execution.")
        idl_script_lines = [
            "filename='run.log'",
            "read_log_data",
            "plot_log_data",
        ]
        notes.append("Use plotmode variants for log plotting as described in the IDL manual.")
    else:
        requires_clarification = True
        guidance.extend(
            [
                "Choose a concrete task (plot, animate, transform, compare, read, read_log, or plot_log).",
                "Provide an output pattern and/or input file to avoid a generic starter script.",
                "Use swmf_list_idl_procedures and swmf_explain_idl_procedure for macro-level details before execution.",
            ]
        )
        idl_script_lines = [
            "; starter IDL session script",
            "set_default_values",
            "; choose one: read_data / show_data / animate_data / read_log_data",
        ]
        notes.append("Request was broad; generated a starter script. Add the specific macro sequence you want.")

    workflow_hints.append("Save idl_script text to idl_script_filename before manual execution.")
    workflow_hints.append(_idl_command_with_env(swmf_root_resolved, idl_script_filename, warnings))

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
        "workflow_hints": workflow_hints,
        "idl_script_filename": idl_script_filename,
        "idl_script": "\n".join(line for line in idl_script_lines if line),
        "guided_next_steps": guidance,
        "requires_clarification": requires_clarification,
        "requires_file_resolution": requires_file_resolution,
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
    shell: str | None = None,
    load_shell_rc: bool = True,
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

    shell_name, shell_error = _normalize_idl_shell(shell)
    if shell_name is None:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "UNSUPPORTED_SHELL",
            "message": shell_error,
            "working_dir": str(work_dir),
            "script_path": str(script_path),
            "allowed_shells": sorted(_IDL_BATCH_SHELL_RC_FILES),
        }

    shell_executable = _resolve_shell_executable(shell_name)
    if shell_executable is None:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "SHELL_NOT_FOUND",
            "message": f"Could not find shell executable for '{shell_name}'.",
            "working_dir": str(work_dir),
            "script_path": str(script_path),
            "shell": shell_name,
        }

    idl_command_resolved, idl_command_source = _resolve_idl_command(idl_command)
    lookup_target = _extract_lookup_target(idl_command_resolved)
    if lookup_target is None:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "IDL_COMMAND_INVALID",
            "message": "Could not parse idl command into an executable target.",
            "working_dir": str(work_dir),
            "script_path": str(script_path),
            "shell": shell_name,
            "idl_command_requested": idl_command,
            "idl_command_resolved": idl_command_resolved,
            "idl_command_source": idl_command_source,
        }

    shell_prefix = _shell_invocation_prefix(shell_executable=shell_executable, shell_name=shell_name)
    lookup_check = _build_lookup_check_command(lookup_target=lookup_target, shell_name=shell_name)
    shell_check_command = _build_shell_command(
        run_part=lookup_check,
        shell_name=shell_name,
        load_shell_rc=load_shell_rc,
    )

    check_proc = subprocess.run(
        [*shell_prefix, shell_check_command],
        cwd=str(work_dir),
        shell=False,
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    if check_proc.returncode != 0:
        return {
            "ok": False,
            "hard_error": False,
            "error_code": "IDL_COMMAND_NOT_FOUND",
            "message": (
                f"Could not resolve IDL executable '{lookup_target}' in shell '{shell_name}' after loading rc files."
            ),
            "working_dir": str(work_dir),
            "script_path": str(script_path),
            "shell": shell_name,
            "load_shell_rc": load_shell_rc,
            "idl_command_requested": idl_command,
            "idl_command_resolved": idl_command_resolved,
            "idl_command_source": idl_command_source,
            "lookup_target": lookup_target,
            "check_command": shell_check_command,
            "check_stdout": check_proc.stdout,
            "check_stderr": check_proc.stderr,
            "how_to_fix": [
                f"Set env '{_IDL_EXEC_ENV}' in mcp.json to your IDL executable (absolute path preferred).",
                "If your setup relies on shell aliases/functions, keep load_shell_rc=true and use shell='zsh' (or your shell).",
                "You can also pass idl_command explicitly for this invocation.",
            ],
            "search_hints": [
                "Run: command -v idl",
                "Run: find /Applications -name idl 2>/dev/null | head",
                "Run: find /opt -name idl 2>/dev/null | head",
            ],
        }

    command = f"{idl_command_resolved} < {script_path.name}"
    shell_command = _build_shell_command(
        run_part=command,
        shell_name=shell_name,
        load_shell_rc=load_shell_rc,
    )

    try:
        proc = subprocess.run(
            [*shell_prefix, shell_command],
            cwd=str(work_dir),
            shell=False,
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
            "shell": shell_name,
            "shell_command": shell_command,
            "load_shell_rc": load_shell_rc,
            "idl_command_resolved": idl_command_resolved,
            "idl_command_source": idl_command_source,
            "lookup_target": lookup_target,
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
            "shell": shell_name,
            "shell_command": shell_command,
            "load_shell_rc": load_shell_rc,
            "idl_command_resolved": idl_command_resolved,
            "idl_command_source": idl_command_source,
            "lookup_target": lookup_target,
        }

    return {
        "ok": proc.returncode == 0,
        "hard_error": proc.returncode != 0,
        "working_dir": str(work_dir),
        "script_path": str(script_path),
        "command": command,
        "shell": shell_name,
        "shell_command": shell_command,
        "load_shell_rc": load_shell_rc,
        "idl_command_resolved": idl_command_resolved,
        "idl_command_source": idl_command_source,
        "lookup_target": lookup_target,
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


def register(app: Any) -> None:
    app.tool(description="Prepare an SWMF IDL workflow script and shell command sequence.")(swmf_prepare_idl_workflow)
    app.tool(description="Inspect FITS magnetogram metadata for SC quickrun preparation.")(swmf_inspect_fits_magnetogram)
    app.tool(description="List indexed SWMF IDL procedures with optional category filtering.")(swmf_list_idl_procedures)
    app.tool(description="Explain one indexed SWMF IDL procedure and its signature details.")(swmf_explain_idl_procedure)
    app.tool(description="Generate an IDL script payload from task-oriented SWMF inputs.")(swmf_generate_idl_script)
    app.tool(description="Run IDL batch script content in a specified working directory.")(swmf_run_idl_batch)
