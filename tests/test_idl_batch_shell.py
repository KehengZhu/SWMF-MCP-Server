from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from swmf_mcp_server.tools import idl as idl_tools


def test_run_idl_batch_uses_user_shell_and_sources_rc(tmp_path, monkeypatch) -> None:
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setenv("SHELL", "/bin/zsh")
    monkeypatch.setattr(idl_tools.shutil, "which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(idl_tools.subprocess, "run", fake_run)

    payload = idl_tools.swmf_run_idl_batch(
        script="print, 1\n",
        working_dir=str(tmp_path),
        idl_command="idl",
        timeout_s=30,
    )

    assert payload["ok"] is True
    assert payload["shell"] == "zsh"
    assert payload["load_shell_rc"] is True
    assert payload["idl_command_resolved"] == "idl"
    assert payload["idl_command_source"] == "argument"

    assert len(calls) == 2
    check_command = calls[0][0][0]
    run_command = calls[1][0][0]

    assert check_command[0] == "/bin/zsh"
    assert check_command[1] == "-i"
    assert check_command[2] == "-c"
    assert "command -v idl" in check_command[3]
    assert ".zshrc" in check_command[3]

    assert run_command[0] == "/bin/zsh"
    assert run_command[1] == "-i"
    assert run_command[2] == "-c"
    assert ".zshrc" in run_command[3]
    assert "idl <" in run_command[3]


def test_run_idl_batch_supports_csh(tmp_path, monkeypatch) -> None:
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(idl_tools.shutil, "which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(idl_tools.subprocess, "run", fake_run)

    payload = idl_tools.swmf_run_idl_batch(
        script="print, 2\n",
        working_dir=str(tmp_path),
        idl_command="idl",
        shell="csh",
    )

    assert payload["ok"] is True
    assert payload["shell"] == "csh"
    assert len(calls) == 2

    command = calls[1][0][0]
    assert command[0] == "/bin/csh"
    assert command[1] == "-i"
    assert command[2] == "-c"
    assert "source \"$HOME/.cshrc\"" in command[3]


def test_run_idl_batch_prefers_env_idl_exec(tmp_path, monkeypatch) -> None:
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setenv(idl_tools._IDL_EXEC_ENV, "/Applications/NV5/idl92/bin/idl")
    monkeypatch.setattr(idl_tools.shutil, "which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(idl_tools.subprocess, "run", fake_run)

    payload = idl_tools.swmf_run_idl_batch(
        script="print, 4\n",
        working_dir=str(tmp_path),
        idl_command="idl",
        shell="zsh",
    )

    assert payload["ok"] is True
    assert payload["idl_command_resolved"] == "/Applications/NV5/idl92/bin/idl"
    assert payload["idl_command_source"] == f"env:{idl_tools._IDL_EXEC_ENV}"
    assert len(calls) == 2
    run_command = calls[1][0][0]
    assert "/Applications/NV5/idl92/bin/idl <" in run_command[3]


def test_run_idl_batch_returns_hints_when_idl_missing(tmp_path, monkeypatch) -> None:
    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    def fake_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=1, stdout="", stderr="not found")

    monkeypatch.delenv(idl_tools._IDL_EXEC_ENV, raising=False)
    monkeypatch.setattr(idl_tools.shutil, "which", lambda name: f"/bin/{name}")
    monkeypatch.setattr(idl_tools.subprocess, "run", fake_run)

    payload = idl_tools.swmf_run_idl_batch(
        script="print, 5\n",
        working_dir=str(tmp_path),
        shell="zsh",
    )

    assert payload["ok"] is False
    assert payload["error_code"] == "IDL_COMMAND_NOT_FOUND"
    assert payload["lookup_target"] == "idl"
    assert payload["search_hints"]
    assert any(idl_tools._IDL_EXEC_ENV in fix for fix in payload["how_to_fix"])
    assert len(calls) == 1


def test_run_idl_batch_rejects_unsupported_shell(tmp_path) -> None:
    payload = idl_tools.swmf_run_idl_batch(
        script="print, 3\n",
        working_dir=str(tmp_path),
        shell="fish",
    )

    assert payload["ok"] is False
    assert payload["error_code"] == "UNSUPPORTED_SHELL"
    assert "Supported shells" in payload["message"]


def test_run_idl_batch_missing_working_dir_returns_path_hints(tmp_path) -> None:
    payload = idl_tools.swmf_run_idl_batch(
        script="print, 6\n",
        working_dir=str(tmp_path / "missing_workdir"),
        shell="zsh",
    )

    assert payload["ok"] is False
    assert payload["error_code"] == "WORKING_DIR_NOT_FOUND"
    assert payload["path_search_hints"]
    assert "path_search_candidates" in payload
