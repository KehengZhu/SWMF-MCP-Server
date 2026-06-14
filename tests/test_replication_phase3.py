"""Phase 3 acceptance tests for swmf-replicate.

Covers:

* `inspect_artifact(artifact_type="paper_spec")` loads agent-authored JSON/YAML and
  surfaces typed fields without inventing.
* MCP does not parse PDFs — given a `.pdf` path the inspector reports a parse
  error or missing-fields finding rather than synthesising values.
* `confidence_per_field` and `source_paper_path` are recorded verbatim under
  `paper_spec_provenance`.
* Missing canonical fields (silent paper) surface under `paper_spec_missing_fields`.
* The `paper_spec` shape matches `ccmc_spec` for downstream merging.
* `swmf-replicate` SKILL.md documents the `intent="paper"` workflow end-to-end.
* `swmf-validation` SKILL.md is fleshed out beyond the Phase 1 stub: it documents
  validation methods, output contract, anti-patterns, and the boundary against
  image-similarity adjudication.
"""
from __future__ import annotations

import json
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


def _call_paper_spec(path: str) -> dict[str, Any]:
    mod = _import_tool("inspect_artifact")
    return mod.inspect_artifact(
        artifact_type="paper_spec",
        path=path,
        swmf_root=str(_repo_root()),
    )


# ─────────────────────────────────────────────────────────────────────────────
# JSON paper_spec loading
# ─────────────────────────────────────────────────────────────────────────────


_GOOD_PAPER_SPEC: dict[str, Any] = {
    "run_id": "sokolov2023_2023-02-24",
    "model": "AWSoM-R + MFLAMPA",
    "model_version": "v2.0",
    "event_time_utc": "2023-02-24T20:30:00+00:00",
    "fr_type": "GL",
    "fr_params": {
        "longitude_deg": 33.0,
        "latitude_deg": 26.0,
        "fr_orientation": 268.62,
        "fr_radius": 0.52,
        "fr_bstrength": 20.98,
    },
    "cone_params": {"longitude_deg": 20.87, "latitude_deg": 10.44, "half_width_deg": 30.0},
    "cme_params": {"speed_km_s": 1276, "mass_g": 1.5e16},
    "mflampa_params": {"nlat": 15, "nlon": 15, "spectral_index": 5},
    "metadata": {"magnetogram_source": "ADAPT", "carrington_rotation": 2266},
    "input_files_listed": ["adapt_2023022420_xx.fts.gz"],
    "output_files_listed": [],
    "quicklook_targets": ["LASCO_C2_base_difference_movie", "OMNI_density_L1"],
    "source_paper_path": "/abs/path/to/sokolov2023.pdf",
    "confidence_per_field": {
        "fr_type": "high",
        "fr_params": "medium",
        "event_time_utc": "high",
        "magnetogram_source": "low",
    },
}


class TestPaperSpecJsonLoading:
    def test_typed_fields_surface(self, tmp_path: Path) -> None:
        spec_path = tmp_path / "paper_spec.json"
        spec_path.write_text(json.dumps(_GOOD_PAPER_SPEC), encoding="utf-8")
        result = _call_paper_spec(str(spec_path))
        summary = next(f for f in result["findings"] if f["kind"] == "paper_spec_summary")

        assert summary["run_id"] == "sokolov2023_2023-02-24"
        assert summary["model"] == "AWSoM-R + MFLAMPA"
        assert summary["model_version"] == "v2.0"
        assert summary["event_time_utc"] == "2023-02-24T20:30:00+00:00"
        assert summary["fr_type"] == "GL"
        assert summary["fr_params"]["longitude_deg"] == 33.0
        assert summary["cme_params"]["speed_km_s"] == 1276
        assert summary["mflampa_params"]["nlat"] == 15
        assert summary["metadata"]["carrington_rotation"] == 2266
        assert summary["source_paper_path"] == "/abs/path/to/sokolov2023.pdf"

        _assert_no_advice_leak(result)

    def test_provenance_finding_records_confidence(self, tmp_path: Path) -> None:
        spec_path = tmp_path / "paper_spec.json"
        spec_path.write_text(json.dumps(_GOOD_PAPER_SPEC), encoding="utf-8")
        result = _call_paper_spec(str(spec_path))
        prov = next(f for f in result["findings"] if f["kind"] == "paper_spec_provenance")

        assert prov["source_paper_path"] == "/abs/path/to/sokolov2023.pdf"
        assert prov["confidence_per_field"]["fr_type"] == "high"
        assert prov["confidence_per_field"]["magnetogram_source"] == "low"

    def test_files_and_quicklook_findings(self, tmp_path: Path) -> None:
        spec_path = tmp_path / "paper_spec.json"
        spec_path.write_text(json.dumps(_GOOD_PAPER_SPEC), encoding="utf-8")
        result = _call_paper_spec(str(spec_path))

        files = next(f for f in result["findings"] if f["kind"] == "paper_spec_files")
        assert "adapt_2023022420_xx.fts.gz" in files["input_files_listed"]

        ql = next(f for f in result["findings"] if f["kind"] == "paper_spec_quicklook")
        assert "LASCO_C2_base_difference_movie" in ql["quicklook_targets"]
        assert "OMNI_density_L1" in ql["quicklook_targets"]

    def test_no_missing_fields_when_complete(self, tmp_path: Path) -> None:
        spec_path = tmp_path / "paper_spec.json"
        spec_path.write_text(json.dumps(_GOOD_PAPER_SPEC), encoding="utf-8")
        result = _call_paper_spec(str(spec_path))
        kinds = {f["kind"] for f in result["findings"]}
        assert "paper_spec_missing_fields" not in kinds


# ─────────────────────────────────────────────────────────────────────────────
# Missing fields and silent paper
# ─────────────────────────────────────────────────────────────────────────────


class TestPaperSpecMissingFields:
    def test_silent_paper_surfaces_gaps(self, tmp_path: Path) -> None:
        # Spec with only run_id and model — every other canonical field absent.
        partial = {"run_id": "anon_2024", "model": "AWSoM-R"}
        spec_path = tmp_path / "paper_spec.json"
        spec_path.write_text(json.dumps(partial), encoding="utf-8")
        result = _call_paper_spec(str(spec_path))
        missing = next(f for f in result["findings"] if f["kind"] == "paper_spec_missing_fields")
        # event_time_utc / fr_type / fr_params / etc. are all absent → reported.
        for needle in ("event_time_utc", "fr_type", "fr_params", "cme_params"):
            assert needle in missing["missing_fields"]

    def test_no_invention_for_missing_fields(self, tmp_path: Path) -> None:
        # MCP must report None for absent fields, never fabricate values.
        partial = {"run_id": "anon_2024"}
        spec_path = tmp_path / "paper_spec.json"
        spec_path.write_text(json.dumps(partial), encoding="utf-8")
        result = _call_paper_spec(str(spec_path))
        summary = next(f for f in result["findings"] if f["kind"] == "paper_spec_summary")
        # All MCP-loaded fields except run_id should be None / empty.
        assert summary["model"] is None
        assert summary["fr_type"] is None
        assert summary["event_time_utc"] is None
        assert summary["fr_params"] == {}
        assert summary["cme_params"] == {}


# ─────────────────────────────────────────────────────────────────────────────
# YAML loading + parse-error surfacing
# ─────────────────────────────────────────────────────────────────────────────


class TestPaperSpecYamlAndErrors:
    def test_yaml_loads(self, tmp_path: Path) -> None:
        spec_path = tmp_path / "paper_spec.yaml"
        spec_path.write_text(
            "run_id: sokolov2023_2023-02-24\n"
            "model: AWSoM-R + MFLAMPA\n"
            "fr_type: GL\n"
            "fr_params:\n"
            "  longitude_deg: 33.0\n"
            "  latitude_deg: 26.0\n"
            "source_paper_path: /abs/path/to/sokolov2023.pdf\n"
            "confidence_per_field:\n"
            "  fr_type: high\n",
            encoding="utf-8",
        )
        result = _call_paper_spec(str(spec_path))
        summary = next(f for f in result["findings"] if f["kind"] == "paper_spec_summary")
        assert summary["fr_type"] == "GL"
        assert summary["fr_params"]["longitude_deg"] == 33.0

    def test_pdf_path_does_not_parse_as_spec(self, tmp_path: Path) -> None:
        # MCP must NOT parse PDFs. Pointing the inspector at a fake PDF should
        # produce parse errors rather than synthesised fields.
        pdf_path = tmp_path / "paper.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\nbinary garbage here\n")
        result = _call_paper_spec(str(pdf_path))
        kinds = {f["kind"] for f in result["findings"]}
        assert "paper_spec_parse_errors" in kinds
        # And no synthesised values: summary fields are all None.
        summary = next(f for f in result["findings"] if f["kind"] == "paper_spec_summary")
        assert summary["run_id"] is None
        assert summary["fr_type"] is None
        assert summary["source_paper_path"] is None

    def test_missing_file(self) -> None:
        result = _call_paper_spec("/nonexistent/path/paper_spec.json")
        kinds = {f["kind"] for f in result["findings"]}
        assert "paper_spec_not_found" in kinds


# ─────────────────────────────────────────────────────────────────────────────
# Shape parity with ccmc_spec — downstream merge target
# ─────────────────────────────────────────────────────────────────────────────


class TestPaperSpecShapeMirrorsCcmcSpec:
    """The ccmc_spec_summary and paper_spec_summary findings must share the
    same canonical key set so the swmf-replicate construction-mode logic can
    branch on intent without re-parsing.
    """

    def test_summary_keys_overlap(self, tmp_path: Path) -> None:
        spec_path = tmp_path / "paper_spec.json"
        spec_path.write_text(json.dumps(_GOOD_PAPER_SPEC), encoding="utf-8")
        result = _call_paper_spec(str(spec_path))
        summary = next(f for f in result["findings"] if f["kind"] == "paper_spec_summary")

        for key in (
            "run_id",
            "model",
            "model_version",
            "event_time_utc",
            "fr_type",
            "fr_params",
            "cone_params",
            "cme_params",
            "mflampa_params",
            "metadata",
        ):
            assert key in summary, f"paper_spec_summary missing canonical key '{key}'"

    def test_paper_only_keys_present(self, tmp_path: Path) -> None:
        spec_path = tmp_path / "paper_spec.json"
        spec_path.write_text(json.dumps(_GOOD_PAPER_SPEC), encoding="utf-8")
        result = _call_paper_spec(str(spec_path))
        summary = next(f for f in result["findings"] if f["kind"] == "paper_spec_summary")
        # paper_spec adds source_paper_path on the summary; confidence_per_field
        # is on the provenance finding.
        assert "source_paper_path" in summary


# ─────────────────────────────────────────────────────────────────────────────
# inspect_artifact contract surface
# ─────────────────────────────────────────────────────────────────────────────


def test_paper_spec_in_valid_artifact_types() -> None:
    mod = _import_tool("inspect_artifact")
    assert "paper_spec" in mod._VALID_ARTIFACT_TYPES


def test_paper_spec_known_unknowns_documents_no_pdf_parsing(tmp_path: Path) -> None:
    spec_path = tmp_path / "paper_spec.json"
    spec_path.write_text(json.dumps(_GOOD_PAPER_SPEC), encoding="utf-8")
    result = _call_paper_spec(str(spec_path))
    notes = " ".join(result["uncertainty"]["known_unknowns"]).lower()
    assert "paper pdf" in notes or "pdfs" in notes
    assert "confidence" in notes


# ─────────────────────────────────────────────────────────────────────────────
# Skill content — swmf-replicate paper intent + swmf-validation Phase 3
# ─────────────────────────────────────────────────────────────────────────────


def test_replicate_skill_documents_paper_intent_full_workflow() -> None:
    text = _skill_path("swmf-replicate", "SKILL.md").read_text(encoding="utf-8")
    # Paper-intent section heading exists.
    assert "## Paper intent" in text
    # The agent calls the paper_spec inspector.
    assert "swmf inspect --type paper_spec" in text
    # Confidence-per-field is documented as required output.
    assert "confidence_per_field" in text
    # Missing-fields discipline is documented.
    assert "paper_spec_missing_fields" in text
    # The CLI does not parse PDFs is explicitly stated.
    assert "the swmf CLI does not parse PDFs" in text
    # Phase 3 wired (status mark may be either "(current)" or just present after Phase 4+).
    assert "Phase 3" in text


def test_validation_skill_fleshed_out_beyond_phase1_stub() -> None:
    text = _skill_path("support", "swmf-validation", "SKILL.md").read_text(encoding="utf-8")
    # No longer a Phase 1 stub.
    assert "Phase 1 stub" not in text
    # Validation method enum present.
    for needle in (
        "deterministic_diff",
        "numerical_metric",
        "idl_overlay",
        "user_visual_confirmation",
    ):
        assert needle in text, f"validation method '{needle}' missing"
    # Output contract carries the required fields.
    for needle in (
        "target_id",
        "reference_artifact",
        "modeled_artifact",
        "comparison_method",
        "provenance_lane",
    ):
        assert needle in text, f"output contract field '{needle}' missing"
    # Anti-patterns include image-similarity rejection and OMNI deferral.
    assert "Image-similarity-as-deterministic-evidence" in text
    assert "compare_insitu.py" in text
    # Boundary against `swmf compare --comparison-type reference` is stated.
    assert "--comparison-type reference" in text
