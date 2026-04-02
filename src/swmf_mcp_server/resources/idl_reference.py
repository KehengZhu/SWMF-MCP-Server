from __future__ import annotations

from typing import Any

from ..catalog import get_idl_procedure, get_source_catalog, list_idl_procedures
from ..core.swmf_root import resolve_swmf_root


def _load_catalog() -> tuple[dict[str, Any] | None, Any | None]:
    root = resolve_swmf_root()
    if not root.ok:
        return {
            "ok": False,
            "error_code": "SWMF_ROOT_RESOLUTION_FAILED",
            "message": root.message,
            "resolution_notes": root.resolution_notes,
        }, None

    catalog_error, catalog = get_source_catalog(root=root, force_refresh=False)
    if catalog_error is not None or catalog is None:
        return catalog_error or {"ok": False, "message": "Failed to load source catalog."}, None

    return None, catalog


def list_idl_reference_resource() -> dict[str, Any]:
    error, catalog = _load_catalog()
    if error is not None or catalog is None:
        return error or {"ok": False, "message": "Catalog unavailable."}

    procedures = list_idl_procedures(catalog.idl_procedures)
    return {
        "ok": True,
        "procedures": procedures,
        "count": len(procedures),
        "swmf_root_resolved": catalog.swmf_root,
    }


def get_idl_reference_resource(procedure: str) -> dict[str, Any]:
    error, catalog = _load_catalog()
    if error is not None or catalog is None:
        return error or {"ok": False, "message": "Catalog unavailable."}

    payload = get_idl_procedure(catalog.idl_procedures, procedure)
    if payload is None:
        return {
            "ok": False,
            "message": f"IDL procedure not found: {procedure}",
            "swmf_root_resolved": catalog.swmf_root,
        }

    return {
        "ok": True,
        "procedure": payload,
        "swmf_root_resolved": catalog.swmf_root,
    }


def register(app: Any) -> None:
    if not hasattr(app, "resource"):
        return

    @app.resource(
        "swmf://idl/procedures",
        name="swmf_idl_procedures",
        description="List indexed SWMF IDL procedures/macros.",
        mime_type="application/json",
    )
    def idl_procedures_resource() -> dict[str, Any]:
        return list_idl_reference_resource()

    @app.resource(
        "swmf://idl/{procedure}",
        name="swmf_idl_procedure",
        description="Return indexed signature/details for one SWMF IDL procedure.",
        mime_type="application/json",
    )
    def idl_procedure_resource(procedure: str) -> dict[str, Any]:
        return get_idl_reference_resource(procedure)
