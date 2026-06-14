"""Disk-backed session tracking for the XML audit gate.

The CLI is invoked one process per call, so the audit gate cannot rely on
in-process memory: the commandgroup reads recorded while the agent inspects
PARAM.XML must survive into the *separate* process that later runs the
launch-time param audit. State is therefore persisted to disk.

A "session" is identified by a run directory. Reads are stored at
``<run_dir>/.swmf_ai/audit.json`` so the state is discoverable, naturally
scoped to the run being authored, and cleaned up with it. Calls that pass no
run directory (ad-hoc use, tests) fall back to a single deterministic default
session under the system temp directory.

The ``session_id`` argument carried through this module *is* the run directory
path (or ``None`` for the default session).
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from threading import Lock


def _default_session_base() -> Path:
    """Deterministic, process-shared location for the no-run-dir session."""
    return Path(tempfile.gettempdir()) / "swmf_ai_session"


@dataclass
class AuditStore:
    """Disk-backed per-session audit tracker.

    Stored keys are ``"{COMPONENT}:{groupname_upper}"`` strings (see
    :func:`swmf_mcp_server.audit.xml_audit.derive_group_key`) so that
    same-named groups across components do not collide.

    ``session_id`` is a run-directory path. A falsy ``session_id`` selects the
    shared default session under :func:`_default_session_base`.
    """

    default_base: Path | None = None

    def __post_init__(self) -> None:
        self._lock = Lock()

    # -- path resolution ---------------------------------------------------- #
    def _session_base(self, session_id: str | None) -> Path:
        if session_id:
            return Path(session_id).expanduser().resolve()
        return self.default_base or _default_session_base()

    def _state_path(self, session_id: str | None) -> Path:
        return self._session_base(session_id) / ".swmf_ai" / "audit.json"

    # -- persistence helpers ------------------------------------------------ #
    @staticmethod
    def _load(path: Path) -> set[str]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return set()
        groups = raw.get("commandgroups_read", []) if isinstance(raw, dict) else []
        return {str(g) for g in groups}

    @staticmethod
    def _save(path: Path, reads: set[str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps({"commandgroups_read": sorted(reads)}, indent=2)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, path)

    # -- public API --------------------------------------------------------- #
    def record_commandgroup_read(self, session_id: str | None, group_key: str) -> None:
        with self._lock:
            path = self._state_path(session_id)
            reads = self._load(path)
            reads.add(group_key)
            self._save(path, reads)

    def get_reads(self, session_id: str | None) -> set[str]:
        with self._lock:
            return self._load(self._state_path(session_id))

    def reset(self, session_id: str | None = None) -> None:
        """Remove one session's persisted state (the default when ``None``)."""
        with self._lock:
            path = self._state_path(session_id)
            try:
                path.unlink()
            except FileNotFoundError:
                pass


_AUDIT_STORE = AuditStore()


def get_audit_store() -> AuditStore:
    return _AUDIT_STORE


def reset_audit_store() -> None:
    """Wipe the default session's persisted state. Primarily used by tests."""
    _AUDIT_STORE.reset()
