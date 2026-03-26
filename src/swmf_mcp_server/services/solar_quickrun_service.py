from __future__ import annotations

from .build_service import prepare_build, prepare_component_config
from .idl_service import inspect_fits_magnetogram
from .run_service import infer_job_layout, prepare_run
from .template_service import default_quickrun_param_skeleton, generate_param_from_template

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
) -> dict:
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
    layout_payload: dict | None = None
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
