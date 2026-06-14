#!/usr/bin/env python3
"""Generate project-local install outputs for one supported agent surface.

Called by ``make install``. Reads configuration from environment variables set
by the Makefile:
  AGENT           - target agent name
  TARGET_DIR      - directory where install outputs are written
  SERVER_PYTHON   - absolute path to the Python interpreter in the project venv
                    (the ``swmf`` console script lives next to it)
  SWMF_ROOT       - absolute path to the SWMF source tree
  SWMF_IDL_EXEC   - optional absolute path to the IDL executable
  SWMFSOLAR_ROOT  - optional absolute path to the SWMFSOLAR source tree

There is no MCP server anymore. Instead install writes:
  1. A self-contained ``swmf`` launcher (a shell wrapper that bakes in SWMF_ROOT
     and friends, then execs the venv ``swmf`` console script).
  2. An agent instruction file = a generated header naming the launcher's
     absolute path, followed by the shared SWMF discipline.
  3. A symlink of the skill tree into the agent's skills directory.
"""
from __future__ import annotations

import os
import shutil
import stat
import sys
from pathlib import Path


PROJECT_NAME = "swmf-ai"
SUPPORTED_AGENTS = ("claude", "copilot-vscode", "copilot-cli", "codex")
AGENT_ALIASES = {
    "claude-code": "claude",
    "copilot": "copilot-vscode",
    "vscode": "copilot-vscode",
    "github-copilot": "copilot-vscode",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _agent_assets_root() -> Path:
    return _repo_root() / "src" / "agent_assets"


def _skills_source_root() -> Path:
    return _agent_assets_root() / "skills"


def _shared_discipline_source() -> Path:
    return _agent_assets_root() / "SWMF_CORE_DISCIPLINE.md"


def _installed_repo_dir(target_dir: Path, repo_root: Path) -> Path:
    if target_dir == repo_root:
        return repo_root
    return target_dir / ".swmf_mcp_server"


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
        return
    if path.exists():
        shutil.rmtree(path)


def _symlink_skill_tree(source: Path, destination: Path) -> None:
    if destination.resolve() == source.resolve():
        return
    _remove_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    relative_source = Path(os.path.relpath(source, start=destination.parent))
    destination.symlink_to(relative_source, target_is_directory=True)


def normalize_agent_name(raw_agent: str) -> str:
    agent = raw_agent.strip().lower()
    return AGENT_ALIASES.get(agent, agent)


def skill_destination_for_agent(agent: str, target_dir: Path) -> Path:
    if agent == "claude":
        return target_dir / ".claude" / "skills"
    if agent in {"copilot-vscode", "copilot-cli"}:
        return target_dir / ".github" / "skills"
    if agent == "codex":
        return target_dir / ".codex" / "skills"
    raise ValueError(f"Unsupported agent: {agent}")


def instruction_destination_for_agent(agent: str, target_dir: Path) -> Path:
    if agent == "claude":
        return target_dir / "CLAUDE.md"
    if agent in {"copilot-vscode", "copilot-cli"}:
        return target_dir / ".github" / "copilot-instructions.md"
    if agent == "codex":
        return target_dir / "AGENTS.md"
    raise ValueError(f"Unsupported agent: {agent}")


def resolve_swmfsolar_root(
    explicit_value: str,
    swmf_root: Path,
    repo_root: Path,
    target_dir: Path,
) -> tuple[Path | None, str]:
    if explicit_value:
        explicit_path = Path(explicit_value).resolve()
        if explicit_path.is_dir():
            return explicit_path, "explicit SWMFSOLAR_ROOT"
        return None, f"explicit SWMFSOLAR_ROOT not found: {explicit_path}"

    candidates = [
        (swmf_root.parent / "SWMFSOLAR").resolve(),
        (repo_root / "SWMFSOLAR").resolve(),
        (target_dir / "SWMFSOLAR").resolve(),
    ]
    labels = [
        "sibling of SWMF_ROOT",
        "repo-local SWMFSOLAR",
        "target-local SWMFSOLAR",
    ]

    for candidate, label in zip(candidates, labels, strict=True):
        if candidate.is_dir():
            return candidate, label

    return None, "not found in auto-detect search paths"


def build_cli_env(
    swmf_root: Path,
    swmf_idl_exec: str,
    swmfsolar_root: Path | None,
) -> dict[str, str]:
    env = {"SWMF_ROOT": str(swmf_root)}
    if swmf_idl_exec:
        env["SWMF_IDL_EXEC"] = str(Path(swmf_idl_exec).resolve())
    if swmfsolar_root is not None:
        env["SWMFSOLAR_ROOT"] = str(swmfsolar_root)
    return env


def _sh_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def write_launcher(target_dir: Path, venv_swmf: Path, env: dict[str, str]) -> Path:
    """Write a self-contained ``swmf`` launcher and return its path.

    The launcher exports SWMF_ROOT (and friends) before exec'ing the venv
    ``swmf`` console script, so the agent can invoke the CLI without any
    environment setup or ``--swmf-root`` flags.
    """
    launcher_path = target_dir / ".swmf_ai" / "swmf"
    launcher_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "#!/bin/sh",
        "# Generated by swmf-mcp-prototype `make install`. Do not edit by hand.",
    ]
    lines.extend(f"export {key}={_sh_quote(value)}" for key, value in env.items())
    lines.append(f"exec {_sh_quote(str(venv_swmf))} \"$@\"")
    launcher_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    launcher_path.chmod(launcher_path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return launcher_path


def _instruction_header(launcher_path: Path, env: dict[str, str]) -> str:
    extra = "".join(
        f"#   {key}={value}\n"
        for key, value in env.items()
        if key != "SWMF_ROOT"
    )
    return (
        "# SWMF AI\n"
        "\n"
        "This workspace is configured for SWMF AI. Use the local `swmf` CLI for all\n"
        "SWMF retrieval and artifact inspection. The skills below refer to the CLI as\n"
        "`swmf`; invoke it with this absolute path:\n"
        "\n"
        f"    {launcher_path}\n"
        "\n"
        f"Example: `{launcher_path} get-context --question \"How does GM couple to IE?\"`.\n"
        "\n"
        f"`SWMF_ROOT={env.get('SWMF_ROOT', '')}` (and any IDL/SWMFSOLAR paths) are baked\n"
        "into that launcher, so you never need to pass `--swmf-root`. Subcommands:\n"
        "`get-context`, `get-evidence`, `inspect`, `compare`, `index`.\n"
        + (("#\n# Also configured:\n" + extra) if extra else "")
        + "\n---\n\n"
    )


def write_instruction_file(
    instruction_path: Path,
    launcher_path: Path,
    env: dict[str, str],
) -> None:
    discipline = _shared_discipline_source().read_text(encoding="utf-8")
    instruction_path.parent.mkdir(parents=True, exist_ok=True)
    _remove_path(instruction_path)
    instruction_path.write_text(_instruction_header(launcher_path, env) + discipline, encoding="utf-8")


def write_agent_install(
    agent: str,
    target_dir: Path,
    venv_swmf: Path,
    env: dict[str, str],
) -> tuple[Path, Path, Path]:
    skills_path = skill_destination_for_agent(agent, target_dir)
    instruction_path = instruction_destination_for_agent(agent, target_dir)

    launcher_path = write_launcher(target_dir, venv_swmf, env)
    write_instruction_file(instruction_path, launcher_path, env)
    _symlink_skill_tree(_skills_source_root(), skills_path)
    return launcher_path, skills_path, instruction_path


def main() -> int:
    raw_agent = os.environ.get("AGENT", "")
    target_dir = os.environ.get("TARGET_DIR", "")
    server_python = os.environ.get("SERVER_PYTHON", "")
    swmf_root = os.environ.get("SWMF_ROOT", "")
    swmf_idl_exec = os.environ.get("SWMF_IDL_EXEC", "")
    explicit_swmfsolar_root = os.environ.get("SWMFSOLAR_ROOT", "")

    missing = [
        name
        for name, value in [
            ("AGENT", raw_agent),
            ("TARGET_DIR", target_dir),
            ("SERVER_PYTHON", server_python),
            ("SWMF_ROOT", swmf_root),
        ]
        if not value
    ]
    if missing:
        print(
            f"ERROR: missing environment variable(s): {', '.join(missing)}",
            file=sys.stderr,
        )
        return 1

    agent = normalize_agent_name(raw_agent)
    if agent not in SUPPORTED_AGENTS:
        supported = ", ".join(SUPPORTED_AGENTS)
        print(f"ERROR: unsupported AGENT '{raw_agent}'. Choose one of: {supported}", file=sys.stderr)
        return 1

    repo_root = _repo_root()
    target_path = Path(target_dir).resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    swmf_path = Path(swmf_root).resolve()
    swmfsolar_path, swmfsolar_note = resolve_swmfsolar_root(
        explicit_value=explicit_swmfsolar_root,
        swmf_root=swmf_path,
        repo_root=repo_root,
        target_dir=target_path,
    )
    env = build_cli_env(
        swmf_root=swmf_path,
        swmf_idl_exec=swmf_idl_exec,
        swmfsolar_root=swmfsolar_path,
    )

    # The `swmf` console script sits next to the venv interpreter. Do NOT
    # resolve() first: the venv python is typically a symlink to the base
    # interpreter, and resolving it would point us at the base bin/ instead of
    # the venv bin/ where the `swmf` console script lives.
    venv_swmf = Path(server_python).expanduser().with_name("swmf")

    launcher_path, skills_path, instruction_path = write_agent_install(
        agent=agent,
        target_dir=target_path,
        venv_swmf=venv_swmf,
        env=env,
    )

    print(f"    AGENT                    : {agent}")
    print(f"    SWMF_ROOT                : {swmf_path}")
    print(
        "    SWMF_IDL_EXEC            : "
        f"{env.get('SWMF_IDL_EXEC', '(not set - omitted from launcher)')}"
    )
    print(
        "    SWMFSOLAR_ROOT           : "
        f"{env.get('SWMFSOLAR_ROOT', '(not written - ' + swmfsolar_note + ')')}"
    )
    print(f"    CLI console script       : {venv_swmf}")
    print(f"    Launcher written         : {launcher_path}")
    print(f"    Instruction file written : {instruction_path}")
    print(f"    Skills symlink           : {skills_path}")
    print("==> Agent install ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
