from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path

from ..parsing.component_map import COMPONENTMAP_ROW
from ..parsing.job_layout import find_likely_job_scripts, infer_job_layout_from_script
from .common import resolve_run_dir


def infer_job_layout(job_script_path: str | None = None, run_dir: str | None = None) -> dict:
    resolved_run_dir = resolve_run_dir(run_dir)

    if job_script_path:
        script_path = Path(job_script_path).expanduser()
        if not script_path.is_absolute():
            script_path = resolved_run_dir / script_path
        script_path = script_path.resolve()
        if not script_path.is_file():
            return {
                "ok": False,
                "hard_error": True,
                "error_code": "JOB_SCRIPT_NOT_FOUND",
                "message": f"Job script does not exist: {script_path}",
            }
    else:
        candidates = find_likely_job_scripts(resolved_run_dir)
        if not candidates:
            return {
                "ok": False,
                "hard_error": True,
                "error_code": "JOB_SCRIPT_NOT_FOUND",
                "message": f"No likely job script found under run_dir: {resolved_run_dir}",
            }
        script_path = candidates[0]

    try:
        script_text = script_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return {
            "ok": False,
            "hard_error": True,
            "error_code": "JOB_SCRIPT_READ_FAILED",
            "message": f"Could not read job script: {exc}",
        }

    payload = infer_job_layout_from_script(script_path=script_path, script_text=script_text)
    payload.update(
        {
            "ok": True,
            "run_dir_resolved": str(resolved_run_dir),
            "authority": "derived",
            "source_kind": "script",
            "source_paths": [str(script_path)],
        }
    )
    return payload


def prepare_run(
    component_map_text: str,
    nproc: int | None = None,
    description: str = "Prototype SWMF run",
    time_accurate: bool = True,
    stop_value: str = "3600.0",
    include_restart: bool = False,
    run_name: str = "run_demo",
    run_dir: str | None = None,
    job_script_path: str | None = None,
) -> dict:
    map_rows: list[str] = []
    map_errors: list[str] = []

    for raw in component_map_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if not COMPONENTMAP_ROW.match(line):
            map_errors.append(f"Could not parse component map row: {line}")
        else:
            map_rows.append(line)

    if not map_rows:
        return {"ok": False, "message": "Provide at least one valid component map row.", "errors": map_errors}
    if map_errors:
        return {"ok": False, "message": "Component map rows contain parse errors.", "errors": map_errors}

    nproc_source = "explicit"
    inferred_layout: dict | None = None
    if nproc is None:
        layout_result = infer_job_layout(job_script_path=job_script_path, run_dir=run_dir)
        if layout_result.get("ok") and layout_result.get("swmf_nproc") is not None:
            nproc = int(layout_result["swmf_nproc"])
            nproc_source = "job_script_inference"
            inferred_layout = layout_result
        else:
            return {
                "ok": False,
                "hard_error": True,
                "error_code": "NPROC_INFERENCE_FAILED",
                "message": "nproc was not provided and could not be inferred from a job script.",
                "how_to_fix": [
                    "Provide nproc explicitly.",
                    "Or provide run_dir/job_script_path and call swmf_infer_job_layout.",
                ],
                "job_layout": layout_result,
            }

    assert nproc is not None
    stop_block = (
        "#STOP\n" + (f"{stop_value} tSimulationMax\n-1 MaxIteration" if time_accurate else f"-1.0 tSimulationMax\n{stop_value} MaxIteration")
    )
    include_block = "#INCLUDE\nRESTART.in\n\n" if include_restart else ""
    time_flag = "T" if time_accurate else "F"

    param_in = (
        "#DESCRIPTION\n"
        f"{description}\n\n"
        f"{include_block}"
        "#TIMEACCURATE\n"
        f"{time_flag} DoTimeAccurate\n\n"
        "ID Proc0 ProcEnd Stride nThread\n"
        "#COMPONENTMAP\n"
        + "\n".join(map_rows)
        + "\n\n"
        + stop_block
        + "\n\n#END\n"
    )

    return {
        "ok": True,
        "authority": "heuristic",
        "source_kind": "curated",
        "source_paths": [],
        "nproc": nproc,
        "nproc_source": nproc_source,
        "job_layout": inferred_layout,
        "run_name": run_name,
        "time_accurate": time_accurate,
        "starter_param_in": param_in,
        "suggested_commands": [
            "make rundir",
            f"mv run {run_name}",
            f"Scripts/TestParam.pl -n={nproc} {run_name}/PARAM.in",
            f"cd {run_name}",
        ],
        "requires_manual_submission": True,
        "auto_submit_permitted": False,
        "suggested_manual_submission": [
            "Edit your scheduler job script (for example job.frontera) for this run directory.",
            "Ensure the script uses SWMF.exe and the intended MPI layout.",
            "Submit manually (example): sbatch job.frontera",
        ],
    }


def _extract_candidate_setup_command_lines(param_text: str) -> list[str]:
    candidates: list[str] = []
    for raw_line in param_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        cleaned = re.sub(r"^\s*(?:[#;!]+|//|\*|-)+\s*", "", raw_line).strip()
        if not cleaned:
            continue

        match = re.search(r"((?:\./)?Config\.pl\s+.+)$", cleaned)
        if match:
            candidates.append(match.group(1).strip())
            continue

        if re.match(r"^make\s+", cleaned):
            candidates.append(cleaned)

    return candidates


def _parse_setup_command(command: str) -> tuple[dict | None, str | None]:
    forbidden_chars = {"|", "&", ">", "<", "`"}
    if any(ch in command for ch in forbidden_chars):
        return None, "Command contains forbidden shell control characters."

    try:
        argv = shlex.split(command, posix=True)
    except ValueError as exc:
        return None, f"Failed to parse command: {exc}"

    if not argv:
        return None, "Empty command."

    program = argv[0]
    if program in {"Config.pl", "./Config.pl"}:
        normalized_argv = ["./Config.pl"] + argv[1:]
        return {"kind": "config", "program": "./Config.pl", "argv": normalized_argv, "normalized": " ".join(normalized_argv)}, None

    if program == "make":
        if argv == ["make", "clean"]:
            return {"kind": "make-clean", "program": "make", "argv": argv, "normalized": "make clean"}, None
        if len(argv) == 2 and re.match(r"^-j\d*$", argv[1]):
            normalized = argv[1] if argv[1] != "-j" else "-j"
            return {"kind": "make-parallel", "program": "make", "argv": ["make", normalized], "normalized": f"make {normalized}"}, None
        return None, "Only 'make clean' and 'make -j' (or -jN) are allowed."

    return None, "Command is not in the allowed SWMF setup whitelist."


def detect_setup_commands(param_text: str) -> dict:
    parsed_commands: list[dict] = []
    rejected: list[dict[str, str]] = []
    seen: set[str] = set()

    for candidate in _extract_candidate_setup_command_lines(param_text):
        parsed, error = _parse_setup_command(candidate)
        if parsed is None:
            rejected.append({"command": candidate, "reason": error or "Rejected."})
            continue
        normalized = parsed["normalized"]
        if normalized in seen:
            continue
        seen.add(normalized)
        parsed_commands.append(parsed)

    return {
        "ok": True,
        "found": len(parsed_commands) > 0,
        "commands": [entry["normalized"] for entry in parsed_commands],
        "commands_structured": parsed_commands,
        "rejected_candidates": rejected,
        "warnings": [item["reason"] for item in rejected],
        "authority": "derived",
        "source_kind": "lightweight_parser",
        "source_paths": [],
    }


def apply_setup_commands(
    swmf_root: str,
    commands: list[str],
    continue_on_error: bool = False,
) -> dict:
    execution_results: list[dict] = []
    all_ok = True

    for command in commands:
        parsed, parse_error = _parse_setup_command(command)
        if parsed is None:
            all_ok = False
            execution_results.append({"ok": False, "command": command, "error": parse_error or "Rejected command.", "cwd": swmf_root})
            if not continue_on_error:
                break
            continue

        argv = parsed["argv"]
        try:
            proc = subprocess.run(
                argv,
                cwd=swmf_root,
                capture_output=True,
                text=True,
                check=False,
                shell=False,
            )
        except OSError as exc:
            all_ok = False
            execution_results.append({"ok": False, "command": parsed["normalized"], "argv": argv, "cwd": swmf_root, "error": f"Execution failed: {exc}"})
            if not continue_on_error:
                break
            continue

        cmd_ok = proc.returncode == 0
        all_ok = all_ok and cmd_ok
        execution_results.append(
            {
                "ok": cmd_ok,
                "command": parsed["normalized"],
                "argv": argv,
                "cwd": swmf_root,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        )
        if (not cmd_ok) and (not continue_on_error):
            break

    return {
        "ok": all_ok,
        "continue_on_error": continue_on_error,
        "results": execution_results,
        "authority": "authoritative",
        "source_kind": "script",
        "source_paths": [str(Path(swmf_root) / "Config.pl")],
    }
