from __future__ import annotations

import copy
import re
import subprocess
from pathlib import Path

from .common import resolve_run_dir
from .run_service import infer_job_layout


_TESTPARAM_CACHE: dict[tuple[str, str, int | None], dict] = {}


def _cache_key(swmf_root_resolved: str, param_path_resolved: str, requested_nproc: int | None) -> tuple[str, str, int | None]:
    return (str(Path(swmf_root_resolved).resolve()), str(Path(param_path_resolved).resolve()), requested_nproc)


def _is_cache_valid(payload: dict) -> bool:
    param_path = payload.get("param_path_resolved")
    testparam_script = None
    source_paths = payload.get("source_paths") or []
    if source_paths:
        testparam_script = source_paths[0]
    try:
        if not param_path or not testparam_script:
            return False
        return (
            Path(param_path).stat().st_mtime == payload.get("_cache_param_mtime")
            and Path(testparam_script).stat().st_mtime == payload.get("_cache_script_mtime")
        )
    except OSError:
        return False


def _cache_store(payload: dict, requested_nproc: int | None) -> None:
    try:
        param_mtime = Path(payload["param_path_resolved"]).stat().st_mtime
        script_mtime = Path(payload["source_paths"][0]).stat().st_mtime
    except (KeyError, IndexError, OSError):
        return
    cached = copy.deepcopy(payload)
    cached["_cache_param_mtime"] = param_mtime
    cached["_cache_script_mtime"] = script_mtime
    _TESTPARAM_CACHE[_cache_key(payload["execution_cwd"], payload["param_path_resolved"], requested_nproc)] = cached


def _cache_get(swmf_root_resolved: str, param_path_resolved: str, requested_nproc: int | None) -> dict | None:
    cached = _TESTPARAM_CACHE.get(_cache_key(swmf_root_resolved, param_path_resolved, requested_nproc))
    if cached is None:
        return None
    if not _is_cache_valid(cached):
        return None
    payload = copy.deepcopy(cached)
    payload["from_cache"] = True
    payload.pop("_cache_param_mtime", None)
    payload.pop("_cache_script_mtime", None)
    return payload


def _resolve_param_path_for_external_tools(param_path: str, run_dir: str | None) -> tuple[Path | None, str | None]:
    try:
        path = Path(param_path).expanduser()
        if not path.is_absolute():
            base_dir = Path(run_dir).expanduser().resolve() if run_dir else Path.cwd().resolve()
            path = base_dir / path
        resolved = path.resolve()
        if not resolved.is_file():
            return None, f"param_path does not point to a file: {resolved}"
        return resolved, None
    except OSError as exc:
        return None, f"Failed to resolve param_path: {exc}"


def _testparam_indicates_missing_component_versions(output_text: str) -> bool:
    text = output_text.lower()
    patterns = [
        r"component.*version.*(not found|missing|cannot|could not)",
        r"version.*for component.*(not found|missing|cannot|could not)",
        r"unknown component version",
        r"empty",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def _key_evidence_lines(output_text: str) -> list[str]:
    lines: list[str] = []
    for line in output_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if any(
            token in lowered
            for token in [
                "could not find config.pl",
                "can't open perl script",
                "cannot open",
                "no such file",
                "error",
                "fatal",
            ]
        ):
            lines.append(stripped)
    return lines[:8]


def _is_launch_context_failure(output_text: str) -> bool:
    text = output_text.lower()
    patterns = [
        r"could not find\s+config\.pl",
        r"can't open perl script",
        r"cannot open perl script",
        r"could not find\s+param\.xml",
        r"no such file.*config\.pl",
        r"no such file.*param\.xml",
        r"missing top[- ]level swmf",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def run_testparam(
    param_path: str,
    swmf_root_resolved: str,
    nproc: int | None = None,
    run_dir: str | None = None,
    job_script_path: str | None = None,
) -> dict:
    requested_nproc = nproc
    resolved_run_dir = resolve_run_dir(run_dir)
    execution_cwd = str(Path(swmf_root_resolved).resolve())
    resolved_param_path, param_error = _resolve_param_path_for_external_tools(param_path=param_path, run_dir=str(resolved_run_dir))
    if param_error is not None or resolved_param_path is None:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "PARAM_PATH_INVALID",
            "message": param_error or "Invalid param_path.",
            "execution_context_ok": False,
            "execution_cwd": execution_cwd,
            "authority": "authoritative",
            "source_kind": "TestParam.pl",
            "source_paths": [],
        }

    testparam_script = Path(swmf_root_resolved) / "Scripts" / "TestParam.pl"
    if not testparam_script.is_file():
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "TESTPARAM_NOT_FOUND",
            "message": f"Could not find Scripts/TestParam.pl under resolved SWMF root: {testparam_script}",
            "execution_context_ok": False,
            "execution_cwd": execution_cwd,
            "authority": "authoritative",
            "source_kind": "TestParam.pl",
            "source_paths": [],
        }

    nproc_source = "explicit"
    inferred_layout: dict | None = None
    if nproc is None:
        if job_script_path:
            layout_result = infer_job_layout(job_script_path=job_script_path, run_dir=str(resolved_run_dir))
            if layout_result.get("ok") and layout_result.get("swmf_nproc") is not None:
                nproc = int(layout_result["swmf_nproc"])
                nproc_source = "job_script_inference"
                inferred_layout = layout_result
            else:
                return {
                    "ok": False,
                    "hard_error": True,
                    "error_code": "NPROC_INFERENCE_FAILED",
                    "message": "nproc was not provided and could not be inferred from the provided job script.",
                    "how_to_fix": [
                        "Provide nproc explicitly.",
                        "Or provide a valid job_script_path with SWMF launch directives.",
                    ],
                    "job_layout": layout_result,
                    "execution_context_ok": False,
                    "execution_cwd": execution_cwd,
                    "authority": "authoritative",
                    "source_kind": "TestParam.pl",
                    "source_paths": [str(testparam_script)],
                }
        else:
            # Fast path: skip expensive run_dir job-script scanning unless explicitly requested.
            nproc = 1
            nproc_source = "fast_default"

    cached = _cache_get(swmf_root_resolved=execution_cwd, param_path_resolved=str(resolved_param_path), requested_nproc=requested_nproc)
    if cached is not None:
        return cached

    assert nproc is not None
    cmd = ["perl", str(testparam_script), f"-n={nproc}", str(resolved_param_path)]
    try:
        # SWMF top-level validation helper expects SWMF source-root execution context.
        result = subprocess.run(cmd, cwd=execution_cwd, capture_output=True, text=True, check=False)
    except OSError as exc:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "TESTPARAM_EXECUTION_FAILED",
            "message": f"Failed to execute TestParam.pl: {exc}",
            "execution_context_ok": False,
            "execution_cwd": execution_cwd,
            "authority": "authoritative",
            "source_kind": "TestParam.pl",
            "source_paths": [str(testparam_script)],
        }

    output_text = "\n".join([result.stdout, result.stderr]).strip()
    key_evidence_lines = _key_evidence_lines(output_text)
    launch_context_invalid = (result.returncode != 0) and _is_launch_context_failure(output_text)
    missing_versions = (result.returncode != 0) and _testparam_indicates_missing_component_versions(output_text)

    if launch_context_invalid:
        error_code = "TESTPARAM_LAUNCH_CONTEXT_INVALID"
        execution_context_ok = False
        quick_interpretation = (
            "TestParam failed due to MCP execution context (launch directory/environment), "
            "not PARAM semantics."
        )
        fix_hint = "Run TestParam from the SWMF source root, not the run directory."
    elif result.returncode == 0:
        error_code = None
        execution_context_ok = True
        quick_interpretation = (
            "TestParam.pl completed successfully (no validation errors reported). Output contains informational messages only."
            if output_text
            else "TestParam.pl completed successfully (no validation errors reported). Silent completion is normal."
        )
        fix_hint = None
    elif missing_versions:
        error_code = "TESTPARAM_MISSING_COMPONENT_VERSIONS"
        execution_context_ok = True
        quick_interpretation = (
            "TestParam.pl reported errors that are likely related to missing compiled component versions. No automatic fix is applied."
        )
        fix_hint = None
    else:
        error_code = "TESTPARAM_VALIDATION_FAILED"
        execution_context_ok = True
        quick_interpretation = "TestParam.pl reported validation errors. Review stdout/stderr for details."
        fix_hint = None

    payload = {
        "ok": result.returncode == 0,
        "authoritative": True,
        "tool": "Scripts/TestParam.pl",
        "error_code": error_code,
        "execution_context_ok": execution_context_ok,
        "authority": "authoritative",
        "source_kind": "TestParam.pl",
        "source_paths": [str(testparam_script)],
        "run_dir_resolved": str(resolved_run_dir),
        "execution_cwd": execution_cwd,
        "param_path_resolved": str(resolved_param_path),
        "command": " ".join(cmd),
        "nproc_used": nproc,
        "nproc_source": nproc_source,
        "job_layout": inferred_layout,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "raw_testparam_output": output_text,
        "key_evidence_lines": key_evidence_lines,
        "quick_interpretation": quick_interpretation,
        "fix_hint": fix_hint,
        "likely_missing_component_versions": missing_versions,
        "component_config_hint": None,
        "auto_fix_attempted": False,
        "requires_explicit_user_request_for_fixes": True,
        "next_step": "Await user instruction before preparing or applying any fixes.",
        "from_cache": False,
    }
    _cache_store(payload, requested_nproc=requested_nproc)
    return payload
