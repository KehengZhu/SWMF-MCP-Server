from __future__ import annotations

import copy
import fnmatch
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from ..catalog import get_source_catalog
from ..catalog.xml_catalog import normalize_command_name
from ..core.authority import AUTHORITY_DERIVED, AUTHORITY_HEURISTIC, SOURCE_KIND_CURATED, SOURCE_KIND_LIGHTWEIGHT_PARSER
from ..core.common import load_param_text, resolve_reference_path, resolve_run_dir
from ..core.models import SourceCatalog, SourceRef
from ..knowledge.curated import CURATED_KNOWLEDGE, normalize_curated_lookup_key
from ..parsing.component_map import expand_component_map_rows
from ..parsing.external_refs import extract_external_references_from_param_text
from ..parsing.param_parser import parse_param_text
from ._helpers import resolve_root_or_failure, with_root


_TESTPARAM_CACHE: dict[tuple[str, str, int | None], dict[str, Any]] = {}


def explain_param(name: str, catalog: SourceCatalog | None) -> dict[str, Any]:
    if catalog is None:
        key = normalize_curated_lookup_key(name)
        curated = CURATED_KNOWLEDGE.get(key)
        if curated is None:
            return {
                "found": False,
                "name": name,
                "message": "No command match found in curated knowledge.",
                "authority": AUTHORITY_HEURISTIC,
                "source_kind": SOURCE_KIND_CURATED,
                "source_paths": [],
                "source_kinds": [SOURCE_KIND_CURATED],
            }

        return {
            "found": True,
            "name": curated["title"],
            "summary": curated.get("summary"),
            "details": curated.get("details"),
            "aliases": curated.get("aliases", []),
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": SOURCE_KIND_CURATED,
            "source_paths": [],
            "source_kinds": [SOURCE_KIND_CURATED],
            "sources": [{"kind": SOURCE_KIND_CURATED, "path": None, "authority": AUTHORITY_HEURISTIC}],
        }

    normalized = normalize_command_name(name)
    command_hits = catalog.commands.get(normalized, [])
    sources: list[SourceRef] = []

    curated_key = normalize_curated_lookup_key(name)
    curated = CURATED_KNOWLEDGE.get(curated_key)

    authority = AUTHORITY_HEURISTIC
    source_kind = SOURCE_KIND_CURATED
    title = name
    summary = None
    details = None
    defaults: dict[str, str] = {}
    allowed_values: list[str] = []
    ranges: list[str] = []
    aliases: list[str] = []
    owners: list[str] = []

    if command_hits:
        authority = "authoritative"
        source_kind = command_hits[0].source_kind
        first = command_hits[0]
        title = first.normalized
        summary = first.description

        for hit in command_hits:
            if hit.component and hit.component not in owners:
                owners.append(hit.component)
            defaults.update(hit.defaults)
            allowed_values.extend(item for item in hit.allowed_values if item not in allowed_values)
            ranges.extend(item for item in hit.ranges if item not in ranges)
            sources.append(SourceRef(kind=hit.source_kind, path=hit.source_path, authority=hit.authority))

    if curated is not None:
        title = curated.get("title", title)
        if summary is None:
            summary = curated.get("summary")
        details = curated.get("details")
        aliases.extend(curated.get("aliases", []))
        sources.append(SourceRef(kind=SOURCE_KIND_CURATED, path=None, authority=AUTHORITY_HEURISTIC))
        if authority == AUTHORITY_HEURISTIC:
            authority = AUTHORITY_DERIVED

    if not command_hits and curated is None:
        return {
            "found": False,
            "name": name,
            "message": "No command match found in curated or indexed SWMF sources.",
            "authority": AUTHORITY_HEURISTIC,
            "source_kind": SOURCE_KIND_CURATED,
            "source_paths": [],
            "source_kinds": [SOURCE_KIND_CURATED],
        }

    seen: set[tuple[str, str | None, str]] = set()
    source_payload: list[dict[str, Any]] = []
    for item in sources:
        key = (item.kind, item.path, item.authority)
        if key in seen:
            continue
        seen.add(key)
        source_payload.append({"kind": item.kind, "path": item.path, "authority": item.authority})

    source_paths = [item["path"] for item in source_payload if item["path"]]
    source_kinds = sorted({item["kind"] for item in source_payload})

    return {
        "found": True,
        "name": title,
        "normalized": normalized,
        "summary": summary,
        "details": details,
        "aliases": sorted(set(aliases)),
        "owner_components": owners,
        "defaults": defaults,
        "allowed_values": allowed_values,
        "ranges": ranges,
        "source_paths": source_paths,
        "source_kind": source_kind,
        "source_kinds": source_kinds,
        "sources": source_payload,
        "authority": authority,
    }


def _find_first_component_map(sessions: list) -> list[dict[str, Any]]:
    for session in sessions:
        if session.component_map_rows:
            return session.component_map_rows
    return []


def _component_ids_from_map(rows: list[dict[str, Any]]) -> set[str]:
    return {row["component"] for row in rows}


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


def classify_lightweight_findings(
    param_text: str,
    parser_errors: list[str],
    parser_warnings: list[str],
    param_path_resolved: str | None,
    run_dir: str | None,
) -> dict[str, Any]:
    syntax_or_structure_errors: list[str] = []
    inferred_issues: list[str] = []

    for err in parser_errors:
        lowered = err.lower()
        if any(token in lowered for token in ["parse", "mismatch", "missing", "unclosed", "nested"]):
            syntax_or_structure_errors.append(err)
        else:
            inferred_issues.append(err)

    for warn in parser_warnings:
        inferred_issues.append(warn)

    unresolved_references: list[str] = []
    base_dir = (
        Path(param_path_resolved).resolve().parent if param_path_resolved else resolve_run_dir(run_dir)
    )

    refs, includes, _ambiguous = extract_external_references_from_param_text(param_text)
    for token in refs + includes:
        if any(sym in token for sym in ["*", "?", "$"]):
            continue
        resolved = resolve_reference_path(token, base_dir)
        if not resolved.is_file():
            unresolved_references.append(str(resolved))

    return {
        "syntax_or_structure_errors": sorted(set(syntax_or_structure_errors)),
        "inferred_issues": sorted(set(inferred_issues)),
        "unresolved_references": sorted(set(unresolved_references)),
        "requires_authoritative_validation": True,
        "authoritative_next_tool": "swmf_run_testparam",
    }


def validate_param(
    param_text: str | None = None,
    nproc: int | None = None,
    run_dir: str | None = None,
    param_path: str | None = None,
) -> dict[str, Any]:
    loaded_text, resolved_param_path, load_error = load_param_text(
        param_text=param_text,
        param_path=param_path,
        run_dir=run_dir,
    )

    if load_error is not None:
        return {
            "ok": False,
            "message": load_error,
            "how_to_fix": [
                "Provide param_text directly.",
                "Or provide a valid param_path (absolute, or relative to run_dir when run_dir is set).",
            ],
        }

    assert loaded_text is not None
    parsed = parse_param_text(loaded_text)

    sessions = parsed.sessions
    errors = list(parsed.errors)
    warnings = list(parsed.warnings)

    first_map = _find_first_component_map(sessions)
    if not first_map:
        errors.append("No #COMPONENTMAP block was found.")
    else:
        mapped_components = _component_ids_from_map(first_map)
        if nproc is not None:
            map_errors, map_warnings = expand_component_map_rows(first_map, nproc)
            errors.extend(map_errors)
            warnings.extend(map_warnings)

        for session in sessions:
            for comp in session.component_blocks:
                if comp not in mapped_components:
                    warnings.append(
                        f"Session {session.index}: component block for {comp} exists, but {comp} is not present in the first #COMPONENTMAP block."
                    )
            for comp, use_comp in session.switched_components:
                if comp not in mapped_components:
                    warnings.append(
                        f"Session {session.index}: #COMPONENT toggles {comp} but {comp} is not present in the first #COMPONENTMAP block."
                    )
                if not use_comp:
                    warnings.append(f"Session {session.index}: {comp} is explicitly disabled in this session.")

    for session in sessions:
        if not session.stop_present:
            errors.append(f"Session {session.index} is missing #STOP.")

    if not [cmd for s in sessions for cmd in s.commands if cmd == "#TIMEACCURATE"]:
        warnings.append(
            "No #TIMEACCURATE command was found. That is not necessarily wrong, because time-accurate mode is the default."
        )

    classified = classify_lightweight_findings(
        param_text=loaded_text,
        parser_errors=errors,
        parser_warnings=warnings,
        param_path_resolved=resolved_param_path,
        run_dir=run_dir,
    )

    return {
        "ok": True,
        "authority": AUTHORITY_HEURISTIC,
        "source_kind": SOURCE_KIND_LIGHTWEIGHT_PARSER,
        "source_paths": [resolved_param_path] if resolved_param_path else [],
        "validation_mode": "lightweight_parser_only",
        "valid": len(errors) == 0,
        "nproc_checked": nproc,
        "param_source": "param_text" if param_text is not None else "param_path",
        "param_path_resolved": resolved_param_path,
        "session_count": len(sessions),
        "required_components_from_param": _infer_required_components_from_sessions(sessions),
        "next_step": "Run swmf_run_testparam for authoritative SWMF validation.",
        "errors": errors,
        "warnings": warnings,
        "syntax_or_structure_errors": classified["syntax_or_structure_errors"],
        "inferred_issues": classified["inferred_issues"],
        "unresolved_references": classified["unresolved_references"],
        "requires_authoritative_validation": classified["requires_authoritative_validation"],
        "authoritative_next_tool": classified["authoritative_next_tool"],
        "prototype_scope": (
            "This is a lightweight parser validator. For authoritative SWMF behavior and component-version diagnostics, use swmf_run_testparam."
        ),
    }


def validate_external_inputs(
    param_text: str | None = None,
    param_path: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    loaded_text, resolved_param_path, load_error = load_param_text(
        param_text=param_text,
        param_path=param_path,
        run_dir=run_dir,
    )
    if load_error is not None:
        return {
            "ok": False,
            "hard_error": True,
            "message": load_error,
            "missing_files": [],
            "existing_files": [],
            "ambiguous_references": [],
            "warnings": [],
            "suggested_next_tool": None,
        }

    assert loaded_text is not None
    base_dir = Path(resolved_param_path).resolve().parent if resolved_param_path else resolve_run_dir(run_dir)
    refs, include_refs, ambiguous = extract_external_references_from_param_text(loaded_text)

    existing_files: list[str] = []
    missing_files: list[str] = []
    warnings: list[str] = []

    checked: set[str] = set()
    for raw_ref in refs + include_refs:
        if raw_ref in checked:
            continue
        checked.add(raw_ref)
        if any(marker in raw_ref for marker in ["$", "*", "?"]):
            ambiguous.append(raw_ref)
            continue
        resolved = resolve_reference_path(raw_ref, base_dir)
        if resolved.is_file() and resolved.exists():
            existing_files.append(str(resolved))
        else:
            missing_files.append(str(resolved))

    for ref in refs:
        lowered = ref.lower()
        if lowered.endswith(".fits") or "gong" in lowered or "magnet" in lowered:
            warnings.append(
                f"Solar external input reference detected: {ref}. Confirm coordinate alignment and date/rotation consistency."
            )

    return {
        "ok": len(missing_files) == 0,
        "authority": AUTHORITY_HEURISTIC,
        "source_kind": SOURCE_KIND_LIGHTWEIGHT_PARSER,
        "source_paths": [resolved_param_path] if resolved_param_path else [],
        "missing_files": sorted(set(missing_files)),
        "existing_files": sorted(set(existing_files)),
        "ambiguous_references": sorted(set(ambiguous)),
        "warnings": sorted(set(warnings)),
        "param_source": "param_text" if param_text is not None else "param_path",
        "param_path_resolved": resolved_param_path,
        "suggested_next_tool": "swmf_validate_param",
    }


def _cache_key(swmf_root_resolved: str, param_path_resolved: str, requested_nproc: int | None) -> tuple[str, str, int | None]:
    return (str(Path(swmf_root_resolved).resolve()), str(Path(param_path_resolved).resolve()), requested_nproc)


def _is_cache_valid(payload: dict[str, Any]) -> bool:
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


def _cache_store(payload: dict[str, Any], requested_nproc: int | None) -> None:
    try:
        param_mtime = Path(payload["param_path_resolved"]).stat().st_mtime
        script_mtime = Path(payload["source_paths"][0]).stat().st_mtime
    except (KeyError, IndexError, OSError):
        return
    cached = copy.deepcopy(payload)
    cached["_cache_param_mtime"] = param_mtime
    cached["_cache_script_mtime"] = script_mtime
    _TESTPARAM_CACHE[_cache_key(payload["execution_cwd"], payload["param_path_resolved"], requested_nproc)] = cached


def _cache_get(swmf_root_resolved: str, param_path_resolved: str, requested_nproc: int | None) -> dict[str, Any] | None:
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
) -> dict[str, Any]:
    from .build_run import infer_job_layout

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
            "execution_constraint": "TestParam.pl must be executed from SWMF_ROOT directory.",
            "execution_hint": f"cd {execution_cwd} && ./Scripts/TestParam.pl -n=<nproc> {resolved_param_path}",
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
            "execution_constraint": "TestParam.pl must be executed from SWMF_ROOT directory.",
            "execution_hint": f"Ensure {testparam_script} exists. Then: cd {execution_cwd} && ./Scripts/TestParam.pl -n=<nproc> {resolved_param_path}",
            "authority": "authoritative",
            "source_kind": "TestParam.pl",
            "source_paths": [],
        }

    nproc_source = "explicit"
    inferred_layout: dict[str, Any] | None = None
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
                    "execution_constraint": "TestParam.pl must be executed from SWMF_ROOT directory.",
                    "authority": "authoritative",
                    "source_kind": "TestParam.pl",
                    "source_paths": [str(testparam_script)],
                }
        else:
            nproc = 1
            nproc_source = "fast_default"

    cached = _cache_get(swmf_root_resolved=execution_cwd, param_path_resolved=str(resolved_param_path), requested_nproc=requested_nproc)
    if cached is not None:
        return cached

    assert nproc is not None
    cmd = ["perl", str(testparam_script), f"-n={nproc}", str(resolved_param_path)]
    try:
        result = subprocess.run(cmd, cwd=execution_cwd, capture_output=True, text=True, check=False)
    except OSError as exc:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "TESTPARAM_EXECUTION_FAILED",
            "message": f"Failed to execute TestParam.pl: {exc}",
            "execution_context_ok": False,
            "execution_cwd": execution_cwd,
            "execution_constraint": "TestParam.pl must be executed from SWMF_ROOT directory.",
            "execution_hint": f"cd {execution_cwd} && ./Scripts/TestParam.pl -n={nproc} {resolved_param_path}",
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
        "execution_constraint": "TestParam.pl must be executed from SWMF_ROOT directory.",
        "execution_hint": f"cd {execution_cwd} && ./Scripts/TestParam.pl -n={nproc} {resolved_param_path}",
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
    from .build_run import infer_job_layout, prepare_component_config

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
) -> dict[str, Any]:
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
        from ..core.common import resolve_input_path

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


def swmf_explain_param(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        fallback = explain_param(name=name, catalog=None)
        fallback["swmf_root_resolved"] = None
        fallback["resolution_failure"] = failure
        return fallback

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    if catalog_error is not None or catalog is None:
        fallback = explain_param(name=name, catalog=None)
        fallback["swmf_root_resolved"] = None
        fallback["resolution_failure"] = catalog_error
        return fallback

    return with_root(explain_param(name=name, catalog=catalog), root)


def swmf_validate_param(
    param_text: str | None = None,
    nproc: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    param_path: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    return with_root(
        validate_param(
            param_text=param_text,
            nproc=nproc,
            run_dir=run_dir,
            param_path=param_path,
        ),
        root,
    )


def swmf_run_testparam(
    param_path: str,
    nproc: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    return with_root(
        run_testparam(
            param_path=param_path,
            swmf_root_resolved=root.swmf_root_resolved or str(Path.cwd()),
            nproc=nproc,
            run_dir=run_dir,
            job_script_path=job_script_path,
        ),
        root,
    )


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


def swmf_generate_param_from_template(
    template_kind: str,
    fits_path: str | None = None,
    run_dir: str | None = None,
    swmf_root: str | None = None,
    nproc: int | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    return with_root(
        generate_param_from_template(
            template_kind=template_kind,
            fits_path=fits_path,
            run_dir=run_dir,
            swmf_root_resolved=root.swmf_root_resolved or str(Path.cwd()),
            nproc=nproc,
        ),
        root,
    )


def swmf_generate_param_block(
    template_kind: str,
    fits_path: str | None = None,
    run_dir: str | None = None,
    swmf_root: str | None = None,
    nproc: int | None = None,
) -> dict[str, Any]:
    return swmf_generate_param_from_template(
        template_kind=template_kind,
        fits_path=fits_path,
        run_dir=run_dir,
        swmf_root=swmf_root,
        nproc=nproc,
    )


def swmf_diagnose_param(
    param_path: str | None = None,
    param_text: str | None = None,
    nproc: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    job_script_path: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    if param_path is None and param_text is None:
        return with_root(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "PARAM_INPUT_MISSING",
                "message": "Provide param_path or param_text.",
            },
            root,
        )

    payload = diagnose_param(
        swmf_root_resolved=root.swmf_root_resolved or str(Path.cwd()),
        param_path=param_path,
        param_text=param_text,
        run_dir=run_dir,
        nproc=nproc,
        job_script_path=job_script_path,
    )
    return with_root(payload, root)


def register(app: Any) -> None:
    app.tool(description="Explain a PARAM command using indexed SWMF PARAM.XML sources.")(swmf_explain_param)
    app.tool(description="Validate PARAM structure with lightweight deterministic checks.")(swmf_validate_param)
    app.tool(description="Run Scripts/TestParam.pl for authoritative SWMF PARAM validation. CONSTRAINT: Must execute from SWMF_ROOT directory. Command format: cd SWMF_ROOT && ./Scripts/TestParam.pl -n=<nproc> <PARAM.in>.")(swmf_run_testparam)
    app.tool(description="Validate external file inputs referenced by PARAM content.")(swmf_validate_external_inputs)
    app.tool(description="Generate suggested PARAM content from a template kind and context.")(swmf_generate_param_from_template)
    app.tool(description="Backward-compatible alias for generating PARAM content from templates.")(swmf_generate_param_block)
    app.tool(description="Diagnose PARAM issues in one call and return prioritized fixes.")(swmf_diagnose_param)
