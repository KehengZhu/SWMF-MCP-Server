#!/usr/bin/env python3
"""Write .mcp.json at TARGET_DIR for the SWMF MCP server.

Called by ``make install``.  Reads configuration from environment variables
set by the Makefile:
  TARGET_DIR      – directory where .mcp.json will be written
  SERVER_PYTHON   – absolute path to the Python interpreter to embed in the config
  SWMF_ROOT       – absolute path to the SWMF source tree
  SWMFSOLAR_ROOT  – optional absolute path to the SWMFSOLAR source tree
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    target_dir    = os.environ.get("TARGET_DIR", "")
    server_python = os.environ.get("SERVER_PYTHON", "")
    swmf_root     = os.environ.get("SWMF_ROOT", "")
    swmfsolar_root = os.environ.get("SWMFSOLAR_ROOT", "")

    # Validate required inputs
    missing = [n for n, v in [("TARGET_DIR", target_dir),
                               ("SERVER_PYTHON", server_python),
                               ("SWMF_ROOT", swmf_root)] if not v]
    if missing:
        print(f"ERROR: missing environment variable(s): {', '.join(missing)}", file=sys.stderr)
        return 1

    target_path = Path(target_dir).resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    swmf_abs = str(Path(swmf_root).resolve())

    # Build the args list for the MCP server command
    args: list[str] = [
        "-m", "swmf_mcp_server.server",
        "--preindex-knowledge",
        "--swmf-root", swmf_abs,
    ]

    if swmfsolar_root:
        solar_path = Path(swmfsolar_root).resolve()
        if solar_path.is_dir():
            args += ["--swmfsolar-root", str(solar_path)]
            print(f"    SWMFSOLAR_ROOT : {solar_path}")
        else:
            print(f"    SWMFSOLAR_ROOT : '{solar_path}' not found – omitted from config")
    else:
        print("    SWMFSOLAR_ROOT : (not set – omitted from config)")

    mcp_config = {
        "mcpServers": {
            "swmf-prototype": {
                "command": server_python,
                "args": args,
            }
        }
    }

    out_path = target_path / ".mcp.json"
    out_path.write_text(json.dumps(mcp_config, indent=2) + "\n")

    print(f"    SWMF_ROOT      : {swmf_abs}")
    print(f"    Python         : {server_python}")
    print(f"    Written        : {out_path}")
    print("==> Done. Open the target directory in VS Code to load the MCP server.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
