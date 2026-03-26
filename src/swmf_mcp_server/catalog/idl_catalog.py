from __future__ import annotations

from pathlib import Path


def discover_idl_macros(swmf_root: Path, max_results: int = 1000) -> list[str]:
    idl_dir = swmf_root / "share" / "IDL"
    if not idl_dir.is_dir():
        return []

    macros: list[str] = []
    for path in idl_dir.rglob("*.pro"):
        macros.append(str(path.resolve()))
        if len(macros) >= max_results:
            break

    return sorted(macros)
