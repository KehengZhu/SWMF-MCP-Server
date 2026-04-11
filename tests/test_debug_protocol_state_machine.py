from __future__ import annotations

from swmf_mcp_server import server
from swmf_mcp_server.core.debug_protocol import (
    FAMILY_SOURCE_CHANGE_VALIDATION,
    STATE_CLASSIFICATION,
    STATE_INTAKE,
    STATE_NORMALIZATION,
    STATE_PATCH_READINESS,
    can_transition,
    protocol_envelope,
)


def test_protocol_transition_rules_are_forward_only() -> None:
    assert can_transition(STATE_INTAKE, STATE_CLASSIFICATION) is True
    assert can_transition(STATE_CLASSIFICATION, STATE_NORMALIZATION) is False
    assert can_transition(STATE_NORMALIZATION, STATE_CLASSIFICATION) is False


def test_protocol_envelope_contains_version_and_patch_gate() -> None:
    payload = protocol_envelope(
        state=STATE_CLASSIFICATION,
        failure_family=FAMILY_SOURCE_CHANGE_VALIDATION,
        patch_ready=False,
        invariants_required=True,
    )

    assert payload["protocol_version"] == "swmf-debug/1.0"
    assert payload["protocol_state"] == STATE_CLASSIFICATION
    assert payload["patch_readiness"]["ready"] is False
    assert payload["patch_readiness"]["invariants_required"] is True


def test_collect_invariant_context_controls_patch_readiness() -> None:
    incomplete = server.swmf_collect_invariant_context(data_structure="VertexState")
    assert incomplete["ok"] is True
    assert incomplete["protocol_state"] == STATE_PATCH_READINESS
    assert incomplete["patch_readiness"]["ready"] is False

    complete = server.swmf_collect_invariant_context(
        data_structure="VertexState",
        invariants_before_change=["nVertex_B >= 0"],
        operations_that_can_violate=["offset shift"],
        diagnostics_to_collect=["print nVertex_B before/after update"],
        runtime_checks=["assert nVertex_B >= 0"],
    )

    assert complete["ok"] is True
    assert complete["patch_readiness"]["ready"] is True
    assert complete["invariant_block"]["data_structure"] == "VertexState"
