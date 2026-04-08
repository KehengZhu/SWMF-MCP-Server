from __future__ import annotations

from pathlib import Path

from swmf_mcp_server.core.common import build_path_search_guidance


def test_path_guidance_keyword_matches_prioritized(tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    preferred = run_root / "demo_param_case"
    preferred.mkdir(parents=True)
    (preferred / "PARAM.in").write_text("# test\n", encoding="utf-8")

    other = run_root / "other_case"
    other.mkdir(parents=True)
    (other / "PARAM.in").write_text("# test\n", encoding="utf-8")

    payload = build_path_search_guidance(
        path_role="param_path",
        search_roots=[run_root],
        expected_entries=["PARAM.in"],
        keyword_hints=["demo"],
    )

    assert payload["path_search_keyword_candidates"]
    assert payload["path_search_keyword_candidates"][0].endswith("demo_param_case")
    assert payload["path_search_candidates"][0].endswith("demo_param_case")
    assert any("Keyword-matched directories were found" in hint for hint in payload["path_search_hints"])


def test_path_guidance_falls_back_when_no_keyword_match(tmp_path: Path) -> None:
    run_root = tmp_path / "runs"
    candidate = run_root / "steady_state"
    candidate.mkdir(parents=True)
    (candidate / "PARAM.in").write_text("# test\n", encoding="utf-8")

    payload = build_path_search_guidance(
        path_role="param_path",
        search_roots=[run_root],
        expected_entries=["PARAM.in"],
        keyword_hints=["nonexistentkeyword"],
    )

    assert payload["path_search_keyword_candidates"] == []
    assert any(path.endswith("steady_state") for path in payload["path_search_candidates"])
    assert any("inspect child directories first" in hint for hint in payload["path_search_hints"])
