from __future__ import annotations

import importlib.util
import json
import socket
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_install_script():
    script_path = _repo_root() / "scripts" / "install.py"
    spec = importlib.util.spec_from_file_location("install_script", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _can_resolve_pypi() -> bool:
    try:
        socket.getaddrinfo("pypi.org", 443)
    except OSError:
        return False
    return True


def _install_for_agent(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    agent: str,
    *,
    include_idl: bool = True,
    explicit_solar: bool = True,
) -> tuple[object, Path, Path, Path]:
    module = _load_install_script()
    target_dir = tmp_path / f"{agent}-bundle"
    swmf_root = tmp_path / "workspace" / "SWMF"
    swmfsolar_root = tmp_path / "workspace" / "SWMFSOLAR"
    swmf_root.mkdir(parents=True)
    swmfsolar_root.mkdir(parents=True)

    monkeypatch.setenv("AGENT", agent)
    monkeypatch.setenv("TARGET_DIR", str(target_dir))
    monkeypatch.setenv("SERVER_PYTHON", "/tmp/.venv/bin/python")
    monkeypatch.setenv("SWMF_ROOT", str(swmf_root))

    if include_idl:
        monkeypatch.setenv("SWMF_IDL_EXEC", "/Applications/NV5/idl92/bin/idl")
    else:
        monkeypatch.delenv("SWMF_IDL_EXEC", raising=False)

    if explicit_solar:
        monkeypatch.setenv("SWMFSOLAR_ROOT", str(swmfsolar_root))
    else:
        monkeypatch.delenv("SWMFSOLAR_ROOT", raising=False)

    assert module.main() == 0
    return module, target_dir, swmf_root, swmfsolar_root


def test_build_server_env_omits_optional_keys_when_not_passed(tmp_path: Path) -> None:
    module = _load_install_script()

    env = module.build_server_env(
        swmf_root=(tmp_path / "SWMF").resolve(),
        swmf_idl_exec="",
        swmfsolar_root=None,
    )

    assert env == {"SWMF_ROOT": str((tmp_path / "SWMF").resolve())}


def test_normalize_agent_name_accepts_aliases() -> None:
    module = _load_install_script()

    assert module.normalize_agent_name("claude-code") == "claude"
    assert module.normalize_agent_name("copilot") == "copilot-vscode"
    assert module.normalize_agent_name("vscode") == "copilot-vscode"


def test_resolve_swmfsolar_root_prefers_explicit_path(tmp_path: Path) -> None:
    module = _load_install_script()
    repo_root = tmp_path / "repo"
    target_dir = tmp_path / "target"
    swmf_root = tmp_path / "workspace" / "SWMF"
    explicit_solar = tmp_path / "explicit" / "SWMFSOLAR"

    repo_root.mkdir()
    target_dir.mkdir()
    swmf_root.mkdir(parents=True)
    explicit_solar.mkdir(parents=True)
    (swmf_root.parent / "SWMFSOLAR").mkdir()

    resolved, note = module.resolve_swmfsolar_root(
        explicit_value=str(explicit_solar),
        swmf_root=swmf_root,
        repo_root=repo_root,
        target_dir=target_dir,
    )

    assert resolved == explicit_solar.resolve()
    assert note == "explicit SWMFSOLAR_ROOT"


def test_resolve_swmfsolar_root_uses_search_order(tmp_path: Path) -> None:
    module = _load_install_script()
    repo_root = tmp_path / "repo"
    target_dir = tmp_path / "target"
    swmf_root = tmp_path / "workspace" / "SWMF"

    repo_root.mkdir()
    target_dir.mkdir()
    swmf_root.mkdir(parents=True)

    sibling_solar = swmf_root.parent / "SWMFSOLAR"
    repo_solar = repo_root / "SWMFSOLAR"
    target_solar = target_dir / "SWMFSOLAR"

    target_solar.mkdir()
    resolved, note = module.resolve_swmfsolar_root("", swmf_root, repo_root, target_dir)
    assert resolved == target_solar.resolve()
    assert note == "target-local SWMFSOLAR"

    repo_solar.mkdir()
    resolved, note = module.resolve_swmfsolar_root("", swmf_root, repo_root, target_dir)
    assert resolved == repo_solar.resolve()
    assert note == "repo-local SWMFSOLAR"

    sibling_solar.mkdir()
    resolved, note = module.resolve_swmfsolar_root("", swmf_root, repo_root, target_dir)
    assert resolved == sibling_solar.resolve()
    assert note == "sibling of SWMF_ROOT"


@pytest.mark.parametrize(
    ("agent", "config_path"),
    [
        ("claude", lambda target: target / ".mcp.json"),
        ("copilot-vscode", lambda target: target / ".vscode" / "mcp.json"),
        ("copilot-cli", lambda target: target / ".mcp.json"),
        ("codex", lambda target: target / ".codex" / "config.toml"),
    ],
)
def test_install_script_writes_only_requested_agent_outputs_and_agent_asset_symlinks(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    agent: str,
    config_path,
) -> None:
    module, target_dir, swmf_root, swmfsolar_root = _install_for_agent(monkeypatch, tmp_path, agent)
    expected_env = {
        "SWMF_ROOT": str(swmf_root.resolve()),
        "SWMF_IDL_EXEC": "/Applications/NV5/idl92/bin/idl",
        "SWMFSOLAR_ROOT": str(swmfsolar_root.resolve()),
    }
    expected_cwd = str((target_dir / ".swmf_mcp_server").resolve())
    config_file = config_path(target_dir)
    skills_path = module.skill_destination_for_agent(agent, target_dir)
    instruction_path = module.instruction_destination_for_agent(agent, target_dir)
    source_skills = _repo_root() / "src" / "agent_assets" / "skills"
    source_instruction = _repo_root() / "src" / "agent_assets" / "SWMF_CORE_DISCIPLINE.md"

    assert config_file.exists()
    assert instruction_path.exists()
    assert skills_path.exists()
    assert instruction_path.is_symlink()
    assert instruction_path.resolve() == source_instruction.resolve()
    assert skills_path.is_symlink() or skills_path.resolve() == source_skills.resolve()
    assert skills_path.resolve() == source_skills.resolve()

    if agent == "claude":
        assert _read_json(config_file) == {
            "mcpServers": {
                "swmf-prototype": {
                    "command": "/tmp/.venv/bin/python",
                    "args": ["-m", "swmf_mcp_server.server"],
                    "env": expected_env,
                }
            }
        }
    elif agent == "copilot-vscode":
        assert _read_json(config_file) == {
            "servers": {
                "swmf-prototype": {
                    "type": "stdio",
                    "command": "/tmp/.venv/bin/python",
                    "args": ["-m", "swmf_mcp_server.server"],
                    "cwd": expected_cwd,
                    "env": expected_env,
                }
            }
        }
    elif agent == "copilot-cli":
        assert _read_json(config_file) == {
            "mcpServers": {
                "swmf-prototype": {
                    "type": "stdio",
                    "command": "/tmp/.venv/bin/python",
                    "args": ["-m", "swmf_mcp_server.server"],
                    "cwd": expected_cwd,
                    "env": expected_env,
                    "tools": ["*"],
                }
            }
        }
    elif agent == "codex":
        assert tomllib.loads(config_file.read_text(encoding="utf-8")) == {
            "mcp_servers": {
                "swmf-prototype": {
                    "command": "/tmp/.venv/bin/python",
                    "args": ["-m", "swmf_mcp_server.server"],
                    "cwd": expected_cwd,
                    "env": expected_env,
                }
            }
        }

    unexpected_configs = [
        target_dir / ".mcp.json",
        target_dir / ".vscode" / "mcp.json",
        target_dir / ".github" / "mcp.json",
        target_dir / ".codex" / "config.toml",
    ]
    unexpected_configs.remove(config_file)
    for unexpected in unexpected_configs:
        assert not unexpected.exists(), f"Unexpected config written for {agent}: {unexpected}"


def test_install_script_auto_detects_swmfsolar_using_documented_precedence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module, target_dir, swmf_root, _ = _install_for_agent(
        monkeypatch,
        tmp_path,
        "claude",
        include_idl=False,
        explicit_solar=False,
    )

    expected_solar, _ = module.resolve_swmfsolar_root(
        explicit_value="",
        swmf_root=swmf_root.resolve(),
        repo_root=_repo_root(),
        target_dir=target_dir.resolve(),
    )
    assert expected_solar is not None

    claude_config = _read_json(target_dir / ".mcp.json")
    assert claude_config["mcpServers"]["swmf-prototype"]["env"] == {
        "SWMF_ROOT": str(swmf_root.resolve()),
        "SWMFSOLAR_ROOT": str(expected_solar),
    }


def test_install_script_requires_supported_agent(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = _load_install_script()
    target_dir = tmp_path / "bundle"
    swmf_root = tmp_path / "SWMF"
    swmf_root.mkdir()

    monkeypatch.setenv("AGENT", "unsupported-agent")
    monkeypatch.setenv("TARGET_DIR", str(target_dir))
    monkeypatch.setenv("SERVER_PYTHON", "/tmp/.venv/bin/python")
    monkeypatch.setenv("SWMF_ROOT", str(swmf_root))

    assert module.main() == 1
    assert "unsupported AGENT" in capsys.readouterr().err


def test_make_help_documents_agent_scoped_install_bundle() -> None:
    result = subprocess.run(
        ["make", "help"],
        cwd=_repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )

    help_text = result.stdout
    assert "AGENT=<name>          Required for make install." in help_text
    assert "Public targets:" in help_text
    assert "make                             Bootstrap uv/.venv, sync dependencies, warm the embedding cache, and build the knowledge index" in help_text
    assert "make install                     Bootstrap uv/.venv if needed, then write one agent-specific install bundle into TARGET_DIR" in help_text
    assert "make clean                       Remove generated Python/build/test artifacts" in help_text
    assert "make bootstrap" not in help_text
    assert "make cache-model" not in help_text
    assert "make preindex" not in help_text
    assert "make prepare" not in help_text
    assert "AGENT=claude          TARGET_DIR/.mcp.json + TARGET_DIR/CLAUDE.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + TARGET_DIR/.claude/skills -> src/agent_assets/skills" in help_text
    assert "AGENT=codex           TARGET_DIR/.codex/config.toml + TARGET_DIR/AGENTS.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + TARGET_DIR/.codex/skills -> src/agent_assets/skills" in help_text
    assert "Copilot CLI             .mcp.json + .github/copilot-instructions.md -> src/agent_assets/SWMF_CORE_DISCIPLINE.md + .github/skills" in help_text


@pytest.mark.skipif(shutil.which("make") is None, reason="make is required for smoke tests")
@pytest.mark.skipif(shutil.which("uv") is None, reason="uv is required for smoke tests")
@pytest.mark.skipif(not _can_resolve_pypi(), reason="network access is required for uv sync smoke tests")
def test_make_install_smoke_writes_expected_codex_bundle(tmp_path: Path) -> None:
    target_dir = tmp_path / "install-target"
    swmf_root = tmp_path / "workspace" / "SWMF"
    solar_root = swmf_root.parent / "SWMFSOLAR"
    swmf_root.mkdir(parents=True)
    solar_root.mkdir()

    subprocess.run(
        [
            "make",
            "install",
            "AGENT=codex",
            f"TARGET_DIR={target_dir}",
            f"SWMF_ROOT={swmf_root}",
            f"PYTHON={sys.executable}",
        ],
        cwd=_repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )

    config_path = target_dir / ".codex" / "config.toml"
    skills_path = target_dir / ".codex" / "skills"
    instruction_path = target_dir / "AGENTS.md"
    symlink_path = target_dir / ".swmf_mcp_server"

    assert config_path.exists()
    assert instruction_path.is_symlink()
    assert instruction_path.resolve() == (_repo_root() / "src" / "agent_assets" / "SWMF_CORE_DISCIPLINE.md").resolve()
    assert skills_path.is_symlink()
    assert skills_path.resolve() == (_repo_root() / "src" / "agent_assets" / "skills").resolve()
    assert symlink_path.is_symlink()
    assert symlink_path.resolve() == _repo_root()

    codex_config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    assert codex_config == {
        "mcp_servers": {
            "swmf-prototype": {
                "command": str(target_dir / ".swmf_mcp_server" / ".venv" / "bin" / "python"),
                "args": ["-m", "swmf_mcp_server.server"],
                "cwd": str(target_dir / ".swmf_mcp_server"),
                "env": {
                    "SWMF_ROOT": str(swmf_root.resolve()),
                    "SWMFSOLAR_ROOT": str(solar_root.resolve()),
                },
            }
        }
    }
