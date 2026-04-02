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
    assert result["inferred_nproc"] == 48
    assert result["inferred_nproc_source"] == "explicit"
    assert "SC/BATSRUS" in result["recommended_components"]
    assert "IH/BATSRUS" in result["recommended_components"]
    assert result["recommended_next_tool"] == "swmf_validate_external_inputs"
    assert "MCP_HEURISTIC_QUICKRUN_PATCH" in result["suggested_param_template_text"]


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
