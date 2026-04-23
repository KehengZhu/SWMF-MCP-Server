from __future__ import annotations

from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _skills_root() -> Path:
    return _repo_root() / "src" / "agent_assets" / "skills"


def _core_playbook_path() -> Path:
    return _repo_root() / "src" / "agent_assets" / "SWMF_CORE_DISCIPLINE.md"


_ENTRY_SKILLS = [
    "swmf-analyze",
    "swmf-build",
    "swmf-compare",
    "swmf-configure",
    "swmf-debug",
    "swmf-explain",
    "swmf-run",
]

_SUPPORT_SKILLS = [
    "swmf-architecture",
    "swmf-exact-lookup",
    "swmf-implementation",
    "swmf-params",
    "swmf-postproc",
]


def test_repository_exposes_entry_and_support_skills() -> None:
    skills_root = _skills_root()
    top_level_dirs = sorted(path.name for path in skills_root.iterdir() if path.is_dir())

    # 7 entry skills + 1 support/ subdirectory
    assert top_level_dirs == sorted(_ENTRY_SKILLS + ["support"])

    for skill_dir_name in _ENTRY_SKILLS:
        assert (skills_root / skill_dir_name / "SKILL.md").is_file(), (
            f"Missing SKILL.md in entry skill: {skill_dir_name}"
        )

    support_dir = skills_root / "support"
    support_subdirs = sorted(path.name for path in support_dir.iterdir() if path.is_dir())
    assert support_subdirs == sorted(_SUPPORT_SKILLS)

    for support_skill_name in _SUPPORT_SKILLS:
        assert (support_dir / support_skill_name / "SKILL.md").is_file(), (
            f"Missing SKILL.md in support skill: {support_skill_name}"
        )


def test_shared_core_playbook_exists() -> None:
    core_playbook = _core_playbook_path()
    assert core_playbook.is_file()

    core_text = core_playbook.read_text(encoding="utf-8")
    # v2 redesign: check for the new structure
    assert "V2 MCP tool surface" in core_text
    assert "inspect_artifact" in core_text
    assert "get_evidence" in core_text


def test_postproc_skill_bundle_files_exist() -> None:
    postproc_dir = _skills_root() / "support" / "swmf-postproc"

    required_files = [
        "SKILL.md",
        "IDL_VISUALIZATION.md",
        "COUPLING_ARCHITECTURE.md",
        "ANSWER_CONTRACTS.md",
    ]

    for file_name in required_files:
        assert (postproc_dir / file_name).is_file(), f"Missing: {file_name}"


def test_postproc_skill_references_companion_playbooks() -> None:
    skill_text = (_skills_root() / "support" / "swmf-postproc" / "SKILL.md").read_text(encoding="utf-8")

    assert "IDL_VISUALIZATION.md" in skill_text
    assert "COUPLING_ARCHITECTURE.md" in skill_text
