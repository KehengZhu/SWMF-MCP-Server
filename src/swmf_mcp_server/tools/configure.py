from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.config import SWMF_ROOT_ENV
from ._helpers import resolve_root_or_failure, with_root
from .build_run import prepare_build, prepare_run


def show_config(swmf_root: str | None = None, run_dir: str | None = None) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    resolved = Path(root.swmf_root_resolved or "").resolve()
    payload = {
        "ok": True,
        "swmf_root": str(resolved),
        "markers": {
            "Config.pl": (resolved / "Config.pl").is_file(),
            "PARAM.XML": (resolved / "PARAM.XML").is_file(),
            "Scripts/TestParam.pl": (resolved / "Scripts" / "TestParam.pl").is_file(),
        },
        "env_var": SWMF_ROOT_ENV,
    }
    return with_root(payload, root)


def select_components(
    components_csv: str,
    compiler: str | None = None,
    debug: bool = False,
    optimization: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    return with_root(
        prepare_build(
            components_csv=components_csv,
            compiler=compiler,
            debug=debug,
            optimization=optimization,
        ),
        root,
    )


def set_grid(
    component_map_text: str,
    nproc: int | None = None,
    run_name: str = "run_demo",
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    payload = prepare_run(
        component_map_text=component_map_text,
        nproc=nproc,
        run_name=run_name,
        run_dir=run_dir,
    )
    payload["note"] = "Grid/process layout is represented via #COMPONENTMAP rows in PARAM.in."
    return with_root(payload, root)


def swmf_show_config(swmf_root: str | None = None, run_dir: str | None = None) -> dict[str, Any]:
    return show_config(swmf_root=swmf_root, run_dir=run_dir)


def swmf_select_components(
    components_csv: str,
    compiler: str | None = None,
    debug: bool = False,
    optimization: int | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    return select_components(
        components_csv=components_csv,
        compiler=compiler,
        debug=debug,
        optimization=optimization,
        swmf_root=swmf_root,
        run_dir=run_dir,
    )


def swmf_set_grid(
    component_map_text: str,
    nproc: int | None = None,
    run_name: str = "run_demo",
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    return set_grid(
        component_map_text=component_map_text,
        nproc=nproc,
        run_name=run_name,
        swmf_root=swmf_root,
        run_dir=run_dir,
    )


def register(app: Any) -> None:
    app.tool()(swmf_show_config)
    app.tool()(swmf_select_components)
    app.tool()(swmf_set_grid)
