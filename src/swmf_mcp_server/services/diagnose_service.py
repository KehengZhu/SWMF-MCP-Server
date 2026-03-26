from __future__ import annotations

from typing import Any

from .build_service import prepare_component_config
from .common import load_param_text, resolve_run_dir
from .run_service import infer_job_layout
from .testparam_service import run_testparam
from .validation_service import validate_external_inputs, validate_param


def _root_cause(
    code: str,
    message: str,
    authority: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "authority": authority,
        "evidence": evidence or {},
    }


def diagnose_param(
    swmf_root_resolved: str,
    param_text: str | None = None,
    param_path: str | None = None,
    run_dir: str | None = None,
    nproc: int | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    run_dir_resolved = str(resolve_run_dir(run_dir))
    loaded_text, resolved_param_path, load_error = load_param_text(
        param_text=param_text,
        param_path=param_path,
        run_dir=run_dir_resolved,
    )
    if load_error is not None or loaded_text is None:
        return {
            "ok": False,
            "summary": "Could not load PARAM input for diagnosis.",
            "root_causes": [
                _root_cause(
                    code="PARAM_LOAD_FAILED",
                    message=load_error or "Unknown PARAM loading error.",
                    authority="heuristic",
                )
            ],
            "fastest_likely_fix": "Provide a valid param_path or pass param_text.",
            "authoritative_result": {
                "executed": False,
                "reason": "PARAM input could not be loaded.",
            },
            "recommended_commands": [],
            "recommended_next_step": "Provide valid PARAM input and rerun swmf_diagnose_param.",
            "authority_by_field": {
                "summary": "heuristic",
                "root_causes": "heuristic",
                "fastest_likely_fix": "heuristic",
                "authoritative_result": "authoritative",
                "recommended_commands": "heuristic",
                "recommended_next_step": "heuristic",
            },
            "authority": "derived",
            "source_kind": "diagnostic_pipeline",
            "source_paths": [],
            "swmf_root_resolved": swmf_root_resolved,
            "run_dir_resolved": run_dir_resolved,
        }

    external_payload = validate_external_inputs(
        param_text=loaded_text,
        run_dir=run_dir_resolved,
    )
    lightweight_payload = validate_param(
        param_text=loaded_text,
        nproc=nproc,
        run_dir=run_dir_resolved,
    )
    component_fix = prepare_component_config(param_text=loaded_text)

    nproc_used = nproc
    nproc_source = "explicit" if nproc is not None else "fallback_default"
    layout_payload: dict[str, Any] | None = None

    if nproc_used is None:
        if job_script_path:
            layout_payload = infer_job_layout(job_script_path=job_script_path, run_dir=run_dir_resolved)
            if layout_payload.get("ok") and layout_payload.get("swmf_nproc") is not None:
                nproc_used = int(layout_payload["swmf_nproc"])
                nproc_source = "job_script_inference"
            else:
                nproc_used = 1
                nproc_source = "diagnostic_fallback"
        else:
            nproc_used = 1
            nproc_source = "fast_default"

    authoritative_result: dict[str, Any]
    if resolved_param_path is None:
        authoritative_result = {
            "executed": False,
            "reason": "Authoritative TestParam requires param_path; param_text-only input was provided.",
        }
    else:
        testparam_payload = run_testparam(
            param_path=resolved_param_path,
            swmf_root_resolved=swmf_root_resolved,
            nproc=nproc_used,
            run_dir=run_dir_resolved,
            job_script_path=None,
        )
        authoritative_result = {
            "executed": True,
            "ok": testparam_payload.get("ok", False),
            "error_code": testparam_payload.get("error_code"),
            "execution_context_ok": testparam_payload.get("execution_context_ok"),
            "exit_code": testparam_payload.get("exit_code"),
            "quick_interpretation": testparam_payload.get("quick_interpretation"),
            "key_evidence_lines": testparam_payload.get("key_evidence_lines", []),
            "raw_output": testparam_payload.get("raw_testparam_output"),
            "command": testparam_payload.get("command"),
            "execution_cwd": testparam_payload.get("execution_cwd"),
            "run_dir_resolved": testparam_payload.get("run_dir_resolved", run_dir_resolved),
            "fix_hint": testparam_payload.get("fix_hint"),
            "nproc_used": testparam_payload.get("nproc_used", nproc_used),
            "nproc_source": testparam_payload.get("nproc_source", nproc_source),
            "likely_missing_component_versions": testparam_payload.get("likely_missing_component_versions", False),
            "source_paths": testparam_payload.get("source_paths", []),
        }

    root_causes: list[dict[str, Any]] = []

    launch_context_invalid = (
        authoritative_result.get("executed")
        and authoritative_result.get("error_code") == "TESTPARAM_LAUNCH_CONTEXT_INVALID"
    )

    if launch_context_invalid:
        root_causes.append(
            _root_cause(
                code="TESTPARAM_LAUNCH_CONTEXT_INVALID",
                message="Authoritative validation could not run from a valid SWMF launch context.",
                authority="authoritative",
                evidence={
                    "execution_cwd": authoritative_result.get("execution_cwd"),
                    "run_dir_resolved": authoritative_result.get("run_dir_resolved"),
                    "key_evidence_lines": authoritative_result.get("key_evidence_lines", []),
                },
            )
        )

    missing_files = external_payload.get("missing_files", [])
    if missing_files and not launch_context_invalid:
        root_causes.append(
            _root_cause(
                code="MISSING_EXTERNAL_INPUTS",
                message="PARAM references files that do not exist or are unreadable.",
                authority="heuristic",
                evidence={"missing_files": missing_files},
            )
        )

    syntax_errors = lightweight_payload.get("syntax_or_structure_errors", [])
    if syntax_errors and not launch_context_invalid:
        root_causes.append(
            _root_cause(
                code="PARAM_STRUCTURE_ERRORS",
                message="PARAM contains structural or syntax-level issues.",
                authority="heuristic",
                evidence={"syntax_or_structure_errors": syntax_errors},
            )
        )

    if authoritative_result.get("executed") and not launch_context_invalid:
        if authoritative_result.get("ok") is False and authoritative_result.get("likely_missing_component_versions"):
            root_causes.append(
                _root_cause(
                    code="MISSING_COMPONENT_VERSIONS",
                    message="Authoritative validation indicates missing compiled component versions.",
                    authority="authoritative",
                    evidence={
                        "required_components": component_fix.get("required_components", []),
                        "recommended_component_versions": component_fix.get("recommended_component_versions", []),
                    },
                )
            )
        elif authoritative_result.get("ok") is False:
            root_causes.append(
                _root_cause(
                    code="AUTHORITATIVE_VALIDATION_FAILED",
                    message="Scripts/TestParam.pl reported validation errors.",
                    authority="authoritative",
                    evidence={"exit_code": authoritative_result.get("exit_code")},
                )
            )

    if not root_causes and authoritative_result.get("ok"):
        root_causes.append(
            _root_cause(
                code="NO_BLOCKING_ISSUES_DETECTED",
                message="No blocking issue was detected by lightweight or authoritative checks.",
                authority="authoritative",
            )
        )

    recommended_commands: list[str] = []
    fastest_likely_fix = "Review authoritative output and apply the smallest targeted PARAM correction."

    has_missing_versions = any(item["code"] == "MISSING_COMPONENT_VERSIONS" for item in root_causes)
    has_missing_inputs = any(item["code"] == "MISSING_EXTERNAL_INPUTS" for item in root_causes)
    has_structure_errors = any(item["code"] == "PARAM_STRUCTURE_ERRORS" for item in root_causes)

    if launch_context_invalid:
        fastest_likely_fix = "Run TestParam from the SWMF source root, not the run directory."
        if authoritative_result.get("command"):
            recommended_commands.append(authoritative_result["command"])
    elif has_missing_versions:
        config_cmd = component_fix.get("recommended_config_command")
        if config_cmd:
            recommended_commands.append(config_cmd)
        recommended_commands.extend(component_fix.get("rebuild_commands", []))
        if authoritative_result.get("command"):
            recommended_commands.append(authoritative_result["command"])
        fastest_likely_fix = (
            "Compile the required component versions with Config.pl -v, rebuild, then rerun TestParam."
        )
    elif has_missing_inputs:
        first_missing = missing_files[0]
        fastest_likely_fix = f"Provide or correct the missing referenced file: {first_missing}"
    elif has_structure_errors:
        first_error = syntax_errors[0]
        fastest_likely_fix = f"Fix the first PARAM structural error: {first_error}"
    elif authoritative_result.get("ok"):
        fastest_likely_fix = "No blocking fix required; proceed with run setup."

    summary = fastest_likely_fix
    if launch_context_invalid:
        summary = "Authoritative validation launch context is invalid; fix infrastructure context before PARAM diagnosis."
    elif authoritative_result.get("executed") and authoritative_result.get("ok") is False:
        summary = "Authoritative validation failed; likely root cause and fix recommendation synthesized."
    elif authoritative_result.get("executed") and authoritative_result.get("ok") is True:
        summary = "Authoritative validation passed; no blocking issue detected."

    next_step = "Apply the fastest likely fix and rerun swmf_diagnose_param once to confirm."
    if authoritative_result.get("executed") is False and resolved_param_path is None:
        next_step = "Provide param_path (or save PARAM.in) and rerun swmf_diagnose_param for authoritative validation."

    source_paths: list[str] = []
    if resolved_param_path:
        source_paths.append(resolved_param_path)
    source_paths.extend(authoritative_result.get("source_paths", []))

    return {
        "ok": True,
        "summary": summary,
        "root_causes": root_causes,
        "fastest_likely_fix": fastest_likely_fix,
        "authoritative_result": authoritative_result,
        "recommended_commands": recommended_commands,
        "recommended_next_step": next_step,
        "authority_by_field": {
            "summary": "derived",
            "root_causes": "derived",
            "fastest_likely_fix": "derived",
            "authoritative_result": "authoritative",
            "recommended_commands": "derived",
            "recommended_next_step": "derived",
        },
        "preflight": {
            "external_inputs": external_payload,
            "lightweight_validation": lightweight_payload,
            "required_components": component_fix.get("required_components", []),
            "nproc_used_for_authoritative": nproc_used,
            "nproc_source_for_authoritative": nproc_source,
            "job_layout": layout_payload,
        },
        "authority": "derived",
        "source_kind": "diagnostic_pipeline",
        "source_paths": sorted(set(source_paths)),
        "swmf_root_resolved": swmf_root_resolved,
        "run_dir_resolved": run_dir_resolved,
    }
