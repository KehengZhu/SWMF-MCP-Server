from __future__ import annotations

from swmf_mcp_server import server
from swmf_mcp_server.core.models import KnowledgeIndexStatus, SwmfRootResolution


def _ready_status(root: str) -> KnowledgeIndexStatus:
    return KnowledgeIndexStatus(
        ok=True,
        db_path=f"{root}/.swmf_mcp_cache/knowledge.db",
        swmf_root=root,
        schema_version="2",
        symbol_count=10,
        file_count=4,
        last_built_epoch_s=1.0,
        is_stale=False,
        message=None,
        corpus_roots=[root],
    )


def test_main_preindexes_with_refresh(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(
        server,
        "resolve_swmf_root",
        lambda swmf_root=None, run_dir=None: SwmfRootResolution(
            True,
            "/tmp/SWMF",
            ["resolved"],
        ),
    )

    def fake_refresh_index(root: str, *, swmfsolar_root=None, mcp_repo_root=None):
        calls.append(("refresh", root, swmfsolar_root, mcp_repo_root))
        return _ready_status(root)

    monkeypatch.setattr(server.ks, "refresh_index", fake_refresh_index)
    monkeypatch.setattr(server.app, "run", lambda **kwargs: calls.append(("run", kwargs["transport"])))

    server.main([
        "--preindex-knowledge",
        "--swmf-root",
        "/tmp/SWMF",
        "--swmfsolar-root",
        "/tmp/SWMFSOLAR",
    ])

    assert ("refresh", "/tmp/SWMF", "/tmp/SWMFSOLAR", None) in calls
    assert ("run", "stdio") in calls


def test_main_force_rebuilds_when_requested(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(
        server,
        "resolve_swmf_root",
        lambda swmf_root=None, run_dir=None: SwmfRootResolution(
            True,
            "/tmp/SWMF",
            ["resolved"],
        ),
    )

    def fake_build_index(root: str, force: bool = False, *, swmfsolar_root=None, mcp_repo_root=None):
        calls.append(("build", root, force, swmfsolar_root, mcp_repo_root))
        return _ready_status(root)

    monkeypatch.setattr(server.ks, "build_index", fake_build_index)
    monkeypatch.setattr(server.app, "run", lambda **kwargs: calls.append(("run", kwargs["transport"])))

    server.main([
        "--preindex-knowledge",
        "--force-rebuild-knowledge",
        "--mcp-repo-root",
        "/tmp/repo",
    ])

    assert ("build", "/tmp/SWMF", True, None, "/tmp/repo") in calls
    assert ("run", "stdio") in calls


def test_main_skips_preindex_when_root_unresolved(monkeypatch) -> None:
    calls: list[tuple[str, object]] = []

    monkeypatch.setattr(
        server,
        "resolve_swmf_root",
        lambda swmf_root=None, run_dir=None: SwmfRootResolution(
            False,
            None,
            ["failed"],
            "missing root",
        ),
    )
    monkeypatch.setattr(server.ks, "refresh_index", lambda *args, **kwargs: calls.append(("refresh", args, kwargs)))
    monkeypatch.setattr(server.app, "run", lambda **kwargs: calls.append(("run", kwargs["transport"])))

    server.main(["--preindex-knowledge"])

    assert all(call[0] != "refresh" for call in calls)
    assert ("run", "stdio") in calls