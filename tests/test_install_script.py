from __future__ import annotations

import importlib.util
import socket
import shutil
import subprocess
import sys
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


def test_build_cli_env_omits_optional_keys_when_not_passed(tmp_path: Path) -> None:
    module = _load_install_script()

    env = module.build_cli_env(
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


@pytest.mark.parametrize("agent", ["claude", "copilot-vscode", "copilot-cli", "codex"])
def test_install_writes_launcher_instruction_and_skills(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    agent: str,
) -> None:
    module, target_dir, swmf_root, swmfsolar_root = _install_for_agent(monkeypatch, tmp_path, agent)

    launcher_path = target_dir / ".swmf_ai" / "swmf"
    skills_path = module.skill_destination_for_agent(agent, target_dir)
    instruction_path = module.instruction_destination_for_agent(agent, target_dir)
    source_skills = _repo_root() / "src" / "agent_assets" / "skills"

    # 1. Self-contained launcher with SWMF_ROOT (and friends) baked in.
    assert launcher_path.exists()
    assert launcher_path.stat().st_mode & 0o111, "launcher must be executable"
    launcher = launcher_path.read_text(encoding="utf-8")
    assert f"export SWMF_ROOT='{swmf_root.resolve()}'" in launcher
    assert f"export SWMFSOLAR_ROOT='{swmfsolar_root.resolve()}'" in launcher
    assert "export SWMF_IDL_EXEC='/Applications/NV5/idl92/bin/idl'" in launcher
    # The console script sits next to the configured venv interpreter.
    assert "exec '/tmp/.venv/bin/swmf' \"$@\"" in launcher

    # 2. Instruction file is GENERATED (not a symlink) = header + discipline.
    assert instruction_path.exists()
    assert not instruction_path.is_symlink()
    instruction = instruction_path.read_text(encoding="utf-8")
    assert str(launcher_path) in instruction
    assert "# SWMF Core Discipline" in instruction
    assert f"SWMF_ROOT={swmf_root.resolve()}" in instruction

    # 3. Skill tree is symlinked.
    assert skills_path.is_symlink()
    assert skills_path.resolve() == source_skills.resolve()

    # 4. No MCP config surfaces are written anymore.
    for stale in (
        target_dir / ".mcp.json",
        target_dir / ".vscode" / "mcp.json",
        target_dir / ".codex" / "config.toml",
    ):
        assert not stale.exists(), f"Unexpected MCP config written for {agent}: {stale}"


def test_install_auto_detects_swmfsolar_into_launcher(
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

    launcher = (target_dir / ".swmf_ai" / "swmf").read_text(encoding="utf-8")
    assert f"export SWMF_ROOT='{swmf_root.resolve()}'" in launcher
    assert f"export SWMFSOLAR_ROOT='{expected_solar}'" in launcher
    assert "SWMF_IDL_EXEC" not in launcher


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


def test_make_help_documents_install_bundle() -> None:
    result = subprocess.run(
        ["make", "help"],
        cwd=_repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )

    help_text = result.stdout
    assert "Public targets:" in help_text
    assert "AGENT=<name>          Required for make install." in help_text
    assert "All agents            TARGET_DIR/.swmf_ai/swmf" in help_text
    assert "AGENT=claude          TARGET_DIR/CLAUDE.md (header + SWMF_CORE_DISCIPLINE.md) + TARGET_DIR/.claude/skills -> src/agent_assets/skills" in help_text
    assert "AGENT=codex           TARGET_DIR/AGENTS.md (header + discipline) + TARGET_DIR/.codex/skills -> src/agent_assets/skills" in help_text
    # MCP config surfaces are gone.
    assert ".mcp.json" not in help_text
    assert "config.toml" not in help_text


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

    launcher_path = target_dir / ".swmf_ai" / "swmf"
    skills_path = target_dir / ".codex" / "skills"
    instruction_path = target_dir / "AGENTS.md"
    symlink_path = target_dir / ".swmf_mcp_server"

    # Generated instruction file (header + discipline), not a symlink.
    assert instruction_path.exists()
    assert not instruction_path.is_symlink()
    instruction = instruction_path.read_text(encoding="utf-8")
    assert "# SWMF Core Discipline" in instruction
    assert str(launcher_path) in instruction

    # Self-contained launcher exists and bakes in SWMF_ROOT.
    assert launcher_path.exists()
    assert f"export SWMF_ROOT='{swmf_root.resolve()}'" in launcher_path.read_text(encoding="utf-8")

    # Skill tree and repo back-link are symlinks.
    assert skills_path.is_symlink()
    assert skills_path.resolve() == (_repo_root() / "src" / "agent_assets" / "skills").resolve()
    assert symlink_path.is_symlink()
    assert symlink_path.resolve() == _repo_root()

    # No MCP config written.
    assert not (target_dir / ".codex" / "config.toml").exists()
