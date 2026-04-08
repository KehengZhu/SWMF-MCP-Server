from __future__ import annotations

from pathlib import Path

from swmf_mcp_server.tools.idl import prepare_idl_workflow


def test_prepare_idl_workflow_animation() -> None:
    payload = prepare_idl_workflow(
        request=None,
        swmf_root_resolved=None,
        run_dir=None,
        output_pattern=None,
        input_file=None,
        artifact_name=None,
        output_format="mp4",
        frame_rate=12,
        preview=False,
        frame_indices=None,
        task="animate",
    )

    assert payload["ok"] is True
    assert payload["guidance_mode"] == "instruction_first"
    assert payload["capability"] == "animate"
    assert "animate_data" in payload["idl_script"]
    assert "videofile='" in payload["idl_script"]
    assert "videorate=12" in payload["idl_script"]
    assert payload["normalized_inputs"]["task"] == "animate"
    assert payload["workflow_guidance"]
    assert payload["decision_branches"]
    assert "TASK" in payload["variable_guidance"]
    assert "idl_authority_sections" in payload
    assert "optional_command_examples" in payload
    execution_hints = payload["optional_command_examples"]["execution_hints"]
    assert any("combined multi-snapshot .outs" in hint for hint in execution_hints)
    assert any("normal IDL command first" in hint for hint in execution_hints)


def test_prepare_idl_workflow_transform() -> None:
    payload = prepare_idl_workflow(
        request="use polar transform",
        swmf_root_resolved=None,
        run_dir=None,
        output_pattern=None,
        input_file=None,
        artifact_name=None,
        output_format=None,
        frame_rate=10,
        preview=False,
        frame_indices=None,
        task="transform",
    )

    assert payload["ok"] is True
    assert payload["guidance_mode"] == "instruction_first"
    assert payload["capability"] == "transform"
    assert "transform='p'" in payload["idl_script"]
    assert "plot_data" in payload["idl_script"]
    assert "TRANSFORM_MODE" in payload["variable_guidance"]


def test_prepare_idl_workflow_frame_indices_generic() -> None:
    payload = prepare_idl_workflow(
        request=None,
        swmf_root_resolved=None,
        run_dir=None,
        output_pattern="IH/z=0_var_3_*.out",
        input_file=None,
        artifact_name="ih_z0_u_frames",
        output_format="png",
        frame_rate=10,
        preview=False,
        frame_indices=[1, 10, 20],
        task="animate",
    )

    assert payload["ok"] is True
    assert payload["guidance_mode"] == "instruction_first"
    assert payload["capability"] == "animate"
    assert "savemovie='png'" in payload["idl_script"]
    assert "firstpict=1" in payload["idl_script"]
    assert "npictmax=3" in payload["idl_script"]


def test_prepare_idl_workflow_requires_task_or_request() -> None:
    payload = prepare_idl_workflow(
        request=None,
        swmf_root_resolved=None,
        run_dir=None,
        output_pattern=None,
        input_file=None,
        artifact_name=None,
        output_format=None,
        frame_rate=10,
        preview=False,
        frame_indices=None,
        task=None,
    )

    assert payload["ok"] is False
    assert payload["error_code"] == "IDL_TASK_OR_REQUEST_REQUIRED"


def test_prepare_idl_workflow_rejects_invalid_task() -> None:
    payload = prepare_idl_workflow(
        request=None,
        swmf_root_resolved=None,
        run_dir=None,
        output_pattern=None,
        input_file=None,
        artifact_name=None,
        output_format=None,
        frame_rate=10,
        preview=False,
        frame_indices=None,
        task="not_a_task",
    )

    assert payload["ok"] is False
    assert payload["error_code"] == "IDL_TASK_INVALID"


def test_prepare_idl_workflow_plot_png_via_postscript_conversion() -> None:
    payload = prepare_idl_workflow(
        request="plot rho",
        swmf_root_resolved=None,
        run_dir=None,
        output_pattern=None,
        input_file="demo.out",
        artifact_name="plot_demo",
        output_format="png",
        frame_rate=10,
        preview=False,
        frame_indices=None,
        task="plot",
    )

    assert payload["ok"] is True
    assert payload["capability"] == "plot"
    assert "set_device,'plot_demo.ps'" in payload["idl_script"]
    assert "SWMF IDL set_device uses a PostScript backend" in " ".join(payload["warnings"])
    assert any(
        "convert 'plot_demo.ps' to 'plot_demo.png'" in hint
        for hint in payload["optional_command_examples"]["execution_hints"]
    )


def test_prepare_idl_workflow_generic_returns_guidance() -> None:
    payload = prepare_idl_workflow(
        request="help me with idl",
        swmf_root_resolved=None,
        run_dir=None,
        output_pattern=None,
        input_file=None,
        artifact_name=None,
        output_format=None,
        frame_rate=10,
        preview=False,
        frame_indices=None,
        task=None,
    )

    assert payload["ok"] is True
    assert payload["guidance_mode"] == "instruction_first"
    assert payload["capability"] == "generic"
    assert payload["requires_clarification"] is True
    assert payload["guided_next_steps"]


def test_prepare_idl_workflow_plot_request_stays_generic() -> None:
    payload = prepare_idl_workflow(
        request="plot beginning intermediate and last frames of ih z=0 cut",
        swmf_root_resolved=None,
        run_dir=None,
        output_pattern="IH/z=0_var_3_t*.out",
        input_file=None,
        artifact_name="ih_z0_u",
        output_format="png",
        frame_rate=10,
        preview=False,
        frame_indices=None,
        task="plot",
    )

    assert payload["ok"] is True
    assert payload["guidance_mode"] == "instruction_first"
    assert payload["capability"] == "plot"
    assert payload["requires_file_resolution"] is True
    assert "filename='example.out'" in payload["idl_script"]
    assert "__FRAME_BEGIN__" not in payload["idl_script"]
    assert any("Provide input_file" in hint for hint in payload["guided_next_steps"])


def test_prepare_idl_workflow_uses_share_idl_sources_only(tmp_path: Path) -> None:
    swmf_root = tmp_path / "SWMF"
    (swmf_root / "share" / "IDL" / "General").mkdir(parents=True)
    (swmf_root / "share" / "IDL" / "doc" / "Tex").mkdir(parents=True)
    (swmf_root / "docs").mkdir(parents=True)

    (swmf_root / "share" / "IDL" / "General" / "idlrc").write_text(
        ".r procedures\n.r set_defaults\n.r vector\n.r funcdef\nloadct,39\n",
        encoding="utf-8",
    )
    (swmf_root / "share" / "IDL" / "General" / "procedures.pro").write_text(
        "pro set_default_values\ntransform='n'\nend\n",
        encoding="utf-8",
    )
    (swmf_root / "share" / "IDL" / "General" / "funcdef.pro").write_text(
        "function funcdef, xx, w, func\nfunctiondef = [[ 'mx', 'rho*ux' ]]\nend\n",
        encoding="utf-8",
    )
    (swmf_root / "share" / "IDL" / "doc" / "Tex" / "idl.tex").write_text(
        "\\section{Running IDL}\nplotmode contour stream\ntransform regular polar\n",
        encoding="utf-8",
    )
    (swmf_root / "docs" / "idl.md").write_text("non-authoritative context\n", encoding="utf-8")

    payload = prepare_idl_workflow(
        request="plot rho",
        swmf_root_resolved=str(swmf_root),
        run_dir=None,
        output_pattern=None,
        input_file="demo.out",
        artifact_name=None,
        output_format=None,
        frame_rate=10,
        preview=False,
        frame_indices=None,
        task="plot",
    )

    assert payload["ok"] is True
    assert payload["source_paths"]
    assert all("/share/IDL/" in path for path in payload["source_paths"])
    assert all("/docs/idl.md" not in path for path in payload["source_paths"])
