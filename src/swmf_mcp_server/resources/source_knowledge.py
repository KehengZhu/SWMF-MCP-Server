"""MCP resource registrations for the SWMF knowledge base.

Resources exposed
-----------------
``swmf://knowledge/symbol/{name}``
    Read-only symbol lookup by exact name.

``swmf://knowledge/index-status``
    Current status of the persistent knowledge index.
"""
from __future__ import annotations

from typing import Any

from ..core import knowledge_service as ks
from ..core.authority import AUTHORITY_HEURISTIC
from ..core.swmf_root import resolve_swmf_root


def _resolve_root() -> str | None:
    result = resolve_swmf_root()
    return result.swmf_root_resolved if result.ok else None


def get_symbol_resource(name: str) -> dict[str, Any]:
    """Return indexed symbol definitions for *name* across all languages."""
    root = _resolve_root()
    if root is None:
        return {
            "ok": False,
            "error_code": "SWMF_ROOT_RESOLUTION_FAILED",
            "message": "Cannot resolve SWMF root. Set SWMF_ROOT or pass swmf_root.",
        }

    status = ks.get_index_status(root)
    if status.is_stale:
        return {
            "ok": False,
            "error_code": "KNOWLEDGE_INDEX_NOT_BUILT",
            "message": "Knowledge index is not built. Run swmf-index build --corpus SWMF --corpus SWMFSOLAR.",
            "index_status": ks.status_as_payload(status),
        }

    matches = ks.lookup_symbol(root, name=name)
    return {
        "ok": True,
        "name": name,
        "match_count": len(matches),
        "matches": matches,
        "authority": AUTHORITY_HEURISTIC,
        "swmf_root_resolved": root,
    }


def get_index_status_resource() -> dict[str, Any]:
    """Return the current knowledge index status."""
    root = _resolve_root()
    if root is None:
        return {
            "ok": False,
            "error_code": "SWMF_ROOT_RESOLUTION_FAILED",
            "message": "Cannot resolve SWMF root. Set SWMF_ROOT or pass swmf_root.",
        }

    status = ks.get_index_status(root)
    payload = ks.status_as_payload(status)
    payload["swmf_root_resolved"] = root
    return payload


def register(app: Any) -> None:
    if not hasattr(app, "resource"):
        return

    @app.resource(
        "swmf://knowledge/symbol/{name}",
        name="swmf_knowledge_symbol",
        description="Indexed SWMF source symbol lookup by exact name across Fortran, Perl, and IDL.",
        mime_type="application/json",
    )
    def symbol_resource(name: str) -> dict[str, Any]:
        return get_symbol_resource(name)

    @app.resource(
        "swmf://knowledge/index-status",
        name="swmf_knowledge_index_status",
        description="Current status of the persistent SWMF knowledge index: file count, symbol count, build time.",
        mime_type="application/json",
    )
    def index_status_resource() -> dict[str, Any]:
        return get_index_status_resource()
