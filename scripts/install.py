#!/usr/bin/env python3
"""Generate project-local MCP install outputs for one supported agent surface.

Called by ``make install``. Reads configuration from environment variables set
by the Makefile:
  AGENT           - target agent name
  TARGET_DIR      - directory where install outputs are written
  SERVER_PYTHON   - absolute path to the Python interpreter embedded in configs
  SWMF_ROOT       - absolute path to the SWMF source tree
  SWMF_IDL_EXEC   - optional absolute path to the IDL executable
  SWMFSOLAR_ROOT  - optional absolute path to the SWMFSOLAR source tree
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


SERVER_NAME = "swmf-prototype"
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


def _write_json(path: Path, content: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")


def _toml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _render_codex_toml(command: str, args: list[str], cwd: Path, env: dict[str, str]) -> str:
    lines = [
        f"[mcp_servers.{SERVER_NAME}]",
        f"command = {_toml_quote(command)}",
        f"args = [{', '.join(_toml_quote(arg) for arg in args)}]",
        f"cwd = {_toml_quote(str(cwd))}",
        "",
        f"[mcp_servers.{SERVER_NAME}.env]",
    ]
    lines.extend(f"{key} = {_toml_quote(value)}" for key, value in env.items())
    return "\n".join(lines) + "\n"


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


def _symlink_file(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        try:
            if destination.resolve() == source.resolve():
                return
        except FileNotFoundError:
            pass
    _remove_path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    relative_source = Path(os.path.relpath(source, start=destination.parent))
    destination.symlink_to(relative_source)


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


def config_destination_for_agent(agent: str, target_dir: Path) -> Path:
    if agent == "claude":
        return target_dir / ".mcp.json"
    if agent == "copilot-vscode":
        return target_dir / ".vscode" / "mcp.json"
    if agent == "copilot-cli":
        return target_dir / ".mcp.json"
    if agent == "codex":
        return target_dir / ".codex" / "config.toml"
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


def build_server_env(
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


def build_claude_config(server_python: str, env: dict[str, str]) -> dict[str, Any]:
    return {
        "mcpServers": {
            SERVER_NAME: {
                "command": server_python,
                "args": ["-m", "swmf_mcp_server.server"],
                "env": env,
            }
        }
    }


def build_vscode_config(server_python: str, cwd: Path, env: dict[str, str]) -> dict[str, Any]:
    return {
        "servers": {
            SERVER_NAME: {
                "type": "stdio",
                "command": server_python,
                "args": ["-m", "swmf_mcp_server.server"],
                "cwd": str(cwd),
                "env": env,
            }
        }
    }


def build_copilot_cli_config(server_python: str, cwd: Path, env: dict[str, str]) -> dict[str, Any]:
    return {
        "mcpServers": {
            SERVER_NAME: {
                "type": "stdio",
                "command": server_python,
                "args": ["-m", "swmf_mcp_server.server"],
                "cwd": str(cwd),
                "env": env,
                "tools": ["*"],
            }
        }
    }


def write_agent_install(
    agent: str,
    target_dir: Path,
    server_python: str,
    installed_repo_dir: Path,
    env: dict[str, str],
) -> tuple[Path, Path, Path]:
    config_path = config_destination_for_agent(agent, target_dir)
    skills_path = skill_destination_for_agent(agent, target_dir)
    instruction_path = instruction_destination_for_agent(agent, target_dir)

    if agent == "claude":
        _write_json(config_path, build_claude_config(server_python, env))
    elif agent == "copilot-vscode":
        _write_json(config_path, build_vscode_config(server_python, installed_repo_dir, env))
    elif agent == "copilot-cli":
        _write_json(config_path, build_copilot_cli_config(server_python, installed_repo_dir, env))
    elif agent == "codex":
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            _render_codex_toml(
                command=server_python,
                args=["-m", "swmf_mcp_server.server"],
                cwd=installed_repo_dir,
                env=env,
            ),
            encoding="utf-8",
        )
    else:
        raise ValueError(f"Unsupported agent: {agent}")

    _symlink_file(_shared_discipline_source(), instruction_path)
    _symlink_skill_tree(_skills_source_root(), skills_path)
    return config_path, skills_path, instruction_path


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
    installed_repo_dir = _installed_repo_dir(target_path, repo_root)
    swmfsolar_path, swmfsolar_note = resolve_swmfsolar_root(
        explicit_value=explicit_swmfsolar_root,
        swmf_root=swmf_path,
        repo_root=repo_root,
        target_dir=target_path,
    )
    env = build_server_env(
        swmf_root=swmf_path,
        swmf_idl_exec=swmf_idl_exec,
        swmfsolar_root=swmfsolar_path,
    )

    config_path, skills_path, instruction_path = write_agent_install(
        agent=agent,
        target_dir=target_path,
        server_python=server_python,
        installed_repo_dir=installed_repo_dir,
        env=env,
    )

    print(f"    AGENT                    : {agent}")
    print(f"    SWMF_ROOT                : {swmf_path}")
    print(
        "    SWMF_IDL_EXEC            : "
        f"{env.get('SWMF_IDL_EXEC', '(not set - omitted from generated config)')}"
    )
    print(
        "    SWMFSOLAR_ROOT           : "
        f"{env.get('SWMFSOLAR_ROOT', '(not written - ' + swmfsolar_note + ')')}"
    )
    print(f"    Runtime Python           : {server_python}")
    print(f"    Runtime cwd              : {installed_repo_dir}")
    print(f"    Config written           : {config_path}")
    print(f"    Instruction symlink      : {instruction_path}")
    print(f"    Skills symlink           : {skills_path}")
    print("==> Agent install ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
