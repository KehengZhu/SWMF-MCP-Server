"""Acceptance tests for the PARAM-corpus miner.

The miner lives at `scripts/mine_param_corpus.py` and produces the
`defaults/mined/` lane of the rules layer. Tests cover:

* smoke: miner runs against the real SWMF/SWMFSOLAR corpus and emits expected files.
* boundary: miner rejects any input path that resolves under `SWMFSOLAR/Run_*/`.
* determinism: two consecutive runs produce byte-identical output.
* archetype routing: every SWMFSOLAR shipped PARAM matches at most one archetype
  entry (no silent ambiguity loss).
* paper_spec: precedent_hint and numerics_phrases fields round-trip.

The tests do not modify the live rules directory — each run goes to a tmp dir.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml  # type: ignore[import-untyped]


_REPO_ROOT = Path(__file__).resolve().parents[1]
_MINER_PATH = _REPO_ROOT / "scripts" / "mine_param_corpus.py"
_RULES_DIR = (
    _REPO_ROOT
    / "src"
    / "agent_assets"
    / "skills"
    / "support"
    / "swmf-params"
    / "rules"
)

_SWMF_ROOT_ENV = os.environ.get("SWMF_ROOT")
_SWMFSOLAR_ROOT_ENV = os.environ.get("SWMFSOLAR_ROOT")


def _resolve_swmf_root() -> Path | None:
    if _SWMF_ROOT_ENV:
        p = Path(_SWMF_ROOT_ENV).expanduser()
        return p if p.is_dir() else None
    for cand in (_REPO_ROOT / "SWMF", _REPO_ROOT.parent / "SWMF"):
        if cand.is_dir() and (cand / "Config.pl").is_file():
            return cand
    return None


def _resolve_swmfsolar_root() -> Path | None:
    if _SWMFSOLAR_ROOT_ENV:
        p = Path(_SWMFSOLAR_ROOT_ENV).expanduser()
        return p if p.is_dir() else None
    for cand in (_REPO_ROOT / "SWMFSOLAR", _REPO_ROOT.parent / "SWMFSOLAR"):
        if cand.is_dir():
            return cand
    return None


_SWMF_ROOT = _resolve_swmf_root()
_SWMFSOLAR_ROOT = _resolve_swmfsolar_root()
_HAS_CORPUS = _SWMF_ROOT is not None


pytestmark = pytest.mark.skipif(
    not _HAS_CORPUS,
    reason="SWMF source tree not available (set SWMF_ROOT or place SWMF/ adjacent to repo)",
)


def _run_miner(output_dir: Path, *, swmfsolar_root: Path | None = None) -> subprocess.CompletedProcess[str]:
    args = [
        sys.executable, str(_MINER_PATH),
        "--swmf-root", str(_SWMF_ROOT),
        "--output-dir", str(output_dir),
    ]
    if swmfsolar_root is not None:
        args.extend(["--swmfsolar-root", str(swmfsolar_root)])
    elif _SWMFSOLAR_ROOT is not None:
        args.extend(["--swmfsolar-root", str(_SWMFSOLAR_ROOT)])
    return subprocess.run(args, capture_output=True, text=True)


# ─────────────────────────────────────────────────────────────────────────────
# Smoke
# ─────────────────────────────────────────────────────────────────────────────


class TestMinerSmoke:
    def test_miner_runs_clean(self, tmp_path: Path) -> None:
        out = tmp_path / "mined"
        proc = _run_miner(out)
        assert proc.returncode == 0, proc.stderr
        assert out.is_dir()
        assert (out / "mining_report.md").is_file()
        assert (out / "equation_set_required.yaml").is_file()
        # At least one archetype-required file should be present given a real corpus.
        required_files = sorted(out.glob("*_required.yaml"))
        assert required_files, f"no _required.yaml emitted; stderr={proc.stderr}"

    def test_required_yaml_shape(self, tmp_path: Path) -> None:
        out = tmp_path / "mined"
        proc = _run_miner(out)
        assert proc.returncode == 0, proc.stderr
        for fp in out.glob("*_required.yaml"):
            if fp.name == "equation_set_required.yaml":
                continue
            data = yaml.safe_load(fp.read_text(encoding="utf-8"))
            assert data["archetype"] == fp.stem.removesuffix("_required")
            assert isinstance(data["required_commands"], list)
            assert isinstance(data["strict_intersection"], list)
            assert data["provenance"].startswith("mined:intersection_")
            assert 0.0 < data["threshold"] <= 1.0

    def test_equation_set_includes_awsom_anisopi(self, tmp_path: Path) -> None:
        out = tmp_path / "mined"
        proc = _run_miner(out)
        assert proc.returncode == 0, proc.stderr
        data = yaml.safe_load((out / "equation_set_required.yaml").read_text(encoding="utf-8"))
        modules = data["modules"]
        assert "AwsomAnisoPi" in modules, list(modules)[:10]
        cmds = set(modules["AwsomAnisoPi"]["required_commands"])
        # Var → command mapping must surface the AnisoPi-keyed physics block.
        assert "#ANISOTROPICPRESSURE" in cmds
        assert "#HEATFLUXCOLLISIONLESS" in cmds
        # Ehot bins should also fire the Spitzer + semi-implicit stack.
        assert "#HEATCONDUCTION" in cmds
        assert "#SEMIIMPLICIT" in cmds
        assert "#SEMIKRYLOV" in cmds


# ─────────────────────────────────────────────────────────────────────────────
# Boundary
# ─────────────────────────────────────────────────────────────────────────────


class TestCorpusBoundary:
    def test_rejects_run_dir_path(self, tmp_path: Path) -> None:
        fake = tmp_path / "fake_swmfsolar" / "Run_Foobar"
        (fake / "Param").mkdir(parents=True)
        (fake / "Param" / "PARAM.in.toy").write_text("#STOP\n0  MaxIter\n", encoding="utf-8")
        out = tmp_path / "mined"
        proc = _run_miner(out, swmfsolar_root=fake)
        assert proc.returncode != 0, (
            f"miner should reject Run_*/ path but exited 0; stderr={proc.stderr}"
        )
        assert "corpus-boundary error" in proc.stderr.lower() or \
               "corpus-boundary error" in proc.stdout.lower()


# ─────────────────────────────────────────────────────────────────────────────
# Determinism
# ─────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_two_runs_byte_identical(self, tmp_path: Path) -> None:
        out_a = tmp_path / "mined_a"
        out_b = tmp_path / "mined_b"
        proc_a = _run_miner(out_a)
        proc_b = _run_miner(out_b)
        assert proc_a.returncode == 0 and proc_b.returncode == 0
        names = sorted(p.name for p in out_a.iterdir())
        # mining_report.md varies if file ordering changes; check it too.
        assert names == sorted(p.name for p in out_b.iterdir())
        for name in names:
            text_a = (out_a / name).read_text(encoding="utf-8")
            text_b = (out_b / name).read_text(encoding="utf-8")
            assert text_a == text_b, f"{name} differs between two miner runs"


# ─────────────────────────────────────────────────────────────────────────────
# Archetype routing
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.skipif(_SWMFSOLAR_ROOT is None, reason="SWMFSOLAR not available")
class TestArchetypeRouting:
    def test_archetypes_yaml_is_a_list(self) -> None:
        data = yaml.safe_load((_RULES_DIR / "archetypes.yaml").read_text(encoding="utf-8"))
        assert isinstance(data, list) and data, "archetypes.yaml must be a non-empty list"
        ids = [str(entry["id"]) for entry in data]
        assert len(ids) == len(set(ids)), f"duplicate archetype ids: {ids}"

    def test_no_swmfsolar_param_matches_two_archetypes(self, tmp_path: Path) -> None:
        """Every shipped SWMFSOLAR/Param/PARAM.in.* should resolve to one archetype
        (or be reported as unmatched — what is forbidden is silent ambiguity)."""
        out = tmp_path / "mined"
        proc = _run_miner(out)
        assert proc.returncode == 0, proc.stderr
        # Read the mining report: each PARAM appears in at most one archetype row.
        report = (out / "mining_report.md").read_text(encoding="utf-8")
        # Build a set of PARAM filenames listed in the coverage table.
        coverage_section, _, _ = report.partition("## Unmatched PARAMs")
        listed: list[str] = []
        for line in coverage_section.splitlines():
            if line.startswith("|") and "PARAM.in." in line:
                listed.extend(
                    tok.strip()
                    for tok in line.split("|")[-2].split(",")
                    if "PARAM.in." in tok
                )
        # SWMFSOLAR-shipped files we expect to see at least once in coverage.
        expected = {
            "PARAM.in.awsom",
            "PARAM.in.awsom.CME",
            "PARAM.in.awsomr.CME",
            "PARAM.in.sofie.MFLAMPA",
        }
        for name in expected:
            occurrences = [item for item in listed if item == name]
            assert len(occurrences) <= 1, (
                f"{name} appears in {len(occurrences)} archetype rows: "
                "silent ambiguity is forbidden"
            )


# ─────────────────────────────────────────────────────────────────────────────
# paper_spec extension
# ─────────────────────────────────────────────────────────────────────────────


class TestPaperSpecExtensions:
    @staticmethod
    def _parse(text: str) -> dict:
        from swmf_mcp_server.parsing.paper_spec import parse_paper_spec_text
        return parse_paper_spec_text(text)

    def test_backwards_compat_no_new_fields(self) -> None:
        result = self._parse('{"run_id": "old", "model": "AWSoM"}')
        assert result["precedent_hint"] == []
        assert result["numerics_phrases"] == []
        # The new keys must not poison unparsed_keys.
        assert "precedent_hint" not in result["unparsed_keys"]
        assert "numerics_phrases" not in result["unparsed_keys"]

    def test_precedent_hint_round_trip(self) -> None:
        result = self._parse(
            '{"precedent_hint": ["Sokolov2021", "Manchester2022"]}'
        )
        assert result["precedent_hint"] == ["Sokolov2021", "Manchester2022"]

    def test_numerics_phrases_round_trip(self) -> None:
        result = self._parse(
            '{"numerics_phrases": ["Spitzer beyond 5 R_sun", "MP5 outer"]}'
        )
        assert result["numerics_phrases"] == ["Spitzer beyond 5 R_sun", "MP5 outer"]

    def test_wrong_type_surfaces_parse_error(self) -> None:
        result = self._parse('{"precedent_hint": "not-a-list"}')
        errors = result.get("parse_errors", [])
        assert any("precedent_hint" in e for e in errors), errors

    def test_null_is_normalized_to_empty_list(self) -> None:
        result = self._parse('{"precedent_hint": null, "numerics_phrases": null}')
        assert result["precedent_hint"] == []
        assert result["numerics_phrases"] == []


# ─────────────────────────────────────────────────────────────────────────────
# Skill wiring
# ─────────────────────────────────────────────────────────────────────────────


class TestSkillWiring:
    def test_swmf_replicate_references_corpus_diff_step(self) -> None:
        skill_md = _REPO_ROOT / "src" / "agent_assets" / "skills" / "swmf-replicate" / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        assert "Corpus diff (mandatory)" in text, "corpus-diff step missing from swmf-replicate"
        assert "defaults/mined/" in text, "mined-defaults lane not referenced"
        assert "equation_set_required.yaml" in text, "equation-set mapping not referenced"

    def test_swmf_replicate_references_archetype_catalog(self) -> None:
        skill_md = _REPO_ROOT / "src" / "agent_assets" / "skills" / "swmf-replicate" / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        assert "archetypes.yaml" in text, "archetype catalog not referenced"

    def test_no_run_max_rp_references(self) -> None:
        """Per the corpus boundary, Run_Max_RP_CME3 must not appear in any
        skill / rules markdown."""
        bases = [
            _REPO_ROOT / "src" / "agent_assets" / "skills",
        ]
        offenders: list[Path] = []
        for base in bases:
            for fp in base.rglob("*.md"):
                if "Run_Max_RP" in fp.read_text(encoding="utf-8"):
                    offenders.append(fp)
            for fp in base.rglob("*.yaml"):
                if "Run_Max_RP" in fp.read_text(encoding="utf-8"):
                    offenders.append(fp)
        assert not offenders, f"Run_Max_RP_* still referenced in: {offenders}"

    def test_awsom_cme_template_uses_shipped_param(self) -> None:
        manifest = _RULES_DIR / "templates" / "awsom_cme.yaml"
        data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
        for key in ("start_template", "restart_template"):
            assert "Run_" not in str(data[key]), f"{key} references Run_*: {data[key]}"
            assert str(data[key]).startswith("SWMFSOLAR/Param/"), (
                f"{key} should point at shipped SWMFSOLAR/Param/: {data[key]}"
            )
