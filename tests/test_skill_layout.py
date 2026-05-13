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
    "swmf-replicate",
    "swmf-run",
]

_SUPPORT_SKILLS = [
    "swmf-architecture",
    "swmf-cme-setup",
    "swmf-exact-lookup",
    "swmf-implementation",
    "swmf-jobscript",
    "swmf-magnetogram",
    "swmf-params",
    "swmf-postproc",
    "swmf-swmfsolar",
    "swmf-validation",
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
    assert "Runlog discipline" in core_text
    assert "Do not directly read a whole `runlog*`" in core_text


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


def test_idl_animation_playbook_documents_out_to_outs_workflow() -> None:
    playbook_text = (
        _skills_root() / "support" / "swmf-postproc" / "IDL_VISUALIZATION.md"
    ).read_text(encoding="utf-8")
    analyze_text = (_skills_root() / "swmf-analyze" / "SKILL.md").read_text(encoding="utf-8")
    postproc_text = (_skills_root() / "support" / "swmf-postproc" / "SKILL.md").read_text(encoding="utf-8")

    assert "cat z=0_var_3_t*.out > z=0_var_3.outs" in playbook_text
    assert "filename='z=0_var_3.outs'" in playbook_text
    assert "func='u bx;by'" in playbook_text
    assert "animate_data" in playbook_text
    assert 'get_evidence(query="animate_data"' in playbook_text
    assert "single-snapshot" in playbook_text
    assert "multi-snapshot" in playbook_text
    assert "prefer an existing extracted run directory over an archive" in analyze_text.lower() or \
           "Prefer an existing extracted run directory over an archive" in analyze_text
    assert "extracted run directory over an archive" in postproc_text


def test_run_dir_postprocessing_skills_require_inspection_first() -> None:
    analyze_text = (_skills_root() / "swmf-analyze" / "SKILL.md").read_text(encoding="utf-8")
    postproc_text = (_skills_root() / "support" / "swmf-postproc" / "SKILL.md").read_text(encoding="utf-8")

    for text in (analyze_text, postproc_text):
        assert 'inspect_artifact(artifact_type="run_dir"' in text
        assert "run_dir_layout" in text
        assert "postproc_state" in text
        assert "component_artifact_inventory" in text
        assert "restart_inventory" in text
        assert "component_output_artifacts" in text
        assert 'inspect_artifact(artifact_type="runlog"' in text
        assert "common command-line tools" in text
        assert "Do not directly read runlogs" in text or "do not directly read whole runlogs" in text

    assert "read the whole run-local `PARAM.in` yourself" in analyze_text
    assert "read the run-local `PARAM.in` completely" in analyze_text

    assert "Clear runtime failures belong to `swmf-debug`" in postproc_text
    assert "`swmf-debug`" in analyze_text


def test_postproc_skill_documents_script_launch_directory() -> None:
    postproc_text = (_skills_root() / "support" / "swmf-postproc" / "SKILL.md").read_text(encoding="utf-8")

    required_terms = [
        "Both `PostProc.pl` and `Restart.pl` are copied into an SWMF run directory",
        "executed from that run directory",
        "Do not run either script\nfrom `RESULTS/<name>/`, a component directory, the SWMF source tree, or\n`share/Scripts`",
        'Call `inspect_artifact(artifact_type="run_dir", path=<path>)`',
        "If the inspected path is `postprocessed_results_tree`, `restart_tree`, or\n   `component_dir`, do not treat it as the command cwd",
        "Prefer the run-local copied scripts: `./PostProc.pl` and `./Restart.pl`",
        "`cd <run_dir> && ./PostProc.pl`",
        "`cd <run_dir> && ./PostProc.pl -M -cat RESULTS/<name>`",
        "`cd <run_dir> && ./Restart.pl -c`",
        "`cd <run_dir> && ./Restart.pl`",
        "`cd <new_run_dir> && ./Restart.pl -i <restart_tree>`",
        "It does\nnot edit `PARAM.in`",
    ]
    for term in required_terms:
        assert term in postproc_text


def test_idl_playbook_documents_full_postprocessing_policy() -> None:
    playbook_text = (
        _skills_root() / "support" / "swmf-postproc" / "IDL_VISUALIZATION.md"
    ).read_text(encoding="utf-8")
    analyze_text = (_skills_root() / "swmf-analyze" / "SKILL.md").read_text(encoding="utf-8")
    compare_text = (_skills_root() / "swmf-compare" / "SKILL.md").read_text(encoding="utf-8")

    required_terms = [
        "## Decision Matrix",
        "Quick single plot: `show_data`",
        "Controlled single snapshot: `read_data` followed by `plot_data`",
        "Multiple frames or files: `animate_data`",
        "Logfile columns: `read_log_data` followed by `plot_log_data`",
        "Derived logfile quantities: read the log as 1D data with `read_data`",
        "Structured 3D slice scan: `read_data`, configure `func`/`plotmode`, then `slice_data`",
        "`IDL_PATH`",
        "`IDL_STARTUP`",
        "`idlrc`",
        "`retall`",
        "`set_default_values`",
        "ASCII",
        "`real4`",
        "`real8`",
        "`transform='regular'`",
        "`transform='polar'`",
        "`transform='unpolar'`",
        "`transform='sphere'`",
        "`transform='my'`",
        "`nxreg`",
        "`xreglimits`",
        "`dotransform`",
        "`w=w1-w0`",
        "`wreg=wreg1-wreg0`",
        "`coarsen`",
        "`!x.range`",
        "`cut=grid(...)`",
        "`triplet(...)`",
        "`quadruplet(...)`",
        "`velpos`",
        "`rcut`",
        "`slice_data_restore`",
        "`multiplot`",
        "`nplotstore`",
        "`set_device,'file.eps'`",
        "`close_device`",
        "`savemovie='mp4'`",
        "`@script`",
        "`.r script`",
        "true `pro name`",
    ]
    for term in required_terms:
        assert term in playbook_text

    assert "manual detail: `func`, `plotmode`, `transform`, `slice`, `export`" in analyze_text
    assert "support/swmf-postproc/IDL_VISUALIZATION.md" in compare_text


def test_idl_playbook_requires_idl_first_export_workflow() -> None:
    playbook_text = (
        _skills_root() / "support" / "swmf-postproc" / "IDL_VISUALIZATION.md"
    ).read_text(encoding="utf-8")
    contract_text = (
        _skills_root() / "support" / "swmf-postproc" / "ANSWER_CONTRACTS.md"
    ).read_text(encoding="utf-8")
    analyze_text = (_skills_root() / "swmf-analyze" / "SKILL.md").read_text(encoding="utf-8")
    compare_text = (_skills_root() / "swmf-compare" / "SKILL.md").read_text(encoding="utf-8")

    required_terms = [
        "## IDL-First Execution Ladder",
        "use SWMF IDL macros before custom\ngraphics",
        "The script should be a macro driver",
        "Create an `analysis/` directory",
        "case-local `.pro` command script",
        "`printf '@analysis/z0_u_bxy_export\\nexit\\n' | idl",
        "analysis/<outbase>.idl.log",
        "Only use Python, SVG, manual Fortran-record plotting",
        "hand-written IDL\n   direct graphics",
        "do not hand-write\n   binary readers or direct graphics",
        "Do not check for Python plotting libraries before trying the\n   IDL path",
        "example filenames",
        "Never\n   open or parse SWMF output files with common command-line tools",
        "magick -density 180 input.ps -background white -alpha remove input.png",
        "`convert` only if `magick` is unavailable",
        "For Codex-generated exports, prefer a command-style `analysis/<name>.pro`",
    ]
    for term in required_terms:
        assert term in playbook_text

    for term in [
        "generated_pro_script",
        "idl_execution_command",
        "idl_log",
        "export_files",
    ]:
        assert term in contract_text

    assert "IDL-first execution ladder" in analyze_text
    assert "Python/SVG/manual binary plotting" in analyze_text
    assert "IDL-first\n     generated `.pro` workflow" in compare_text


def test_idl_protocol_doc_contains_gold_prompt_set() -> None:
    protocol_text = (_repo_root() / "docs" / "idl_visualization_skill_protocol.md").read_text(encoding="utf-8")
    for prompt in [
        "List the IDL plotting procedures in SWMF.",
        "What `plotmode` should I use for streamlines on an irregular 2D grid?",
        "How do I plot a quantity from a SWMF log file in IDL?",
        "animate IH results (z=0 cut, visualize U overlayed with bx by vectors) in Run_Max_RP_CME3",
    ]:
        assert prompt in protocol_text


def test_idl_protocol_doc_contains_distill_protocol() -> None:
    protocol_text = (_repo_root() / "docs" / "idl_visualization_skill_protocol.md").read_text(encoding="utf-8")
    required_terms = [
        "## Distill Protocol",
        "chat history, transcript, or session export",
        "identify the root cause and the smallest general fix",
        "Reconstruct the Intended Workflow",
        "Evaluate Success and Failure",
        "Root-Cause Pattern",
        "Propose General Improvements",
        "MCP evidence gap",
        "Boundary violation",
        "SWMF macro-first driver",
        "Macro-first gap",
        "hand-written direct graphics",
        "custom parsers",
        "MCP change, only if needed",
        "workflow inference remains in the skill",
        "add MCP fields only when the skill lacks factual\nevidence",
        "Ask Immediately When Intent Is Ambiguous",
        "Do not ask questions\nwhose answers can be discovered",
        "`observed_behavior`",
        "`root_cause`",
        "`generalized_improvement`",
        "`mcp_changes_if_needed`",
    ]
    for term in required_terms:
        assert term in protocol_text
