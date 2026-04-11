from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


DebugProtocolState = Literal[
    "intake",
    "classification",
    "evidence_collection",
    "normalization",
    "hypothesis_staging",
    "discriminating_experiment",
    "patch_readiness",
    "validation",
]

DebugFailureFamily = Literal[
    "input_schema",
    "build_config",
    "startup_initialization",
    "runtime_crash_stop",
    "hang_stall_performance",
    "coupling_mpi_layout",
    "numerical_physics_anomaly",
    "postprocess_restart_output",
    "source_change_validation",
    "unknown",
]

PROTOCOL_VERSION = "swmf-debug/1.0"

STATE_INTAKE: DebugProtocolState = "intake"
STATE_CLASSIFICATION: DebugProtocolState = "classification"
STATE_EVIDENCE_COLLECTION: DebugProtocolState = "evidence_collection"
STATE_NORMALIZATION: DebugProtocolState = "normalization"
STATE_HYPOTHESIS_STAGING: DebugProtocolState = "hypothesis_staging"
STATE_DISCRIMINATING_EXPERIMENT: DebugProtocolState = "discriminating_experiment"
STATE_PATCH_READINESS: DebugProtocolState = "patch_readiness"
STATE_VALIDATION: DebugProtocolState = "validation"

STATE_ORDER: list[DebugProtocolState] = [
    STATE_INTAKE,
    STATE_CLASSIFICATION,
    STATE_EVIDENCE_COLLECTION,
    STATE_NORMALIZATION,
    STATE_HYPOTHESIS_STAGING,
    STATE_DISCRIMINATING_EXPERIMENT,
    STATE_PATCH_READINESS,
    STATE_VALIDATION,
]

STATE_INDEX = {state: idx for idx, state in enumerate(STATE_ORDER)}

FAMILY_INPUT_SCHEMA: DebugFailureFamily = "input_schema"
FAMILY_BUILD_CONFIG: DebugFailureFamily = "build_config"
FAMILY_STARTUP_INITIALIZATION: DebugFailureFamily = "startup_initialization"
FAMILY_RUNTIME_CRASH_STOP: DebugFailureFamily = "runtime_crash_stop"
FAMILY_HANG_STALL_PERFORMANCE: DebugFailureFamily = "hang_stall_performance"
FAMILY_COUPLING_MPI_LAYOUT: DebugFailureFamily = "coupling_mpi_layout"
FAMILY_NUMERICAL_PHYSICS_ANOMALY: DebugFailureFamily = "numerical_physics_anomaly"
FAMILY_POSTPROCESS_RESTART_OUTPUT: DebugFailureFamily = "postprocess_restart_output"
FAMILY_SOURCE_CHANGE_VALIDATION: DebugFailureFamily = "source_change_validation"
FAMILY_UNKNOWN: DebugFailureFamily = "unknown"


@dataclass
class InvariantBlock:
    data_structure: str
    invariants_before_change: list[str] = field(default_factory=list)
    operations_that_can_violate: list[str] = field(default_factory=list)
    diagnostics_to_collect: list[str] = field(default_factory=list)
    runtime_checks: list[str] = field(default_factory=list)

    def as_payload(self) -> dict[str, Any]:
        return asdict(self)


def is_valid_state(state: str) -> bool:
    return state in STATE_INDEX


def allowed_next_states(state: DebugProtocolState) -> list[DebugProtocolState]:
    current = STATE_INDEX[state]
    out: list[DebugProtocolState] = [state]
    if current + 1 < len(STATE_ORDER):
        out.append(STATE_ORDER[current + 1])
    return out


def can_transition(current_state: str | None, next_state: str) -> bool:
    if next_state not in STATE_INDEX:
        return False
    if current_state is None:
        return next_state == STATE_INTAKE
    if current_state not in STATE_INDEX:
        return False

    current_index = STATE_INDEX[current_state]
    next_index = STATE_INDEX[next_state]
    if next_index < current_index:
        return False
    return (next_index - current_index) <= 1


def protocol_envelope(
    state: DebugProtocolState,
    failure_family: DebugFailureFamily,
    observation_report: list[str] | None = None,
    mechanism_candidates: list[dict[str, Any]] | None = None,
    unresolved_conflicts: list[str] | None = None,
    next_discriminating_checks: list[str] | None = None,
    patch_ready: bool = False,
    patch_readiness_reason: str | None = None,
    invariants_required: bool = False,
    invariant_block: InvariantBlock | None = None,
) -> dict[str, Any]:
    reason = patch_readiness_reason
    if reason is None:
        reason = "ready_for_minimal_patch" if patch_ready else "collect_more_evidence_before_patch"

    return {
        "protocol_version": PROTOCOL_VERSION,
        "protocol_state": state,
        "failure_family": failure_family,
        "allowed_next_states": allowed_next_states(state),
        "observation_report": observation_report or [],
        "mechanism_candidates": mechanism_candidates or [],
        "unresolved_conflicts": unresolved_conflicts or [],
        "next_discriminating_checks": next_discriminating_checks or [],
        "patch_readiness": {
            "ready": patch_ready,
            "reason": reason,
            "invariants_required": invariants_required,
        },
        "invariant_block": invariant_block.as_payload() if invariant_block is not None else None,
        "legacy_contract": {
            "status": "active",
            "policy": "additive_protocol_fields_first",
            "deprecation_strategy": "gradual",
        },
    }
