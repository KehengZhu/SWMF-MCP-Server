"""Public API tool: inspect_artifact.

Purpose
-------
Inspect one specific local artifact deeply. Supports logs, PARAM.in files,
PARAM.XML specs, run directories, build outputs, and generated result files.
Returns findings, evidence excerpts, and provenance.

Internal backends (hidden from caller)
---------------------------------------
- log parser (error/stacktrace/component/timing extraction)
- param parser (command/section structure, includes, component map, external refs)
- XML parser (schema extraction, command listing)
- run directory scanner (file inventory, layout, artifact presence, log discovery)
- build output reader (root markers, compile/link errors)
- result file type detector

Output contract
---------------
{
  "summary": str,
  "findings": list[FindingItem],
  "evidence": list[EvidenceItem],
  "provenance": {"artifact_type": str, "path": str},
  "uncertainty": {"known_unknowns": list[str]}
}

FindingItem shape
-----------------
{
  "kind": "error" | "warning" | "info" | "layout" | "schema" | "config" | ...,
  "message": str,
  "location": str | None,
  "snippet": str | None
}

EvidenceItem shape
------------------
{
  "path": str,
  "snippet": str,
  "score": float | None
}

Field semantics
---------------
artifact_type : Required. One of:
                "log"         — runtime log file (SWMF or component)
                "param"       — PARAM.in input file
                "xml"         — PARAM.XML schema file
                "run_dir"     — entire run directory (inventory + layout)
                "build_output"— build/configure output (file or root directory)
                "result"      — generated output file (IDL save, netCDF, etc.)
path          : Required. Absolute or relative path to the artifact.
question      : Optional. Freeform question to focus inspection.
swmf_root     : Optional explicit SWMF source root path.
run_dir       : Optional run directory used for root resolution.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from ._helpers import resolve_root_or_failure, with_root
from ._router import raw_result_to_evidence_item, _check_index
from .debug_protocol import _extract_first_error_payload, _extract_stacktrace_lines
from ..core.common import read_text_file
from ..knowledge import service as ks
from ..parsing.param_parser import parse_param_text
from ..parsing.external_refs import extract_external_references_from_param_text
from ..parsing.component_map import expand_component_map_rows
from ..parsing.job_layout import find_likely_job_scripts, infer_job_layout_from_script
from ..parsing.xml_parser import parse_param_xml_file

_VALID_ARTIFACT_TYPES = frozenset({
    "log",
    "param",
    "xml",
    "run_dir",
    "build_output",
    "result",
})

_MAX_FILE_CHARS = 200_000  # guard against very large files

# Component name patterns in logs (2-letter codes like GM, IE, SC, etc.)
_COMPONENT_HEADER_RE = re.compile(
    r"\b([A-Z]{2})\s+(?:SWMF|init|start|WARNING|ERROR|stop|coupling)",
    re.IGNORECASE,
)
_COMPONENT_PREFIX_RE = re.compile(r"^([A-Z]{2})\s+", re.MULTILINE)
# Simulation time pattern
_SIM_TIME_RE = re.compile(r"(?:t\s*=\s*|Simulation\s+[Tt]ime[:\s]+)([\d.eE+\-]+)", re.IGNORECASE)
# MPI rank patterns
_RANK_RE = re.compile(r"(?:rank|proc|pe|cpu)\s*[#=:]\s*(\d+)", re.IGNORECASE)
# Warning patterns
_WARNING_RE = re.compile(r"\bWARNING\b", re.IGNORECASE)
# Success/completion
_SUCCESS_RE = re.compile(r"SWMF\s+(?:FINISHED|SUCCESS|DONE)\b", re.IGNORECASE)

# Binary file extensions (cannot be read as text)
_BINARY_EXTENSIONS = frozenset({".sav", ".nc", ".cdf", ".fits", ".fit", ".hdf", ".hdf5", ".bin"})
# SWMF text output extensions
_SWMF_OUTPUT_EXTENSIONS = frozenset({".out", ".dat", ".log"})

# Build error patterns
_COMPILE_ERROR_RE = re.compile(
    r"(?:error:|fatal error:|compilation failed|Error in compilation|mpif90.*error|ifort.*error)",
    re.IGNORECASE,
)
_LINKER_ERROR_RE = re.compile(
    r"(?:undefined reference|undefined symbol|cannot find -l|ld: |linker error)",
    re.IGNORECASE,
)
_BUILD_WARNING_RE = re.compile(r"\bwarning:", re.IGNORECASE)

# SWMF root markers
_SWMF_ROOT_MARKERS = [
    "Config.pl",
    "PARAM.XML",
    "Scripts/TestParam.pl",
    "Makefile",
    "src/",
]


def _read_file_safe(path_str: str) -> tuple[str | None, str | None]:
    """Read a text file, returning (text, error_msg)."""
    p = Path(path_str)
    if not p.exists():
        return None, f"File not found: {path_str}"
    if p.is_dir():
        return None, f"Path is a directory, not a file: {path_str}"
    try:
        text = p.read_text(encoding="utf-8", errors="replace")
        return text[:_MAX_FILE_CHARS], None
    except OSError as e:
        return None, f"Cannot read file: {e}"


# ---------------------------------------------------------------------------
# log inspector
# ---------------------------------------------------------------------------

def _inspect_log(path_str: str, question: str) -> tuple[str, list[dict[str, Any]]]:
    text, err = _read_file_safe(path_str)
    if err or text is None:
        return err or "Could not read log.", []

    first_error = _extract_first_error_payload(text)
    stacktrace = _extract_stacktrace_lines(text, max_lines=20)
    lines = text.splitlines()
    total_lines = len(lines)

    findings: list[dict[str, Any]] = []

    # --- first error ---
    if first_error.get("found"):
        findings.append({
            "kind": "first_error",
            "location": f"line {first_error['line_number']}",
            "description": first_error.get("line", ""),
            "context_before": first_error.get("context_before", []),
            "context_after": first_error.get("context_after", []),
        })

    # --- stacktrace ---
    if stacktrace:
        findings.append({
            "kind": "stacktrace",
            "location": "log",
            "description": "Stacktrace / signal info found",
            "lines": stacktrace[:20],
        })

    # --- component detection ---
    component_hits: dict[str, int] = {}
    for line in lines[:500]:  # scan first 500 lines for component headers
        m = _COMPONENT_PREFIX_RE.match(line)
        if m:
            comp = m.group(1).upper()
            # Only count 2-letter codes that look like SWMF components
            if len(comp) == 2 and comp.isalpha():
                component_hits[comp] = component_hits.get(comp, 0) + 1
    # Also scan the entire log for component name patterns
    for m in _COMPONENT_HEADER_RE.finditer(text[:50_000]):
        comp = m.group(1).upper()
        if len(comp) == 2 and comp.isalpha():
            component_hits[comp] = component_hits.get(comp, 0) + 1

    if component_hits:
        active_components = sorted(component_hits, key=lambda c: -component_hits[c])[:8]
        findings.append({
            "kind": "active_components",
            "location": "log",
            "description": f"Components detected in log: {', '.join(active_components)}",
            "components": active_components,
        })

    # --- simulation time at last occurrence ---
    sim_times: list[str] = []
    for line in lines:
        m = _SIM_TIME_RE.search(line)
        if m:
            sim_times.append(m.group(1))
    if sim_times:
        findings.append({
            "kind": "simulation_time",
            "location": "log",
            "description": f"Last simulation time seen: {sim_times[-1]} (first: {sim_times[0]})",
            "first_time": sim_times[0],
            "last_time": sim_times[-1],
            "sample_count": len(sim_times),
        })

    # --- MPI rank info (first few occurrences) ---
    rank_samples: list[str] = []
    for line in lines:
        if _RANK_RE.search(line):
            rank_samples.append(line.strip()[:120])
        if len(rank_samples) >= 3:
            break
    if rank_samples:
        findings.append({
            "kind": "mpi_rank_info",
            "location": "log",
            "description": "MPI rank references detected",
            "samples": rank_samples,
        })

    # --- warning count ---
    warning_count = sum(1 for line in lines if _WARNING_RE.search(line))
    if warning_count:
        findings.append({
            "kind": "warning_count",
            "location": "log",
            "description": f"{warning_count} line(s) containing 'WARNING'.",
            "count": warning_count,
        })

    # --- success / completion ---
    for line in reversed(lines[-100:]):  # check last 100 lines
        m = _SUCCESS_RE.search(line)
        if m:
            findings.append({
                "kind": "run_completed",
                "location": "log",
                "description": f"Completion indicator found: {line.strip()[:120]}",
            })
            break

    if not any(f["kind"] in ("first_error", "stacktrace", "run_completed") for f in findings):
        findings.append({
            "kind": "no_error",
            "location": "log",
            "description": "No error patterns detected in the log.",
        })

    error_line = f"First error at line {first_error['line_number']}." if first_error.get("found") else "No errors found."
    comp_str = f" Components: {', '.join(active_components)}." if component_hits else ""
    summary = f"Log file: {total_lines} lines. {error_line}{comp_str}" + (
        " Stacktrace detected." if stacktrace else ""
    )
    return summary, findings


# ---------------------------------------------------------------------------
# param inspector
# ---------------------------------------------------------------------------

def _inspect_param(
    path_str: str,
    question: str,
    swmf_root: str,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    text, err = _read_file_safe(path_str)
    if err or text is None:
        return err or "Could not read PARAM.in.", [], []

    parsed = parse_param_text(text)
    refs, include_refs, ambiguous = extract_external_references_from_param_text(text)

    base_dir = Path(path_str).resolve().parent

    # Resolve include files
    include_files: list[dict[str, Any]] = []
    missing_includes: list[str] = []
    for include_ref in include_refs:
        resolved = base_dir / include_ref
        exists = resolved.is_file()
        include_files.append({"raw": include_ref, "resolved": str(resolved), "exists": exists})
        if not exists:
            missing_includes.append(str(resolved))

    # Resolve external references
    unresolved_external: list[str] = []
    for token in refs:
        if any(symbol in token for symbol in ["$", "*", "?"]):
            continue
        resolved = base_dir / token
        if not resolved.is_file():
            unresolved_external.append(token)

    # Component map rows
    all_component_map_rows: list[dict[str, Any]] = []
    for session in parsed.sessions:
        all_component_map_rows.extend(session.component_map_rows)

    # Required components
    required_components: list[str] = []
    seen_comps: set[str] = set()
    for session in parsed.sessions:
        for row in session.component_map_rows:
            comp = str(row.get("component", "")).strip().upper()
            if len(comp) == 2 and comp not in seen_comps:
                seen_comps.add(comp)
                required_components.append(comp)
        for comp in session.component_blocks:
            comp_id = comp.strip().upper()
            if len(comp_id) == 2 and comp_id not in seen_comps:
                seen_comps.add(comp_id)
                required_components.append(comp_id)

    n_sessions = len(parsed.sessions)

    # Build findings
    findings: list[dict[str, Any]] = []

    q_lower = question.lower()
    focus_includes = any(tok in q_lower for tok in ("include", "resolve include"))
    focus_compmap = any(tok in q_lower for tok in ("component map", "componentmap", "#componentmap"))
    focus_validate = any(tok in q_lower for tok in ("validate", "validation", "testparam"))
    focus_external = any(tok in q_lower for tok in ("external", "external ref", "file ref"))

    # Always add structure finding
    findings.append({
        "kind": "param_structure",
        "location": path_str,
        "description": (
            f"{n_sessions} session(s), "
            f"{len(all_component_map_rows)} component-map row(s), "
            f"{len(include_refs)} include(s), "
            f"{len(refs)} external file reference(s)."
        ),
        "session_count": n_sessions,
        "required_components": required_components,
        "parser_errors": parsed.errors,
        "parser_warnings": parsed.warnings,
    })

    # Session commands (limited)
    if n_sessions > 0:
        commands_by_session = [session.commands for session in parsed.sessions[:5]]
        findings.append({
            "kind": "session_commands",
            "location": path_str,
            "description": f"Commands per session (first {min(n_sessions, 5)}).",
            "commands_by_session": commands_by_session,
        })

    # Include files
    if include_refs or focus_includes:
        findings.append({
            "kind": "include_files",
            "location": path_str,
            "description": (
                f"{len(include_refs)} include reference(s). "
                f"{len(missing_includes)} missing."
            ),
            "include_files": include_files,
            "missing_includes": missing_includes,
        })

    # Component map
    if all_component_map_rows or focus_compmap:
        findings.append({
            "kind": "component_map",
            "location": path_str,
            "description": (
                f"{len(all_component_map_rows)} component-map row(s) for "
                f"{len(required_components)} component(s): {', '.join(required_components) or 'none'}."
            ),
            "rows": all_component_map_rows,
            "components": required_components,
        })

    # External refs
    if refs or focus_external:
        findings.append({
            "kind": "external_references",
            "location": path_str,
            "description": (
                f"{len(refs)} external file reference(s). "
                f"{len(unresolved_external)} unresolved."
            ),
            "all_refs": sorted(set(refs))[:30],
            "unresolved": sorted(set(unresolved_external))[:20],
            "ambiguous": sorted(set(ambiguous))[:10],
        })

    # Validation note
    if focus_validate or parsed.errors:
        validation_note = (
            "Lightweight parser only. "
            "Authoritative validation still requires Scripts/TestParam.pl from the SWMF root."
        )
        if parsed.errors:
            validation_note = f"Parser detected {len(parsed.errors)} error(s). " + validation_note
        findings.append({
            "kind": "validation_note",
            "location": path_str,
            "description": validation_note,
            "parser_errors": parsed.errors[:10],
        })

    # Evidence from question
    evidence: list[dict[str, Any]] = []
    if question and not focus_includes and not focus_compmap and not focus_validate:
        raw = ks.search_source(
            swmf_root,
            query=question,
            max_results=5,
            search_mode="keyword",
            ensure_ready=False,
        )
        evidence = [raw_result_to_evidence_item(r) for r in raw.get("results", [])]

    summary = (
        f"PARAM.in at '{path_str}': {n_sessions} session(s), "
        f"{len(required_components)} component(s) ({', '.join(required_components) or 'none'}), "
        f"{len(missing_includes)} missing include(s)."
    )
    return summary, findings, evidence


# ---------------------------------------------------------------------------
# xml inspector
# ---------------------------------------------------------------------------

def _inspect_xml(path_str: str, question: str) -> tuple[str, list[dict[str, Any]]]:
    p = Path(path_str)

    # Use the actual XML parser to extract commands
    component: str | None = None
    # Infer component from path (e.g. GM/BATSRUS/PARAM.XML → "GM")
    parts = p.parts
    for i, part in enumerate(parts):
        if part.upper() in {"GM", "IE", "SC", "IH", "OH", "UA", "RB", "SP", "IM", "PW"}:
            component = part.upper()
            break

    commands = parse_param_xml_file(p, component)

    if not commands:
        # Fallback to raw text inspection
        text, err = _read_file_safe(path_str)
        if err or text is None:
            return err or "Could not read XML.", []
        total_lines = len(text.splitlines())
        import re as _re
        command_count = len(_re.findall(r"<command\b", text, _re.IGNORECASE))
        return (
            f"PARAM.XML at '{path_str}': {total_lines} lines, ~{command_count} command definition(s) (parser found none).",
            [{
                "kind": "xml_structure",
                "location": path_str,
                "description": f"PARAM.XML: {total_lines} lines, ~{command_count} command definition(s).",
            }],
        )

    total_commands = len(commands)
    command_names = [cmd.normalized for cmd in commands[:80]]

    findings: list[dict[str, Any]] = [
        {
            "kind": "xml_structure",
            "location": path_str,
            "description": (
                f"PARAM.XML: {total_commands} command definition(s) parsed."
                + (f" Component: {component}." if component else "")
            ),
            "command_names": command_names,
            "component": component,
        }
    ]

    # If question, search for matching commands
    if question:
        q_norm = question.upper().strip()
        if not q_norm.startswith("#"):
            q_norm = "#" + q_norm
        q_lower = question.lower()

        matched_cmds = [
            cmd for cmd in commands
            if q_lower in (cmd.name or "").lower()
            or q_lower in (cmd.normalized or "").lower()
        ]
        if not matched_cmds:
            # fuzzy: any command whose name contains any word from the question
            words = [w for w in q_lower.split() if len(w) > 2]
            matched_cmds = [
                cmd for cmd in commands
                if any(w in (cmd.name or "").lower() for w in words)
            ]

        if matched_cmds:
            findings.append({
                "kind": "command_matches",
                "location": path_str,
                "description": f"{len(matched_cmds)} command(s) matching '{question}'.",
                "matches": [
                    {
                        "name": cmd.normalized,
                        "component": cmd.component,
                        "description": cmd.description,
                        "defaults": cmd.defaults,
                        "allowed_values": cmd.allowed_values,
                        "ranges": cmd.ranges,
                    }
                    for cmd in matched_cmds[:10]
                ],
            })
        else:
            findings.append({
                "kind": "no_command_match",
                "location": path_str,
                "description": f"No command matching '{question}' found in PARAM.XML.",
            })

    summary = (
        f"PARAM.XML at '{path_str}': {total_commands} command(s) parsed"
        + (f" for component {component}" if component else "")
        + "."
    )
    return summary, findings


# ---------------------------------------------------------------------------
# run_dir inspector
# ---------------------------------------------------------------------------

def _inspect_run_dir(
    path_str: str,
    question: str,
    swmf_root: str,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    p = Path(path_str)
    if not p.is_dir():
        return f"Not a directory: {path_str}", [], []

    findings: list[dict[str, Any]] = []

    # --- Directory inventory ---
    files_found: list[str] = []
    for item in sorted(p.iterdir()):
        files_found.append(item.name + ("/" if item.is_dir() else ""))
    files_found = files_found[:60]

    findings.append({
        "kind": "directory_inventory",
        "location": path_str,
        "description": f"{len(files_found)} top-level items in run directory.",
        "items": files_found,
    })

    # --- Artifact presence (SWMF status files) ---
    artifact_keys = [
        "PARAM.in", "RESTART.in", "RESTART.out",
        "SWMF.SUCCESS", "SWMF.DONE", "SWMF.KILLED",
    ]
    artifact_presence: dict[str, bool] = {
        name: (p / name).exists() for name in artifact_keys
    }
    # Infer run status
    if artifact_presence.get("SWMF.SUCCESS") or artifact_presence.get("SWMF.DONE"):
        run_status = "completed"
    elif artifact_presence.get("SWMF.KILLED"):
        run_status = "killed"
    elif artifact_presence.get("PARAM.in"):
        run_status = "prepared_or_running"
    else:
        run_status = "unknown"

    findings.append({
        "kind": "artifact_presence",
        "location": path_str,
        "description": f"Run status: {run_status}. Key artifacts detected.",
        "artifact_presence": artifact_presence,
        "run_status": run_status,
    })

    # --- Log file discovery and first-error preview ---
    log_candidates: list[Path] = []
    for pattern in ["runlog*", "*.log", "*.out"]:
        log_candidates.extend(sorted(p.glob(pattern)))
    log_candidates = log_candidates[:5]

    if log_candidates:
        primary_log = log_candidates[0]
        try:
            log_text = primary_log.read_text(encoding="utf-8", errors="replace")[:_MAX_FILE_CHARS]
            first_error = _extract_first_error_payload(log_text)
            log_lines = len(log_text.splitlines())
        except OSError:
            first_error = {"found": False}
            log_lines = 0

        log_finding: dict[str, Any] = {
            "kind": "log_discovery",
            "location": str(primary_log),
            "description": (
                f"Primary log: {primary_log.name} ({log_lines} lines). "
                + (f"First error at line {first_error['line_number']}." if first_error.get("found") else "No errors detected.")
            ),
            "log_files": [str(lf) for lf in log_candidates],
            "primary_log": str(primary_log),
        }
        if first_error.get("found"):
            log_finding["first_error"] = first_error
        findings.append(log_finding)

    # --- Job script detection ---
    job_scripts = find_likely_job_scripts(p)
    if job_scripts:
        primary_js = job_scripts[0]
        try:
            js_text = primary_js.read_text(encoding="utf-8", errors="replace")
            layout = infer_job_layout_from_script(primary_js, js_text)
        except OSError:
            layout = {}

        js_finding: dict[str, Any] = {
            "kind": "job_scripts",
            "location": str(primary_js),
            "description": (
                f"{len(job_scripts)} job script(s) found. "
                + (f"Scheduler: {layout.get('scheduler', 'unknown')}. " if layout else "")
                + (f"SWMF nproc: {layout.get('swmf_nproc', 'unknown')}." if layout else "")
            ),
            "job_scripts": [str(js) for js in job_scripts[:5]],
        }
        if layout:
            js_finding["job_layout"] = {
                k: v for k, v in layout.items()
                if k in ("scheduler", "nodes", "tasks_per_node", "swmf_nproc", "swmf_executable", "machine_hint")
            }
        findings.append(js_finding)

    # --- Output subdirectory detection ---
    output_dirs: list[str] = []
    for subdir in p.iterdir():
        if subdir.is_dir() and any(
            subdir.name.upper().startswith(comp)
            for comp in ("GM", "IE", "SC", "IH", "OH", "UA")
        ):
            output_dirs.append(subdir.name + "/")
    if output_dirs:
        findings.append({
            "kind": "output_subdirs",
            "location": path_str,
            "description": f"Component output subdirectories found: {', '.join(output_dirs[:8])}",
            "subdirs": output_dirs[:8],
        })

    # --- Evidence from question ---
    evidence: list[dict[str, Any]] = []
    if question:
        raw = ks.search_source(
            swmf_root,
            query=question,
            max_results=4,
            search_mode="keyword",
            ensure_ready=False,
        )
        evidence = [raw_result_to_evidence_item(r) for r in raw.get("results", [])]

    summary = (
        f"Run directory '{path_str}': {len(files_found)} items. "
        f"Status: {run_status}. "
        f"Logs: {len(log_candidates)}. "
        f"Job scripts: {len(job_scripts)}."
    )
    return summary, findings, evidence


# ---------------------------------------------------------------------------
# build_output inspector
# ---------------------------------------------------------------------------

def _inspect_build_output(path_str: str, question: str) -> tuple[str, list[dict[str, Any]]]:
    p = Path(path_str)

    # If path is a directory, treat as SWMF root directory → check root markers
    if p.is_dir():
        findings: list[dict[str, Any]] = []
        marker_status: dict[str, bool] = {
            marker: (p / marker).exists() for marker in _SWMF_ROOT_MARKERS
        }
        present = [m for m, ok in marker_status.items() if ok]
        missing = [m for m, ok in marker_status.items() if not ok]
        is_swmf_root = len(present) >= 2

        findings.append({
            "kind": "swmf_root_markers",
            "location": path_str,
            "description": (
                f"{'Appears to be a SWMF root' if is_swmf_root else 'May not be a SWMF root'}. "
                f"{len(present)} of {len(_SWMF_ROOT_MARKERS)} markers present."
            ),
            "present": present,
            "missing": missing,
            "is_swmf_root": is_swmf_root,
        })

        # Look for build log files inside
        build_logs: list[str] = []
        for pattern in ["*.log", "build*.txt", "configure*.txt", "make*.log"]:
            build_logs.extend(str(f) for f in p.glob(pattern))
        if build_logs:
            findings.append({
                "kind": "build_log_candidates",
                "location": path_str,
                "description": f"{len(build_logs)} candidate build log file(s) in root.",
                "files": build_logs[:10],
            })
        else:
            findings.append({
                "kind": "no_build_log",
                "location": path_str,
                "description": "No build log files found directly in this directory.",
            })

        summary = (
            f"Build output (directory): '{path_str}'. "
            f"SWMF root: {is_swmf_root}. "
            f"Markers present: {', '.join(present) or 'none'}."
        )
        return summary, findings

    # Regular file: scan for build errors
    text, err = _read_file_safe(path_str)
    if err or text is None:
        return err or "Could not read build output.", []

    lines_list = text.splitlines()
    total_lines = len(lines_list)
    findings = []

    # First error (general patterns)
    first_error = _extract_first_error_payload(text)
    if first_error.get("found"):
        findings.append({
            "kind": "first_error",
            "location": f"line {first_error['line_number']}",
            "description": first_error.get("line", ""),
            "context_before": first_error.get("context_before", []),
            "context_after": first_error.get("context_after", []),
        })

    # Compile errors (Fortran-specific)
    compile_errors: list[str] = []
    linker_errors: list[str] = []
    for i, line in enumerate(lines_list):
        if _COMPILE_ERROR_RE.search(line) and len(compile_errors) < 5:
            compile_errors.append(f"line {i+1}: {line.strip()[:120]}")
        if _LINKER_ERROR_RE.search(line) and len(linker_errors) < 5:
            linker_errors.append(f"line {i+1}: {line.strip()[:120]}")

    if compile_errors:
        findings.append({
            "kind": "compile_errors",
            "location": path_str,
            "description": f"{len(compile_errors)} compile error line(s) found.",
            "samples": compile_errors,
        })
    if linker_errors:
        findings.append({
            "kind": "linker_errors",
            "location": path_str,
            "description": f"{len(linker_errors)} linker error line(s) found.",
            "samples": linker_errors,
        })

    # Warning count
    warning_count = sum(1 for line in lines_list if _BUILD_WARNING_RE.search(line))
    if warning_count:
        findings.append({
            "kind": "warning_count",
            "location": "build_output",
            "description": f"{warning_count} warning line(s) found.",
            "count": warning_count,
        })

    if not findings:
        findings.append({
            "kind": "no_error",
            "location": "build_output",
            "description": "No error or warning patterns detected.",
        })

    error_desc = (
        f"First error at line {first_error['line_number']}."
        if first_error.get("found")
        else "No errors found."
    )
    summary = f"Build output: {total_lines} lines. {error_desc}"
    if compile_errors or linker_errors:
        summary += f" ({len(compile_errors)} compile, {len(linker_errors)} linker error(s))."
    return summary, findings


# ---------------------------------------------------------------------------
# result inspector
# ---------------------------------------------------------------------------

def _inspect_result(path_str: str, question: str) -> tuple[str, list[dict[str, Any]]]:
    p = Path(path_str)

    if p.is_dir():
        return (
            f"'{path_str}' is a directory; use artifact_type='run_dir' instead.",
            [{
                "kind": "wrong_type",
                "location": path_str,
                "description": "Path is a directory. Use artifact_type='run_dir'.",
            }],
        )

    suffix = p.suffix.lower()
    findings: list[dict[str, Any]] = []

    # --- Binary file types ---
    if suffix in _BINARY_EXTENSIONS:
        try:
            size_bytes = p.stat().st_size
        except OSError:
            size_bytes = -1

        type_descriptions: dict[str, str] = {
            ".sav": "IDL save file (binary). Use IDL restore command or PostProc.pl to read.",
            ".nc": "NetCDF file (binary). Use ncdump, Python netCDF4, or IDL to inspect.",
            ".cdf": "CDF/netCDF file (binary). Use ncdump or IDL to inspect.",
            ".fits": "FITS file (binary). Use FITS viewer, Python astropy, or IDL to inspect.",
            ".fit": "FITS file (binary). Use FITS viewer, Python astropy, or IDL to inspect.",
            ".hdf": "HDF file (binary). Use h5dump or Python h5py to inspect.",
            ".hdf5": "HDF5 file (binary). Use h5dump or Python h5py to inspect.",
            ".bin": "Binary data file. Format depends on producing code.",
        }
        type_desc = type_descriptions.get(suffix, f"Binary file ({suffix}). Cannot display as text.")

        findings.append({
            "kind": "binary_file",
            "location": path_str,
            "description": type_desc,
            "file_size_bytes": size_bytes,
            "extension": suffix,
        })
        summary = f"Binary result file '{p.name}' ({size_bytes:,} bytes). {type_desc}"
        return summary, findings

    # --- SWMF text output formats ---
    text, err = _read_file_safe(path_str)
    if err or text is None:
        return err or "Could not read result.", []

    lines = text.splitlines()
    total_lines = len(lines)

    if suffix in _SWMF_OUTPUT_EXTENSIONS or not suffix:
        # Try to detect SWMF-formatted output (header + variable line + data)
        # SWMF .out files typically have a structured header
        is_swmf_output = False
        variable_names: list[str] = []
        header_lines: list[str] = []

        for i, line in enumerate(lines[:20]):
            stripped = line.strip()
            if stripped.startswith("#"):
                header_lines.append(stripped)
            # Variable name line: space-separated identifiers (2nd or 3rd line often)
            elif i in (1, 2) and all(tok.replace("_", "").replace("-", "").isalnum() for tok in stripped.split() if tok):
                variable_names = stripped.split()[:20]
                is_swmf_output = bool(variable_names)

        if is_swmf_output or header_lines:
            findings.append({
                "kind": "swmf_output_format",
                "location": path_str,
                "description": (
                    f"SWMF-formatted output detected. "
                    f"{len(header_lines)} header directive(s). "
                    f"Variables: {', '.join(variable_names[:10]) or 'unknown'}."
                ),
                "header_lines": header_lines[:10],
                "variable_names": variable_names,
            })

    # Content preview (first 20 lines)
    preview = "\n".join(lines[:20])
    findings.append({
        "kind": "content_preview",
        "location": path_str,
        "description": f"First 20 lines of result file ({total_lines} total).",
        "preview": preview,
    })

    summary = f"Result file '{p.name}': {total_lines} lines ({suffix or 'no extension'})."
    return summary, findings


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------

def inspect_artifact(
    artifact_type: str,
    path: str,
    question: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Inspect one specific local SWMF artifact deeply.

    Use for logs, PARAM.in files, PARAM.XML specs, run directories, build
    outputs, or generated result files. Returns structured findings and
    evidence excerpts. Start debugging tasks here before calling get_evidence.

    Phase 4 specialized inspectors:
    - log: error/stacktrace + component detection + simulation time + MPI rank info
    - param: full structure (sessions, component map, includes, external refs) + question dispatch
    - xml: command listing from PARAM.XML parser + command search
    - run_dir: artifact presence + log discovery + job scripts + output subdirs
    - build_output: SWMF root markers (dir) or compile/linker errors (file)
    - result: file type detection (binary vs SWMF text output) + structured header parsing
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    resolved_type = artifact_type if artifact_type in _VALID_ARTIFACT_TYPES else "log"
    type_warning: str | None = None
    if artifact_type not in _VALID_ARTIFACT_TYPES:
        type_warning = f"Unknown artifact_type '{artifact_type}'; defaulted to 'log'."

    resolved_question = question or ""
    assert root.swmf_root_resolved is not None
    swmf_root_str = root.swmf_root_resolved

    evidence: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    summary = ""

    if resolved_type == "log":
        summary, findings = _inspect_log(path, resolved_question)
    elif resolved_type == "param":
        summary, findings, evidence = _inspect_param(path, resolved_question, swmf_root_str)
    elif resolved_type == "xml":
        summary, findings = _inspect_xml(path, resolved_question)
    elif resolved_type == "run_dir":
        summary, findings, evidence = _inspect_run_dir(path, resolved_question, swmf_root_str)
    elif resolved_type == "build_output":
        summary, findings = _inspect_build_output(path, resolved_question)
    elif resolved_type == "result":
        summary, findings = _inspect_result(path, resolved_question)

    # Known unknowns per type
    known_unknowns_by_type: dict[str, list[str]] = {
        "log": [
            "Only static analysis performed; no runtime context consulted.",
            "Component detection based on log line prefixes; may miss components with non-standard output.",
        ],
        "param": [
            "Lightweight parser only — not authoritative. Full validation still requires Scripts/TestParam.pl from the SWMF root.",
            "External file references resolved relative to PARAM.in directory; may miss environment variables.",
        ],
        "xml": [
            "Command extraction based on PARAM.XML structure; runtime behavior not inspected.",
        ],
        "run_dir": [
            "Only static filesystem scan; no runtime context or process state consulted.",
            "Log first-error is from primary log only; component-specific logs not scanned.",
        ],
        "build_output": [
            "Error detection is pattern-based; may miss non-standard compiler messages.",
        ],
        "result": [
            "Binary files cannot be inspected without specialized tools (IDL, netCDF, etc.).",
            "SWMF output format detection is heuristic; may misclassify custom outputs.",
        ],
    }

    payload: dict[str, Any] = {
        "ok": True,
        "artifact_type": resolved_type,
        "path": path,
        "question": resolved_question,
        "summary": summary,
        "findings": findings,
        "evidence": evidence,
        "provenance": {"artifact_type": resolved_type, "path": path},
        "uncertainty": {
            "known_unknowns": known_unknowns_by_type.get(resolved_type, [
                "Only static analysis performed; no runtime context consulted.",
            ]),
        },
    }
    if type_warning:
        payload["warnings"] = [type_warning]
    return with_root(payload, root)


def register(app: Any) -> None:
    app.tool(
        description=(
            "Inspect one specific local SWMF artifact deeply. "
            "artifact_type must be one of: 'log', 'param', 'xml', 'run_dir', "
            "'build_output', 'result'. "
            "Use for debugging log files, inspecting PARAM.in structure, validating "
            "run directories, or examining build output. Start debugging tasks here "
            "before calling get_evidence. "
            "Specialized inspectors: log detects first error, stacktrace, components, "
            "simulation time; param extracts sessions, component map, includes, external "
            "refs; xml lists commands from PARAM.XML; run_dir checks artifact presence "
            "(SWMF.SUCCESS/DONE), discovers logs with first-error, and finds job scripts; "
            "build_output checks SWMF root markers or compile/linker errors; result "
            "detects binary vs text format and previews structured SWMF output headers."
        )
    )(inspect_artifact)
