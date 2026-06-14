"""End-to-end regression for the Liu et al. 2026 #CURLB0 failure mode.

This is the test that justifies the entire Option-2 refactor:

The Xianyu26Paper/replication_v3 PARAM.in (the pre-refactor agent attempt)
silently omitted #CURLB0 because the rules layer's mined `_required.yaml`
files didn't list it for the awsom_steady_sc_only archetype (only 2 corpus
files in that mined slice). After the refactor, three guards together
should prevent silent omission:

1. The agent reads PARAM.XML's SCHEME PARAMETERS commandgroup before
   authoring the B0 / scheme block. The new `xml_scope="commandgroup:..."`
   surface returns `#CURLB0` with parameters and defaults.
2. The crosswalk `rules/crosswalks/sources_and_b0.yaml` maps the paper's
   "source surface at 2.5 R⊙" phrase to `#CURLB0.rCurrentFreeB0`.
3. The XML audit gate refuses to bless a PARAM.in for launch when any
   commandgroup containing an emitted command was never read this session.

These three guards each test a separate failure mode (discovery, paper
phrase mapping, post-hoc enforcement).
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from swmf_mcp_server.audit import (
    audit_param_against_xml_reads,
    derive_group_key,
    get_audit_store,
    record_commandgroup_read,
    reset_audit_store,
)
from swmf_mcp_server.parsing.xml_parser import parse_param_xml_file
from swmf_mcp_server.tools.inspect_artifact import inspect_artifact


_SWMF_ROOT = Path("/Users/zkeheng/SWMFSoftware/SWMF")
_PARAM_XML = _SWMF_ROOT / "SC" / "BATSRUS" / "PARAM.XML"
_CROSSWALKS = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "agent_assets"
    / "skills"
    / "support"
    / "swmf-params"
    / "rules"
    / "crosswalks"
    / "sources_and_b0.yaml"
)


pytestmark = pytest.mark.skipif(
    not _PARAM_XML.is_file(),
    reason="SC/BATSRUS/PARAM.XML not present; live-XML regression skipped.",
)


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_audit_store()


def test_curlb0_is_discoverable_via_commandgroup_xml_scope() -> None:
    """Guard 1: PARAM.XML access surfaces #CURLB0 when the agent reads the
    SCHEME PARAMETERS commandgroup. Pre-refactor, the agent had no
    discovery channel and never saw the command."""
    result = inspect_artifact(
        artifact_type="xml",
        path=str(_PARAM_XML),
        xml_scope="commandgroup:SCHEME PARAMETERS",
        swmf_root=str(_SWMF_ROOT),
    )
    findings = result.get("findings", [])
    assert findings, "commandgroup query returned no findings"
    finding = findings[0]
    assert finding.get("kind") == "commandgroup_contents"
    commands_in_group = [c["name"] for c in finding.get("commands", [])]
    assert "#CURLB0" in commands_in_group, (
        "PARAM.XML SCHEME PARAMETERS group must surface #CURLB0; the new "
        "xml_scope='commandgroup:...' channel is what closes the discovery "
        "gap from Liu et al. 2026."
    )

    # Verify the rCurrentFreeB0 parameter is in the parsed schema with the
    # 2.5 R⊙ default the paper's "source surface" wording refers to.
    curlb0 = next(c for c in finding["commands"] if c["name"] == "#CURLB0")
    rcurrent_param = next(
        (p for p in curlb0["parameters"] if p.get("name") == "rCurrentFreeB0"),
        None,
    )
    assert rcurrent_param is not None
    assert rcurrent_param.get("default") == "2.5", (
        f"#CURLB0.rCurrentFreeB0 default should be 2.5 R⊙; got "
        f"{rcurrent_param.get('default')!r}"
    )


def test_crosswalk_maps_source_surface_to_curlb0() -> None:
    """Guard 2: the crosswalk rules layer maps the paper's natural-language
    phrase ('source surface at 2.5 R⊙') to #CURLB0.rCurrentFreeB0, so the
    agent finds the command even if it skipped the XML read."""
    data = yaml.safe_load(_CROSSWALKS.read_text(encoding="utf-8"))
    crosswalks = data.get("crosswalks", [])
    matching = [
        entry for entry in crosswalks
        if any("source surface" in p.lower() for p in entry.get("phrases", []))
    ]
    assert matching, "no crosswalk entry mentions 'source surface'"
    entry = matching[0]
    assert any(
        "#CURLB0" in cmd for cmd in entry.get("commands", [])
    ), f"crosswalk does not map source-surface phrase to #CURLB0: {entry}"


def test_audit_gate_blocks_curlb0_omission() -> None:
    """Guard 3: even if guards 1 and 2 fail to fire, the XML audit gate
    blocks launch when #CURLB0 is emitted without the agent having read
    the SCHEME PARAMETERS commandgroup."""
    # Build a minimal catalog from the live PARAM.XML.
    from swmf_mcp_server.core.models import SourceCatalog
    import time
    commands = parse_param_xml_file(_PARAM_XML, component="SC")
    catalog_commands = {cmd.normalized: [cmd] for cmd in commands}
    catalog = SourceCatalog(
        swmf_root=str(_SWMF_ROOT),
        built_at_epoch_s=time.time(),
        commands=catalog_commands,
        components={},
        templates=[],
        scripts=[],
        idl_macros=[],
        source_files=[],
    )

    store = get_audit_store()
    # Simulate the Liu 2026 failure: agent read STAND ALONE MODE but skipped
    # SCHEME PARAMETERS.
    record_commandgroup_read(
        store, session_id=None, component=None, group_name="STAND ALONE MODE"
    )

    result = audit_param_against_xml_reads(
        catalog,
        param_commands_by_component={"SC": ["#CURLB0", "#SCHEME"]},
        reads=store.get_reads(None),
    )

    assert result["ok"] is False
    violations = result["audit_violations"]
    assert any(
        v["commandgroup_key"] == "SC:SCHEME PARAMETERS"
        for v in violations
    ), f"audit gate should block on unread SCHEME PARAMETERS, got: {violations}"


def test_curlb0_discoverable_path_records_to_audit_store() -> None:
    """Integration: calling inspect_artifact with the new xml_scope
    automatically records the commandgroup in the audit store, so that
    the subsequent param launch-gate cross-reference passes."""
    inspect_artifact(
        artifact_type="xml",
        path=str(_PARAM_XML),
        xml_scope="commandgroup:SCHEME PARAMETERS",
        swmf_root=str(_SWMF_ROOT),
    )
    reads = get_audit_store().get_reads(None)
    key = derive_group_key("SC", "SCHEME PARAMETERS")
    assert key in reads, (
        f"inspect_artifact(xml_scope='commandgroup:SCHEME PARAMETERS') did "
        f"not record audit read; expected key {key!r}, store has {reads!r}"
    )
