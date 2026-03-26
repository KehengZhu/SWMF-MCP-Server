from __future__ import annotations

from pathlib import Path


def resolve_run_dir(run_dir: str | None) -> Path:
    if run_dir:
        return Path(run_dir).expanduser().resolve()
    return Path.cwd().resolve()


def load_param_text(
    param_text: str | None,
    param_path: str | None,
    run_dir: str | None,
) -> tuple[str | None, str | None, str | None]:
    if param_text is not None:
        return param_text, None, None

    if param_path is None:
        return None, None, "Provide param_text or param_path."

    try:
        path = Path(param_path).expanduser()
        if not path.is_absolute():
            base_dir = resolve_run_dir(run_dir)
            path = base_dir / path
        resolved = path.resolve()
        if not resolved.is_file():
            return None, str(resolved), f"param_path does not point to a file: {resolved}"
        return resolved.read_text(encoding="utf-8"), str(resolved), None
    except OSError as exc:
        return None, None, f"Failed to read param_path: {exc}"


def resolve_input_path(path_text: str, run_dir: str | None = None) -> tuple[Path | None, str | None]:
    try:
        path = Path(path_text).expanduser()
        if not path.is_absolute():
            path = resolve_run_dir(run_dir) / path
        resolved = path.resolve()
        if not resolved.is_file():
            return None, f"Input path does not point to a file: {resolved}"
        return resolved, None
    except OSError as exc:
        return None, f"Failed to resolve path '{path_text}': {exc}"


def resolve_reference_path(raw_ref: str, base_dir: Path) -> Path:
    path = Path(raw_ref).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()
