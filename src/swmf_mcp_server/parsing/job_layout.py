from __future__ import annotations

import shlex
from pathlib import Path
from typing import Any


def safe_parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if value and value.lstrip("-").isdigit():
        return int(value)
    return None


def parse_slurm_directives(script_text: str) -> dict[str, Any]:
    nodes: int | None = None
    tasks_per_node: int | None = None
    ntasks: int | None = None

    for line in script_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#SBATCH"):
            continue
        body = stripped[len("#SBATCH") :].strip()
        tokens = shlex.split(body)

        i = 0
        while i < len(tokens):
            token = tokens[i]
            next_token = tokens[i + 1] if i + 1 < len(tokens) else None

            if token == "-N" and next_token is not None:
                nodes = safe_parse_int(next_token) or nodes
                i += 2
                continue
            if token.startswith("--nodes="):
                nodes = safe_parse_int(token.split("=", 1)[1]) or nodes
                i += 1
                continue
            if token == "--nodes" and next_token is not None:
                nodes = safe_parse_int(next_token) or nodes
                i += 2
                continue
            if token.startswith("--tasks-per-node="):
                tasks_per_node = safe_parse_int(token.split("=", 1)[1]) or tasks_per_node
                i += 1
                continue
            if token == "--tasks-per-node" and next_token is not None:
                tasks_per_node = safe_parse_int(next_token) or tasks_per_node
                i += 2
                continue
            if token == "-n" and next_token is not None:
                ntasks = safe_parse_int(next_token) or ntasks
                i += 2
                continue
            if token.startswith("--ntasks="):
                ntasks = safe_parse_int(token.split("=", 1)[1]) or ntasks
                i += 1
                continue
            if token == "--ntasks" and next_token is not None:
                ntasks = safe_parse_int(next_token) or ntasks
                i += 2
                continue

            i += 1

    ntasks_total = ntasks
    if ntasks_total is None and nodes is not None and tasks_per_node is not None:
        ntasks_total = nodes * tasks_per_node

    return {"nodes": nodes, "tasks_per_node": tasks_per_node, "ntasks_total": ntasks_total}


def parse_ibrun_launches(script_text: str) -> list[dict[str, Any]]:
    launches: list[dict[str, Any]] = []

    for line in script_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "ibrun" not in stripped:
            continue
        try:
            tokens = shlex.split(stripped)
        except ValueError:
            launches.append({"raw": stripped, "launcher": "ibrun", "nproc": None, "rank_offset": None, "executable": None})
            continue

        if "ibrun" not in tokens:
            continue
        i = tokens.index("ibrun") + 1
        nproc: int | None = None
        rank_offset: int | None = None
        executable: str | None = None

        while i < len(tokens):
            token = tokens[i]
            next_token = tokens[i + 1] if i + 1 < len(tokens) else None
            if token == "-n" and next_token is not None:
                nproc = safe_parse_int(next_token)
                i += 2
                continue
            if token == "-o" and next_token is not None:
                rank_offset = safe_parse_int(next_token)
                i += 2
                continue
            if token.startswith("-"):
                i += 1
                continue
            executable = token
            break

        launches.append(
            {
                "raw": stripped,
                "launcher": "ibrun",
                "nproc": nproc,
                "rank_offset": rank_offset,
                "executable": executable,
            }
        )

    return launches


def machine_hint_from_job_script_name(path: Path) -> str | None:
    name = path.name
    if name.startswith("job.") and len(name.split(".", 1)) == 2:
        return name.split(".", 1)[1]
    stem = path.stem
    if stem and stem.lower() not in {"job", "run", "submit"}:
        return stem
    return None


def infer_job_layout_from_script(script_path: Path, script_text: str) -> dict[str, Any]:
    warnings: list[str] = []
    directives = parse_slurm_directives(script_text)
    launches = parse_ibrun_launches(script_text)

    swmf_launch = next((item for item in launches if (item.get("executable") or "").endswith("SWMF.exe")), None)
    if swmf_launch is None:
        for item in launches:
            exe = item.get("executable") or ""
            if "SWMF.exe" in exe:
                swmf_launch = item
                break

    postproc_launch = next((item for item in launches if "PostProc.pl" in (item.get("executable") or "")), None)
    postproc_detected = postproc_launch is not None

    nodes = directives["nodes"]
    tasks_per_node = directives["tasks_per_node"]
    ntasks_total = directives["ntasks_total"]

    swmf_nproc: int | None = None
    swmf_rank_offset: int | None = None
    swmf_executable: str | None = None

    if swmf_launch is not None:
        swmf_executable = swmf_launch.get("executable")
        swmf_rank_offset = swmf_launch.get("rank_offset")
        swmf_nproc = swmf_launch.get("nproc")

    if swmf_nproc is None and nodes is not None and tasks_per_node is not None:
        if postproc_detected and nodes > 1:
            swmf_nproc = (nodes - 1) * tasks_per_node
            if swmf_rank_offset is None:
                swmf_rank_offset = tasks_per_node
        elif ntasks_total is not None and swmf_rank_offset is not None:
            swmf_nproc = max(ntasks_total - swmf_rank_offset, 0)

    if swmf_nproc is None:
        warnings.append("Could not confidently infer SWMF MPI rank count from the job script.")

    return {
        "job_script_resolved": str(script_path),
        "scheduler": "slurm" if "#SBATCH" in script_text else "unknown",
        "machine_hint": machine_hint_from_job_script_name(script_path),
        "nodes": nodes,
        "tasks_per_node": tasks_per_node,
        "ntasks_total": ntasks_total,
        "swmf_executable": swmf_executable,
        "swmf_rank_offset": swmf_rank_offset,
        "swmf_nproc": swmf_nproc,
        "postproc_detected": postproc_detected,
        "launch_summary": launches,
        "warnings": warnings,
    }


def find_likely_job_scripts(run_dir: Path) -> list[Path]:
    patterns = ["job.*", "*.slurm", "*.sbatch"]
    matches: set[Path] = set()

    # Fast path: direct files in run_dir are the common case.
    for pattern in patterns:
        for path in run_dir.glob(pattern):
            if path.is_file():
                matches.add(path.resolve())

    if matches:
        return sorted(matches)

    # Shallow search first, avoids traversing huge run trees.
    for pattern in patterns:
        for path in run_dir.rglob(pattern):
            if path.is_file():
                try:
                    rel_parts = path.resolve().relative_to(run_dir.resolve()).parts
                except ValueError:
                    rel_parts = ()
                if len(rel_parts) <= 4:
                    matches.add(path.resolve())

    if matches:
        return sorted(matches)

    # Bounded fallback: sample limited files for #SBATCH markers.
    scanned = 0
    scan_limit = 300
    for path in run_dir.rglob("*"):
        if scanned >= scan_limit:
            break
        if not path.is_file():
            continue
        scanned += 1
        try:
            head = path.read_text(encoding="utf-8", errors="ignore")[:8192]
        except OSError:
            continue
        if "#SBATCH" in head:
            matches.add(path.resolve())

    if matches:
        return sorted(matches)

    # Last resort: unbounded pattern search.
    for pattern in patterns:
        for path in run_dir.rglob(pattern):
            if path.is_file():
                matches.add(path.resolve())

    return sorted(matches)
