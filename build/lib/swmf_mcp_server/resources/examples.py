from __future__ import annotations

from pathlib import Path
from typing import Any

from ..reference.service import swmf_find_example_params


def get_examples_resource(name: str) -> dict[str, Any]:
    query = name.strip().lower()
    payload = swmf_find_example_params(query=query or "param", max_results=800)
    if not payload.get("ok"):
        return payload

    templates = payload.get("matches", [])
    if query in {"", "all", "*"}:
        matches = templates
    else:
        matches = [path for path in templates if query in Path(path).name.lower() or query in path.lower()]

    return {
        "ok": True,
        "name": name,
        "count": len(matches),
        "examples": matches,
        "swmf_root_resolved": payload.get("swmf_root_resolved"),
    }


def register(app: Any) -> None:
    if not hasattr(app, "resource"):
        return

    @app.resource(
        "swmf://examples/{name}",
        name="swmf_examples",
        description="List indexed SWMF PARAM example files filtered by name.",
        mime_type="application/json",
    )
    def examples_resource(name: str) -> dict[str, Any]:
        return get_examples_resource(name)
