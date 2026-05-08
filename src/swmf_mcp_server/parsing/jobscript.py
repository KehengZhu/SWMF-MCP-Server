"""Deterministic parser for SWMF cluster job scripts.

Used by `inspect_artifact(artifact_type="jobscript")`. Produces typed, evidence-only
fields: scheduler, directives, nodes/tasks, walltime, executable invocations,
postproc/FDIPS/HARMONICS detection, and substitution-token surfacing. No advice fields.
"""
from __future__ import annotations

import re
import shlex
from pathlib import Path
from typing import Any

from .job_layout import safe_parse_int


_SBATCH_RE = re.compile(r"^\s*#SBATCH\b(.*)$")
_PBS_RE = re.compile(r"^\s*#PBS\b(.*)$")
_SUBSTITUTION_RE = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}|<([A-Z0-9_]+)>")
_PLACEHOLDER_NAME_RE = re.compile(r"\b(amap\d+|jobname|JOBNAME|RUNTIME|ALLOCATION|allocation)\b")
_LAUNCHER_TOKENS = ("ibrun", "mpirun", "mpiexec", "srun", "aprun")
_EXECUTABLE_SUFFIXES = (".exe", ".pl", ".py", ".sh")


def _classify_scheduler(text: str) -> str:
    if "#SBATCH" in text:
        return "slurm"
    if "#PBS" in text:
        return "pbs"
    if any(tok in text for tok in _LAUNCHER_TOKENS) or "#!/" in text.splitlines()[0:1] and False:
        return "local"
    # Fallback: bash with explicit launcher → local
    head = text.lstrip()
    if head.startswith("#!"):
        if any(launcher in text for launcher in _LAUNCHER_TOKENS):
            return "local"
    return "unknown"


def _parse_directives_slurm(text: str) -> list[dict[str, Any]]:
    directives: list[dict[str, Any]] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        match = _SBATCH_RE.match(raw)
        if not match:
            continue
        body = match.group(1).strip()
        try:
            tokens = shlex.split(body)
        except ValueError:
            tokens = body.split()
        if not tokens:
            continue
        # Capture canonical key/value pairs without prescribing semantics.
        entry: dict[str, Any] = {"raw": raw.strip(), "line": line_number}
        token = tokens[0]
        if token.startswith("--") and "=" in token:
            key, _, value = token[2:].partition("=")
            entry["key"] = key
            entry["value"] = value
        elif token.startswith("--"):
            entry["key"] = token[2:]
            entry["value"] = tokens[1] if len(tokens) > 1 else None
        elif token.startswith("-") and len(token) >= 2:
            entry["key"] = token.lstrip("-")
            entry["value"] = tokens[1] if len(tokens) > 1 else None
        else:
            entry["key"] = token
            entry["value"] = " ".join(tokens[1:]) or None
        directives.append(entry)
    return directives


def _parse_directives_pbs(text: str) -> list[dict[str, Any]]:
    directives: list[dict[str, Any]] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        match = _PBS_RE.match(raw)
        if not match:
            continue
        body = match.group(1).strip()
        tokens = body.split(maxsplit=1)
        if not tokens:
            continue
        entry: dict[str, Any] = {
            "raw": raw.strip(),
            "line": line_number,
            "key": tokens[0].lstrip("-"),
            "value": tokens[1] if len(tokens) > 1 else None,
        }
        directives.append(entry)
    return directives


def _slurm_dimensions(directives: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: int | None = None
    tasks_per_node: int | None = None
    ntasks: int | None = None
    walltime: str | None = None
    for d in directives:
        key = (d.get("key") or "").lower()
        value = d.get("value")
        if key in {"n", "nodes"}:
            parsed = safe_parse_int(str(value)) if value is not None else None
            if parsed is not None:
                nodes = parsed
        elif key == "tasks-per-node":
            parsed = safe_parse_int(str(value)) if value is not None else None
            if parsed is not None:
                tasks_per_node = parsed
        elif key in {"ntasks", "n-tasks"}:
            parsed = safe_parse_int(str(value)) if value is not None else None
            if parsed is not None:
                ntasks = parsed
        elif key == "t" or key == "time":
            if value:
                walltime = str(value).strip()
    total = ntasks
    if total is None and nodes is not None and tasks_per_node is not None:
        total = nodes * tasks_per_node
    return {
        "nodes": nodes,
        "tasks_per_node": tasks_per_node,
        "ntasks": ntasks,
        "total_ranks": total,
        "walltime": walltime,
    }


def _pbs_dimensions(directives: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: int | None = None
    tasks_per_node: int | None = None
    walltime: str | None = None
    select_re = re.compile(r"select=(\d+)(?::ncpus=(\d+))?")
    for d in directives:
        key = (d.get("key") or "").lower()
        value = d.get("value") or ""
        if key == "l":
            select_match = select_re.search(value)
            if select_match:
                parsed_nodes = safe_parse_int(select_match.group(1))
                if parsed_nodes is not None:
                    nodes = parsed_nodes
                if select_match.group(2):
                    parsed_tpn = safe_parse_int(select_match.group(2))
                    if parsed_tpn is not None:
                        tasks_per_node = parsed_tpn
            walltime_match = re.search(r"walltime=([0-9:]+)", value)
            if walltime_match:
                walltime = walltime_match.group(1)
    total = nodes * tasks_per_node if nodes is not None and tasks_per_node is not None else None
    return {
        "nodes": nodes,
        "tasks_per_node": tasks_per_node,
        "ntasks": None,
        "total_ranks": total,
        "walltime": walltime,
    }


def _parse_executable_invocations(text: str) -> list[dict[str, Any]]:
    """Return one entry per launcher-line, in script order."""
    invocations: list[dict[str, Any]] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Strip leading `cd ...; ` style prefixes by tokenizing.
        try:
            tokens = shlex.split(stripped, posix=True)
        except ValueError:
            tokens = stripped.split()
        if not tokens:
            continue
        launcher: str | None = None
        launcher_index: int | None = None
        for i, tok in enumerate(tokens):
            if tok in _LAUNCHER_TOKENS:
                launcher = tok
                launcher_index = i
                break
        if launcher is None:
            continue
        assert launcher_index is not None
        rest = tokens[launcher_index + 1 :]
        executable: str | None = None
        nproc: int | None = None
        rank_offset: int | None = None
        i = 0
        while i < len(rest):
            tok = rest[i]
            nxt = rest[i + 1] if i + 1 < len(rest) else None
            if tok in {"-n", "-np"} and nxt is not None:
                nproc = safe_parse_int(nxt) or nproc
                i += 2
                continue
            if tok == "-o" and nxt is not None:
                rank_offset = safe_parse_int(nxt) or rank_offset
                i += 2
                continue
            if tok.startswith("-"):
                i += 1
                continue
            if tok.startswith("./") or tok.startswith("/") or tok.endswith(_EXECUTABLE_SUFFIXES):
                executable = tok
                break
            i += 1
        if executable is None:
            for tok in rest:
                if tok.startswith("./") or tok.startswith("/") or tok.endswith(_EXECUTABLE_SUFFIXES):
                    executable = tok
                    break
        invocations.append(
            {
                "line": line_number,
                "launcher": launcher,
                "executable": executable,
                "nproc": nproc,
                "rank_offset": rank_offset,
                "raw": stripped,
            }
        )
    return invocations


def _detect_substitution_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    seen: set[str] = set()
    for match in _SUBSTITUTION_RE.finditer(text):
        token = match.group(1) or match.group(2)
        if token and token not in seen:
            seen.add(token)
            tokens.append(token)
    for match in _PLACEHOLDER_NAME_RE.finditer(text):
        token = match.group(1)
        if token and token not in seen:
            seen.add(token)
            tokens.append(token)
    return tokens


def parse_jobscript_text(script_text: str, script_path: str | None = None) -> dict[str, Any]:
    """Pure parser for a job-script string. Returns typed evidence fields."""
    scheduler = _classify_scheduler(script_text)

    if scheduler == "slurm":
        directives = _parse_directives_slurm(script_text)
        dims = _slurm_dimensions(directives)
    elif scheduler == "pbs":
        directives = _parse_directives_pbs(script_text)
        dims = _pbs_dimensions(directives)
    else:
        directives = []
        dims = {
            "nodes": None,
            "tasks_per_node": None,
            "ntasks": None,
            "total_ranks": None,
            "walltime": None,
        }

    invocations = _parse_executable_invocations(script_text)

    swmf_invoked = any((inv.get("executable") or "").endswith("SWMF.exe") for inv in invocations)
    fdips_invoked = any("FDIPS.exe" in (inv.get("executable") or "") for inv in invocations)
    harmonics_invoked = any("HARMONICS.exe" in (inv.get("executable") or "") for inv in invocations)
    postproc_present = any("PostProc.pl" in (inv.get("executable") or "") for inv in invocations)

    substitution_tokens = _detect_substitution_tokens(script_text)

    return {
        "scheduler": scheduler,
        "directives": directives,
        "nodes": dims["nodes"],
        "tasks_per_node": dims["tasks_per_node"],
        "total_ranks": dims["total_ranks"],
        "walltime": dims["walltime"],
        "executable_invocations": invocations,
        "swmf_invoked": swmf_invoked,
        "postproc_present": postproc_present,
        "fdips_invoked": fdips_invoked,
        "harmonics_invoked": harmonics_invoked,
        "substitution_tokens": substitution_tokens,
        "script_path": script_path,
    }


def parse_jobscript_file(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return None, f"Could not read jobscript at '{path}': {exc}"
    return parse_jobscript_text(text, script_path=str(path)), None
