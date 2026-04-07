from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..core.common import resolve_run_dir
from ..core.swmf_root import resolve_swmf_root


_DOMAIN_UNKNOWN = "unknown"
_DOMAIN_TESTPARAM = "testparam"
_DOMAIN_BUILD = "build_compile"
_DOMAIN_RUNTIME = "runtime_log"
_DOMAIN_RESTART = "restart"
_DOMAIN_MPI = "mpi_scheduler"

_DOMAIN_ORDER = [
    _DOMAIN_TESTPARAM,
    _DOMAIN_BUILD,
    _DOMAIN_RUNTIME,
    _DOMAIN_RESTART,
    _DOMAIN_MPI,
]

_SOURCE_HINT_ALIASES = {
    "": _DOMAIN_UNKNOWN,
    "auto": _DOMAIN_UNKNOWN,
    "unknown": _DOMAIN_UNKNOWN,
    "testparam": _DOMAIN_TESTPARAM,
    "param": _DOMAIN_TESTPARAM,
    "param_validation": _DOMAIN_TESTPARAM,
    "build": _DOMAIN_BUILD,
    "compile": _DOMAIN_BUILD,
    "compiler": _DOMAIN_BUILD,
    "make": _DOMAIN_BUILD,
    "runtime": _DOMAIN_RUNTIME,
    "runtime_log": _DOMAIN_RUNTIME,
    "log": _DOMAIN_RUNTIME,
    "restart": _DOMAIN_RESTART,
    "restart_pl": _DOMAIN_RESTART,
    "mpi": _DOMAIN_MPI,
    "scheduler": _DOMAIN_MPI,
    "slurm": _DOMAIN_MPI,
    "pbs": _DOMAIN_MPI,
}

_DOMAIN_KEYWORDS = {
    _DOMAIN_TESTPARAM: ["testparam", "param.in", "config.pl", "component version", "param.xml"],
    _DOMAIN_BUILD: ["make", "compiler", "ifort", "gfortran", "undefined reference", "module file"],
    _DOMAIN_RUNTIME: ["cfl", "nan", "segmentation fault", "runtime", "iteration", "stop"],
    _DOMAIN_RESTART: ["restart", "restart.in", "restart.pl", "background", "snapshot"],
    _DOMAIN_MPI: ["mpi", "mpi_abort", "rank", "sbatch", "qsub", "slurm", "pbs"],
}

# Signature rules are intentionally concise and domain-focused.
_DOMAIN_SIGNATURES: dict[str, list[dict[str, Any]]] = {
    _DOMAIN_TESTPARAM: [
        {
            "code": "TESTPARAM_LAUNCH_CONTEXT_INVALID",
            "patterns": [r"testparam[_ ]error", r"could not find\s+config\.pl", r"cannot find\s+config\.pl"],
            "message": "TestParam was likely run outside SWMF root or without a valid SWMF launch context.",
            "solutions": [
                "Run from SWMF root: cd SWMF_ROOT && ./Scripts/TestParam.pl -n=<nproc> /path/to/PARAM.in",
                "Verify SWMF_ROOT contains Config.pl, PARAM.XML, and Scripts/TestParam.pl.",
            ],
            "confidence": 0.97,
            "authority": "derived",
        },
        {
            "code": "TESTPARAM_MISSING_COMPONENT_VERSIONS",
            "patterns": [r"missing compiled component", r"component version", r"not compiled"],
            "message": "PARAM likely references components that were not compiled into this SWMF build.",
            "solutions": [
                "Reconfigure build with component versions via Config.pl -v=Empty,<versions...>.",
                "Rebuild with make clean && make -j, then rerun TestParam.",
            ],
            "confidence": 0.9,
            "authority": "derived",
        },
        {
            "code": "TESTPARAM_VALIDATION_FAILED",
            "patterns": [r"testparam.*failed", r"validation error", r"invalid\s+param"],
            "message": "TestParam reported PARAM validation issues.",
            "solutions": [
                "Inspect the failing command block in PARAM.in and compare with PARAM.XML definitions.",
                "Run swmf_diagnose_param for integrated lightweight plus authoritative diagnosis.",
            ],
            "confidence": 0.78,
            "authority": "derived",
        },
    ],
    _DOMAIN_BUILD: [
        {
            "code": "FORTRAN_MODULE_NOT_FOUND",
            "patterns": [r"cannot open module file", r"fatal error:.*module file"],
            "message": "A required Fortran module was not built or include paths are inconsistent.",
            "solutions": [
                "Run make clean && make -j to force correct module rebuild order.",
                "Confirm compiler and MPI wrappers are consistent with your SWMF build configuration.",
            ],
            "confidence": 0.94,
            "authority": "derived",
        },
        {
            "code": "LINKER_UNDEFINED_REFERENCE",
            "patterns": [r"undefined reference to", r"ld: symbol\(s\) not found"],
            "message": "Link stage failed due to missing objects or incompatible component selections.",
            "solutions": [
                "Verify component versions selected in Config.pl match required components in PARAM.",
                "Rebuild from clean state and ensure external libraries are available.",
            ],
            "confidence": 0.9,
            "authority": "derived",
        },
        {
            "code": "BUILD_TARGET_MISSING",
            "patterns": [r"no rule to make target", r"missing separator", r"stop\.?$"],
            "message": "Build input or Makefile dependencies are incomplete or inconsistent.",
            "solutions": [
                "Check file paths and generated targets referenced by make.",
                "Regenerate setup with Config.pl and rerun make.",
            ],
            "confidence": 0.75,
            "authority": "derived",
        },
        {
            "code": "COMPILER_NOT_FOUND",
            "patterns": [r"command not found: .*ifort", r"command not found: .*gfortran", r"command not found: .*mpif90"],
            "message": "Compiler or MPI wrapper is unavailable in the active shell environment.",
            "solutions": [
                "Load compiler/MPI modules expected by your site.",
                "Ensure the compiler chosen in Config.pl matches available executables.",
            ],
            "confidence": 0.93,
            "authority": "derived",
        },
    ],
    _DOMAIN_RUNTIME: [
        {
            "code": "RUNTIME_STABILITY_CFL",
            "patterns": [r"cfl", r"time step.*too large", r"dt.*too large"],
            "message": "Runtime appears unstable due to CFL or timestep constraints.",
            "solutions": [
                "Reduce timestep controls in PARAM and retry.",
                "Check boundary conditions and initial state consistency.",
            ],
            "confidence": 0.88,
            "authority": "derived",
        },
        {
            "code": "RUNTIME_NUMERICAL_FAILURE",
            "patterns": [r"\bnan\b", r"floating point exception", r"segmentation fault", r"sigsegv"],
            "message": "Runtime encountered numerical blow-up or memory access failure.",
            "solutions": [
                "Inspect the first failing iteration block and recently changed parameters.",
                "Revert to a known-good PARAM baseline and reintroduce changes incrementally.",
            ],
            "confidence": 0.84,
            "authority": "derived",
        },
    ],
    _DOMAIN_RESTART: [
        {
            "code": "RESTART_INPUT_MISSING",
            "patterns": [r"restart\.in", r"cannot open.*restart", r"restart file.*not found"],
            "message": "Restart input files are missing or paths in restart configuration are invalid.",
            "solutions": [
                "Verify restart tree location and RESTART.in paths.",
                "Use Restart.pl planning first, then run check mode before linking.",
            ],
            "confidence": 0.9,
            "authority": "derived",
        },
        {
            "code": "RESTART_SCRIPT_USAGE_ERROR",
            "patterns": [r"restart\.pl", r"unknown option", r"usage:.*restart"],
            "message": "Restart.pl command usage or option combination appears invalid.",
            "solutions": [
                "Generate commands with swmf_plan_restart_from_background to avoid option mismatches.",
                "Run check mode first before link/validate/submit steps.",
            ],
            "confidence": 0.82,
            "authority": "derived",
        },
    ],
    _DOMAIN_MPI: [
        {
            "code": "MPI_ABORTED",
            "patterns": [r"mpi_abort", r"rank\s+\d+", r"application called mpi_abort"],
            "message": "MPI layer reported fatal abort; inspect first rank that failed.",
            "solutions": [
                "Find earliest rank-specific error line preceding MPI_ABORT.",
                "Verify nproc/component layout consistency with job script and PARAM.",
            ],
            "confidence": 0.86,
            "authority": "derived",
        },
        {
            "code": "SCHEDULER_SUBMIT_FAILED",
            "patterns": [r"sbatch: error", r"qsub: command not found", r"invalid account", r"requested node configuration is not available"],
            "message": "Scheduler submission or allocation request failed.",
            "solutions": [
                "Validate account/partition/queue fields in the job script.",
                "Infer and align MPI layout with swmf_infer_job_layout before submit.",
            ],
            "confidence": 0.9,
            "authority": "derived",
        },
    ],
}


def _normalize_source_hint(source_hint: str | None) -> str:
    if source_hint is None:
        return _DOMAIN_UNKNOWN
    key = source_hint.strip().lower()
    return _SOURCE_HINT_ALIASES.get(key, _DOMAIN_UNKNOWN)


def _score_domain(text_lower: str, domain: str, match_count: int) -> int:
    keywords = _DOMAIN_KEYWORDS.get(domain, [])
    keyword_hits = sum(1 for kw in keywords if kw in text_lower)
    return keyword_hits + (match_count * 4)


def _extract_evidence_lines(text: str, pattern: str, max_lines: int = 2) -> list[str]:
    lines = text.splitlines()
    evid: list[str] = []
    try:
        regex = re.compile(pattern, flags=re.IGNORECASE)
    except re.error:
        return evid

    for line in lines:
        if regex.search(line):
            evid.append(line.strip())
            if len(evid) >= max_lines:
                break
    return evid


def _match_domain(text: str, domain: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for signature in _DOMAIN_SIGNATURES.get(domain, []):
        matched_pattern: str | None = None
        for pattern in signature.get("patterns", []):
            if re.search(pattern, text, flags=re.IGNORECASE):
                matched_pattern = pattern
                break
        if matched_pattern is None:
            continue

        matches.append(
            {
                "code": signature["code"],
                "message": signature["message"],
                "confidence": signature.get("confidence", 0.6),
                "authority": signature.get("authority", "derived"),
                "likely_domain": domain,
                "evidence_lines": _extract_evidence_lines(text, matched_pattern),
                "possible_solutions": signature.get("solutions", []),
            }
        )
    return matches


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = item.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _recommended_tools(detected_domain: str, has_param: bool, has_root: bool) -> list[str]:
    base: list[str] = []
    if detected_domain == _DOMAIN_TESTPARAM:
        base.extend(["swmf_run_testparam", "swmf_diagnose_param", "swmf_prepare_component_config"])
    elif detected_domain == _DOMAIN_BUILD:
        base.extend(["swmf_prepare_build", "swmf_explain_component_config_fix"])
    elif detected_domain == _DOMAIN_RUNTIME:
        base.extend(["swmf_prepare_run", "swmf_plan_restart_from_background"])
    elif detected_domain == _DOMAIN_RESTART:
        base.extend(["swmf_plan_restart_from_background", "swmf_run_testparam"])
    elif detected_domain == _DOMAIN_MPI:
        base.extend(["swmf_infer_job_layout", "swmf_prepare_run"])
    else:
        base.extend(["swmf_diagnose_param", "swmf_trace_param_command"])

    if has_param and "swmf_diagnose_param" not in base:
        base.append("swmf_diagnose_param")
    if has_root and "swmf_run_testparam" not in base:
        base.append("swmf_run_testparam")
    return _dedupe_preserve_order(base)


def diagnose_error(
    error_text: str,
    source_hint: str | None = None,
    param_path: str | None = None,
    run_dir: str | None = None,
    log_path: str | None = None,
    swmf_root_resolved: str | None = None,
) -> dict[str, Any]:
    text = (error_text or "").strip()
    if not text:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "ERROR_TEXT_MISSING",
            "message": "Provide error_text with at least one error line.",
            "how_to_fix": [
                "Pass the key error line from TestParam/build/runtime logs.",
                "Optionally pass source_hint to improve domain routing.",
            ],
            "authority": "derived",
            "source_kind": "diagnostic_pipeline",
            "source_paths": [],
        }

    hint = _normalize_source_hint(source_hint)
    all_matches: dict[str, list[dict[str, Any]]] = {}
    domain_scores: dict[str, int] = {}
    text_lower = text.lower()

    for domain in _DOMAIN_ORDER:
        matches = _match_domain(text=text, domain=domain)
        all_matches[domain] = matches
        domain_scores[domain] = _score_domain(text_lower=text_lower, domain=domain, match_count=len(matches))

    if hint != _DOMAIN_UNKNOWN:
        detected_domain = hint
        routing_reason = "source_hint"
    else:
        scored = sorted(domain_scores.items(), key=lambda item: item[1], reverse=True)
        top_domain, top_score = scored[0] if scored else (_DOMAIN_UNKNOWN, 0)
        detected_domain = top_domain if top_score > 0 else _DOMAIN_UNKNOWN
        routing_reason = "signature_and_keyword_routing"

    root_causes = all_matches.get(detected_domain, [])
    if not root_causes:
        fallback: list[dict[str, Any]] = []
        for domain in _DOMAIN_ORDER:
            fallback.extend(all_matches.get(domain, []))
        fallback.sort(key=lambda item: float(item.get("confidence", 0.0)), reverse=True)
        root_causes = fallback[:3]

    if not root_causes:
        root_causes = [
            {
                "code": "UNCLASSIFIED_SWMF_ERROR",
                "message": "No specific SWMF diagnostic signature matched this error text.",
                "confidence": 0.35,
                "authority": "heuristic",
                "likely_domain": _DOMAIN_UNKNOWN,
                "evidence_lines": [line.strip() for line in text.splitlines()[:2] if line.strip()],
                "possible_solutions": [
                    "Provide 10-30 surrounding log lines around the first failure.",
                    "Set source_hint to narrow domain, e.g. testparam, build, runtime_log, restart, mpi.",
                ],
            }
        ]

    possible_solutions = _dedupe_preserve_order(
        [
            solution
            for cause in root_causes
            for solution in cause.get("possible_solutions", [])
            if isinstance(solution, str)
        ]
    )

    summary = root_causes[0]["message"]
    source_paths: list[str] = []
    if param_path:
        source_paths.append(str(Path(param_path).expanduser()))
    if log_path:
        source_paths.append(str(Path(log_path).expanduser()))

    payload = {
        "ok": True,
        "summary": summary,
        "detected_domain": detected_domain,
        "routing_reason": routing_reason,
        "source_hint_normalized": hint,
        "domain_scores": domain_scores,
        "root_causes": root_causes,
        "possible_solutions": possible_solutions,
        "recommended_next_tools": _recommended_tools(
            detected_domain=detected_domain,
            has_param=bool(param_path),
            has_root=bool(swmf_root_resolved),
        ),
        "input_context": {
            "param_path": param_path,
            "run_dir": run_dir,
            "log_path": log_path,
        },
        "authority": "derived",
        "source_kind": "diagnostic_pipeline",
        "source_paths": _dedupe_preserve_order(source_paths),
        "swmf_root_resolved": swmf_root_resolved,
    }

    return payload


def swmf_diagnose_error(
    error_text: str,
    source_hint: str | None = None,
    param_path: str | None = None,
    run_dir: str | None = None,
    log_path: str | None = None,
    swmf_root: str | None = None,
) -> dict[str, Any]:
    resolved_run_dir = str(resolve_run_dir(run_dir))
    root_resolution = resolve_swmf_root(swmf_root=swmf_root, run_dir=run_dir)

    payload = diagnose_error(
        error_text=error_text,
        source_hint=source_hint,
        param_path=param_path,
        run_dir=resolved_run_dir,
        log_path=log_path,
        swmf_root_resolved=root_resolution.swmf_root_resolved,
    )
    payload.setdefault("resolution_notes", root_resolution.resolution_notes)
    payload.setdefault("run_dir_resolved", resolved_run_dir)
    return payload


def register(app: Any) -> None:
    app.tool(
        description=(
            "Diagnose SWMF errors from free-form error text (TestParam, compile/build, runtime logs, restart, "
            "MPI/scheduler) and return ranked explanations with possible solutions."
        )
    )(swmf_diagnose_error)
