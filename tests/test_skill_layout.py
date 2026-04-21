from __future__ import annotations

from pathlib import Path


def _skills_root() -> Path:
    return Path(__file__).resolve().parents[1] / ".github" / "skills"


def test_repository_exposes_exactly_five_visible_swmf_skills() -> None:
    skills_root = _skills_root()
    visible_skill_dirs = sorted(path.name for path in skills_root.iterdir() if path.is_dir())

    assert visible_skill_dirs == [
        "swmf-build-run",
        "swmf-debug",
        "swmf-implementation",
        "swmf-param-specialist",
        "swmf-postproc",
    ]

    for skill_dir_name in visible_skill_dirs:
        assert (skills_root / skill_dir_name / "SKILL.md").is_file()


def test_postproc_skill_bundle_files_exist() -> None:
    postproc_dir = _skills_root() / "swmf-postproc"

    required_files = [
        "SKILL.md",
        "IDL_VISUALIZATION.md",
        "COUPLING_ARCHITECTURE.md",
        "TOOL_ROUTING.md",
        "ANSWER_CONTRACTS.md",
    ]

    for file_name in required_files:
        assert (postproc_dir / file_name).is_file()


def test_postproc_skill_router_references_companion_playbooks() -> None:
    skill_text = (_skills_root() / "swmf-postproc" / "SKILL.md").read_text(encoding="utf-8")

    assert "## Immediate Load Rules" in skill_text
    assert "IDL_VISUALIZATION.md" in skill_text
    assert "COUPLING_ARCHITECTURE.md" in skill_text
    assert "TOOL_ROUTING.md" in skill_text
    assert "ANSWER_CONTRACTS.md" in skill_text