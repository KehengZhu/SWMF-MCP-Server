from __future__ import annotations

import difflib
import hashlib
import re
from pathlib import Path
from typing import Any

from ..catalog import get_source_catalog
from ..core.common import build_path_search_guidance, load_param_text, resolve_reference_path, resolve_run_dir
from ..core.debug_protocol import (
    FAMILY_BUILD_CONFIG,
    FAMILY_COUPLING_MPI_LAYOUT,
    FAMILY_INPUT_SCHEMA,
    FAMILY_POSTPROCESS_RESTART_OUTPUT,
    FAMILY_RUNTIME_CRASH_STOP,
    FAMILY_SOURCE_CHANGE_VALIDATION,
    InvariantBlock,
    STATE_EVIDENCE_COLLECTION,
    STATE_NORMALIZATION,
    STATE_PATCH_READINESS,
    STATE_VALIDATION,
    protocol_envelope,
)
from ..parsing.component_map import COMPONENTMAP_ROW, expand_component_map_rows
from ..parsing.external_refs import extract_external_references_from_param_text
from ..parsing.job_layout import find_likely_job_scripts
from ..parsing.param_parser import parse_param_text
from ._helpers import resolve_root_or_failure, with_root
from .build_run import infer_job_layout


_ERROR_PATTERNS = [
    re.compile(pattern, flags=re.IGNORECASE)
    for pattern in [
        r"\berror\b",
        r"\bfatal\b",
        r"segmentation fault",
        r"sigsegv",
        r"mpi_abort",
        r"traceback",
        r"exception",
        r"abort",
    ]
]

_STACK_PATTERNS = [
    re.compile(pattern, flags=re.IGNORECASE)
    for pattern in [
        r"traceback",
        r"backtrace",
        r"program received signal",
        r"^\s*#\d+",
        r"\bat\s+.*:\d+",
        r"call stack",
    ]
]


def _dedupe_keep_order(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _merge_protocol(payload: dict[str, Any], protocol: dict[str, Any]) -> dict[str, Any]:
    merged = dict(payload)
    merged.update(protocol)
    return merged


def _infer_required_components_from_sessions(sessions: list[Any]) -> list[str]:
    required: list[str] = []
    seen: set[str] = set()

    def add_component(comp: str) -> None:
        comp_id = comp.strip().upper()
        if len(comp_id) != 2:
            return
        if comp_id in seen:
            return
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


def _resolve_file(path_text: str, run_dir: str | None = None) -> Path:
    candidate = Path(path_text).expanduser()
    if not candidate.is_absolute():
        candidate = resolve_run_dir(run_dir) / candidate
    return candidate.resolve()


def _read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _extract_first_error_payload(text: str, context_lines: int = 2) -> dict[str, Any]:
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        if any(pattern.search(line) for pattern in _ERROR_PATTERNS):
            before_start = max(0, idx - context_lines)
            after_end = min(len(lines), idx + context_lines + 1)
            return {
                "found": True,
                "line_number": idx + 1,
                "line": line.strip(),
                "context_before": [item.rstrip() for item in lines[before_start:idx]],
                "context_after": [item.rstrip() for item in lines[idx + 1 : after_end]],
            }

    return {
        "found": False,
        "line_number": None,
        "line": None,
        "context_before": [],
        "context_after": [],
    }


def _extract_stacktrace_lines(text: str, max_lines: int = 40) -> list[str]:
    lines = text.splitlines()
    extracted: list[str] = []
    started = False

    for line in lines:
        matched = any(pattern.search(line) for pattern in _STACK_PATTERNS)
        if matched and not started:
            started = True

        if started:
            stripped = line.rstrip()
            if stripped:
                extracted.append(stripped)
            elif extracted:
                break

        if len(extracted) >= max_lines:
            break

    if extracted:
        return extracted

    for line in lines:
        if any(pattern.search(line) for pattern in _STACK_PATTERNS):
            extracted.append(line.rstrip())
            if len(extracted) >= max_lines:
                break

    return extracted


def _stable_file_hash(path: Path, max_bytes: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        digest.update(stream.read(max_bytes))
    return digest.hexdigest()


def swmf_collect_param_context(
    param_text: str | None = None,
    param_path: str | None = None,
    run_dir: str | None = None,
    nproc: int | None = None,
) -> dict[str, Any]:
    loaded_text, resolved_param_path, load_error = load_param_text(
        param_text=param_text,
        param_path=param_path,
        run_dir=run_dir,
    )

    if load_error is not None or loaded_text is None:
        return _merge_protocol(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "PARAM_LOAD_FAILED",
                "message": load_error or "Could not load PARAM input.",
                "how_to_fix": [
                    "Provide param_text directly.",
                    "Or pass param_path (absolute or relative to run_dir).",
                ],
            },
            protocol_envelope(
                state=STATE_EVIDENCE_COLLECTION,
                failure_family=FAMILY_INPUT_SCHEMA,
                observation_report=["PARAM input could not be loaded."],
                next_discriminating_checks=["Resolve param_path and rerun context collection."],
                patch_ready=False,
            ),
        )

    parsed = parse_param_text(loaded_text)
    refs, include_refs, ambiguous = extract_external_references_from_param_text(loaded_text)

    base_dir = Path(resolved_param_path).resolve().parent if resolved_param_path else resolve_run_dir(run_dir)
    include_files: list[dict[str, Any]] = []
    missing_include_files: list[str] = []

    for include_ref in include_refs:
        resolved = resolve_reference_path(include_ref, base_dir)
        exists = resolved.is_file()
        include_files.append(
            {
                "raw": include_ref,
                "resolved": str(resolved),
                "exists": exists,
            }
        )
        if not exists:
            missing_include_files.append(str(resolved))

    unresolved_external_refs: list[str] = []
    for token in refs:
        if any(symbol in token for symbol in ["$", "*", "?"]):
            continue
        resolved = resolve_reference_path(token, base_dir)
        if not resolved.is_file():
            unresolved_external_refs.append(str(resolved))

    all_component_map_rows: list[dict[str, Any]] = []
    for session in parsed.sessions:
        all_component_map_rows.extend(session.component_map_rows)

    component_map_validation: dict[str, Any] | None = None
    if nproc is not None and all_component_map_rows:
        errors, warnings = expand_component_map_rows(all_component_map_rows, nproc=nproc)
        component_map_validation = {
            "nproc_checked": nproc,
            "errors": errors,
            "warnings": warnings,
            "valid": len(errors) == 0,
        }

    observation_report = [
        f"Loaded PARAM input from {'param_text' if param_text is not None else resolved_param_path}.",
        f"Detected {len(parsed.sessions)} sessions and {len(all_component_map_rows)} component-map rows.",
        f"Detected {len(include_refs)} include references and {len(refs)} external file references.",
    ]

    next_checks = [
        "Resolve include and external reference paths before mechanism inference.",
        "Run authoritative validation with swmf_run_testparam after input context is complete.",
    ]

    return _merge_protocol(
        {
            "ok": True,
            "authority": "derived",
            "source_kind": "lightweight_parser",
            "source_paths": [resolved_param_path] if resolved_param_path else [],
            "run_dir_resolved": str(resolve_run_dir(run_dir)),
            "param_source": "param_text" if param_text is not None else "param_path",
            "param_path_resolved": resolved_param_path,
            "session_count": len(parsed.sessions),
            "commands_by_session": [session.commands for session in parsed.sessions],
            "required_components": _infer_required_components_from_sessions(parsed.sessions),
            "component_map_rows": all_component_map_rows,
            "component_map_validation": component_map_validation,
            "parser_errors": parsed.errors,
            "parser_warnings": parsed.warnings,
            "include_files": include_files,
            "missing_include_files": sorted(set(missing_include_files)),
            "external_references": sorted(set(refs)),
            "unresolved_external_references": sorted(set(unresolved_external_refs)),
            "ambiguous_references": sorted(set(ambiguous)),
            "recommended_next_tools": _dedupe_keep_order(
                [
                    "swmf_resolve_param_includes",
                    "swmf_extract_component_map",
                    "swmf_validate_external_inputs",
                    "swmf_run_testparam",
                ]
            ),
        },
        protocol_envelope(
            state=STATE_EVIDENCE_COLLECTION,
            failure_family=FAMILY_INPUT_SCHEMA,
            observation_report=observation_report,
            next_discriminating_checks=next_checks,
            patch_ready=False,
        ),
    )


def swmf_resolve_param_includes(
    param_text: str | None = None,
    param_path: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    loaded_text, resolved_param_path, load_error = load_param_text(
        param_text=param_text,
        param_path=param_path,
        run_dir=run_dir,
    )

    if load_error is not None or loaded_text is None:
        return _merge_protocol(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "PARAM_LOAD_FAILED",
                "message": load_error or "Could not load PARAM input.",
            },
            protocol_envelope(
                state=STATE_NORMALIZATION,
                failure_family=FAMILY_INPUT_SCHEMA,
                observation_report=["PARAM input could not be loaded for include resolution."],
                next_discriminating_checks=["Resolve PARAM source path and rerun include resolution."],
                patch_ready=False,
            ),
        )

    _, include_refs, _ = extract_external_references_from_param_text(loaded_text)

    base_dir = Path(resolved_param_path).resolve().parent if resolved_param_path else resolve_run_dir(run_dir)
    resolved_includes: list[dict[str, Any]] = []
    missing: list[str] = []

    for include_ref in include_refs:
        resolved = resolve_reference_path(include_ref, base_dir)
        exists = resolved.is_file()
        resolved_includes.append(
            {
                "raw": include_ref,
                "resolved": str(resolved),
                "exists": exists,
            }
        )
        if not exists:
            missing.append(str(resolved))

    payload: dict[str, Any] = {
        "ok": len(missing) == 0,
        "authority": "derived",
        "source_kind": "lightweight_parser",
        "source_paths": [resolved_param_path] if resolved_param_path else [],
        "include_count": len(include_refs),
        "resolved_includes": resolved_includes,
        "missing_include_paths": sorted(set(missing)),
        "recommended_next_tools": ["swmf_collect_param_context", "swmf_run_testparam"],
    }

    if missing:
        search_roots = [base_dir, base_dir.parent]
        expected = [Path(item).name for item in include_refs]
        guidance = build_path_search_guidance(
            path_role="PARAM include file",
            search_roots=search_roots,
            expected_entries=expected,
            keyword_hints=[base_dir.name, "include", "param"],
        )
        payload.update(guidance)

    return _merge_protocol(
        payload,
        protocol_envelope(
            state=STATE_NORMALIZATION,
            failure_family=FAMILY_INPUT_SCHEMA,
            observation_report=[f"Resolved {len(include_refs)} include references."],
            unresolved_conflicts=["Some include files are missing."] if missing else [],
            next_discriminating_checks=["Resolve missing include files before rerunning validation."] if missing else [],
            patch_ready=False,
        ),
    )


def swmf_extract_component_map(
    component_map_text: str | None = None,
    param_text: str | None = None,
    param_path: str | None = None,
    run_dir: str | None = None,
    nproc: int | None = None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    source_paths: list[str] = []

    if component_map_text is not None:
        for raw_line in component_map_text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            match = COMPONENTMAP_ROW.match(line)
            if match is None:
                parse_errors.append(f"Could not parse component-map row: {line}")
                continue
            rows.append(
                {
                    "component": match.group("id"),
                    "proc0": int(match.group("proc0")),
                    "procend": int(match.group("procend")),
                    "stride": int(match.group("stride")),
                    "nthread": int(match.group("nthread")) if match.group("nthread") is not None else None,
                    "raw": line,
                }
            )
    else:
        loaded_text, resolved_param_path, load_error = load_param_text(
            param_text=param_text,
            param_path=param_path,
            run_dir=run_dir,
        )
        if load_error is not None or loaded_text is None:
            return _merge_protocol(
                {
                    "ok": False,
                    "hard_error": True,
                    "error_code": "COMPONENTMAP_INPUT_MISSING",
                    "message": "Provide component_map_text or PARAM input.",
                    "how_to_fix": [
                        "Pass component_map_text directly.",
                        "Or pass param_text / param_path with a #COMPONENTMAP block.",
                    ],
                },
                protocol_envelope(
                    state=STATE_NORMALIZATION,
                    failure_family=FAMILY_COUPLING_MPI_LAYOUT,
                    observation_report=["Component-map extraction input is missing."],
                    patch_ready=False,
                ),
            )

        source_paths = [resolved_param_path] if resolved_param_path else []
        parsed = parse_param_text(loaded_text)
        for session in parsed.sessions:
            rows.extend(session.component_map_rows)

    if not rows:
        return _merge_protocol(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "COMPONENTMAP_NOT_FOUND",
                "message": "No parseable component-map rows were found.",
                "parse_errors": parse_errors,
            },
            protocol_envelope(
                state=STATE_NORMALIZATION,
                failure_family=FAMILY_COUPLING_MPI_LAYOUT,
                observation_report=["No parseable #COMPONENTMAP rows were found."],
                next_discriminating_checks=["Verify #COMPONENTMAP formatting and retry extraction."],
                patch_ready=False,
            ),
        )

    map_validation: dict[str, Any] | None = None
    if nproc is not None:
        map_errors, map_warnings = expand_component_map_rows(rows, nproc=nproc)
        map_validation = {
            "nproc_checked": nproc,
            "errors": map_errors,
            "warnings": map_warnings,
            "valid": len(map_errors) == 0,
        }

    components = sorted({row["component"] for row in rows})

    return _merge_protocol(
        {
            "ok": len(parse_errors) == 0,
            "authority": "derived",
            "source_kind": "lightweight_parser",
            "source_paths": source_paths,
            "rows": rows,
            "component_count": len(components),
            "components": components,
            "parse_errors": parse_errors,
            "validation": map_validation,
            "recommended_next_tools": ["swmf_collect_run_context", "swmf_collect_build_context"],
        },
        protocol_envelope(
            state=STATE_NORMALIZATION,
            failure_family=FAMILY_COUPLING_MPI_LAYOUT,
            observation_report=[f"Extracted {len(rows)} component-map rows for {len(components)} components."],
            unresolved_conflicts=parse_errors,
            next_discriminating_checks=["Validate nproc/layout consistency with job script."] if nproc is not None else [],
            patch_ready=False,
        ),
    )


def swmf_collect_build_context(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    job_script_path: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return _merge_protocol(
            failure or {
                "ok": False,
                "hard_error": True,
                "error_code": "SWMF_ROOT_RESOLUTION_FAILED",
                "message": "Could not resolve SWMF root.",
            },
            protocol_envelope(
                state=STATE_EVIDENCE_COLLECTION,
                failure_family=FAMILY_BUILD_CONFIG,
                observation_report=["SWMF root could not be resolved."],
                next_discriminating_checks=["Provide explicit swmf_root and rerun."],
                patch_ready=False,
            ),
        )

    root_path = Path(root.swmf_root_resolved or ".").resolve()
    markers = {
        "Config.pl": (root_path / "Config.pl").is_file(),
        "PARAM.XML": (root_path / "PARAM.XML").is_file(),
        "Scripts/TestParam.pl": (root_path / "Scripts" / "TestParam.pl").is_file(),
        "Makefile": (root_path / "Makefile").is_file(),
    }

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=force_refresh)
    catalog_summary: dict[str, Any] = {
        "available": False,
        "component_count": 0,
        "command_count": 0,
        "script_count": 0,
        "template_count": 0,
    }
    source_paths: list[str] = []

    if catalog is not None:
        catalog_summary = {
            "available": True,
            "component_count": len(catalog.components),
            "command_count": sum(len(values) for values in catalog.commands.values()),
            "script_count": len(catalog.scripts),
            "template_count": len(catalog.templates),
        }
        source_paths.extend(catalog.source_files[:40])

    job_layout: dict[str, Any] | None = None
    if job_script_path is not None or run_dir is not None:
        layout = infer_job_layout(job_script_path=job_script_path, run_dir=run_dir)
        if layout.get("ok"):
            job_layout = layout

    payload = {
        "ok": True,
        "authority": "derived",
        "source_kind": "diagnostic_pipeline",
        "source_paths": _dedupe_keep_order(source_paths),
        "run_dir_resolved": str(resolve_run_dir(run_dir)),
        "marker_status": markers,
        "catalog_summary": catalog_summary,
        "catalog_error": catalog_error,
        "job_layout": job_layout,
        "environment_hints": {
            "FC": None,
            "CC": None,
            "MPIFC": None,
            "MPICC": None,
        },
        "recommended_next_tools": [
            "swmf_collect_run_context",
            "swmf_extract_component_map",
            "swmf_run_testparam",
        ],
    }

    payload = with_root(payload, root)
    return _merge_protocol(
        payload,
        protocol_envelope(
            state=STATE_EVIDENCE_COLLECTION,
            failure_family=FAMILY_BUILD_CONFIG,
            observation_report=[
                "Collected SWMF root markers and catalog summary.",
                f"Catalog available: {catalog_summary['available']}.",
            ],
            next_discriminating_checks=["Confirm component/version selections and compile toolchain consistency."],
            patch_ready=False,
        ),
    )


def swmf_collect_run_context(
    run_dir: str,
    log_path: str | None = None,
    job_script_path: str | None = None,
    swmf_root: str | None = None,
) -> dict[str, Any]:
    resolved_run_dir = resolve_run_dir(run_dir)
    if not resolved_run_dir.is_dir():
        guidance = build_path_search_guidance(
            path_role="run_dir",
            search_roots=[resolved_run_dir, resolved_run_dir.parent],
            expected_entries=["PARAM.in", "runlog", "job.long"],
            keyword_hints=[resolved_run_dir.name, "run", "case", "output"],
        )
        return _merge_protocol(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "RUN_DIR_NOT_FOUND",
                "message": f"run_dir does not exist: {resolved_run_dir}",
                **guidance,
            },
            protocol_envelope(
                state=STATE_EVIDENCE_COLLECTION,
                failure_family=FAMILY_RUNTIME_CRASH_STOP,
                observation_report=["Run directory could not be resolved."],
                patch_ready=False,
            ),
        )

    root_failure, root = resolve_root_or_failure(swmf_root, str(resolved_run_dir))
    job_layout: dict[str, Any] | None = None

    if job_script_path is not None:
        layout = infer_job_layout(job_script_path=job_script_path, run_dir=str(resolved_run_dir))
        if layout.get("ok"):
            job_layout = layout
    else:
        job_candidates = find_likely_job_scripts(resolved_run_dir)
        if job_candidates:
            layout = infer_job_layout(job_script_path=str(job_candidates[0]), run_dir=str(resolved_run_dir))
            if layout.get("ok"):
                job_layout = layout

    log_candidate: Path | None = None
    if log_path is not None:
        candidate = _resolve_file(log_path, run_dir=str(resolved_run_dir))
        if candidate.is_file():
            log_candidate = candidate
    else:
        for pattern in ["runlog*", "*.log", "*.out"]:
            matches = sorted(resolved_run_dir.glob(pattern))
            if matches:
                log_candidate = matches[0]
                break

    first_error_payload = {
        "found": False,
        "line_number": None,
        "line": None,
        "context_before": [],
        "context_after": [],
    }
    source_paths: list[str] = []
    if log_candidate is not None:
        source_paths.append(str(log_candidate))
        first_error_payload = _extract_first_error_payload(_read_text_file(log_candidate))

    artifact_presence = {
        "PARAM.in": (resolved_run_dir / "PARAM.in").is_file(),
        "RESTART.in": (resolved_run_dir / "RESTART.in").is_file(),
        "RESTART.out": (resolved_run_dir / "RESTART.out").is_file(),
        "SWMF.SUCCESS": (resolved_run_dir / "SWMF.SUCCESS").is_file(),
        "SWMF.DONE": (resolved_run_dir / "SWMF.DONE").is_file(),
    }

    payload = {
        "ok": True,
        "authority": "derived",
        "source_kind": "diagnostic_pipeline",
        "source_paths": source_paths,
        "run_dir_resolved": str(resolved_run_dir),
        "swmf_root_resolution_failure": root_failure,
        "swmf_root_resolved": root.swmf_root_resolved if root is not None else None,
        "artifact_presence": artifact_presence,
        "job_layout": job_layout,
        "first_error": first_error_payload,
        "recommended_next_tools": [
            "swmf_extract_first_error",
            "swmf_extract_stacktrace",
            "swmf_compare_run_artifacts",
        ],
    }

    return _merge_protocol(
        payload,
        protocol_envelope(
            state=STATE_EVIDENCE_COLLECTION,
            failure_family=FAMILY_RUNTIME_CRASH_STOP,
            observation_report=[
                f"Collected run context under {resolved_run_dir}.",
                f"Detected log file: {str(log_candidate) if log_candidate else 'none'}.",
            ],
            next_discriminating_checks=["Compare first failing log evidence with job layout and PARAM context."],
            patch_ready=False,
        ),
    )


def swmf_extract_first_error(
    log_text: str | None = None,
    log_path: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    text = log_text
    source_paths: list[str] = []

    if text is None and log_path is not None:
        resolved_log_path = _resolve_file(log_path, run_dir=run_dir)
        if not resolved_log_path.is_file():
            guidance = build_path_search_guidance(
                path_role="log_path",
                search_roots=[resolve_run_dir(run_dir), resolve_run_dir(run_dir).parent],
                expected_entries=[resolved_log_path.name, "runlog", "*.log", "*.out"],
                keyword_hints=[resolved_log_path.stem, "run", "error", "log"],
            )
            return _merge_protocol(
                {
                    "ok": False,
                    "hard_error": True,
                    "error_code": "LOG_PATH_NOT_FOUND",
                    "message": f"log_path does not exist: {resolved_log_path}",
                    **guidance,
                },
                protocol_envelope(
                    state=STATE_NORMALIZATION,
                    failure_family=FAMILY_RUNTIME_CRASH_STOP,
                    observation_report=["Requested log file was not found."],
                    patch_ready=False,
                ),
            )
        text = _read_text_file(resolved_log_path)
        source_paths.append(str(resolved_log_path))

    if text is None:
        return _merge_protocol(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "LOG_INPUT_MISSING",
                "message": "Provide log_text or log_path.",
            },
            protocol_envelope(
                state=STATE_NORMALIZATION,
                failure_family=FAMILY_RUNTIME_CRASH_STOP,
                observation_report=["No log input was provided."],
                patch_ready=False,
            ),
        )

    evidence = _extract_first_error_payload(text)
    return _merge_protocol(
        {
            "ok": evidence["found"],
            "authority": "derived",
            "source_kind": "diagnostic_pipeline",
            "source_paths": source_paths,
            "first_error": evidence,
            "recommended_next_tools": ["swmf_extract_stacktrace", "swmf_collect_run_context"],
        },
        protocol_envelope(
            state=STATE_NORMALIZATION,
            failure_family=FAMILY_RUNTIME_CRASH_STOP,
            observation_report=["Extracted first error evidence from log."],
            next_discriminating_checks=["Confirm whether first error aligns with stacktrace and rank context."],
            patch_ready=False,
        ),
    )


def swmf_extract_stacktrace(
    log_text: str | None = None,
    log_path: str | None = None,
    run_dir: str | None = None,
    max_lines: int = 40,
) -> dict[str, Any]:
    text = log_text
    source_paths: list[str] = []

    if text is None and log_path is not None:
        resolved_log_path = _resolve_file(log_path, run_dir=run_dir)
        if not resolved_log_path.is_file():
            guidance = build_path_search_guidance(
                path_role="log_path",
                search_roots=[resolve_run_dir(run_dir), resolve_run_dir(run_dir).parent],
                expected_entries=[resolved_log_path.name, "runlog", "*.log", "*.out"],
                keyword_hints=[resolved_log_path.stem, "stack", "trace", "log"],
            )
            return _merge_protocol(
                {
                    "ok": False,
                    "hard_error": True,
                    "error_code": "LOG_PATH_NOT_FOUND",
                    "message": f"log_path does not exist: {resolved_log_path}",
                    **guidance,
                },
                protocol_envelope(
                    state=STATE_NORMALIZATION,
                    failure_family=FAMILY_RUNTIME_CRASH_STOP,
                    observation_report=["Requested log file was not found for stacktrace extraction."],
                    patch_ready=False,
                ),
            )
        text = _read_text_file(resolved_log_path)
        source_paths.append(str(resolved_log_path))

    if text is None:
        return _merge_protocol(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "LOG_INPUT_MISSING",
                "message": "Provide log_text or log_path.",
            },
            protocol_envelope(
                state=STATE_NORMALIZATION,
                failure_family=FAMILY_RUNTIME_CRASH_STOP,
                observation_report=["No log input was provided for stacktrace extraction."],
                patch_ready=False,
            ),
        )

    stacktrace_lines = _extract_stacktrace_lines(text, max_lines=max_lines)
    return _merge_protocol(
        {
            "ok": len(stacktrace_lines) > 0,
            "authority": "derived",
            "source_kind": "diagnostic_pipeline",
            "source_paths": source_paths,
            "stacktrace_lines": stacktrace_lines,
            "stacktrace_found": len(stacktrace_lines) > 0,
            "recommended_next_tools": ["swmf_extract_first_error", "swmf_collect_run_context"],
        },
        protocol_envelope(
            state=STATE_NORMALIZATION,
            failure_family=FAMILY_RUNTIME_CRASH_STOP,
            observation_report=[f"Extracted {len(stacktrace_lines)} stacktrace lines."],
            next_discriminating_checks=["Align stacktrace lines with first-error and rank-specific evidence."],
            patch_ready=False,
        ),
    )


def swmf_collect_source_context(
    source_path: str,
    symbol_hint: str | None = None,
    line_number: int | None = None,
    context_lines: int = 20,
    run_dir: str | None = None,
) -> dict[str, Any]:
    resolved_source_path = _resolve_file(source_path, run_dir=run_dir)
    if not resolved_source_path.is_file():
        guidance = build_path_search_guidance(
            path_role="source_path",
            search_roots=[resolve_run_dir(run_dir), resolve_run_dir(run_dir).parent],
            expected_entries=[resolved_source_path.name],
            keyword_hints=[resolved_source_path.stem, symbol_hint or "", "src", "mod"],
        )
        return _merge_protocol(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "SOURCE_FILE_NOT_FOUND",
                "message": f"source_path does not exist: {resolved_source_path}",
                **guidance,
            },
            protocol_envelope(
                state=STATE_EVIDENCE_COLLECTION,
                failure_family=FAMILY_SOURCE_CHANGE_VALIDATION,
                observation_report=["Source file could not be resolved."],
                patch_ready=False,
                invariants_required=True,
            ),
        )

    text = _read_text_file(resolved_source_path)
    lines = text.splitlines()
    center = 1

    if line_number is not None and 1 <= line_number <= len(lines):
        center = line_number
    elif symbol_hint:
        for idx, line in enumerate(lines, start=1):
            if symbol_hint in line:
                center = idx
                break

    start = max(1, center - context_lines)
    end = min(len(lines), center + context_lines)

    excerpt = [
        {
            "line_number": idx,
            "text": lines[idx - 1],
        }
        for idx in range(start, end + 1)
    ]

    return _merge_protocol(
        {
            "ok": True,
            "authority": "derived",
            "source_kind": "script",
            "source_paths": [str(resolved_source_path)],
            "symbol_hint": symbol_hint,
            "center_line": center,
            "excerpt": excerpt,
            "recommended_next_tools": [
                "swmf_collect_invariant_context",
                "swmf_extract_first_error",
            ],
        },
        protocol_envelope(
            state=STATE_EVIDENCE_COLLECTION,
            failure_family=FAMILY_SOURCE_CHANGE_VALIDATION,
            observation_report=[
                f"Collected source context around line {center} in {resolved_source_path.name}.",
            ],
            next_discriminating_checks=[
                "Define invariants for touched data structures before proposing edits.",
            ],
            patch_ready=False,
            invariants_required=True,
        ),
    )


def swmf_collect_invariant_context(
    data_structure: str,
    invariants_before_change: list[str] | None = None,
    operations_that_can_violate: list[str] | None = None,
    diagnostics_to_collect: list[str] | None = None,
    runtime_checks: list[str] | None = None,
) -> dict[str, Any]:
    invariants = invariants_before_change or []
    violating_ops = operations_that_can_violate or []
    diagnostics = diagnostics_to_collect or []
    checks = runtime_checks or []

    invariant_block = InvariantBlock(
        data_structure=data_structure,
        invariants_before_change=invariants,
        operations_that_can_violate=violating_ops,
        diagnostics_to_collect=diagnostics,
        runtime_checks=checks,
    )

    ready = bool(invariants and diagnostics and checks)
    reason = "invariant_block_complete" if ready else "invariant_block_incomplete"

    return _merge_protocol(
        {
            "ok": True,
            "authority": "derived",
            "source_kind": "diagnostic_pipeline",
            "source_paths": [],
            "invariant_block": invariant_block.as_payload(),
            "recommended_next_tools": ["swmf_collect_source_context", "swmf_collect_run_context"],
        },
        protocol_envelope(
            state=STATE_PATCH_READINESS,
            failure_family=FAMILY_SOURCE_CHANGE_VALIDATION,
            observation_report=[f"Captured invariant block for {data_structure}."],
            next_discriminating_checks=["Run targeted diagnostics to test candidate invariant violations."],
            patch_ready=ready,
            patch_readiness_reason=reason,
            invariants_required=True,
            invariant_block=invariant_block,
        ),
    )


def swmf_compare_run_artifacts(
    reference_path: str,
    candidate_path: str,
    run_dir: str | None = None,
    max_diff_lines: int = 120,
) -> dict[str, Any]:
    reference = _resolve_file(reference_path, run_dir=run_dir)
    candidate = _resolve_file(candidate_path, run_dir=run_dir)

    missing = []
    if not reference.exists():
        missing.append(str(reference))
    if not candidate.exists():
        missing.append(str(candidate))

    if missing:
        guidance = build_path_search_guidance(
            path_role="artifact path",
            search_roots=[resolve_run_dir(run_dir), resolve_run_dir(run_dir).parent],
            expected_entries=[Path(reference_path).name, Path(candidate_path).name],
            keyword_hints=[Path(reference_path).stem, Path(candidate_path).stem, "run", "output"],
        )
        return _merge_protocol(
            {
                "ok": False,
                "hard_error": True,
                "error_code": "ARTIFACT_PATH_NOT_FOUND",
                "message": "One or more artifact paths do not exist.",
                "missing_paths": missing,
                **guidance,
            },
            protocol_envelope(
                state=STATE_VALIDATION,
                failure_family=FAMILY_POSTPROCESS_RESTART_OUTPUT,
                observation_report=["Artifact comparison failed due to missing paths."],
                patch_ready=False,
            ),
        )

    if reference.is_dir() and candidate.is_dir():
        def scan_dir(path: Path, max_files: int = 500) -> set[str]:
            items: set[str] = set()
            for entry in path.rglob("*"):
                if len(items) >= max_files:
                    break
                if entry.is_file():
                    try:
                        rel = str(entry.resolve().relative_to(path.resolve()))
                    except ValueError:
                        continue
                    items.add(rel)
            return items

        left = scan_dir(reference)
        right = scan_dir(candidate)
        only_left = sorted(left - right)
        only_right = sorted(right - left)

        payload = {
            "ok": True,
            "authority": "derived",
            "source_kind": "diagnostic_pipeline",
            "source_paths": [str(reference), str(candidate)],
            "comparison_type": "directory",
            "reference_only": only_left,
            "candidate_only": only_right,
            "common_file_count": len(left & right),
            "changed": bool(only_left or only_right),
            "recommended_next_tools": ["swmf_collect_run_context"],
        }
    else:
        if reference.is_dir() != candidate.is_dir():
            return _merge_protocol(
                {
                    "ok": False,
                    "hard_error": True,
                    "error_code": "ARTIFACT_TYPE_MISMATCH",
                    "message": "reference_path and candidate_path must both be files or both be directories.",
                },
                protocol_envelope(
                    state=STATE_VALIDATION,
                    failure_family=FAMILY_POSTPROCESS_RESTART_OUTPUT,
                    observation_report=["Artifact type mismatch blocked comparison."],
                    patch_ready=False,
                ),
            )

        left_text = _read_text_file(reference)
        right_text = _read_text_file(candidate)
        diff_lines = list(
            difflib.unified_diff(
                left_text.splitlines(),
                right_text.splitlines(),
                fromfile=str(reference),
                tofile=str(candidate),
                lineterm="",
                n=2,
            )
        )

        payload = {
            "ok": True,
            "authority": "derived",
            "source_kind": "diagnostic_pipeline",
            "source_paths": [str(reference), str(candidate)],
            "comparison_type": "file",
            "changed": left_text != right_text,
            "reference_size": reference.stat().st_size,
            "candidate_size": candidate.stat().st_size,
            "reference_hash": _stable_file_hash(reference),
            "candidate_hash": _stable_file_hash(candidate),
            "diff_line_count": len(diff_lines),
            "diff_sample": diff_lines[:max_diff_lines],
            "recommended_next_tools": ["swmf_extract_first_error", "swmf_collect_run_context"],
        }

    return _merge_protocol(
        payload,
        protocol_envelope(
            state=STATE_VALIDATION,
            failure_family=FAMILY_POSTPROCESS_RESTART_OUTPUT,
            observation_report=[
                f"Compared artifacts: {reference} vs {candidate}.",
                f"Changed: {payload.get('changed', False)}.",
            ],
            next_discriminating_checks=["Correlate artifact deltas with runtime phase and input differences."],
            patch_ready=False,
        ),
    )


def register(app: Any) -> None:
    app.tool(description="Collect structured PARAM input context pack for SWMF debugging.")(swmf_collect_param_context)
    app.tool(description="Resolve and verify #INCLUDE file references from PARAM input.")(swmf_resolve_param_includes)
    app.tool(description="Extract and validate #COMPONENTMAP rows from text or PARAM input.")(swmf_extract_component_map)
    app.tool(description="Collect SWMF build/config evidence context from root, catalog, and optional job script.")(swmf_collect_build_context)
    app.tool(description="Collect run-directory runtime context including artifacts, inferred layout, and first-error hints.")(swmf_collect_run_context)
    app.tool(description="Extract first failing log line with local context window.")(swmf_extract_first_error)
    app.tool(description="Extract stacktrace/backtrace-style evidence from log input.")(swmf_extract_stacktrace)
    app.tool(description="Collect focused source file context around symbol or line for debugging evidence.")(swmf_collect_source_context)
    app.tool(description="Capture invariant checklist context before any source-level patching.")(swmf_collect_invariant_context)
    app.tool(description="Compare run artifacts (files/directories) to support validation and regression checks.")(swmf_compare_run_artifacts)
