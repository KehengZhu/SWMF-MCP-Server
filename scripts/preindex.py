#!/usr/bin/env python3
"""Pre-index the SWMF and SWMFSOLAR knowledge bases.

Called by ``make`` as part of local MCP preparation. Reads paths from
environment variables set by the Makefile:
  SWMF_ROOT       – required; path to SWMF source tree
  SWMFSOLAR_ROOT  – optional; path to SWMFSOLAR source tree
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the package importable when the venv is active (it normally is, because
# the Makefile invokes this via $(PYTHON) which is the venv interpreter, and
# the package is installed with ``pip install -e .``).
_REPO = Path(__file__).resolve().parents[1]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))

from swmf_mcp_server.knowledge import service as ks  # noqa: E402  (after path fixup)


def main() -> int:
    swmf_root = os.environ.get("SWMF_ROOT", "")
    swmfsolar_root = os.environ.get("SWMFSOLAR_ROOT", "")

    if not swmf_root:
        print("ERROR: SWMF_ROOT environment variable is not set.", file=sys.stderr)
        return 1

    swmf_path = Path(swmf_root).resolve()
    if not swmf_path.is_dir():
        print(f"ERROR: SWMF_ROOT '{swmf_path}' does not exist.", file=sys.stderr)
        return 1

    solar_path: Path | None = None
    if swmfsolar_root:
        candidate = Path(swmfsolar_root).resolve()
        if candidate.is_dir():
            solar_path = candidate
        else:
            print(f"    SWMFSOLAR_ROOT '{candidate}' not found – skipping.")

    print(f"    SWMF root      : {swmf_path}")
    print(f"    SWMFSOLAR root : {solar_path or '(none)'}")
    print("    Building index (force=True)…")

    status = ks.build_index(
        str(swmf_path),
        force=True,
        swmfsolar_root=str(solar_path) if solar_path else None,
    )

    if status.ok and not status.is_stale:
        print(
            f"    Index ready: {status.symbol_count} symbols across "
            f"{status.file_count} files"
        )
        return 0

    print(
        f"ERROR: index build did not produce a ready index.\n  {status}",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
