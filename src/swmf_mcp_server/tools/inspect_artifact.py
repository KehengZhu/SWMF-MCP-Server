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
                "runlog"      — alias for "log"
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

from collections import Counter, deque
import os
import re
import struct
from pathlib import Path
from typing import Any

from ._helpers import resolve_root_or_failure, with_root
from ._router import raw_result_to_evidence_item, _check_index
from .debug_protocol import _extract_first_error_payload, _extract_stacktrace_lines
from ..core.common import build_path_search_guidance
from ..knowledge import service as ks
from ..parsing.param_parser import parse_param_text
from ..parsing.external_refs import extract_external_references_from_param_text
from ..parsing.component_map import expand_component_map_rows
from ..parsing.job_layout import find_likely_job_scripts, infer_job_layout_from_script
from ..parsing.xml_parser import parse_param_xml_file

_VALID_ARTIFACT_TYPES = frozenset({
    "log",
    "runlog",
    "param",
    "xml",
    "run_dir",
    "build_output",
    "result",
})
_MAX_FILE_CHARS = 200_000  # guard against very large non-log text files
_LOG_HEAD_LINES = 40
_LOG_TAIL_LINES = 120
_LOG_TAIL_SIGNAL_LINES = 24
_LOG_CONTEXT_LINES = 2
_LOG_MAX_DIAGNOSTICS = 40

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
_SUCCESS_RE = re.compile(
    r"(?:SWMF\s+(?:FINISHED|SUCCESS|DONE)\b|Finished\s+(?:Numerical Simulation|Finalizing SWMF))",
    re.IGNORECASE,
)
_NONZERO_EXIT_RE = re.compile(r"\b(?:MPI job exited with code|exit(?:ed)? code)[:\s]+([1-9]\d*)\b", re.IGNORECASE)
_LOG_ERROR_RE = re.compile(
    r"\b(?:ERROR|FATAL|abort(?:ing|ed)?|segmentation fault|sigsegv|mpi_abort|exception|traceback)\b",
    re.IGNORECASE,
)
_LOG_DIAGNOSTIC_RE = re.compile(
    r"\b(?:ERROR|FATAL|WARNING|abort(?:ing|ed)?|segmentation fault|sigsegv|mpi_abort|exception|traceback|NaN|overflow|First error)\b",
    re.IGNORECASE,
)
_PROGRESS_RE = re.compile(
    r"Progress:\s*(?P<step>\d+)\s+steps,\s*(?P<sim_time>[\d.eE+\-]+)\s+s simulation time,\s*"
    r"(?P<cpu_time>[\d.eE+\-]+)\s+s CPU time(?:,\s*Date:\s*(?P<date>\S+))?",
    re.IGNORECASE,
)
_TIMING_BLOCK_RE = re.compile(r"\b(?:TIMING TREE|SORTED TIMING)\b", re.IGNORECASE)
_SAVED_OUTPUT_RE = re.compile(r"^(?P<component>[A-Z]{2}):saved\s+iFile=\s*\d+\s+type=(?P<type>\S+)", re.IGNORECASE)
_NUMERIC_TOKEN_RE = re.compile(r"[+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?")
_SEPARATOR_RE = re.compile(r"^-{8,}$")
_TIMING_ROW_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_./-]*(?:\s+[+-]?\d+(?:\.\d+)?){3,}\s*$")
_STACKTRACE_SIGNAL_RE = re.compile(
    r"(?:traceback|backtrace|program received signal|^\s*#\d+|^\s*at\s+\S.*(?::\d+|\([^)]*\))|call stack)",
    re.IGNORECASE,
)

# Binary file extensions (cannot be read as text)
_BINARY_EXTENSIONS = frozenset({".sav", ".nc", ".cdf", ".fits", ".fit", ".hdf", ".hdf5", ".bin"})
# SWMF text output extensions
_SWMF_OUTPUT_EXTENSIONS = frozenset({".out", ".dat", ".log"})
_IDL_PLOT_EXTENSIONS = frozenset({".out", ".outs"})

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

_COMPONENT_DIR_PREFIXES = ("GM", "IE", "SC", "IH", "OH", "UA", "IM", "PW", "RB", "SP")
_KNOWN_COMPONENT_CODES = frozenset(_COMPONENT_DIR_PREFIXES + ("CON", "PC", "PT"))
_COMPONENT_OUTPUT_ROOTS: dict[str, tuple[str, ...]] = {
    "SC": ("SC/IO2", "SC/plots", "SC"),
    "IH": ("IH/IO2", "IH/plots", "IH"),
    "OH": ("OH/IO2", "OH/plots", "OH"),
    "GM": ("GM/IO2", "GM/plots", "GM"),
    "IE": ("IE/ionosphere", "IE/Output", "IE"),
    "UA": ("UA/Output", "UA/data", "UA"),
    "IM": ("IM/plots", "IM/Output", "IM"),
    "PW": ("PW/plots", "PW/Output", "PW"),
    "RB": ("RB/plots", "RB/Output", "RB"),
    "SP": ("SP/plots", "SP/Output", "SP"),
}
_STATUS_MARKER_NAMES = (
    "PARAM.in",
    "SWMF.SUCCESS",
    "SWMF.DONE",
    "SWMF.KILL",
    "SWMF.KILLED",
    "SWMF.STOP",
    "PostProc.STOP",
    "RESTART.in",
    "RESTART.out",
    "PostProc.pl",
    "PostProc.log",
    "RESULTS",
)
_RUN_DIR_EXPECTED_ENTRIES = [
    "PARAM.in",
    "runlog",
    "SWMF.SUCCESS",
    "SWMF.DONE",
    "IH",
    "GM",
    "IE",
    "SC",
    "OH",
    "UA",
]

_PARAM_SETTING_KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_\[\]/^.\-]*$")
_PARAM_BEGIN_COMPONENT_RE = re.compile(r"^#BEGIN_COMP\s+([A-Z0-9]{2})\b", re.IGNORECASE)
_PARAM_END_COMPONENT_RE = re.compile(r"^#END_COMP\s+([A-Z0-9]{2})\b", re.IGNORECASE)
_PARAM_TIMELINE_COMMANDS = frozenset({
    "#BEGIN_COMP",
    "#END_COMP",
    "#COMPONENTMAP",
    "#COMPONENT",
    "#COUPLE1",
    "#COUPLE2",
    "#SAVEPLOT",
    "#STOP",
    "#RUN",
    "#END",
})
_PARAM_CONTROL_COMMANDS = frozenset({
    "#TIMEACCURATE",
    "#USEDATETIME",
    "#STOP",
    "#COUPLE1",
    "#COUPLE2",
    "#SAVERESTART",
    "#SAVELOGFILE",
    "#SAVETECPLOT",
    "#SAVEPLOT",
})
_PARAM_SAVE_CADENCE_KEYS = frozenset({"DnSavePlot", "DtSavePlot", "DxSavePlot"})
_PARAM_SAVE_COUNT_KEYS = frozenset({"nPlotFile", "nFileOut", "nPlot", "nOutputFile"})


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

def _normalize_log_pattern(line: str) -> str:
    normalized = _NUMERIC_TOKEN_RE.sub("<N>", line.strip())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized[:180]


def _compact_line(line: str, max_chars: int = 180) -> str:
    return re.sub(r"\s+", " ", line.strip())[:max_chars]


def _is_low_signal_repeated_pattern(pattern: str) -> bool:
    if _SEPARATOR_RE.match(pattern):
        return True
    if pattern in {
        "name #iter #calls sec s/iter s/call percent",
        "name sec percent #iter #calls",
        "SC:",
    }:
        return True
    if _TIMING_BLOCK_RE.search(pattern):
        return True
    if _TIMING_ROW_RE.match(pattern):
        return True
    return (
        pattern.count("<N>") >= 3
        and not pattern.startswith("Progress:")
        and not _LOG_DIAGNOSTIC_RE.search(pattern)
    )


def _is_low_signal_tail_line(line: str) -> bool:
    if _SEPARATOR_RE.match(line):
        return True
    if line in {"name #iter #calls sec s/iter s/call percent", "name sec percent #iter #calls"}:
        return True
    if _TIMING_BLOCK_RE.search(line):
        return True
    return bool(_TIMING_ROW_RE.match(line))


def _tail_signal_lines(tail_lines: list[str]) -> dict[str, Any]:
    signal = [line for line in tail_lines if line and not _is_low_signal_tail_line(line)]
    omitted = len([line for line in tail_lines if line and _is_low_signal_tail_line(line)])
    if not signal:
        signal = [line for line in tail_lines if line][-_LOG_TAIL_SIGNAL_LINES:]
    return {
        "lines": signal[-_LOG_TAIL_SIGNAL_LINES:],
        "omitted_low_signal_lines": omitted,
    }


def _assemble_error_message(first_error: dict[str, Any]) -> str | None:
    line = first_error.get("line")
    if not line:
        return None
    pieces = [_compact_line(line, max_chars=260)]
    for follow in first_error.get("context_after", []):
        compact_follow = _compact_line(follow, max_chars=260)
        if not compact_follow:
            continue
        should_attach = (
            pieces[-1].endswith(("=", ":", "message:", "PE="))
            or " with message:" in pieces[-1]
            or (pieces[-1].count("(") > pieces[-1].count(")"))
        )
        if not should_attach:
            break
        pieces.append(compact_follow)
    return " ".join(pieces)[:520]


def _is_actionable_error_line(line: str) -> bool:
    compact = _compact_line(line).lower()
    if not compact:
        return False
    if re.match(r"error in component [a-z]{2} in session\b", compact):
        return False
    if "error report: no errors" in compact:
        return False
    return bool(_LOG_ERROR_RE.search(line))


def _is_diagnostic_line(line: str) -> bool:
    compact = _compact_line(line).lower()
    if "error report: no errors" in compact:
        return False
    return bool(_LOG_DIAGNOSTIC_RE.search(line))


def _update_sampled_counter(
    counter: Counter[str],
    samples: dict[str, dict[str, Any]],
    key: str,
    *,
    line_number: int,
    line: str,
) -> None:
    counter[key] += 1
    if key not in samples:
        samples[key] = {"line_number": line_number, "line": _compact_line(line)}


def _stream_log_summary(path_str: str) -> tuple[dict[str, Any] | None, str | None]:
    p = Path(path_str)
    if not p.exists():
        return None, f"File not found: {path_str}"
    if p.is_dir():
        return None, f"Path is a directory, not a file: {path_str}"

    try:
        file_size = p.stat().st_size
    except OSError:
        file_size = None

    line_count = 0
    head_lines: list[str] = []
    tail_lines: deque[str] = deque(maxlen=_LOG_TAIL_LINES)
    before_context: deque[str] = deque(maxlen=_LOG_CONTEXT_LINES)
    first_error: dict[str, Any] | None = None
    first_error_after_remaining = 0
    stacktrace_lines: list[str] = []
    stacktrace_started = False
    diagnostics = Counter()
    diagnostic_samples: dict[str, dict[str, Any]] = {}
    repeated_patterns = Counter()
    repeated_samples: dict[str, dict[str, Any]] = {}
    component_hits = Counter()
    rank_samples: list[str] = []
    warning_count = 0
    success_lines: list[dict[str, Any]] = []
    nonzero_exit_lines: list[dict[str, Any]] = []
    sim_times: list[str] = []
    progress_count = 0
    progress_first: dict[str, Any] | None = None
    progress_last: dict[str, Any] | None = None
    timing_blocks = Counter()
    saved_outputs = Counter()

    try:
        with p.open("r", encoding="utf-8", errors="replace") as stream:
            for raw_line in stream:
                line_count += 1
                line = raw_line.rstrip("\n\r")
                compact = _compact_line(line)

                if line_count <= _LOG_HEAD_LINES:
                    head_lines.append(compact)
                tail_lines.append(compact)

                pattern = _normalize_log_pattern(line)
                if pattern:
                    _update_sampled_counter(
                        repeated_patterns,
                        repeated_samples,
                        pattern,
                        line_number=line_count,
                        line=line,
                    )

                if first_error is not None and first_error_after_remaining > 0:
                    first_error["context_after"].append(line.rstrip())
                    first_error_after_remaining -= 1

                if first_error is None and _is_actionable_error_line(line):
                    first_error = {
                        "found": True,
                        "line_number": line_count,
                        "line": line.strip(),
                        "context_before": [item.rstrip() for item in before_context],
                        "context_after": [],
                    }
                    first_error_after_remaining = _LOG_CONTEXT_LINES

                if _is_diagnostic_line(line):
                    key = _normalize_log_pattern(line)
                    if key:
                        _update_sampled_counter(
                            diagnostics,
                            diagnostic_samples,
                            key,
                            line_number=line_count,
                            line=line,
                        )

                if _WARNING_RE.search(line):
                    warning_count += 1

                if len(rank_samples) < 3 and _RANK_RE.search(line):
                    rank_samples.append(compact[:120])

                if _SUCCESS_RE.search(line):
                    success_lines.append({"line_number": line_count, "line": compact})
                    success_lines = success_lines[-5:]

                if _NONZERO_EXIT_RE.search(line):
                    nonzero_exit_lines.append({"line_number": line_count, "line": compact})
                    nonzero_exit_lines = nonzero_exit_lines[-5:]

                prefix_match = _COMPONENT_PREFIX_RE.match(line)
                if prefix_match:
                    comp = prefix_match.group(1).upper()
                    if comp in _KNOWN_COMPONENT_CODES:
                        component_hits[comp] += 1
                header_match = _COMPONENT_HEADER_RE.search(line)
                if header_match:
                    comp = header_match.group(1).upper()
                    if comp in _KNOWN_COMPONENT_CODES:
                        component_hits[comp] += 1

                sim_match = _SIM_TIME_RE.search(line)
                if sim_match:
                    sim_times.append(sim_match.group(1))

                progress_match = _PROGRESS_RE.search(line)
                if progress_match:
                    progress_count += 1
                    progress_item = {
                        "line_number": line_count,
                        "step": int(progress_match.group("step")),
                        "simulation_time_s": progress_match.group("sim_time"),
                        "cpu_time_s": progress_match.group("cpu_time"),
                        "date": progress_match.group("date"),
                    }
                    if progress_first is None:
                        progress_first = progress_item
                    progress_last = progress_item

                timing_match = _TIMING_BLOCK_RE.search(line)
                if timing_match:
                    timing_blocks[timing_match.group(0).upper()] += 1

                saved_match = _SAVED_OUTPUT_RE.search(line)
                if saved_match:
                    saved_outputs[f"{saved_match.group('component').upper()}:{saved_match.group('type')}"] += 1

                stack_matched = bool(_STACKTRACE_SIGNAL_RE.search(line))
                if stack_matched and not stacktrace_started:
                    stacktrace_started = True
                if stacktrace_started and len(stacktrace_lines) < 20:
                    if compact:
                        stacktrace_lines.append(compact)
                    elif stacktrace_lines:
                        stacktrace_started = False

                before_context.append(line)
    except OSError as e:
        return None, f"Cannot read file: {e}"

    if first_error is None:
        first_error = {
            "found": False,
            "line_number": None,
            "line": None,
            "context_before": [],
            "context_after": [],
        }
    else:
        first_error["message"] = _assemble_error_message(first_error)

    completed = bool(success_lines)
    failed = bool(nonzero_exit_lines) or (
        first_error.get("found") and not completed and any("abort" in key.lower() for key in diagnostics)
    )
    if failed:
        status = "failed"
    elif completed and diagnostics:
        status = "completed_with_diagnostics"
    elif completed:
        status = "completed"
    else:
        status = "unknown"

    tail_signal = _tail_signal_lines(list(tail_lines))
    top_repeated = [
        {
            "pattern": pattern,
            "count": count,
            "first_sample": repeated_samples[pattern],
        }
        for pattern, count in repeated_patterns.most_common(12)
        if count >= 5 and not _is_low_signal_repeated_pattern(pattern)
    ]
    top_diagnostics = [
        {
            "pattern": pattern,
            "count": count,
            "first_sample": diagnostic_samples[pattern],
        }
        for pattern, count in diagnostics.most_common(_LOG_MAX_DIAGNOSTICS)
    ]

    return {
        "path": str(p),
        "bytes": file_size,
        "line_count": line_count,
        "status": status,
        "first_error": first_error,
        "head_lines": head_lines,
        "tail_lines": tail_signal["lines"],
        "raw_tail_line_count": len(tail_lines),
        "tail_omitted_low_signal_lines": tail_signal["omitted_low_signal_lines"],
        "component_hits": dict(component_hits),
        "rank_samples": rank_samples,
        "warning_count": warning_count,
        "success_lines": success_lines,
        "nonzero_exit_lines": nonzero_exit_lines,
        "simulation_times": {
            "first": sim_times[0] if sim_times else None,
            "last": sim_times[-1] if sim_times else None,
            "sample_count": len(sim_times),
        },
        "progress": {
            "count": progress_count,
            "first": progress_first,
            "last": progress_last,
        },
        "timing_blocks": dict(timing_blocks),
        "saved_outputs": [
            {"key": key, "count": count}
            for key, count in saved_outputs.most_common(12)
        ],
        "diagnostics": top_diagnostics,
        "repeated_patterns": top_repeated,
        "stacktrace_lines": stacktrace_lines,
    }, None


def _discover_run_log_candidates(run_dir: Path) -> list[Path]:
    """Find top-level runtime logs without treating ordinary data .out files as logs."""
    patterns = [
        "runlog*",
        "*.log",
        "slurm*.out",
        "SWMF*.out",
        "swmf*.out",
        "job*.out",
        "stdout*.out",
        "stderr*.out",
    ]
    candidates: dict[Path, None] = {}
    for pattern in patterns:
        for candidate in run_dir.glob(pattern):
            if candidate.is_file():
                candidates[candidate] = None
    return sorted(candidates)


def _run_log_chronology_key(path: Path) -> tuple[int, float, str]:
    digit_groups = re.findall(r"\d+", path.name)
    numeric_key = int(digit_groups[-1]) if digit_groups else -1
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    return numeric_key, mtime, path.name


def _status_from_primary_log(marker_status: str, log_status: str | None) -> str:
    if marker_status == "killed":
        return marker_status
    if log_status in {"failed", "completed", "completed_with_diagnostics"}:
        return log_status
    return marker_status


def _inspect_log(path_str: str, question: str) -> tuple[str, list[dict[str, Any]]]:
    compact, err = _stream_log_summary(path_str)
    if err or compact is None:
        return err or "Could not read log.", []

    first_error = compact["first_error"]
    stacktrace = compact["stacktrace_lines"]
    total_lines = compact["line_count"]

    findings: list[dict[str, Any]] = []

    findings.append({
        "kind": "log_compaction",
        "location": path_str,
        "description": (
            f"Scanned full log ({total_lines} lines"
            + (f", {compact['bytes']} bytes" if compact.get("bytes") is not None else "")
            + "); returned compact head/tail, diagnostics, progress, timing, and repeated-pattern summaries."
        ),
        "line_count": total_lines,
        "bytes": compact.get("bytes"),
        "head_lines": compact["head_lines"],
        "tail_lines": compact["tail_lines"],
        "raw_tail_line_count": compact["raw_tail_line_count"],
        "tail_omitted_low_signal_lines": compact["tail_omitted_low_signal_lines"],
        "repeated_patterns": compact["repeated_patterns"],
    })

    findings.append({
        "kind": "run_status",
        "location": "log",
        "description": f"Run status classified as {compact['status']}.",
        "status": compact["status"],
        "success_lines": compact["success_lines"],
        "nonzero_exit_lines": compact["nonzero_exit_lines"],
    })

    # --- first error ---
    if first_error.get("found"):
        findings.append({
            "kind": "first_error",
            "location": f"line {first_error['line_number']}",
            "description": first_error.get("message") or first_error.get("line", ""),
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
    component_hits: dict[str, int] = compact["component_hits"]

    if component_hits:
        active_components = sorted(component_hits, key=lambda c: -component_hits[c])[:8]
        findings.append({
            "kind": "active_components",
            "location": "log",
            "description": f"Components detected in log: {', '.join(active_components)}",
            "components": active_components,
        })

    # --- simulation time at last occurrence ---
    sim_times = compact["simulation_times"]
    if sim_times["sample_count"]:
        findings.append({
            "kind": "simulation_time",
            "location": "log",
            "description": f"Last simulation time seen: {sim_times['last']} (first: {sim_times['first']})",
            "first_time": sim_times["first"],
            "last_time": sim_times["last"],
            "sample_count": sim_times["sample_count"],
        })

    # --- MPI rank info (first few occurrences) ---
    rank_samples: list[str] = compact["rank_samples"]
    if rank_samples:
        findings.append({
            "kind": "mpi_rank_info",
            "location": "log",
            "description": "MPI rank references detected",
            "samples": rank_samples,
        })

    # --- warning count ---
    warning_count = compact["warning_count"]
    if warning_count:
        findings.append({
            "kind": "warning_count",
            "location": "log",
            "description": f"{warning_count} line(s) containing 'WARNING'.",
            "count": warning_count,
        })

    if compact["diagnostics"]:
        findings.append({
            "kind": "diagnostic_summary",
            "location": "log",
            "description": f"{len(compact['diagnostics'])} diagnostic signature(s) retained after deduplication.",
            "diagnostics": compact["diagnostics"],
        })

    progress = compact["progress"]
    if progress["count"]:
        findings.append({
            "kind": "progress_summary",
            "location": "log",
            "description": (
                f"{progress['count']} progress line(s); "
                f"first step {progress['first']['step']} and last step {progress['last']['step']}."
            ),
            "count": progress["count"],
            "first": progress["first"],
            "last": progress["last"],
        })

    if compact["timing_blocks"] or compact["saved_outputs"]:
        findings.append({
            "kind": "runtime_output_summary",
            "location": "log",
            "description": "Timing blocks and saved-output messages summarized compactly.",
            "timing_blocks": compact["timing_blocks"],
            "saved_outputs": compact["saved_outputs"],
        })

    # --- success / completion ---
    if compact["success_lines"]:
        last_success = compact["success_lines"][-1]
        findings.append({
            "kind": "run_completed",
            "location": f"line {last_success['line_number']}",
            "description": f"Completion indicator found: {last_success['line'][:120]}",
        })

    if not any(f["kind"] in ("first_error", "stacktrace", "run_completed") for f in findings):
        findings.append({
            "kind": "no_error",
            "location": "log",
            "description": "No error patterns detected in the log.",
        })

    error_line = f"First error at line {first_error['line_number']}." if first_error.get("found") else "No errors found."
    comp_str = f" Components: {', '.join(active_components)}." if component_hits else ""
    summary = f"Log file: {total_lines} lines. Status: {compact['status']}. {error_line}{comp_str}" + (
        " Stacktrace detected." if stacktrace else ""
    )
    return summary, findings


# ---------------------------------------------------------------------------
# param inspector
# ---------------------------------------------------------------------------

def _strip_inline_param_comment(line: str) -> str:
    in_single_quote = False
    in_double_quote = False
    out_chars: list[str] = []
    for ch in line:
        if ch == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif ch == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
        elif ch == "!" and not in_single_quote and not in_double_quote:
            break
        out_chars.append(ch)
    return "".join(out_chars).rstrip()


def _coerce_param_scalar(token: str) -> Any:
    lower = token.lower()
    if lower in {"t", ".true."}:
        return True
    if lower in {"f", ".false."}:
        return False
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        return token


def _row_to_param_setting(row: str) -> dict[str, Any] | None:
    tokens = row.split()
    if len(tokens) < 2:
        return None
    key = tokens[-1]
    if not _PARAM_SETTING_KEY_RE.match(key):
        return None
    value_tokens = tokens[:-1]
    if not value_tokens:
        return None
    value: Any
    if len(value_tokens) == 1:
        value = _coerce_param_scalar(value_tokens[0])
    else:
        value = " ".join(value_tokens)
    return {"key": key, "value": value, "raw": row}


def _infer_required_components_from_sessions(sessions: list[Any]) -> list[str]:
    required: list[str] = []
    seen: set[str] = set()

    def _add_component(comp: str) -> None:
        comp_id = comp.strip().upper()
        if len(comp_id) != 2 or comp_id in seen:
            return
        seen.add(comp_id)
        required.append(comp_id)

    for session in sessions:
        for row in session.component_map_rows:
            _add_component(str(row.get("component", "")))
        for comp in session.component_blocks:
            _add_component(comp)
        for comp, _ in session.switched_components:
            _add_component(comp)

    return required


def _parse_param_command_blocks(param_text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current_block: dict[str, Any] | None = None
    session_index = 1
    current_component: str | None = None

    def _finish_current_block() -> None:
        nonlocal current_block
        if current_block is not None:
            blocks.append(current_block)
        current_block = None

    for line_number, raw_line in enumerate(param_text.splitlines(), start=1):
        cleaned = _strip_inline_param_comment(raw_line).strip()
        if not cleaned:
            continue

        if cleaned.startswith("#"):
            _finish_current_block()
            command = cleaned.split()[0].upper()
            current_block = {
                "command": command,
                "session_index": session_index,
                "line_number": line_number,
                "component": current_component,
                "rows": [],
            }

            if command == "#RUN":
                session_index += 1
            elif command == "#END":
                break

            begin_match = _PARAM_BEGIN_COMPONENT_RE.match(cleaned)
            if begin_match:
                current_component = begin_match.group(1).upper()
            end_match = _PARAM_END_COMPONENT_RE.match(cleaned)
            if end_match:
                current_component = None
            continue

        if current_block is not None:
            current_block["rows"].append(cleaned)

    _finish_current_block()
    return blocks


def _parse_saveplot_string_descriptor(value: str) -> dict[str, str | None]:
    tokens = value.split()
    if not tokens:
        return {"plot_area": None, "plot_category": None, "plot_form": None}
    if len(tokens) == 1:
        return {"plot_area": tokens[0], "plot_category": None, "plot_form": None}
    return {
        "plot_area": tokens[0],
        "plot_category": tokens[1] if len(tokens) >= 2 else None,
        "plot_form": tokens[-1],
    }


def _extract_param_semantics(param_text: str, parsed: Any) -> dict[str, Any]:
    command_blocks = _parse_param_command_blocks(param_text)

    session_timeline: list[dict[str, Any]] = []
    key_command_timeline: list[dict[str, Any]] = []
    for session in parsed.sessions[:20]:
        commands = [str(command).upper() for command in session.commands]
        session_timeline.append({
            "session_index": session.index,
            "command_count": len(commands),
            "commands": commands[:20],
            "stop_present": session.stop_present,
            "component_blocks": sorted(session.component_blocks),
        })
        for order, command in enumerate(commands, start=1):
            if command not in _PARAM_TIMELINE_COMMANDS:
                continue
            if len(key_command_timeline) >= 80:
                break
            key_command_timeline.append({
                "session_index": session.index,
                "order": order,
                "command": command,
            })

    control_blocks: list[dict[str, Any]] = []
    control_values: dict[str, list[str]] = {}
    for block in command_blocks:
        command = str(block.get("command", ""))
        if command not in _PARAM_CONTROL_COMMANDS or command == "#SAVEPLOT":
            continue
        settings = [
            parsed_setting
            for row in block.get("rows", [])
            if (parsed_setting := _row_to_param_setting(str(row))) is not None
        ]
        if not settings and not block.get("rows"):
            continue

        for setting in settings:
            key = str(setting.get("key", ""))
            value_text = str(setting.get("value", ""))
            values = control_values.setdefault(key, [])
            if value_text not in values and len(values) < 4:
                values.append(value_text)

        control_blocks.append({
            "command": command,
            "session_index": block.get("session_index"),
            "component": block.get("component"),
            "line_number": block.get("line_number"),
            "settings": settings[:20],
            "raw_rows": [str(row) for row in block.get("rows", [])[:20]],
        })

    control_summary = [
        {"key": key, "values": values}
        for key, values in sorted(control_values.items())
    ]

    saveplot_blocks: list[dict[str, Any]] = []
    for block in command_blocks:
        if block.get("command") != "#SAVEPLOT":
            continue

        declared_plot_count: int | None = None
        global_cadence: dict[str, Any] = {}
        block_options: dict[str, Any] = {}
        entries: list[dict[str, Any]] = []
        current_entry: dict[str, Any] | None = None
        unparsed_rows: list[str] = []

        for row in block.get("rows", []):
            row_text = str(row)
            setting = _row_to_param_setting(row_text)
            if setting is None:
                unparsed_rows.append(row_text)
                continue

            key = str(setting["key"])
            value = setting["value"]
            value_text = str(value)

            if key in _PARAM_SAVE_COUNT_KEYS:
                if declared_plot_count is None:
                    parsed_count: int | None = None
                    if isinstance(value, int):
                        parsed_count = value
                    else:
                        try:
                            parsed_count = int(float(value_text))
                        except ValueError:
                            parsed_count = None
                    declared_plot_count = parsed_count
                block_options[key] = value
                continue

            if key == "StringPlot":
                if current_entry is not None:
                    entries.append(current_entry)
                descriptor = _parse_saveplot_string_descriptor(value_text)
                current_entry = {
                    "string_plot": value_text,
                    "plot_area": descriptor.get("plot_area"),
                    "plot_category": descriptor.get("plot_category"),
                    "plot_form": descriptor.get("plot_form"),
                    "cadence": {},
                    "name_vars": [],
                    "name_pars": [],
                    "options": {},
                }
                continue

            if key in _PARAM_SAVE_CADENCE_KEYS:
                if current_entry is not None:
                    current_entry["cadence"][key] = value
                else:
                    global_cadence[key] = value
                continue

            if key == "NameVars":
                vars_tokens = value_text.split()
                if current_entry is not None:
                    current_entry["name_vars"] = vars_tokens[:40]
                else:
                    block_options["NameVars"] = vars_tokens[:40]
                continue

            if key == "NamePars":
                pars_tokens = value_text.split()
                if current_entry is not None:
                    current_entry["name_pars"] = pars_tokens[:40]
                else:
                    block_options["NamePars"] = pars_tokens[:40]
                continue

            if current_entry is not None:
                current_entry["options"][key] = value
            else:
                block_options[key] = value

        if current_entry is not None:
            entries.append(current_entry)

        if global_cadence and entries:
            for entry in entries:
                cadence = entry.setdefault("cadence", {})
                for cadence_key, cadence_value in global_cadence.items():
                    cadence.setdefault(cadence_key, cadence_value)

        saveplot_blocks.append({
            "session_index": block.get("session_index"),
            "component": block.get("component"),
            "line_number": block.get("line_number"),
            "declared_plot_count": declared_plot_count,
            "entry_count": len(entries),
            "plot_forms": sorted({str(entry.get("plot_form")) for entry in entries if entry.get("plot_form")}),
            "plot_areas": sorted({str(entry.get("plot_area")) for entry in entries if entry.get("plot_area")}),
            "shared_cadence": global_cadence,
            "entries": entries[:12],
            "options": block_options,
            "unparsed_rows": unparsed_rows[:20],
        })

    return {
        "session_timeline": session_timeline,
        "key_command_timeline": key_command_timeline,
        "control_command_blocks": control_blocks,
        "control_summary": control_summary,
        "saveplot_blocks": saveplot_blocks,
    }


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

    required_components = _infer_required_components_from_sessions(parsed.sessions)

    n_sessions = len(parsed.sessions)
    param_semantics = _extract_param_semantics(text, parsed)
    saveplot_blocks = param_semantics.get("saveplot_blocks", [])

    # Build findings
    findings: list[dict[str, Any]] = []

    q_lower = question.lower()
    focus_includes = any(tok in q_lower for tok in ("include", "resolve include"))
    focus_compmap = any(tok in q_lower for tok in ("component map", "componentmap", "#componentmap"))
    focus_validate = any(tok in q_lower for tok in ("validate", "validation", "testparam"))
    focus_external = any(tok in q_lower for tok in ("external", "external ref", "file ref"))
    focus_timeline = any(tok in q_lower for tok in ("session", "timeline", "run phases", "phase"))
    focus_control = any(tok in q_lower for tok in ("control", "timeaccurate", "stop", "couple", "cadence"))
    focus_saveplot = any(tok in q_lower for tok in ("saveplot", "#saveplot", "stringplot", "outs", "plot"))

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
    if param_semantics["session_timeline"] or focus_timeline:
        findings.append({
            "kind": "param_session_timeline",
            "location": path_str,
            "description": (
                f"Session timeline extracted for {len(param_semantics['session_timeline'])} session(s). "
                f"{len(param_semantics['key_command_timeline'])} key command event(s)."
            ),
            "sessions": param_semantics["session_timeline"][:12],
            "key_command_timeline": param_semantics["key_command_timeline"][:60],
        })

    if param_semantics["control_summary"] or focus_control:
        findings.append({
            "kind": "param_control_settings",
            "location": path_str,
            "description": (
                f"{len(param_semantics['control_command_blocks'])} control-command block(s) "
                f"with {len(param_semantics['control_summary'])} key setting(s)."
            ),
            "control_settings": param_semantics["control_summary"][:40],
            "control_command_blocks": param_semantics["control_command_blocks"][:20],
        })

    if saveplot_blocks or focus_saveplot:
        findings.append({
            "kind": "param_saveplot_blocks",
            "location": path_str,
            "description": f"{len(saveplot_blocks)} #SAVEPLOT block(s) parsed.",
            "saveplot_blocks": saveplot_blocks[:20],
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
    if question and not any(
        (
            focus_includes,
            focus_compmap,
            focus_validate,
            focus_timeline,
            focus_control,
            focus_saveplot,
        )
    ):
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
        f"{len(missing_includes)} missing include(s), "
        f"{len(saveplot_blocks)} #SAVEPLOT block(s)."
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

def _dedupe_paths(paths: list[Path]) -> list[Path]:
    deduped: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        try:
            key = str(path.expanduser().resolve())
        except OSError:
            key = str(path.expanduser())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path.expanduser())
    return deduped


def _run_dir_search_roots(path_str: str, swmf_root: str) -> list[Path]:
    raw_path = Path(path_str).expanduser()
    cwd = Path.cwd().resolve()
    resolved_missing = raw_path if raw_path.is_absolute() else cwd / raw_path
    swmf_root_path = Path(swmf_root).expanduser().resolve()
    workspace_root = swmf_root_path.parent

    roots = [
        cwd,
        resolved_missing.parent,
        resolved_missing.parent.parent,
        workspace_root,
        workspace_root / "SWMFSOLAR",
        cwd.parent,
        cwd.parent / "SWMFSOLAR",
    ]

    for parent in list(resolved_missing.parents[:4]):
        roots.append(parent)
        roots.append(parent / "SWMFSOLAR")

    return _dedupe_paths(roots)


def _has_expected_run_entry(path_text: str) -> bool:
    path = Path(path_text)
    if not path.is_dir():
        return False
    return any((path / entry).exists() for entry in _RUN_DIR_EXPECTED_ENTRIES)


def _build_run_dir_not_found_finding(
    path_str: str,
    swmf_root: str,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    raw_path = Path(path_str).expanduser()
    keyword_hints = [raw_path.name, raw_path.stem, "run01", "run", "case", "output"]
    guidance = build_path_search_guidance(
        path_role="run_dir",
        search_roots=_run_dir_search_roots(path_str, swmf_root),
        expected_entries=_RUN_DIR_EXPECTED_ENTRIES,
        keyword_hints=keyword_hints,
    )

    candidates = guidance.get("path_search_candidates", [])
    if isinstance(candidates, list):
        swmf_workspace = Path(swmf_root).resolve().parent
        requested_name = raw_path.name.lower()

        def _candidate_rank(candidate: str) -> tuple[bool, bool, bool, str]:
            candidate_path = Path(candidate).resolve()
            under_workspace = False
            try:
                candidate_path.relative_to(swmf_workspace)
                under_workspace = True
            except ValueError:
                pass
            return (
                not under_workspace,
                requested_name not in str(candidate_path).lower(),
                not _has_expected_run_entry(candidate),
                str(candidate_path),
            )

        candidates = sorted(
            (str(candidate) for candidate in candidates),
            key=_candidate_rank,
        )
        guidance["path_search_candidates"] = candidates

    finding = {
        "kind": "run_dir_not_found",
        "location": path_str,
        "description": f"Path is not a directory: {path_str}. Candidate run directories were searched.",
        **guidance,
    }
    summary = f"Not a directory: {path_str}. Path-search candidates: {len(candidates)}."
    return summary, [finding], []


def _component_from_dir_name(name: str) -> str | None:
    upper = name.upper()
    for comp in _COMPONENT_DIR_PREFIXES:
        if upper == comp or upper.startswith(comp):
            return comp
    return None


def _sample_names(paths: list[Path], limit: int = 8) -> list[str]:
    return [path.name for path in sorted(paths)[:limit]]


def _path_sample(paths: list[Path], base: Path, limit: int = 8) -> list[str]:
    samples: list[str] = []
    for path in sorted(paths)[:limit]:
        try:
            samples.append(str(path.relative_to(base)))
        except ValueError:
            samples.append(str(path))
    return samples


def _safe_is_symlink_target(path: Path) -> str | None:
    if not path.is_symlink():
        return None
    try:
        return os.readlink(path)
    except OSError:
        return "<unreadable>"


def _iter_files_limited(root: Path, limit: int = 10_000) -> list[Path]:
    files: list[Path] = []
    if not root.exists():
        return files
    if root.is_file():
        return [root]
    try:
        iterator = root.rglob("*")
        for item in iterator:
            if item.is_file():
                files.append(item)
                if len(files) >= limit:
                    break
    except OSError:
        return files
    return files


def _extension_counts(files: list[Path]) -> dict[str, int]:
    counts = Counter(path.suffix.lower() or "<none>" for path in files)
    return dict(sorted(counts.items()))


def _snapshot_groups(component_dir: Path) -> list[dict[str, Any]]:
    groups: dict[str, list[Path]] = {}
    for output_file in component_dir.glob("*.out"):
        match = re.match(r"(.+)_t\d+(?:_n\d+)?\.out$", output_file.name)
        if not match:
            continue
        groups.setdefault(match.group(1), []).append(output_file)

    grouped: list[dict[str, Any]] = []
    for base_name, files in sorted(groups.items()):
        combined_name = f"{base_name}.outs"
        has_step_suffix = any(re.search(r"_t\d+_n\d+\.out$", item.name) for item in files)
        grouped.append({
            "base": base_name,
            "pattern": f"{base_name}_t*_n*.out" if has_step_suffix else f"{base_name}_t*.out",
            "count": len(files),
            "samples": _sample_names(files, limit=2),
            "expected_outs": combined_name,
            "combined_outs": combined_name,
            "combined_outs_exists": (component_dir / combined_name).is_file(),
        })
    return grouped[:12]


def _snapshot_groups_recursive(root: Path, base: Path) -> list[dict[str, Any]]:
    grouped: list[dict[str, Any]] = []
    for directory in sorted({path.parent for path in root.rglob("*.out") if path.is_file()}):
        for group in _snapshot_groups(directory):
            group = dict(group)
            try:
                group["directory"] = str(directory.relative_to(base))
            except ValueError:
                group["directory"] = str(directory)
            grouped.append(group)
            if len(grouped) >= 24:
                return grouped
    return grouped


def _observed_snapshot_groups(p: Path, components: list[str]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for comp in components:
        for rel_root in _COMPONENT_OUTPUT_ROOTS.get(comp, (comp,)):
            root = p / rel_root
            if not root.is_dir():
                continue
            for group in _snapshot_groups_recursive(root, p):
                directory = str(group.get("directory") or rel_root)
                base_name = str(group.get("base") or "")
                if not base_name:
                    continue
                key = (comp, directory, base_name)
                if key in seen:
                    continue
                seen.add(key)
                groups.append({
                    "component": comp,
                    "directory": directory,
                    "base": base_name,
                    "pattern": group.get("pattern"),
                    "count": group.get("count", 0),
                    "combined_outs": group.get("combined_outs"),
                    "combined_outs_exists": bool(group.get("combined_outs_exists")),
                    "samples": group.get("samples", [])[:2],
                })
    return sorted(groups, key=lambda item: (str(item["component"]), str(item["directory"]), str(item["base"])))


def _status_markers(p: Path) -> dict[str, dict[str, Any]]:
    markers: dict[str, dict[str, Any]] = {}
    for name in _STATUS_MARKER_NAMES:
        path = p / name
        if not path.exists():
            continue
        item: dict[str, Any] = {
            "path": str(path),
            "is_dir": path.is_dir(),
            "is_symlink": path.is_symlink(),
        }
        target = _safe_is_symlink_target(path)
        if target is not None:
            item["symlink_target"] = target
        markers[name] = item
    return markers


def _classify_run_dir_layout(p: Path, markers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    component_dirs = [
        item.name
        for item in sorted(p.iterdir())
        if item.is_dir() and _component_from_dir_name(item.name) is not None
    ]
    has_param = "PARAM.in" in markers
    has_results = "RESULTS" in markers
    has_log = bool(_discover_run_log_candidates(p))
    has_framework_restart = "RESTART.in" in markers or "RESTART.out" in markers
    has_restart_subdir = (p / "RESTART").is_dir()
    per_comp_restart = any(
        ((p / comp / "restartIN").exists() or (p / comp / "restartOUT").exists())
        for comp in component_dirs
    )

    if has_param and (has_restart_subdir or p.parent.name.lower() in {"results", "result"}):
        layout = "postprocessed_results_tree"
    elif has_param and (has_log or component_dirs or "SWMF.SUCCESS" in markers or "SWMF.KILL" in markers):
        layout = "live_run_dir"
    elif has_framework_restart or per_comp_restart or has_restart_subdir:
        layout = "restart_tree"
    elif _component_from_dir_name(p.name) is not None:
        layout = "component_dir"
    elif has_results:
        layout = "live_run_dir"
    else:
        layout = "unknown"

    evidence: dict[str, Any] = {}
    if has_param:
        evidence["has_param_in"] = True
    if has_results:
        evidence["has_results_dir"] = True
    if has_log:
        evidence["has_run_logs"] = True
    if has_framework_restart:
        evidence["has_framework_restart"] = True
    if has_restart_subdir:
        evidence["has_restart_subdir"] = True
    if component_dirs:
        evidence["component_dirs"] = component_dirs[:20]
    return {
        "kind": "run_dir_layout",
        "location": str(p),
        "description": f"Run-directory layout classified as {layout}.",
        "layout": layout,
        "evidence": evidence,
    }


def _postproc_state(p: Path, markers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    log_path = p / "PostProc.log"
    log_tail: list[str] = []
    log_status = "missing"
    warning_count = 0
    diagnostic_count = 0
    error_count = 0
    repeat_mode = False
    completed = False
    if log_path.is_file():
        compact, err = _stream_log_summary(str(log_path))
        if compact is None:
            log_status = "unreadable"
            log_tail = [err or "PostProc.log could not be read."]
        else:
            log_status = compact["status"]
            log_tail = compact["tail_lines"]
            warning_count = compact["warning_count"]
            diagnostic_count = len(compact["diagnostics"])
            error_count = sum(
                1
                for item in compact["diagnostics"]
                if re.search(r"\b(?:ERROR|FATAL|abort|exception|traceback)\b", str(item.get("pattern", "")), re.IGNORECASE)
            )
            tail_text = "\n".join(log_tail).lower()
            repeat_mode = "repeat" in tail_text
            completed = log_status in {"completed", "completed_with_diagnostics"} or "normal completion" in tail_text

    if "PostProc.STOP" in markers:
        state = "running_or_stopped"
    elif log_path.is_file() and any("ERROR in PostProc.pl" in line for line in log_tail):
        state = "failed"
    elif log_path.is_file() and (log_status == "failed" or error_count):
        state = "failed"
    elif log_path.is_file() and repeat_mode:
        state = "running_repeat_mode"
    elif log_path.is_file() and warning_count:
        state = "completed_with_warnings" if completed else "unknown_with_warnings"
    elif log_path.is_file() and completed:
        state = "completed"
    elif "RESULTS" in markers:
        state = "completed_or_collected"
    elif log_path.is_file():
        state = "unknown"
    else:
        state = "not_run"

    result = {
        "kind": "postproc_state",
        "location": str(log_path if log_path.exists() else p),
        "description": f"PostProc state classified as {state}.",
        "state": state,
        "warning_count": warning_count,
        "diagnostic_count": diagnostic_count,
        "error_diagnostic_count": error_count,
    }
    if log_path.is_file():
        result["postproc_log"] = str(log_path)
        result["tail_lines"] = log_tail[-12:]
    if "PostProc.STOP" in markers:
        result["postproc_stop"] = markers["PostProc.STOP"]
    if "RESULTS" in markers:
        result["results_dir"] = markers["RESULTS"]
    return result


def _declared_components_from_param(required_components: list[str], saveplot_blocks: list[dict[str, Any]]) -> list[str]:
    declared: set[str] = set(required_components)
    for block in saveplot_blocks:
        comp = block.get("component")
        if isinstance(comp, str) and len(comp) == 2:
            declared.add(comp.upper())
    return sorted(declared)


def _component_artifact_inventory(
    p: Path,
    declared_components: list[str],
) -> dict[str, Any]:
    discovered = {
        comp
        for item in p.iterdir()
        if item.is_dir() and (comp := _component_from_dir_name(item.name)) is not None
    }
    components = sorted(discovered | set(declared_components))
    inventories: list[dict[str, Any]] = []
    for comp in components:
        roots: list[dict[str, Any]] = []
        all_files: list[Path] = []
        for rel_root in _COMPONENT_OUTPUT_ROOTS.get(comp, (comp,)):
            root = p / rel_root
            if not root.exists():
                continue
            root_files = _iter_files_limited(root)
            all_files.extend(root_files)
            root_item: dict[str, Any] = {
                "relative_path": rel_root,
                "path": str(root),
                "is_symlink": root.is_symlink(),
                "file_count": len(root_files),
                "extension_counts": _extension_counts(root_files),
            }
            target = _safe_is_symlink_target(root)
            if target is not None:
                root_item["symlink_target"] = target
            roots.append(root_item)

        log_files = [
            path for path in all_files
            if path.name.lower().startswith("log") or path.suffix.lower() == ".log"
        ]
        inventory = {
            "component": comp,
            "declared_in_param": comp in declared_components,
            "discovered": comp in discovered,
            "file_count": len(set(all_files)),
            "extension_counts": _extension_counts(list(set(all_files))),
        }
        if roots:
            inventory["output_roots"] = roots
        if log_files:
            inventory["logs"] = _path_sample(log_files, p, limit=8)
        inventories.append(inventory)

    return {
        "kind": "component_artifact_inventory",
        "location": str(p),
        "description": f"Inventoried artifacts for {len(inventories)} component(s).",
        "components": inventories,
    }


def _restart_inventory(p: Path) -> dict[str, Any]:
    framework = []
    for name in ("RESTART.in", "RESTART.out"):
        path = p / name
        if not path.exists():
            continue
        item = {
            "name": name,
            "path": str(path),
            "is_symlink": path.is_symlink(),
        }
        target = _safe_is_symlink_target(path)
        if target is not None:
            item["symlink_target"] = target
        framework.append(item)

    components: list[dict[str, Any]] = []
    for item in sorted(p.iterdir()):
        if not item.is_dir():
            continue
        comp = _component_from_dir_name(item.name)
        if comp is None:
            continue
        restart_dirs = []
        for name in ("restartIN", "restartOUT"):
            restart_path = item / name
            if not restart_path.exists():
                continue
            files = _iter_files_limited(restart_path)
            item = {
                "name": name,
                "path": str(restart_path),
                "is_symlink": restart_path.is_symlink(),
                "file_count": len(files),
                "samples": _path_sample(files, p, limit=6),
            }
            target = _safe_is_symlink_target(restart_path)
            if target is not None:
                item["symlink_target"] = target
            restart_dirs.append(item)
        if restart_dirs:
            components.append({"component": comp, "restart_dirs": restart_dirs})

    candidates = []
    for pattern in ("RESTART*", "RESULTS/*/RESTART", "RESULTS/*/RESTART*"):
        for candidate in sorted(p.glob(pattern))[:20]:
            candidates.append(str(candidate))

    return {
        "kind": "restart_inventory",
        "location": str(p),
        "description": (
            f"Restart inventory: {len(framework)} framework marker(s), "
            f"{len(components)} component restart area(s)."
        ),
        "framework": framework,
        "components": components,
        "restart_tree_candidates": candidates[:40],
    }


def _saveplot_entries_by_component(
    saveplot_blocks: list[dict[str, Any]],
    fallback_components: list[str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for block in saveplot_blocks:
        block_component = block.get("component")
        components = [str(block_component).upper()] if block_component else fallback_components
        for entry in block.get("entries", []):
            entries.append({
                "components": components,
                "plot_area": entry.get("plot_area"),
                "plot_form": entry.get("plot_form"),
                "cadence": entry.get("cadence", {}),
            })
    return entries


def _component_output_artifacts(
    p: Path,
    saveplot_blocks: list[dict[str, Any]],
    declared_components: list[str],
) -> dict[str, Any]:
    fallback_components = declared_components or sorted(
        {
            comp
            for item in p.iterdir()
            if item.is_dir() and (comp := _component_from_dir_name(item.name)) is not None
        }
    )
    saveplot_entries = _saveplot_entries_by_component(saveplot_blocks, fallback_components)
    observed_groups = _observed_snapshot_groups(p, fallback_components)

    entries: list[dict[str, Any]] = []
    for group in observed_groups:
        group_base = str(group.get("base") or "")
        group_base_lower = group_base.lower()
        matched_saveplot = None
        for candidate in saveplot_entries:
            if group.get("component") not in candidate["components"]:
                continue
            plot_area = str(candidate.get("plot_area") or "")
            if plot_area and plot_area.lower() not in group_base_lower:
                continue
            matched_saveplot = candidate
            break

        item = {
            "component": group.get("component"),
            "plot_area": matched_saveplot.get("plot_area") if matched_saveplot else None,
            "plot_form": matched_saveplot.get("plot_form") if matched_saveplot else None,
            "cadence": matched_saveplot.get("cadence", {}) if matched_saveplot else {},
            "directory": group.get("directory"),
            "pattern": group.get("pattern"),
            "raw_frame_count": group.get("count", 0),
            "combined_outs_present": bool(group.get("combined_outs_exists")),
            "example_files": group.get("samples", [])[:2],
        }
        if group.get("combined_outs_exists"):
            item["combined_outs"] = group.get("combined_outs")
        entries.append(item)

    return {
        "kind": "component_output_artifacts",
        "location": str(p),
        "description": f"Summarized {len(entries)} observed component output artifact group(s).",
        "entries": entries[:40],
    }


def _inspect_run_dir(
    path_str: str,
    question: str,
    swmf_root: str,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    p = Path(path_str)
    if not p.is_dir():
        return _build_run_dir_not_found_finding(path_str, swmf_root)

    findings: list[dict[str, Any]] = []

    # --- Directory inventory ---
    total_top_level_items = 0
    files_found: list[str] = []
    for item in sorted(p.iterdir()):
        total_top_level_items += 1
        if len(files_found) < 60:
            files_found.append(item.name + ("/" if item.is_dir() else ""))

    findings.append({
        "kind": "directory_inventory",
        "location": path_str,
        "description": f"{total_top_level_items} top-level items in run directory.",
        "total_count": total_top_level_items,
        "items": files_found,
    })

    markers = _status_markers(p)
    findings.append({
        "kind": "status_markers",
        "location": path_str,
        "description": "SWMF, restart, and PostProc marker files inventoried.",
        "markers": markers,
    })
    findings.append(_classify_run_dir_layout(p, markers))
    findings.append(_postproc_state(p, markers))

    # --- Artifact presence (SWMF status files) ---
    artifact_keys = [
        "PARAM.in", "RESTART.in", "RESTART.out",
        "SWMF.SUCCESS", "SWMF.DONE", "SWMF.KILL", "SWMF.KILLED", "SWMF.STOP",
    ]
    artifact_presence: dict[str, str] = {
        name: str(p / name) for name in artifact_keys if (p / name).exists()
    }
    # Infer marker-only status first. Runtime logs can refine this below.
    if "SWMF.KILL" in artifact_presence or "SWMF.KILLED" in artifact_presence:
        marker_run_status = "killed"
    elif "SWMF.SUCCESS" in artifact_presence and "SWMF.DONE" in artifact_presence:
        marker_run_status = "completed"
    elif "SWMF.SUCCESS" in artifact_presence:
        marker_run_status = "graceful_stop_or_partial"
    elif "SWMF.STOP" in artifact_presence:
        marker_run_status = "stopped"
    elif "PARAM.in" in artifact_presence:
        marker_run_status = "prepared_or_running"
    else:
        marker_run_status = "unknown"

    run_status = marker_run_status
    artifact_finding = {
        "kind": "artifact_presence",
        "location": path_str,
        "description": f"Run status: {run_status}. Key artifacts detected.",
        "artifact_presence": artifact_presence,
        "marker_run_status": marker_run_status,
        "run_status": run_status,
    }
    findings.append(artifact_finding)

    param_status = "missing"
    param_path = p / "PARAM.in"
    required_components: list[str] = []
    saveplot_blocks: list[dict[str, Any]] = []
    if param_path.is_file():
        param_text, param_err = _read_file_safe(str(param_path))
        if param_err or param_text is None:
            param_status = "unreadable"
            findings.append({
                "kind": "run_dir_param_unreadable",
                "location": str(param_path),
                "description": param_err or "PARAM.in exists but could not be read.",
            })
        else:
            parsed_param = parse_param_text(param_text)
            required_components = _infer_required_components_from_sessions(parsed_param.sessions)
            param_semantics = _extract_param_semantics(param_text, parsed_param)
            saveplot_blocks = param_semantics.get("saveplot_blocks", [])
            param_status = "parsed"

            findings.append({
                "kind": "run_dir_param_summary",
                "location": str(param_path),
                "description": (
                    f"PARAM.in present: {len(param_text.splitlines())} line(s), "
                    f"{len(parsed_param.sessions)} session(s), "
                    f"{len(required_components)} component(s), "
                    f"{len(saveplot_blocks)} #SAVEPLOT block(s)."
                ),
                "param_path": str(param_path),
                "line_count": len(param_text.splitlines()),
                "session_count": len(parsed_param.sessions),
                "required_components": required_components,
                "saveplot_block_count": len(saveplot_blocks),
                "parser_error_count": len(parsed_param.errors),
                "parser_warning_count": len(parsed_param.warnings),
            })
    else:
        findings.append({
            "kind": "run_dir_param_missing",
            "location": str(param_path),
            "description": "PARAM.in is missing from this run directory.",
        })

    # --- Log file discovery and first-error preview ---
    log_candidates = _discover_run_log_candidates(p)
    primary_log: Path | None = sorted(log_candidates, key=_run_log_chronology_key)[-1] if log_candidates else None
    primary_log_compact: dict[str, Any] | None = None
    primary_log_error: str | None = None

    if primary_log is not None:
        primary_log_compact, primary_log_error = _stream_log_summary(str(primary_log))
        if primary_log_compact is None:
            first_error = {"found": False}
            log_lines = 0
            log_status = "unknown"
            log_bytes = None
        else:
            first_error = primary_log_compact["first_error"]
            log_lines = primary_log_compact["line_count"]
            log_status = primary_log_compact["status"]
            log_bytes = primary_log_compact.get("bytes")

        run_status = _status_from_primary_log(marker_run_status, log_status)
        artifact_finding["run_status"] = run_status
        artifact_finding["description"] = f"Run status: {run_status}. Key artifacts detected."
        if run_status != marker_run_status:
            artifact_finding["status_source"] = "primary_log"

        log_finding: dict[str, Any] = {
            "kind": "log_discovery",
            "location": str(primary_log),
            "description": (
                f"Primary log: {primary_log.name} ({log_lines} lines"
                + (f", {log_bytes} bytes" if log_bytes is not None else "")
                + f", status={log_status}). "
                + (f"Listed {len(log_candidates)} discovered log(s); content summary is from the latest log only. ")
                + (f"First error at line {first_error['line_number']}." if first_error.get("found") else "No errors detected.")
            ),
            "log_files": [str(lf) for lf in log_candidates],
            "primary_log": str(primary_log),
            "status": log_status,
            "line_count": log_lines,
            "bytes": log_bytes,
        }
        if primary_log_error:
            log_finding["read_error"] = primary_log_error
        if first_error.get("found"):
            log_finding["first_error"] = first_error
        if primary_log_compact is not None:
            log_finding["tail_lines"] = primary_log_compact["tail_lines"]
            log_finding["tail_omitted_low_signal_lines"] = primary_log_compact["tail_omitted_low_signal_lines"]
            log_finding["diagnostics"] = primary_log_compact["diagnostics"][:8]
            log_finding["progress"] = primary_log_compact["progress"]
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
        if subdir.is_dir() and _component_from_dir_name(subdir.name) is not None:
            output_dirs.append(subdir.name + "/")
    if output_dirs:
        findings.append({
            "kind": "output_subdirs",
            "location": path_str,
            "description": f"Component output subdirectories found: {', '.join(output_dirs[:8])}",
            "subdirs": output_dirs[:8],
        })

    declared_components = _declared_components_from_param(required_components, saveplot_blocks)
    inventory_components = sorted(
        {
            comp
            for item in p.iterdir()
            if item.is_dir() and (comp := _component_from_dir_name(item.name)) is not None
        }
        | set(declared_components)
    )
    findings.append(_component_artifact_inventory(p, declared_components))
    restart_inventory = _restart_inventory(p)
    if restart_inventory["framework"] or restart_inventory["components"] or restart_inventory["restart_tree_candidates"]:
        findings.append(restart_inventory)
    output_artifacts = _component_output_artifacts(p, saveplot_blocks, inventory_components)
    if output_artifacts["entries"]:
        findings.append(output_artifacts)

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
        f"Run directory '{path_str}': {total_top_level_items} items. "
        f"Status: {run_status}. "
        f"PARAM.in: {param_status}. "
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

def _read_fortran_record(data: bytes, offset: int, endian: str) -> tuple[bytes, int] | None:
    if offset + 8 > len(data):
        return None
    (length,) = struct.unpack_from(f"{endian}I", data, offset)
    start = offset + 4
    end = start + length
    trailer_end = end + 4
    if length > 10_000_000 or trailer_end > len(data):
        return None
    (trailer,) = struct.unpack_from(f"{endian}I", data, end)
    if trailer != length:
        return None
    return data[start:end], trailer_end


def _decode_idl_string(raw: bytes) -> str:
    return raw.decode("ascii", errors="replace").replace("\x00", " ").strip()


def _split_idl_names(raw: str) -> list[str]:
    return [token for token in re.split(r"[\s,]+", raw.strip()) if token]


def _parse_idl_binary_plot_header(path: Path) -> dict[str, Any] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) < 32:
        return None

    for endian in ("<", ">"):
        offset = 0
        first = _read_fortran_record(data, offset, endian)
        if first is None:
            continue
        headline_raw, offset = first
        if len(headline_raw) not in (79, 500):
            continue

        second = _read_fortran_record(data, offset, endian)
        if second is None:
            continue
        header_raw, offset = second
        if len(header_raw) == 20:
            filetype = "real4" if len(headline_raw) == 79 else "REAL4"
            it, time_value, ndim_raw, neqpar, nw = struct.unpack(f"{endian}ifiii", header_raw)
            real_bytes = 4
        elif len(header_raw) == 24:
            filetype = "real8" if len(headline_raw) == 79 else "REAL8"
            it, time_value, ndim_raw, neqpar, nw = struct.unpack(f"{endian}idiii", header_raw)
            real_bytes = 8
        else:
            continue

        ndim = abs(int(ndim_raw))
        if ndim < 1 or ndim > 3 or neqpar < 0 or nw < 0:
            continue

        nx_record = _read_fortran_record(data, offset, endian)
        if nx_record is None:
            continue
        nx_raw, offset = nx_record
        if len(nx_raw) < 4 * ndim:
            continue
        nx = list(struct.unpack(f"{endian}{ndim}i", nx_raw[: 4 * ndim]))

        if neqpar:
            eqpar_record = _read_fortran_record(data, offset, endian)
            if eqpar_record is None:
                continue
            _, offset = eqpar_record

        var_record = _read_fortran_record(data, offset, endian)
        if var_record is None:
            continue
        var_raw, offset_after_header = var_record
        names = _split_idl_names(_decode_idl_string(var_raw))
        coord_names = names[:ndim]
        variable_names = names[ndim: ndim + nw]
        parameter_names = names[ndim + nw: ndim + nw + neqpar]

        ncell = 1
        for n in nx:
            ncell *= max(1, int(n))
        pictsize = offset_after_header + 8 * (1 + nw) + real_bytes * (ndim + nw) * ncell
        npictinfile = None
        if pictsize > 0 and len(data) >= pictsize and len(data) % pictsize == 0:
            npictinfile = len(data) // pictsize

        return {
            "kind": "idl_plot_file_header",
            "format": "binary",
            "location": str(path),
            "description": f"SWMF IDL binary plot-file header detected ({filetype}).",
            "filetype": filetype,
            "npictinfile": npictinfile,
            "headline": _decode_idl_string(headline_raw),
            "it": int(it),
            "time": float(time_value),
            "gencoord": int(ndim_raw < 0),
            "ndim": ndim,
            "neqpar": int(neqpar),
            "nw": int(nw),
            "nx": nx,
            "coord_names": coord_names,
            "variable_names": variable_names,
            "parameter_names": parameter_names,
            "header_length": len(headline_raw),
        }
    return None


def _parse_idl_ascii_plot_header(path: Path) -> dict[str, Any] | None:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeDecodeError):
        return None

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 4:
        return None

    header_tokens = lines[1].split()
    if len(header_tokens) < 5:
        return None
    try:
        it = int(header_tokens[0])
        time_value = float(header_tokens[1])
        ndim_raw = int(header_tokens[2])
        neqpar = int(header_tokens[3])
        nw = int(header_tokens[4])
    except ValueError:
        return None

    ndim = abs(ndim_raw)
    if ndim < 1 or ndim > 3 or neqpar < 0 or nw < 0 or len(lines) < 4 + (1 if neqpar else 0):
        return None

    try:
        nx = [int(token) for token in lines[2].split()[:ndim]]
    except ValueError:
        return None
    if len(nx) != ndim:
        return None

    var_line_index = 3 + (1 if neqpar else 0)
    if var_line_index >= len(lines):
        return None
    names = _split_idl_names(lines[var_line_index])

    return {
        "kind": "idl_plot_file_header",
        "format": "ascii",
        "location": str(path),
        "description": "SWMF IDL ASCII plot-file header detected.",
        "filetype": "ascii",
        "npictinfile": 1,
        "headline": lines[0],
        "it": it,
        "time": time_value,
        "gencoord": int(ndim_raw < 0),
        "ndim": ndim,
        "neqpar": neqpar,
        "nw": nw,
        "nx": nx,
        "coord_names": names[:ndim],
        "variable_names": names[ndim: ndim + nw],
        "parameter_names": names[ndim + nw: ndim + nw + neqpar],
    }


def _inspect_idl_plot_result(path: Path) -> tuple[str, list[dict[str, Any]]] | None:
    header = _parse_idl_binary_plot_header(path)
    if header is None:
        header = _parse_idl_ascii_plot_header(path)
    if header is None:
        return None

    variables = ", ".join(header.get("variable_names", [])[:12]) or "unknown"
    summary = (
        f"SWMF IDL plot file '{path.name}': {header['filetype']}, "
        f"ndim={header['ndim']}, nw={header['nw']}, variables: {variables}."
    )
    return summary, [header]

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

    if suffix in _IDL_PLOT_EXTENSIONS:
        idl_result = _inspect_idl_plot_result(p)
        if idl_result is not None:
            return idl_result

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
    - param: structure + session timeline + control settings + #SAVEPLOT extraction
    - xml: command listing from PARAM.XML parser + command search
    - run_dir: artifact presence + PARAM.in summary + log discovery + job scripts + output subdirs
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

    if resolved_type in {"log", "runlog"}:
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
        "runlog": [
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
            "'build_output', 'result'. 'runlog' is accepted as a log alias. "
            "Use for debugging log files, inspecting PARAM.in structure, validating "
            "run directories, or examining build output. Start debugging tasks here "
            "before calling get_evidence. "
            "Specialized inspectors: log detects first error, stacktrace, components, "
            "simulation time; param extracts sessions, component map, includes, external "
            "refs, command timeline, control settings, and #SAVEPLOT blocks; xml lists "
            "commands from PARAM.XML; run_dir checks artifact presence (SWMF.SUCCESS/DONE), "
            "summarizes PARAM.in intent, discovers logs with first-error, summarizes "
            "component output artifacts compactly, and finds job scripts; build_output checks SWMF root markers or compile/linker errors; "
            "result detects binary vs text format and previews structured SWMF output headers."
        )
    )(inspect_artifact)
