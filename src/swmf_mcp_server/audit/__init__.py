"""Server-side audit gates that enforce skill discipline.

The XML audit (see :mod:`xml_audit`) records every
``inspect_artifact(artifact_type='xml', xml_scope='commandgroup:...')`` call
in per-session state and refuses to bless a PARAM.in launch when any
emitted command belongs to a commandgroup that was never read.

This turns the swmf-replicate "read PARAM.XML before authoring" ladder rung
from a prompt aspiration into a deterministic gate.
"""

from .session_state import AuditStore, get_audit_store, reset_audit_store
from .xml_audit import (
    audit_param_against_xml_reads,
    record_commandgroup_read,
    derive_group_key,
)

__all__ = [
    "AuditStore",
    "audit_param_against_xml_reads",
    "derive_group_key",
    "get_audit_store",
    "record_commandgroup_read",
    "reset_audit_store",
]
