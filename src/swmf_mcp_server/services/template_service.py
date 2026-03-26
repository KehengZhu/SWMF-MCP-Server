from __future__ import annotations

import fnmatch
import os
from pathlib import Path

from .common import resolve_input_path


def template_directory_candidates(swmf_root_resolved: str) -> list[Path]:
    root = Path(swmf_root_resolved)
    candidates = [root / "Param", root / "PARAM", root / "Examples", root / "example"]
    return [candidate for candidate in candidates if candidate.is_dir()]


def find_param_templates(swmf_root_resolved: str, template_kind: str) -> list[Path]:
    preferred = ["*SC*IH*PARAM*.in", "*IH*SC*PARAM*.in", "*SC*IH*.in"] if template_kind == "solar_sc_ih" else ["*SC*PARAM*.in", "*solar*SC*.in", "*SC*.in"]

    matches: list[Path] = []
    for directory in template_directory_candidates(swmf_root_resolved):
        for root_dir, _dirs, files in os.walk(directory):
            rel_parts = Path(root_dir).relative_to(directory).parts
            if len(rel_parts) > 4:
                continue
            for filename in files:
                for pattern in preferred:
                    if fnmatch.fnmatch(filename, pattern):
                        matches.append(Path(root_dir) / filename)
                        break

    return sorted({item.resolve() for item in matches})[:20]


def default_quickrun_param_skeleton(mode: str, fits_path_resolved: str | None, nproc: int) -> str:
    if mode == "sc_steady" or nproc <= 1:
        map_rows = "SC 0 -1 1"
    else:
        map_rows = "\n".join([f"SC 0 {max(nproc - 2, 0)} 1", "IH -1 -1 1"])

    time_accurate = mode == "sc_ih_timeaccurate"
    time_flag = "T" if time_accurate else "F"
    stop_line = "7200.0 tSimulationMax" if time_accurate else "4000 MaxIteration"

    return "\n".join(
        [
            "#DESCRIPTION",
            "MCP heuristic quick solar-corona setup from magnetogram metadata",
            "",
            "! BEGIN MCP_HEURISTIC_QUICKRUN_PATCH",
            "! This section is heuristic and should be reviewed against your SWMF docs/examples.",
            f"! Magnetogram source: {fits_path_resolved or 'not provided'}",
            "#TIMEACCURATE",
            f"{time_flag} DoTimeAccurate",
            "",
            "ID Proc0 ProcEnd Stride nThread",
            "#COMPONENTMAP",
            map_rows,
            "",
            "#BEGIN_COMP SC",
            "#MAGNETOGRAM",
            f"{fits_path_resolved or 'magnetogram.fits'} NameMagnetogramFile",
            "#END_COMP SC",
            "",
            "#STOP",
            stop_line,
            "-1 MaxIteration",
            "! END MCP_HEURISTIC_QUICKRUN_PATCH",
            "",
            "#END",
        ]
    )


def apply_quickrun_template_patch(
    template_text: str,
    mode: str,
    fits_path_resolved: str | None,
) -> tuple[str, list[str]]:
    patch_summary: list[str] = [
        "Added explicit heuristic patch markers for quick-run settings.",
        "Added/updated magnetogram input hint for SC component block.",
        "Added quick-run note clarifying non-authoritative physics assumptions.",
    ]
    patch_block = "\n".join(
        [
            "! BEGIN MCP_HEURISTIC_QUICKRUN_PATCH",
            f"! Mode: {mode}",
            "! This section is heuristic and should be validated with Scripts/TestParam.pl and solar docs.",
            f"! Suggested magnetogram: {fits_path_resolved or 'magnetogram.fits'}",
            "#BEGIN_COMP SC",
            "#MAGNETOGRAM",
            f"{fits_path_resolved or 'magnetogram.fits'} NameMagnetogramFile",
            "#END_COMP SC",
            "! END MCP_HEURISTIC_QUICKRUN_PATCH",
        ]
    )
    return template_text.rstrip() + "\n\n" + patch_block + "\n", patch_summary


def generate_param_from_template(
    template_kind: str,
    fits_path: str | None,
    run_dir: str | None,
    swmf_root_resolved: str,
    nproc: int | None,
) -> dict:
    if template_kind not in {"solar_sc", "solar_sc_ih"}:
        return {
            "ok": False,
            "hard_error": True,
            "message": f"Unsupported template_kind: {template_kind}",
            "how_to_fix": ["Use template_kind='solar_sc' or template_kind='solar_sc_ih'."],
        }

    mode = "sc_ih_steady" if template_kind == "solar_sc_ih" else "sc_steady"
    nproc_effective = nproc if nproc is not None else 64
    fits_path_resolved: str | None = None
    warnings: list[str] = []

    if fits_path is not None:
        resolved_fits, fits_error = resolve_input_path(fits_path, run_dir=run_dir)
        if fits_error:
            warnings.append(f"Could not resolve fits_path for template patching: {fits_error}")
        elif resolved_fits is not None:
            fits_path_resolved = str(resolved_fits)

    templates = find_param_templates(swmf_root_resolved, template_kind=template_kind)
    if templates:
        selected_template = templates[0]
        try:
            template_text = selected_template.read_text(encoding="utf-8")
        except OSError as exc:
            return {
                "ok": False,
                "hard_error": True,
                "message": f"Failed to read template {selected_template}: {exc}",
            }

        suggested_text, patch_summary = apply_quickrun_template_patch(
            template_text=template_text,
            mode=mode,
            fits_path_resolved=fits_path_resolved,
        )
        return {
            "ok": True,
            "template_kind": template_kind,
            "template_source": str(selected_template),
            "template_found": True,
            "heuristic": True,
            "authority": "derived",
            "source_kind": "example PARAM.in",
            "source_paths": [str(selected_template)],
            "suggested_param_text": suggested_text,
            "suggested_param_patch_summary": patch_summary,
            "warnings": warnings,
        }

    fallback_text = default_quickrun_param_skeleton(mode=mode, fits_path_resolved=fits_path_resolved, nproc=nproc_effective)
    return {
        "ok": True,
        "template_kind": template_kind,
        "template_source": None,
        "template_found": False,
        "heuristic": True,
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": [],
        "suggested_param_text": fallback_text,
        "suggested_param_patch_summary": [
            "No template was found; returned a minimal heuristic PARAM skeleton.",
            "Inserted SC magnetogram input placeholder and component map suggestion.",
        ],
        "warnings": warnings + ["No suitable solar template found under common SWMF template directories."],
    }
