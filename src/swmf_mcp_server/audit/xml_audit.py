"""XML audit gate — refuse PARAM.in launch unless the relevant PARAM.XML
commandgroups have been read this session.

The agent emits a PARAM block (e.g. the B0 block with ``#CURLB0``). Before
the launch gate, ``swmf inspect --type param --check-xml-audit`` calls into
this module to cross-reference every emitted command against the catalog's
command → commandgroup map. Any commandgroup the agent skipped reading via
``swmf inspect --type xml --xml-scope 'commandgroup:...'`` (with the same
``--run-dir``) is surfaced as an :class:`audit_violation` and the launch is
blocked.

Without this gate, the new authoring ladder is just prompt aspiration.
"""
from __future__ import annotations

from typing import Any, Iterable

from ..core.models import SourceCatalog
from .session_state import AuditStore


def derive_group_key(component: str | None, group_name: str | None) -> str | None:
    """Return ``"{COMPONENT}:{groupname_upper}"`` or ``None`` if no group.

    "TOP" is used as the component prefix for commands that live in the
    top-level ``SWMF/PARAM.XML`` (no per-component PARAM.XML).
    """
    if not group_name:
        return None
    comp = (component or "TOP").strip().upper() or "TOP"
    return f"{comp}:{group_name.strip().upper()}"


def record_commandgroup_read(
    store: AuditStore,
    session_id: str | None,
    component: str | None,
    group_name: str | None,
) -> str | None:
    """Record one commandgroup read; returns the canonical key (or None)."""
    key = derive_group_key(component, group_name)
    if key is None:
        return None
    store.record_commandgroup_read(session_id, key)
    return key


def _command_to_group_keys(catalog: SourceCatalog) -> dict[str, list[str]]:
    """Forward map: normalized command name -> list of group_keys it appears in.

    A command can technically live in multiple per-component PARAM.XML files
    under different commandgroups (e.g. SC vs IH), so the value is a list.
    """
    forward: dict[str, list[str]] = {}
    for normalized, entries in catalog.commands.items():
        keys: list[str] = []
        seen: set[str] = set()
        for entry in entries:
            key = derive_group_key(entry.component, entry.commandgroup)
            if key is None or key in seen:
                continue
            seen.add(key)
            keys.append(key)
        if keys:
            forward[normalized] = keys
    return forward


def audit_param_against_xml_reads(
    catalog: SourceCatalog,
    param_commands_by_component: dict[str | None, Iterable[str]],
    reads: set[str],
    waivers: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Cross-reference emitted PARAM commands against recorded XML reads.

    Parameters
    ----------
    catalog:
        Source catalog produced by ``ReferenceService._build_catalog`` —
        must carry the new ``commandgroup`` field on every CommandMetadata.
    param_commands_by_component:
        ``{component_or_None: [normalized command names emitted in that
        component's session block]}``. Pass ``None`` as the component when
        the command was emitted outside a ``#BEGIN_COMP``.
    reads:
        Set of ``"{COMPONENT}:{group_upper}"`` keys recorded for this session
        via ``inspect_artifact(xml_scope='commandgroup:...')``.
    waivers:
        Optional iterable of group_keys the user has explicitly waived in
        the PARAM REPORT (e.g. ``"SC:SCHEME PARAMETERS"``).

    Returns
    -------
    dict
        ``{"ok": bool, "audit_violations": [...], "groups_read": [...],
        "groups_required": [...], "groups_waived": [...]}``.
    """
    waiver_set: set[str] = {w.strip().upper() for w in (waivers or []) if w}
    forward = _command_to_group_keys(catalog)

    required: set[str] = set()
    violations_by_key: dict[str, dict[str, Any]] = {}

    for component, commands in param_commands_by_component.items():
        comp_upper = (component or "").strip().upper() or None
        for command in commands:
            norm = command if command.startswith("#") else f"#{command.upper()}"
            norm = norm.upper()
            candidate_keys = forward.get(norm, [])
            if not candidate_keys:
                # Command not in catalog at all (unknown / typo / fresh
                # command not yet in PARAM.XML). Surface as a separate
                # finding so the agent can investigate, but don't block
                # — that's the xml_corrections.md tier.
                continue
            # Filter candidates to the component the command was emitted in
            # when possible.
            relevant_keys = [
                key for key in candidate_keys
                if comp_upper is None or key.startswith(f"{comp_upper}:")
            ] or candidate_keys
            relevant_keys = [k for k in relevant_keys if k not in waiver_set]
            if not relevant_keys:
                continue
            # If *any* candidate key was read, the command is covered.
            if any(key in reads for key in relevant_keys):
                continue
            # Otherwise record violations against the first plausible key.
            primary_key = relevant_keys[0]
            required.add(primary_key)
            existing = violations_by_key.setdefault(
                primary_key,
                {
                    "commandgroup_key": primary_key,
                    "commandgroup": primary_key.split(":", 1)[1] if ":" in primary_key else primary_key,
                    "component": primary_key.split(":", 1)[0] if ":" in primary_key else None,
                    "commands": [],
                    "remedy": (
                        f"run `swmf inspect --type xml "
                        f"--xml-scope 'commandgroup:{primary_key.split(':', 1)[1] if ':' in primary_key else primary_key}' "
                        f"--path SC/BATSRUS/PARAM.XML` (or the matching component's PARAM.XML), "
                        f"passing the same --run-dir, then re-emit PARAM.in."
                    ),
                },
            )
            if norm not in existing["commands"]:
                existing["commands"].append(norm)

    return {
        "ok": not violations_by_key,
        "audit_violations": list(violations_by_key.values()),
        "groups_read": sorted(reads),
        "groups_required": sorted(required),
        "groups_waived": sorted(waiver_set),
    }
