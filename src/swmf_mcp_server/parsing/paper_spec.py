"""Deterministic loader for agent-authored `paper_spec` JSON/YAML files.

A `paper_spec` is the structured normalization of paper-extracted parameters.
The agent (LLM) does the extraction; MCP only surfaces what is literally present
in the JSON/YAML. No PDF parsing happens here (see plan §9.2 anti-pattern
"MCP-as-PDF-parser").

The shape mirrors `ccmc_spec` (so the downstream skill can merge both paths)
plus paper-only fields:

* `source_paper_path`  — path to the source paper artifact (PDF, preprint, etc.).
* `confidence_per_field` — agent-supplied confidence map (string or numeric); MCP
  records it verbatim and does not adjudicate.
* `precedent_hint` — list of strings. The LLM extracts paper-cited prior runs
  (e.g. "we use the setup of Sokolov et al. 2021 with modifications X, Y"). When
  non-empty, the downstream skill ranks hinted precedents above the
  archetype-default secondary precedents (cf. capability_enrichment_plan.md §5.4).
* `numerics_phrases` — list of strings. Verbatim phrases from the paper that
  trigger derivation/default lookups (e.g. "Spitzer heat conduction with
  collisionless flux beyond 5 R_s"). The skill uses these to decide which
  equation-set or mined required-command blocks must appear in the emitted
  PARAM (cf. capability_enrichment_plan.md §5.3 two-source join).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - dependency declared in pyproject.toml
    yaml = None  # type: ignore[assignment]


_CCMC_SHAPE_KEYS = (
    "run_id",
    "model",
    "model_version",
    "event_time_utc",
    "fr_type",
    "fr_params",
    "cone_params",
    "cme_params",
    "mflampa_params",
    "metadata",
    "input_files_listed",
    "output_files_listed",
    "quicklook_targets",
)

_DICT_KEYS = {"fr_params", "cone_params", "cme_params", "mflampa_params", "metadata"}
_LIST_KEYS = {"input_files_listed", "output_files_listed", "quicklook_targets"}

# Paper-only list fields beyond the ccmc_spec shape. Empty list is the default.
_PAPER_LIST_KEYS = ("precedent_hint", "numerics_phrases")


def _empty_paper_spec() -> dict[str, Any]:
    out: dict[str, Any] = {key: None for key in _CCMC_SHAPE_KEYS}
    for key in _DICT_KEYS:
        out[key] = {}
    for key in _LIST_KEYS:
        out[key] = []
    out["source_paper_path"] = None
    out["confidence_per_field"] = {}
    for key in _PAPER_LIST_KEYS:
        out[key] = []
    out["missing_fields"] = []
    out["unparsed_keys"] = []
    return out


def _normalize_loaded(raw: Any) -> tuple[dict[str, Any], list[str], list[str]]:
    """Return ``(parsed, missing_fields, parse_errors)`` for a raw loaded mapping."""
    parsed = _empty_paper_spec()
    parse_errors: list[str] = []

    if raw is None:
        parse_errors.append("Spec file is empty.")
        return parsed, list(_CCMC_SHAPE_KEYS), parse_errors
    if not isinstance(raw, dict):
        parse_errors.append(
            f"Top-level element must be a mapping (got {type(raw).__name__})."
        )
        return parsed, list(_CCMC_SHAPE_KEYS), parse_errors

    for key in _CCMC_SHAPE_KEYS:
        if key not in raw:
            continue
        value = raw[key]
        if key in _DICT_KEYS:
            if isinstance(value, dict):
                parsed[key] = value
            elif value is None:
                parsed[key] = {}
            else:
                parse_errors.append(f"Field '{key}' must be a mapping; got {type(value).__name__}.")
        elif key in _LIST_KEYS:
            if isinstance(value, list):
                parsed[key] = [str(item) for item in value]
            elif value is None:
                parsed[key] = []
            else:
                parse_errors.append(f"Field '{key}' must be a list; got {type(value).__name__}.")
        else:
            parsed[key] = value

    if "source_paper_path" in raw:
        value = raw["source_paper_path"]
        parsed["source_paper_path"] = None if value is None else str(value)

    if "confidence_per_field" in raw:
        confidence = raw["confidence_per_field"]
        if isinstance(confidence, dict):
            parsed["confidence_per_field"] = confidence
        elif confidence is None:
            parsed["confidence_per_field"] = {}
        else:
            parse_errors.append(
                f"Field 'confidence_per_field' must be a mapping; got {type(confidence).__name__}."
            )

    for key in _PAPER_LIST_KEYS:
        if key not in raw:
            continue
        value = raw[key]
        if isinstance(value, list):
            parsed[key] = [str(item) for item in value]
        elif value is None:
            parsed[key] = []
        else:
            parse_errors.append(
                f"Field '{key}' must be a list; got {type(value).__name__}."
            )

    missing = [
        key for key in _CCMC_SHAPE_KEYS
        if (parsed[key] in (None, {}, []) and key not in raw)
    ]
    parsed["missing_fields"] = missing

    known = set(_CCMC_SHAPE_KEYS) | {"source_paper_path", "confidence_per_field"} | set(_PAPER_LIST_KEYS)
    parsed["unparsed_keys"] = sorted(k for k in raw.keys() if k not in known)

    return parsed, missing, parse_errors


def parse_paper_spec_text(text: str, *, fmt_hint: str | None = None) -> dict[str, Any]:
    """Parse JSON or YAML text. ``fmt_hint`` of ``"json"``/``"yaml"`` skips autodetect."""
    raw: Any = None
    parse_errors: list[str] = []

    candidate = (fmt_hint or "").lower()
    if candidate == "json":
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            parse_errors.append(f"JSON parse error: {exc}")
    elif candidate in {"yaml", "yml"}:
        if yaml is None:
            parse_errors.append("PyYAML not available; cannot load YAML paper_spec.")
        else:
            try:
                raw = yaml.safe_load(text)
            except yaml.YAMLError as exc:  # type: ignore[union-attr]
                parse_errors.append(f"YAML parse error: {exc}")
    else:
        # Autodetect: try JSON first, then YAML.
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as json_exc:
            if yaml is None:
                parse_errors.append(f"JSON parse error: {json_exc}")
            else:
                try:
                    raw = yaml.safe_load(text)
                except yaml.YAMLError as yaml_exc:  # type: ignore[union-attr]
                    parse_errors.append(f"JSON parse error: {json_exc}")
                    parse_errors.append(f"YAML parse error: {yaml_exc}")

    if parse_errors and raw is None:
        parsed = _empty_paper_spec()
        parsed["missing_fields"] = list(_CCMC_SHAPE_KEYS)
        parsed["parse_errors"] = parse_errors
        return parsed

    parsed, _missing, normalization_errors = _normalize_loaded(raw)
    if normalization_errors:
        parsed["parse_errors"] = normalization_errors
    return parsed


def parse_paper_spec_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    fmt_hint: str | None = None
    if suffix in {".json"}:
        fmt_hint = "json"
    elif suffix in {".yaml", ".yml"}:
        fmt_hint = "yaml"

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        parsed = _empty_paper_spec()
        parsed["missing_fields"] = list(_CCMC_SHAPE_KEYS)
        parsed["read_error"] = str(exc)
        return parsed

    parsed = parse_paper_spec_text(text, fmt_hint=fmt_hint)
    return parsed
