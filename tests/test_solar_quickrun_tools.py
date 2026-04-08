from __future__ import annotations

from pathlib import Path

import pytest

from swmf_mcp_server import server


@pytest.fixture()
def swmf_root_and_run_dir(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "SWMF"
    (root / "Scripts").mkdir(parents=True)
    (root / "Config.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")
    (root / "PARAM.XML").write_text("<param/>\n", encoding="utf-8")
    (root / "Scripts" / "TestParam.pl").write_text("#!/usr/bin/env perl\n", encoding="utf-8")

    run_dir = root / "runs" / "demo"
    run_dir.mkdir(parents=True)
    return root, run_dir


@pytest.fixture()
def tiny_gong_fits(swmf_root_and_run_dir: tuple[Path, Path]) -> Path:
    root, run_dir = swmf_root_and_run_dir
    _ = root
    fits_mod = pytest.importorskip("astropy.io.fits", reason="astropy is needed for FITS tests")

    import numpy as np

    input_dir = run_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    fits_path = input_dir / "gong_synoptic.fits"

    data = np.array([[1.0, -2.0], [3.5, 0.25]], dtype=np.float32)
    hdu = fits_mod.PrimaryHDU(data)
    hdu.header["INSTRUME"] = "GONG"
    hdu.header["ORIGIN"] = "NSO"
    hdu.header["DATE-OBS"] = "2026-03-10T00:00:00"
    hdu.header["MAPDATE"] = "2026-03-11T00:00:00"
    hdu.header["CAR_ROT"] = 2311
    hdu.header["CTYPE1"] = "CRLN-CEA"
    hdu.header["CTYPE2"] = "CRLT-CEA"
    hdu.header["OBJECT"] = "synoptic magnetogram"
    hdu.writeto(fits_path, overwrite=True)

    return fits_path


def test_swmf_inspect_fits_magnetogram_metadata(tiny_gong_fits: Path, swmf_root_and_run_dir: tuple[Path, Path]) -> None:
    root, run_dir = swmf_root_and_run_dir
    result = server.swmf_inspect_fits_magnetogram(
        fits_path=str(tiny_gong_fits),
        run_dir=str(run_dir),
        swmf_root=str(root),
        read_data=True,
    )

    assert result["ok"] is True
    assert result["instrument"] == "GONG"
    assert result["source"] == "NSO"
    assert result["carrington_rotation"] == "2311"
    assert result["probable_map_type"] == "synoptic"
    assert result["data_summary"]["shape"] == [2, 2]
    assert result["data_summary"]["min"] == pytest.approx(-2.0)
    assert result["data_summary"]["max"] == pytest.approx(3.5)


def test_swmf_inspect_fits_missing_dependency(monkeypatch: pytest.MonkeyPatch, swmf_root_and_run_dir: tuple[Path, Path]) -> None:
    root, run_dir = swmf_root_and_run_dir
    fake_fits = run_dir / "fake.fits"
    fake_fits.write_text("not-really-fits", encoding="utf-8")

    monkeypatch.setattr(
        "swmf_mcp_server.tools.idl._try_import_astropy_fits",
        lambda: (None, "Optional dependency 'astropy' is required"),
    )

    result = server.swmf_inspect_fits_magnetogram(
        fits_path=str(fake_fits),
        run_dir=str(run_dir),
        swmf_root=str(root),
        read_data=False,
    )

    assert result["ok"] is False
    assert result["hard_error"] is False
    assert "astropy" in result["message"].lower()


def test_swmf_inspect_fits_bad_path(swmf_root_and_run_dir: tuple[Path, Path]) -> None:
    root, run_dir = swmf_root_and_run_dir
    result = server.swmf_inspect_fits_magnetogram(
        fits_path="input/missing.fits",
        run_dir=str(run_dir),
        swmf_root=str(root),
    )

    assert result["ok"] is False
    assert result["hard_error"] is True
    assert "does not point to a file" in result["message"]


def test_swmf_inspect_relative_path_resolution(tiny_gong_fits: Path, swmf_root_and_run_dir: tuple[Path, Path]) -> None:
    root, run_dir = swmf_root_and_run_dir
    rel_path = tiny_gong_fits.relative_to(run_dir)

    result = server.swmf_inspect_fits_magnetogram(
        fits_path=str(rel_path),
        run_dir=str(run_dir),
        swmf_root=str(root),
    )

    assert result["ok"] is True
    assert result["fits_path_resolved"] == str(tiny_gong_fits.resolve())


def test_prepare_sc_quickrun_explicit_nproc(tiny_gong_fits: Path, swmf_root_and_run_dir: tuple[Path, Path]) -> None:
    root, run_dir = swmf_root_and_run_dir
    result = server.swmf_prepare_sc_quickrun_from_magnetogram(
        fits_path=str(tiny_gong_fits),
        run_dir=str(run_dir),
        swmf_root=str(root),
        mode="sc_ih_steady",
        nproc=48,
    )

    assert result["ok"] is True
    assert result["guidance_mode"] == "instruction_first"
    assert result["inferred_nproc"] == 48
    assert result["inferred_nproc_source"] == "explicit"
    assert "SC/BATSRUS" in result["recommended_components"]
    assert "IH/BATSRUS" in result["recommended_components"]
    assert result["recommended_next_tool"] == "swmf_validate_external_inputs"
    assert "MCP_HEURISTIC_QUICKRUN_PATCH" in result["suggested_param_template_text"]
    assert result["workflow_guidance"]
    assert result["decision_branches"]
    assert result["variable_guidance"]
    assert "optional_command_examples" in result


def test_prepare_sc_quickrun_inferred_nproc(tiny_gong_fits: Path, swmf_root_and_run_dir: tuple[Path, Path]) -> None:
    root, run_dir = swmf_root_and_run_dir
    job_script = run_dir / "job.frontera"
    job_script.write_text(
        "\n".join(
            [
                "#!/bin/bash",
                "#SBATCH -N 2",
                "#SBATCH --tasks-per-node=56",
                "ibrun -n 1 ./PostProc.pl -M",
                "ibrun -o 56 -n 56 ./SWMF.exe",
            ]
        ),
        encoding="utf-8",
    )

    result = server.swmf_prepare_sc_quickrun_from_magnetogram(
        fits_path=str(tiny_gong_fits),
        run_dir=str(run_dir),
        swmf_root=str(root),
        mode="sc_steady",
        nproc=None,
        job_script_path=str(job_script),
    )

    assert result["ok"] is True
    assert result["inferred_nproc"] == 56
    assert result["inferred_nproc_source"] == "job_script_inference"


def test_prepare_sc_quickrun_enriched_with_swmfsolar_makefile(
    tiny_gong_fits: Path,
    swmf_root_and_run_dir: tuple[Path, Path],
) -> None:
    root, run_dir = swmf_root_and_run_dir
    swmfsolar = root.parent / "SWMFSOLAR"
    (swmfsolar / "Scripts").mkdir(parents=True)
    (swmfsolar / "README").write_text(
        "The SWMFSOLAR directory must be linked to an installed SWMF source code directory.\n"
        "It is required to have the symobolic link of SWMF to the installed SWMF.\n",
        encoding="utf-8",
    )
    (swmfsolar / "Makefile").write_text(
        "\n".join(
            [
                "MODEL = AWSoMR",
                "MACHINE = frontera",
                "PFSS = FDIPS",
                "TIME = MapTime",
                "MAP = NoMap",
                "PARAM = Default",
                "REALIZATIONS = 1,2,3,4,5,6,7,8,9,10,11,12",
                "POYNTINGFLUX = -1.0",
                "JOBNAME = amap",
                "DOINSTALL = T",
                "",
                "compile:",
                "\t@echo compile",
                "backup_run:",
                "\t@echo backup",
                "copy_param:",
                "\t@echo copy",
                "rundir_realizations:",
                "\t@echo rundir",
                "clean_rundir_tmp:",
                "\t@echo clean",
                "run:",
                '\t@if [[ "${MACHINE}" == "frontera" ]]; then sbatch job.long; fi',
                "adapt_run:",
                "\tmake rundir_local",
                "\tmake run",
                "rundir_local:",
                "\t@python Scripts/change_awsom_param.py --map ${MAP} -t ${TIME} -B0 ${PFSS} -p ${POYNTINGFLUX}",
                "help:",
                '\t@echo " MODEL=AWSoM - select model"',
                "",
                "# ERROR: MODEL must be either AWSoM, AWSoM2T, AWSoMR or AWSoMR_SOFIE.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = server.swmf_prepare_sc_quickrun_from_magnetogram(
        fits_path=str(tiny_gong_fits),
        run_dir=str(run_dir),
        swmf_root=str(root),
        mode="sc_steady",
        nproc=32,
    )

    assert result["ok"] is True
    assert result["swmfsolar_makefile_detected"] is True
    assert result["swmfsolar_root_resolved"] == str(swmfsolar.resolve())
    assert result["swmfsolar_makefile_path"] == str((swmfsolar / "Makefile").resolve())

    capabilities = result["swmfsolar_makefile_capabilities"]
    assert "compile" in capabilities["targets"]
    assert "run" in capabilities["workflow_targets"]
    assert "AWSoMR_SOFIE" in capabilities["supported_models"]
    assert capabilities["default_variables"]["pfss"] == "FDIPS"

    vars_payload = result["swmfsolar_recommended_variables"]
    assert vars_payload["model"] == "AWSoMR"
    assert vars_payload["pfss"] == "FDIPS"
    assert vars_payload["simdir"] == run_dir.name
    assert vars_payload["machine"] == "frontera"
    assert vars_payload["realizations_expression"] == "1"

    command_examples = result["optional_command_examples"]["swmfsolar_commands"]
    compile_cmd = command_examples["compile"][0]
    assert "make compile" in compile_cmd
    assert "MODEL=AWSoMR" in compile_cmd
    adapt_cmd = command_examples["adapt_run"][0]
    assert "make adapt_run" in adapt_cmd
    assert f"SIMDIR={run_dir.name}" in adapt_cmd
    assert "MACHINE=frontera" in adapt_cmd
    assert any("change_awsom_param.py" in cmd for cmd in command_examples["prepare"])
    assert result["optional_command_examples"]["selected_build_sequence"] == command_examples["compile"]
    assert result["optional_command_examples"]["selected_run_sequence"] == command_examples["adapt_run"]
    assert str((swmfsolar / "Makefile").resolve()) in result["source_paths"]
    assert str((swmfsolar / "README").resolve()) in result["source_paths"]
    assert "MODEL" in result["variable_guidance"]
    assert result["optional_command_examples"]["swmfsolar_commands"]
    assert "target_recipes" in result
    assert "adapt_run" in result["target_recipes"]
    assert "scheduler_branches" in result
    assert any(item.get("machine") == "frontera" for item in result["scheduler_branches"])
    assert "environment_prerequisites" in result
    assert any("required" in item.lower() or "must" in item.lower() for item in result["environment_prerequisites"])


def test_prepare_sc_quickrun_model_simdir_machine_overrides(
    tiny_gong_fits: Path,
    swmf_root_and_run_dir: tuple[Path, Path],
) -> None:
    root, run_dir = swmf_root_and_run_dir
    swmfsolar = root.parent / "SWMFSOLAR"
    (swmfsolar / "Scripts").mkdir(parents=True)
    (swmfsolar / "Makefile").write_text(
        "\n".join(
            [
                "MODEL = AWSoM",
                "PFSS = HARMONICS",
                "TIME = MapTime",
                "PARAM = Default",
                "POYNTINGFLUX = -1.0",
                "JOBNAME = amap",
                "adapt_run:",
                "\t@echo adapt",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    result = server.swmf_prepare_sc_quickrun_from_magnetogram(
        fits_path=str(tiny_gong_fits),
        run_dir=str(run_dir),
        swmf_root=str(root),
        mode="sc_steady",
        nproc=32,
        model="AWSoMR_SOFIE",
        simdir="Run_Max_SA",
        machine="frontera",
    )

    assert result["ok"] is True
    vars_payload = result["swmfsolar_recommended_variables"]
    assert vars_payload["model"] == "AWSoMR_SOFIE"
    assert vars_payload["simdir"] == "Run_Max_SA"
    assert vars_payload["machine"] == "frontera"

    adapt_cmd = result["optional_command_examples"]["swmfsolar_commands"]["adapt_run"][0]
    assert "MODEL=AWSoMR_SOFIE" in adapt_cmd
    assert "SIMDIR=Run_Max_SA" in adapt_cmd
    assert "MACHINE=frontera" in adapt_cmd
    assert result["optional_command_examples"]["selected_run_sequence"] == result["optional_command_examples"]["swmfsolar_commands"]["adapt_run"]
