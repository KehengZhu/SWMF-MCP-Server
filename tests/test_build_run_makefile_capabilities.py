from __future__ import annotations

from pathlib import Path

from swmf_mcp_server import server


def _make_fake_swmf_root_with_makefile(tmp_path: Path) -> Path:
    root = tmp_path / "SWMF"
    (root / "Scripts").mkdir(parents=True)
    (root / "Config.pl").write_text(
        "\n".join(
            [
                "#!/usr/bin/env perl",
                '"Additional options for SWMF/Config.pl:',
                "-v=VERSION     select component version VERSION.",
                "-o=ID:OPTIONS  set options OPTIONS for the component identified with ID.",
                "Examples for the SWMF Config.pl:",
                "    Config.pl -v=Empty,GM/BATSRUS",
                "    Config.pl -o=GM:g=8,8,8",
                "#EOC",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "PARAM.XML").write_text("<param/>\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")

    (root / "Makefile").write_text(
        "\n".join(
            [
                "SHELL=/bin/sh",
                "CONFIG_PL=./Config.pl",
                "NP=2",
                "RUNDIR=run",
                "include Makefile.def",
                "default : SWMF",
                ".NOTPARALLEL:",
                "SWMF:",
                "\t@echo swmf",
                "ALL:",
                "\t@echo all",
                "PIDL:",
                "\t@echo pidl",
                "rundir:",
                "\t@echo rundir ${RUNDIR}",
                "parallelrun:",
                "\t@echo parallel ${NP}",
                "serialrun:",
                "\t@echo serial",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return root


def test_prepare_build_enriched_by_swmf_makefile(tmp_path: Path) -> None:
    root = _make_fake_swmf_root_with_makefile(tmp_path)

    result = server.swmf_prepare_build(
        components_csv="SC/BATSRUS,IH/BATSRUS",
        swmf_root=str(root),
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert result["swmf_makefile_detected"] is True
    assert result["recommended_make_build_target"] == "SWMF"
    assert result["optional_command_examples"]["build"] == ["make SWMF"]
    assert result["workflow_guidance"]
    assert result["decision_branches"]
    assert "COMPONENTS" in result["variable_guidance"]
    assert "optional_command_examples" in result
    assert result["swmf_config_guidance_detected"] is True
    assert result["config_option_reference"]
    assert any(item["name"].startswith("-v") for item in result["config_option_reference"])
    assert result["config_examples"]
    assert result["makefile_target_recipes"]
    assert "environment_prerequisites" in result
    assert str((root / "Config.pl").resolve()) in result["source_paths"]

    capabilities = result["swmf_makefile_capabilities"]
    assert capabilities["is_notparallel"] is True
    assert "SWMF" in capabilities["build_targets"]
    assert "rundir" in capabilities["run_targets"]
    assert capabilities["default_variables"]["np"] == "2"
    assert str((root / "Makefile").resolve()) in result["source_paths"]


def test_prepare_run_enriched_by_swmf_makefile(tmp_path: Path) -> None:
    root = _make_fake_swmf_root_with_makefile(tmp_path)
    run_dir = root / "runs" / "demo"
    run_dir.mkdir(parents=True)

    result = server.swmf_prepare_run(
        component_map_text="SC 0 -1 1",
        nproc=8,
        run_name="run_case",
        swmf_root=str(root),
        run_dir=str(run_dir),
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert result["swmf_makefile_detected"] is True
    assert result["optional_command_examples"]["prepare"][0] == "make rundir RUNDIR=run_case"
    assert any("make serialrun" in cmd for cmd in result["optional_command_examples"]["local_execution"])
    assert any("make parallelrun NP=8" in cmd for cmd in result["optional_command_examples"]["local_execution"])
    assert result["workflow_guidance"]
    assert result["decision_branches"]
    assert "NPROC" in result["variable_guidance"]
    assert "optional_command_examples" in result
    assert result["swmf_config_guidance_detected"] is True
    assert result["config_option_reference"]
    assert result["makefile_target_recipes"]
    assert "rundir" in result["makefile_target_recipes"]
    assert "environment_prerequisites" in result
    assert str((root / "Config.pl").resolve()) in result["source_paths"]
    assert str((root / "Makefile").resolve()) in result["source_paths"]
