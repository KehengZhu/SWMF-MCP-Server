from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class SwmfError(Exception):
    error_code: str
    message: str
    hard_error: bool = True
    how_to_fix: list[str] | None = None


def error_payload(exc: SwmfError, **extra: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "error_code": exc.error_code,
        "hard_error": exc.hard_error,
        "message": exc.message,
    }
    if exc.how_to_fix:
        payload["how_to_fix"] = exc.how_to_fix
    payload.update(extra)
    return payload


def resolution_failure_payload(message: str, notes: list[str]) -> dict[str, Any]:
    return {
        "ok": False,
        "error_code": "SWMF_ROOT_RESOLUTION_FAILED",
        "hard_error": True,
        "message": message,
        "swmf_root_resolved": None,
        "resolution_notes": notes,
        "how_to_fix": [
            "Pass swmf_root as an absolute path to your SWMF source tree.",
            "Set SWMF_ROOT to an absolute path to your SWMF source tree.",
        ],
    }


def not_found_error_payload(
    error_code: str,
    message: str,
    how_to_fix: list[str] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    return error_payload(
        SwmfError(
            error_code=error_code,
            message=message,
            hard_error=True,
            how_to_fix=how_to_fix,
        ),
        **extra,
    )
