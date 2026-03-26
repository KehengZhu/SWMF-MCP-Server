from __future__ import annotations

from pathlib import Path

from ..core.authority import AUTHORITY_HEURISTIC, SOURCE_KIND_LIGHTWEIGHT_PARSER
from ..parsing.component_map import expand_component_map_rows
from ..parsing.external_refs import extract_external_references_from_param_text
from ..parsing.param_parser import parse_param_text
from .common import load_param_text, resolve_reference_path, resolve_run_dir


def _find_first_component_map(sessions: list) -> list[dict]:
    for session in sessions:
        if session.component_map_rows:
            return session.component_map_rows
    return []


def _component_ids_from_map(rows: list[dict]) -> set[str]:
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
) -> dict:
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
) -> dict:
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
) -> dict:
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
