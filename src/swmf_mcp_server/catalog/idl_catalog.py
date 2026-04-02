from __future__ import annotations

from pathlib import Path
from typing import Any

from ..parsing.idl_parser import parse_idl_file


def _infer_category(name: str, file_path: Path, docstring: str | None) -> str:
    lowered_name = name.lower()
    lowered_path = str(file_path).lower()
    lowered_doc = (docstring or "").lower()
    stacked = " ".join([lowered_name, lowered_path, lowered_doc])

    if any(token in stacked for token in ["magnetogram", "fits", "read_magnetogram"]):
        return "magnetogram"
    if any(token in stacked for token in ["animate", "movie", "videofile", "moviedir"]):
        return "animation"
    if any(token in stacked for token in ["plot", "contour", "stream", "vector", "show_data", "plot_log"]):
        return "plotting"
    if any(token in stacked for token in ["read_", "getpict", "getlog", "read_log_data", ".log", ".sat"]):
        return "data_reading"
    return "utility"


def discover_idl_procedures(swmf_root: Path, max_results: int = 4000) -> dict[str, dict[str, Any]]:
    idl_dir = swmf_root / "share" / "IDL"
    if not idl_dir.is_dir():
        return {}

    procedures: dict[str, dict[str, Any]] = {}
    discovered = 0

    for path in sorted(idl_dir.rglob("*.pro")):
        for item in parse_idl_file(path):
            discovered += 1
            if discovered > max_results:
                return procedures

            category = _infer_category(item.name, path, item.docstring)
            key = item.name.lower()
            payload = {
                "name": item.name,
                "kind": item.kind,
                "file_path": str(path.resolve()),
                "signature": item.signature,
                "params": item.params,
                "keywords": item.keywords,
                "docstring": item.docstring,
                "category": category,
                "line_number": item.line_number,
            }

            if key not in procedures:
                procedures[key] = payload

    return procedures


def discover_idl_macros(swmf_root: Path, max_results: int = 1000) -> list[str]:
    idl_dir = swmf_root / "share" / "IDL"
    if not idl_dir.is_dir():
        return []

    macros: list[str] = []
    for path in sorted(idl_dir.rglob("*.pro")):
        macros.append(str(path.resolve()))
        if len(macros) >= max_results:
            break

    return macros


def list_idl_procedures(
    procedures: dict[str, dict[str, Any]],
    category: str | None = None,
) -> list[dict[str, Any]]:
    normalized = category.strip().lower() if category else None
    rows: list[dict[str, Any]] = []

    for payload in procedures.values():
        if normalized and payload.get("category", "").lower() != normalized:
            continue
        rows.append(
            {
                "name": payload["name"],
                "kind": payload["kind"],
                "category": payload["category"],
                "file_path": payload["file_path"],
                "signature": payload["signature"],
            }
        )

    rows.sort(key=lambda item: (item["category"], item["name"].lower()))
    return rows


def get_idl_procedure(
    procedures: dict[str, dict[str, Any]],
    name: str,
) -> dict[str, Any] | None:
    return procedures.get(name.strip().lower())
