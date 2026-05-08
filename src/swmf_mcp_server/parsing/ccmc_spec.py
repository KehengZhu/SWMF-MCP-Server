"""Deterministic parser for CCMC `Run information_CCMC.md` structured specs.

Used by `inspect_artifact(artifact_type="ccmc_spec")`. Reads the markdown table layout
and surfaces typed fields with the same names the spec uses. No invention; absent fields
remain `None`.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


_HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")
_TABLE_ROW_RE = re.compile(r"^\|\s*(?P<key>.+?)\s*\|\s*(?P<value>.*?)\s*\|\s*$")
_RUN_ID_RE = re.compile(r"Run ID[:\s]*`?(?P<run_id>[^`\s]+)`?", re.IGNORECASE)
_LIST_BULLET_RE = re.compile(r"^[\-\*]\s+(?P<text>.+?)\s*$")
_DATE_RE = re.compile(
    r"^(?P<y>\d{4})[/-](?P<m>\d{2})[/-](?P<d>\d{2})\s+(?P<H>\d{2}):(?P<M>\d{2})(?::(?P<S>\d{2}))?$"
)


def _coerce_value(text: str) -> Any:
    text = text.strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered in {"t", "true", "yes"}:
        return True
    if lowered in {"f", "false", "no"}:
        return False
    try:
        if "." in text or "e" in lowered:
            return float(text)
        return int(text)
    except ValueError:
        return text


def _normalize_event_time(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    match = _DATE_RE.match(text)
    if not match:
        return text
    sec = match.group("S") or "00"
    return (
        f"{match.group('y')}-{match.group('m')}-{match.group('d')}T"
        f"{match.group('H')}:{match.group('M')}:{sec}+00:00"
    )


def _drop_unit_brackets(key: str) -> str:
    """Strip trailing parentheticals so 'CME speed (km/s)' → 'CME speed'."""
    return re.sub(r"\s*\(.*?\)\s*$", "", key).strip()


def _slug(key: str) -> str:
    cleaned = _drop_unit_brackets(key)
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", cleaned).strip("_").lower()
    return cleaned


def _parse_sections(text: str) -> list[dict[str, Any]]:
    """Return a list of `{level, title, lines}` blocks delimited by markdown headings."""
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw in text.splitlines():
        match = _HEADING_RE.match(raw)
        if match:
            if current is not None:
                sections.append(current)
            current = {
                "level": len(match.group("hashes")),
                "title": match.group("title").strip(),
                "lines": [],
            }
            continue
        if current is not None:
            current["lines"].append(raw)
        else:
            sections.append({"level": 0, "title": "", "lines": [raw]})
            current = sections.pop()
            sections.append(current)

    if current is not None and (not sections or sections[-1] is not current):
        sections.append(current)
    elif current is not None and sections and sections[-1] is current:
        pass
    return sections


def _table_rows(lines: list[str]) -> list[tuple[str, str]]:
    """Extract `(key, value)` pairs from a Field/Value markdown table."""
    rows: list[tuple[str, str]] = []
    seen_header = False
    for raw in lines:
        match = _TABLE_ROW_RE.match(raw)
        if not match:
            continue
        key = match.group("key").strip()
        value = match.group("value").strip()
        if not seen_header and key.lower() == "field" and value.lower() == "value":
            seen_header = True
            continue
        if set(key) <= {"-", " ", ":"} and set(value) <= {"-", " ", ":"}:
            # separator row e.g. | --- | --- |
            continue
        if not key:
            continue
        rows.append((key, value))
    return rows


def _bullet_items(lines: list[str]) -> list[str]:
    out: list[str] = []
    for raw in lines:
        match = _LIST_BULLET_RE.match(raw)
        if match:
            out.append(match.group("text").strip())
    return out


def parse_ccmc_spec_text(text: str) -> dict[str, Any]:
    sections = _parse_sections(text)

    parsed: dict[str, Any] = {
        "run_id": None,
        "model": None,
        "model_version": None,
        "event_time_utc": None,
        "fr_type": None,
        "fr_params": {},
        "cone_params": {},
        "cme_params": {},
        "mflampa_params": {},
        "metadata": {},
        "input_files_listed": [],
        "output_files_listed": [],
        "quicklook_targets": [],
        "unparsed_sections": [],
    }

    for sec in sections:
        title = sec["title"]
        title_lower = title.lower()
        rows = _table_rows(sec["lines"])
        bullets = _bullet_items(sec["lines"])

        # Run-summary section (Run ID etc.)
        if title_lower == "run summary":
            for line in sec["lines"]:
                run_match = _RUN_ID_RE.search(line)
                if run_match:
                    parsed["run_id"] = run_match.group("run_id")
                    break
            continue

        if title_lower == "run metadata":
            metadata: dict[str, Any] = {}
            for key, value in rows:
                slug = _slug(key)
                metadata[slug] = _coerce_value(value)
                if slug == "model_name":
                    parsed["model"] = str(value)
                elif slug == "model_version":
                    parsed["model_version"] = str(value)
            parsed["metadata"] = metadata
            continue

        if "cme eruption time" in title_lower:
            for key, value in rows:
                slug = _slug(key)
                if slug == "date":
                    parsed["event_time_utc"] = _normalize_event_time(value)
                else:
                    parsed["cme_params"][slug] = _coerce_value(value)
            continue

        if "flux rope parameters" in title_lower:
            fr_params: dict[str, Any] = {}
            for key, value in rows:
                slug = _slug(key)
                if slug == "fr_type":
                    parsed["fr_type"] = str(value)
                else:
                    fr_params[slug] = _coerce_value(value)
            parsed["fr_params"] = fr_params
            continue

        if "cone opening angle" in title_lower:
            cone: dict[str, Any] = {}
            for key, value in rows:
                cone[_slug(key)] = _coerce_value(value)
            parsed["cone_params"] = cone
            continue

        if "cme parameters" in title_lower:
            for key, value in rows:
                parsed["cme_params"][_slug(key)] = _coerce_value(value)
            continue

        if "mflampa parameters" in title_lower:
            mflampa: dict[str, Any] = {}
            for key, value in rows:
                mflampa[_slug(key)] = _coerce_value(value)
            parsed["mflampa_params"] = mflampa
            continue

        if title_lower == "input data":
            parsed["input_files_listed"] = bullets
            continue

        if title_lower == "output data":
            parsed["output_files_listed"] = bullets
            continue

        if title_lower == "quick look graphics":
            parsed["quicklook_targets"] = bullets
            continue

        # Anything else with a Field/Value table → record as untyped section evidence.
        if rows:
            parsed["unparsed_sections"].append({
                "title": title,
                "rows": [{"field": k, "value": v} for (k, v) in rows],
            })

    return parsed


def parse_ccmc_spec_file(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return {
            "run_id": None,
            "model": None,
            "model_version": None,
            "event_time_utc": None,
            "fr_type": None,
            "fr_params": {},
            "cone_params": {},
            "cme_params": {},
            "mflampa_params": {},
            "metadata": {},
            "input_files_listed": [],
            "output_files_listed": [],
            "quicklook_targets": [],
            "unparsed_sections": [],
            "read_error": str(exc),
        }
    return parse_ccmc_spec_text(text)
