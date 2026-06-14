"""Unit tests for the XML audit gate (Part A3 of the Option-2 refactor)."""
from __future__ import annotations

import time

import pytest

from swmf_mcp_server.audit import (
    audit_param_against_xml_reads,
    derive_group_key,
    get_audit_store,
    record_commandgroup_read,
    reset_audit_store,
)
from swmf_mcp_server.core.models import (
    CommandMetadata,
    ComponentVersion,
    SourceCatalog,
)


def _make_catalog() -> SourceCatalog:
    curlb0 = CommandMetadata(
        name="CURLB0",
        normalized="#CURLB0",
        component="SC",
        description=None,
        commandgroup="SCHEME PARAMETERS",
    )
    description = CommandMetadata(
        name="DESCRIPTION",
        normalized="#DESCRIPTION",
        component=None,
        description=None,
        commandgroup="STAND ALONE MODE",
    )
    saveplot = CommandMetadata(
        name="SAVEPLOT",
        normalized="#SAVEPLOT",
        component="SC",
        description=None,
        commandgroup="OUTPUT PARAMETERS",
    )
    return SourceCatalog(
        swmf_root="/fake/SWMF",
        built_at_epoch_s=time.time(),
        commands={
            "#CURLB0": [curlb0],
            "#DESCRIPTION": [description],
            "#SAVEPLOT": [saveplot],
        },
        components={"SC": ComponentVersion(component="SC", versions=["BATSRUS"])},
        templates=[],
        scripts=[],
        idl_macros=[],
        source_files=[],
    )


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_audit_store()


def test_derive_group_key_normalizes_case_and_component() -> None:
    assert derive_group_key("sc", "Scheme Parameters") == "SC:SCHEME PARAMETERS"
    assert derive_group_key(None, "Stand Alone Mode") == "TOP:STAND ALONE MODE"
    assert derive_group_key("SC", None) is None
    assert derive_group_key("SC", "") is None


def test_recording_then_audit_succeeds_for_read_group() -> None:
    catalog = _make_catalog()
    store = get_audit_store()

    record_commandgroup_read(
        store, session_id=None, component="SC", group_name="SCHEME PARAMETERS"
    )
    record_commandgroup_read(
        store, session_id=None, component=None, group_name="STAND ALONE MODE"
    )
    record_commandgroup_read(
        store, session_id=None, component="SC", group_name="OUTPUT PARAMETERS"
    )

    result = audit_param_against_xml_reads(
        catalog,
        param_commands_by_component={
            None: ["#DESCRIPTION"],
            "SC": ["#CURLB0", "#SAVEPLOT"],
        },
        reads=store.get_reads(None),
    )

    assert result["ok"] is True
    assert result["audit_violations"] == []
    assert "SC:SCHEME PARAMETERS" in result["groups_read"]


def test_unread_group_blocks_audit() -> None:
    """Reproduces the Liu et al. 2026 #CURLB0 failure mode."""
    catalog = _make_catalog()
    store = get_audit_store()

    # Agent reads STAND ALONE MODE but skips SCHEME PARAMETERS — exactly the
    # original Liu 2026 mistake. The audit must catch this.
    record_commandgroup_read(
        store, session_id=None, component=None, group_name="STAND ALONE MODE"
    )

    result = audit_param_against_xml_reads(
        catalog,
        param_commands_by_component={
            None: ["#DESCRIPTION"],
            "SC": ["#CURLB0"],
        },
        reads=store.get_reads(None),
    )

    assert result["ok"] is False
    assert len(result["audit_violations"]) == 1
    violation = result["audit_violations"][0]
    assert violation["commandgroup_key"] == "SC:SCHEME PARAMETERS"
    assert "#CURLB0" in violation["commands"]
    assert "SC:SCHEME PARAMETERS" in result["groups_required"]


def test_explicit_waiver_clears_violation() -> None:
    catalog = _make_catalog()
    store = get_audit_store()
    record_commandgroup_read(
        store, session_id=None, component=None, group_name="STAND ALONE MODE"
    )

    result = audit_param_against_xml_reads(
        catalog,
        param_commands_by_component={None: ["#DESCRIPTION"], "SC": ["#CURLB0"]},
        reads=store.get_reads(None),
        waivers=["SC:SCHEME PARAMETERS"],
    )

    assert result["ok"] is True
    assert result["audit_violations"] == []
    assert "SC:SCHEME PARAMETERS" in result["groups_waived"]


def test_unknown_commands_do_not_block() -> None:
    catalog = _make_catalog()
    # Command not in catalog (typo / fresh command). The audit should not
    # surface it as a violation — that's xml_corrections.md territory.
    result = audit_param_against_xml_reads(
        catalog,
        param_commands_by_component={"SC": ["#FRESHCOMMAND"]},
        reads=set(),
    )
    assert result["ok"] is True


def test_audit_store_resets_between_sessions(tmp_path) -> None:
    # Sessions are keyed by run directory; the disk store persists state under
    # each run dir's .swmf_ai/audit.json.
    store = get_audit_store()
    dir_a = str(tmp_path / "runA")
    dir_b = str(tmp_path / "runB")
    record_commandgroup_read(store, session_id=dir_a, component="SC", group_name="SCHEME PARAMETERS")
    record_commandgroup_read(store, session_id=dir_b, component="SC", group_name="OUTPUT PARAMETERS")
    assert store.get_reads(dir_a) == {"SC:SCHEME PARAMETERS"}
    assert store.get_reads(dir_b) == {"SC:OUTPUT PARAMETERS"}
    store.reset(dir_a)
    assert store.get_reads(dir_a) == set()
    assert store.get_reads(dir_b) == {"SC:OUTPUT PARAMETERS"}
