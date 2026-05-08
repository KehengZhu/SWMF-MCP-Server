"""Deterministic classifier for SWMF magnetogram inputs.

Used by `inspect_artifact(artifact_type="magnetogram")`. Returns format and provenance
fields extracted from FITS headers and filename patterns. No network calls; no advice.

Recognized formats:

* `fits`           — synoptic / Carrington FITS (ADAPT/GONG/HMI/MDI variants).
* `map_out`        — ASCII synoptic map produced by SWMF (`map_NN.out`).
* `harmonics_dat`  — ASCII harmonics coefficient file produced by HARMONICS.exe.
* `unknown`        — anything else.

Map-type detection prefers FITS header keywords (`ORIGIN`, `OBS-SITE`, `TELESCOP`) and
falls back to filename patterns.
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path
from typing import Any

try:  # astropy is a project dependency.
    from astropy.io import fits as _fits
except ImportError:  # pragma: no cover - astropy missing surface
    _fits = None  # type: ignore[assignment]


_FILENAME_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # ADAPT: e.g. adapt40311_03k012_202402121200_i00010600n1.fts
    (re.compile(r"^adapt[0-9_a-zA-Z]+\.f(?:ts|its)$", re.IGNORECASE), "ADAPT"),
    # GONG QRII synoptic: mrzqs<YYMMDD>t<HHMM>c<CR>_<long0>.fits / .fts
    (re.compile(r"^mrzqs\d{6}t\d{4}c\d{4}_\d+\.f(?:ts|its)$", re.IGNORECASE), "GONG"),
    # GONG zero-point synoptic: mrbqs / mrnqs / mrmqs siblings
    (re.compile(r"^mr[a-z]qs\d{6}t\d{4}c\d{4}_\d+\.f(?:ts|its)$", re.IGNORECASE), "GONG"),
    # HMI: e.g. hmi.synoptic_mr_polfil_720s.<CR>.Mr_polfil.fits
    (re.compile(r"^hmi[._].*\.fits$", re.IGNORECASE), "HMI"),
    # MDI: e.g. synop_Mr_0.<CR>.fits
    (re.compile(r"^synop_mr_.*\.fits$", re.IGNORECASE), "MDI"),
]

_GONG_FILENAME_RE = re.compile(
    r"^(?P<series>mr[a-z]qs)(?P<yy>\d{2})(?P<mm>\d{2})(?P<dd>\d{2})t"
    r"(?P<hh>\d{2})(?P<mn>\d{2})c(?P<cr>\d{4})_(?P<long0>\d+)",
    re.IGNORECASE,
)


def _classify_format_by_extension_or_content(path: Path, head_bytes: bytes) -> str:
    suffix = path.suffix.lower()
    if suffix in {".fits", ".fts"}:
        return "fits"
    # FITS files commonly start with "SIMPLE  =" but require ASCII parsing; fall back to
    # heuristic on the head bytes when extension is unconventional.
    if head_bytes.startswith(b"SIMPLE"):
        return "fits"
    name = path.name.lower()
    if name.startswith("map_") and suffix == ".out":
        return "map_out"
    if name in {"mf.dat", "harmonics_adapt.dat", "harmonics_bxyz.dat"} or "harmonics" in name:
        return "harmonics_dat"
    if suffix == ".dat":
        # ASCII tabular files. Without the header keys we cannot say more; mark unknown.
        return "harmonics_dat" if "harmonic" in name else "unknown"
    return "unknown"


def _map_type_from_header(header: dict[str, Any]) -> str | None:
    text = " ".join(
        str(header.get(k, "")) for k in ("ORIGIN", "OBS-SITE", "TELESCOP", "INSTRUME")
    )
    text = text.upper()
    if "ADAPT" in text:
        return "ADAPT"
    if "GONG" in text:
        return "GONG"
    if "HMI" in text or "SDO" in text:
        return "HMI"
    if "MDI" in text or "SOHO" in text:
        return "MDI"
    return None


def _map_type_from_filename(path: Path) -> str | None:
    name = path.name
    for pattern, label in _FILENAME_PATTERNS:
        if pattern.match(name):
            return label
    return None


def _carrington_from_header(header: dict[str, Any]) -> int | None:
    for key in ("CAR_ROT", "CARROT", "MAPCRDR", "CRROT", "CR"):
        value = header.get(key)
        if value is None:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def _observation_time_from_header(header: dict[str, Any]) -> str | None:
    iso = header.get("DATE-OBS")
    time_obs = header.get("TIME-OBS")
    if iso and "T" in str(iso):
        return str(iso)
    if iso and time_obs:
        return f"{iso}T{time_obs}"
    if iso:
        return str(iso)
    map_date = header.get("MAPDATE")
    map_time = header.get("MAPTIME")
    if map_date and map_time:
        return f"{map_date}T{map_time}"
    if map_date:
        return str(map_date)
    return None


def _carrington_from_filename(path: Path) -> tuple[int | None, str | None, int | None]:
    """Return (CR, observation_time_iso, long0) inferred from a GONG-style filename."""
    match = _GONG_FILENAME_RE.match(path.name)
    if not match:
        return None, None, None
    yy = 2000 + int(match.group("yy"))
    obs = _dt.datetime(
        yy,
        int(match.group("mm")),
        int(match.group("dd")),
        int(match.group("hh")),
        int(match.group("mn")),
        tzinfo=_dt.timezone.utc,
    )
    return int(match.group("cr")), obs.strftime("%Y-%m-%dT%H:%M:%S+00:00"), int(match.group("long0"))


def parse_magnetogram_file(path: Path) -> dict[str, Any]:
    """Pure parser for a magnetogram file. Returns typed evidence fields."""
    file_size = path.stat().st_size if path.is_file() else 0
    out: dict[str, Any] = {
        "format": "unknown",
        "carrington_rotation": None,
        "observation_time": None,
        "map_type": "unknown",
        "realization_count": None,
        "grid": {"nlon": None, "nlat": None},
        "file_size_bytes": file_size,
        "filename": path.name,
        "filename_inferred_long0": None,
        "fits_header_keys": [],
        "evidence_source": "filename",
        "warnings": [],
    }

    try:
        with path.open("rb") as fh:
            head_bytes = fh.read(32)
    except OSError as exc:
        out["warnings"].append(f"Could not read file head: {exc}")
        return out

    fmt = _classify_format_by_extension_or_content(path, head_bytes)
    out["format"] = fmt

    cr_filename, time_filename, long0_filename = _carrington_from_filename(path)
    if cr_filename is not None:
        out["carrington_rotation"] = cr_filename
        out["observation_time"] = time_filename
        out["filename_inferred_long0"] = long0_filename
    map_type_filename = _map_type_from_filename(path)
    if map_type_filename:
        out["map_type"] = map_type_filename

    if fmt == "fits" and _fits is not None:
        try:
            with _fits.open(path, memmap=False) as hdul:
                primary = hdul[0]
                header = dict(primary.header)
                naxis1 = header.get("NAXIS1")
                naxis2 = header.get("NAXIS2")
                naxis3 = header.get("NAXIS3")
                grid_lon = int(naxis1) if isinstance(naxis1, (int, float)) else None
                grid_lat = int(naxis2) if isinstance(naxis2, (int, float)) else None
                realizations: int | None = None
                if isinstance(naxis3, (int, float)):
                    realizations = int(naxis3)

                map_type_header = _map_type_from_header(header)
                if map_type_header:
                    out["map_type"] = map_type_header

                cr_header = _carrington_from_header(header)
                if cr_header is not None:
                    out["carrington_rotation"] = cr_header
                    out["evidence_source"] = "fits_header"

                obs_header = _observation_time_from_header(header)
                if obs_header:
                    out["observation_time"] = obs_header
                    out["evidence_source"] = "fits_header"

                out["grid"] = {"nlon": grid_lon, "nlat": grid_lat}
                out["realization_count"] = realizations
                out["fits_header_keys"] = sorted(
                    [str(k) for k in header.keys() if k and not str(k).startswith(" ")]
                )[:80]
        except Exception as exc:  # pragma: no cover - astropy parse failure
            out["warnings"].append(f"FITS parse failed: {exc}")
    elif fmt == "fits" and _fits is None:  # pragma: no cover - astropy missing surface
        out["warnings"].append("astropy not installed; FITS header not read.")

    return out
