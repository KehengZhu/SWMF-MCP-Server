from __future__ import annotations

from typing import Any

from ..reference.service import swmf_explain_idl_procedure, swmf_list_idl_procedures


def list_idl_reference_resource() -> dict[str, Any]:
    payload = swmf_list_idl_procedures()
    if not payload.get("ok"):
        return payload

    procedures = payload.get("procedures", [])
    return {
        "ok": True,
        "procedures": procedures,
        "count": len(procedures),
        "swmf_root_resolved": payload.get("swmf_root_resolved"),
    }


def get_idl_reference_resource(procedure: str) -> dict[str, Any]:
    payload = swmf_explain_idl_procedure(name=procedure)
    if not payload.get("ok"):
        return payload

    return {
        "ok": True,
        "procedure": payload,
        "swmf_root_resolved": payload.get("swmf_root_resolved"),
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
