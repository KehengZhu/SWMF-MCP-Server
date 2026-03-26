from __future__ import annotations

from pathlib import Path


_PRIORITY_SCRIPTS = [
    "Config.pl",
    "Scripts/TestParam.pl",
    "Restart.pl",
    "PostProc.pl",
]


def discover_scripts(swmf_root: Path) -> list[str]:
    results: list[str] = []
    for rel in _PRIORITY_SCRIPTS:
        path = swmf_root / rel
        if path.is_file():
            results.append(str(path.resolve()))

    scripts_dir = swmf_root / "Scripts"
    if scripts_dir.is_dir():
        for path in scripts_dir.glob("*.pl"):
            resolved = str(path.resolve())
            if resolved not in results:
                results.append(resolved)

    return sorted(results)
