"""Phase 2 acceptance tests for swmf-replicate.

Covers:

* `inspect_artifact(artifact_type="magnetogram")` parses the bundled GONG FITS files.
* `inspect_artifact(artifact_type="ccmc_spec")` extracts typed fields from the bundled
  CCMC `Run information_CCMC.md`.
* `physical_constraints.yaml` `any_of` predicate lets the gold-target restart PARAM pass
  the gate cleanly while still blocking a synthetic broken case.
* Phase 2 rules-directory expansion is present (sofie_mflampa_cme recipe, template,
  derivations, defaults).
* Phase 2 support skills (`swmf-magnetogram`, `swmf-cme-setup`, `swmf-swmfsolar`) are
  fleshed out beyond the Phase 1 stubs.
* `swmf-replicate` SKILL.md documents construction mode and the §6.7 spec→PARAM map.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _import_tool(name: str) -> Any:
    import importlib

    return importlib.import_module(f"swmf_mcp_server.tools.{name}")


def _skill_path(*parts: str) -> Path:
    return _repo_root() / "src" / "agent_assets" / "skills" / Path(*parts)


def _rules_path(*parts: str) -> Path:
    return _skill_path("support", "swmf-params", "rules", *parts)


_ADVICE_NEEDLES = (
    "recommended_next_tool",
    "recommended_workflow",
    "suggested_steps",
    "best_workflow",
)


def _assert_no_advice_leak(payload: Any) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            assert not any(s in key for s in ("recommended_next", "suggested_steps", "best_workflow")), (
                f"Advice field leaked: {key!r}"
            )
            _assert_no_advice_leak(value)
    elif isinstance(payload, list):
        for item in payload:
            _assert_no_advice_leak(item)
    elif isinstance(payload, str):
        for needle in _ADVICE_NEEDLES:
            assert needle not in payload, f"Advice substring leaked: {needle!r}"


# ─────────────────────────────────────────────────────────────────────────────
# Magnetogram inspection — bundled real FITS files
# ─────────────────────────────────────────────────────────────────────────────


class TestMagnetogramInspection:
    def _call(self, path: str) -> dict[str, Any]:
        mod = _import_tool("inspect_artifact")
        return mod.inspect_artifact(
            artifact_type="magnetogram",
            path=path,
            swmf_root=str(_repo_root()),
        )

    def test_gong_fits_in_swmfsolar(self) -> None:
        fits_path = _repo_root().parent / "SWMFSOLAR" / "mrzqs190801t0014c2220_229.fits"
        if not fits_path.is_file():
            pytest.skip(f"FITS file not present at {fits_path}")
        result = self._call(str(fits_path))
        finding = next(
            f for f in result["findings"] if f["kind"] == "magnetogram_classification"
        )
        assert finding["format"] == "fits"
        assert finding["map_type"] == "GONG"
        assert finding["carrington_rotation"] == 2220
        assert finding["observation_time"] is not None
        assert "2019-08-01" in finding["observation_time"]
        assert finding["grid"]["nlon"] == 360
        assert finding["grid"]["nlat"] == 180
        assert finding["evidence_source"] == "fits_header"
        _assert_no_advice_leak(result)

    def test_gong_fits_in_examples(self) -> None:
        fits_path = (
            _repo_root() / "examples" / "CCMC_run_weihao" / "mrzqs230224t1904c2268_303.fits"
        )
        if not fits_path.is_file():
            pytest.skip(f"FITS file not present at {fits_path}")
        result = self._call(str(fits_path))
        finding = next(
            f for f in result["findings"] if f["kind"] == "magnetogram_classification"
        )
        assert finding["format"] == "fits"
        assert finding["map_type"] == "GONG"
        assert finding["carrington_rotation"] == 2268
        assert finding["observation_time"] is not None
        assert "2023-02-24" in finding["observation_time"]
        assert finding["filename_inferred_long0"] == 303
        _assert_no_advice_leak(result)

    def test_filename_only_pattern_inference(self, tmp_path: Path) -> None:
        # A non-FITS placeholder with a GONG-style name still surfaces a CR via filename.
        bogus = tmp_path / "mrzqs240801t0004c2287_235.fits"
        bogus.write_bytes(b"NOT A FITS FILE")
        result = self._call(str(bogus))
        finding = next(
            f for f in result["findings"] if f["kind"] == "magnetogram_classification"
        )
        assert finding["map_type"] == "GONG"
        assert finding["carrington_rotation"] == 2287
        assert finding["filename_inferred_long0"] == 235
        # The format detection looks at file head bytes; bogus content is reported as
        # whichever the extension says rather than blocking the inspector.
        assert finding["format"] in {"fits", "unknown"}


# ─────────────────────────────────────────────────────────────────────────────
# CCMC spec inspection — bundled gold target
# ─────────────────────────────────────────────────────────────────────────────


class TestCcmcSpecInspection:
    def _call(self, path: str) -> dict[str, Any]:
        mod = _import_tool("inspect_artifact")
        return mod.inspect_artifact(
            artifact_type="ccmc_spec",
            path=path,
            swmf_root=str(_repo_root()),
        )

    def test_weihao_spec_fields(self) -> None:
        spec_path = (
            _repo_root() / "examples" / "CCMC_run_weihao" / "Run information_CCMC.md"
        )
        if not spec_path.is_file():
            pytest.skip(f"Spec file not present at {spec_path}")
        result = self._call(str(spec_path))
        summary = next(f for f in result["findings"] if f["kind"] == "ccmc_spec_summary")

        assert summary["run_id"] == "Weihao_Liu_011326_SH_1"
        assert summary["model"] == "SWMF-AWSoM"
        assert summary["event_time_utc"] == "2023-02-24T20:29:00+00:00"
        assert summary["fr_type"] == "GL"

        fr = summary["fr_params"]
        assert fr["longitude"] == 33
        assert fr["latitude"] == 26
        assert fr["fr_orientation"] == 268.62
        assert fr["fr_radius"] == 0.52
        assert fr["fr_bstrength"] == 20.98

        cone = summary["cone_params"]
        assert cone["longitude"] == 20.87
        assert cone["latitude"] == 10.44

        cme = summary["cme_params"]
        assert cme["cme_speed"] == 1276
        assert cme["cme_traveling_time_in_corona"] == 43200
        assert cme["smoothing_factor"] == 2
        assert cme["poynting_ratio"] == 0.4
        assert cme["coronal_heating"] == 1.5

        mflampa = summary["mflampa_params"]
        assert mflampa["nlat"] == 15
        assert mflampa["nlon"] == 15
        assert mflampa["meanfreepath0"] == 0.3
        assert mflampa["spectralindex"] == 5
        assert mflampa["efficency"] == 0.1
        assert mflampa["latmax"] == pytest.approx(36.44)
        assert mflampa["lonmax"] == pytest.approx(53.87)

        # Quick-look list and input/output items present.
        ql = next(f for f in result["findings"] if f["kind"] == "ccmc_spec_quicklook")
        assert any("LASCO C2" in t for t in ql["quicklook_targets"])
        files = next(f for f in result["findings"] if f["kind"] == "ccmc_spec_files")
        assert any("Magnetogram" in t for t in files["input_files_listed"])

        _assert_no_advice_leak(result)


# ─────────────────────────────────────────────────────────────────────────────
# any_of predicate semantics
# ─────────────────────────────────────────────────────────────────────────────


class TestAnyOfPredicate:
    def _call(self, path: str) -> dict[str, Any]:
        mod = _import_tool("inspect_artifact")
        return mod.inspect_artifact(
            artifact_type="param",
            path=path,
            check_rules=True,
            swmf_root=str(_repo_root()),
        )

    def test_weihao_restart_passes_via_include(self) -> None:
        path = (
            _repo_root()
            / "examples"
            / "CCMC_run_weihao"
            / "Weihao_Liu_011326_SH_1_PARAM.expand.restart"
        )
        if not path.is_file():
            pytest.skip(f"Restart PARAM not present at {path}")
        result = self._call(str(path))
        rule_finding = next(
            f for f in result["findings"] if f["kind"] == "rule_violations"
        )
        # The restart PARAM has #CME but no #STARTTIME (it #INCLUDEs RESTART.in).
        # The any_of clause must accept this.
        block_ids = {
            v["rule_id"] for v in rule_finding["rule_violations"] if v["severity"] == "block"
        }
        assert "cme_requires_starttime" not in block_ids
        # Total: gold-target restart should pass with no block-severity violations.
        assert rule_finding["rule_check_summary"]["block"] == 0

    def test_synthetic_broken_still_blocks(self, tmp_path: Path) -> None:
        broken = tmp_path / "broken.in"
        broken.write_text(
            "#DESCRIPTION\nbroken\n\n"
            "#TIMEACCURATE\nF\tIsTimeAccurate\n\n"
            "#BEGIN_COMP SC\n#CME\nGL\tTypeCme\nT\tUseCme\n#END_COMP SC\n\n"
            "#STOP\n-1\tMaxIter\n3600.0\tTimeMax\n\n#END\n",
            encoding="utf-8",
        )
        result = self._call(str(broken))
        rule_finding = next(
            f for f in result["findings"] if f["kind"] == "rule_violations"
        )
        block_ids = {
            v["rule_id"] for v in rule_finding["rule_violations"] if v["severity"] == "block"
        }
        # No #STARTTIME and no #INCLUDE → any_of fails → block.
        assert "cme_requires_starttime" in block_ids


# ─────────────────────────────────────────────────────────────────────────────
# Phase 2 rules-directory expansion
# ─────────────────────────────────────────────────────────────────────────────


def test_phase2_rules_present() -> None:
    # Reshaped in Option-2 refactor: defaults/*.yaml folded into case_recipes
    # and templates/*.yaml replaced by templates/INDEX.md.
    assert _rules_path("case_recipes", "sofie_mflampa_cme.md").is_file()
    assert _rules_path("derivations", "spheromak_shape.yaml").is_file()
    assert _rules_path("templates", "INDEX.md").is_file()
    assert _rules_path("templates", "discovery.md").is_file()
    assert _rules_path("crosswalks", "heating.yaml").is_file()
    assert _rules_path("crosswalks", "grids_amr.yaml").is_file()


def test_geometric_derivations_extended() -> None:
    text = _rules_path("derivations", "geometric.yaml").read_text(encoding="utf-8")
    for needle in (
        "cmebox_from_fr_and_cone",
        "coneih_rotation_from_fr",
        "mflampa_origin_from_spec_ranges",
        "poyntingflux_from_spec_ratio",
        "coronalheating_lperp_from_spec",
        "cme_block_from_spec",
    ):
        assert needle in text, f"derivation '{needle}' missing"


def test_sofie_mflampa_recipe_documents_two_param_split() -> None:
    text = _rules_path("case_recipes", "sofie_mflampa_cme.md").read_text(encoding="utf-8")
    for needle in (
        "PARAM.expand.start",
        "PARAM.expand.restart",
        "Two-PARAM split",
        "AwsomR",
        "MFLAMPA",
        "#CME",
        "#FIELDLINE",
        "Quick-look mapping",
    ):
        assert needle in text


def test_sofie_template_index_references_shipped_param_set() -> None:
    # In Option-2 the template YAMLs are gone; INDEX.md points at *sets* of
    # shipped PARAMs (not forked copies).
    text = _rules_path("templates", "INDEX.md").read_text(encoding="utf-8")
    for needle in (
        "sofie_mflampa_cme",
        "PARAM.sofie",
    ):
        assert needle in text


# ─────────────────────────────────────────────────────────────────────────────
# Skill content updates
# ─────────────────────────────────────────────────────────────────────────────


def test_swmf_magnetogram_skill_full() -> None:
    text = _skill_path("support", "swmf-magnetogram", "SKILL.md").read_text(encoding="utf-8")
    for needle in (
        "--type magnetogram",
        "carrington_rotation",
        "GONG",
        "ADAPT",
        "expected_param_blocks",
        "alignment_concerns",
    ):
        assert needle in text


def test_swmf_cme_setup_skill_full() -> None:
    text = _skill_path("support", "swmf-cme-setup", "SKILL.md").read_text(encoding="utf-8")
    for needle in (
        "TypeCme",
        "SPHEROMAK",
        "two_param_split",
        "spheromak_shape_defaults",
        "case_recipes",
        "derivations",
    ):
        assert needle in text


def test_swmf_swmfsolar_skill_full() -> None:
    text = _skill_path("support", "swmf-swmfsolar", "SKILL.md").read_text(encoding="utf-8")
    for needle in (
        "Makefile targets",
        "change_param.py",
        "change_awsom_param.py",
        "download_ADAPT.py",
        "version_drift_warning",
    ):
        assert needle in text


def test_swmf_replicate_documents_construction_mode() -> None:
    text = _skill_path("swmf-replicate", "SKILL.md").read_text(encoding="utf-8")
    for needle in (
        "Construction mode (Phase 2)",
        "ccmc_spec",
        "Two-PARAM split",
        "PARAM.expand.start",
        "PARAM.expand.restart",
        "authoring ladder",
        "sofie_mflampa_cme",
        "Surface translations",
    ):
        assert needle in text
