from __future__ import annotations

from swmf_mcp_server.services.idl_service import prepare_idl_workflow


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
    assert payload["capability"] == "animate"
    assert "animate_data" in payload["idl_script"]
    assert "videofile='" in payload["idl_script"]
    assert "videorate=12" in payload["idl_script"]
    assert payload["normalized_inputs"]["task"] == "animate"
    assert any(command.startswith("cat ") for command in payload["shell_commands"])


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
    assert payload["capability"] == "transform"
    assert "transform='p'" in payload["idl_script"]
    assert "plot_data" in payload["idl_script"]


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
    assert any("convert -density 300 plot_demo.ps plot_demo.png" in cmd for cmd in payload["shell_commands"])
