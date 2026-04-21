from __future__ import annotations

from pathlib import Path


def test_repository_exposes_exactly_five_visible_swmf_skills() -> None:
    skills_root = Path(__file__).resolve().parents[1] / ".github" / "skills"
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