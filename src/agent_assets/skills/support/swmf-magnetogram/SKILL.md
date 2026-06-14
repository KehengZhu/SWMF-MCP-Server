---
name: swmf-magnetogram
type: support
description: "Support skill. Owns the policy for magnetogram inputs: ADAPT vs GONG vs HMI vs MDI; FITS vs map_NN.out vs harmonics .dat; how PARAM commands #HARMONICSFILE/#HARMONICSGRID/#FDIPS reference them; alignment with #STARTTIME. Loaded by swmf-replicate and swmf-configure."
---

# swmf-magnetogram (Support)

This is a **support skill**. `swmf-replicate` and `swmf-configure` consult it whenever a
magnetogram is named, mentioned, or required.

## Purpose

Answer one thing: given a magnetogram file (or a target event time), what is its type
and observation context, and how does it slot into PARAM.in / FDIPS / HARMONICS?

## Scope

* Magnetogram-type detection (ADAPT, GONG, HMI, MDI) from FITS headers and filename
  patterns.
* File-format detection: FITS, `map_NN.out` ASCII synoptic, harmonics `.dat`.
* How PARAM commands consume each format:
  * `#HARMONICSFILE` + `#HARMONICSGRID` for harmonics-derived inputs (`mf.dat`,
    `harmonics_adapt.dat`).
  * `#FDIPS` block for FDIPS-derived `fdips_bxyz.out` paths.
* Carrington-rotation and observation-time alignment with PARAM `#STARTTIME`.

Not in scope: network downloads (use `SWMFSOLAR/Scripts/download_ADAPT.py`); image-level
analysis; arbitrary FITS science processing.

## Tool Protocol

For one named magnetogram:

```bash
swmf inspect --type magnetogram --path <fits_or_map_or_harmonics>
```

For locating a download entrypoint when no file is named:

```bash
swmf get-evidence --query "magnetogram" --task-type configuration --goal "magnetogram entrypoint and file conventions"
```

The skill runs `swmf inspect` first whenever a candidate file exists locally; it falls back to
`swmf get-evidence` only when no file is named or when the user asks "where do I get one."

## Authority Order

1. `swmf inspect --type magnetogram` — FITS header + filename pattern.
2. Filename pattern alone, when the file head bytes are not parseable. The GONG-style
   pattern is `mr<series>qs<YYMMDD>t<HHMM>c<CR>_<long0>.{fits,fts}`; ADAPT files start
   with `adapt`; HMI files start with `hmi.`; MDI files with `synop_Mr_`.
3. `swmf get-evidence --task-type configuration` for entrypoints and conventions.
4. `SWMFSOLAR/Scripts/download_ADAPT.py` and `change_awsom_param.py` for the operational
   acquisition + alignment workflow.

## Output Contract

For a named file:

* `format` ∈ {fits, map_out, harmonics_dat, unknown}.
* `map_type` ∈ {ADAPT, GONG, HMI, MDI, other, unknown}.
* `carrington_rotation` (CR number) and `observation_time` (ISO).
* `realization_count` (typically 12 for ADAPT bundles).
* `grid` `{nlon, nlat}`.
* `evidence_source` — `fits_header` or `filename`.
* `expected_param_blocks` — derived from `format`:
  * `fits` → `#HARMONICSGRID` + `#HARMONICSFILE` (after running `HARMONICS.exe`).
  * `harmonics_dat` → `#HARMONICSFILE` direct.
  * `map_out` → `#HARMONICSGRID` + harmonics step.
* `alignment_concerns` — list, e.g.:
  * "spec event time is N hours after magnetogram observation time; verify rotation
    alignment via SWMFSOLAR change_awsom_param.py."
  * "ADAPT realization not yet selected; default 1..12 sweep available."

## Anti-patterns

* Do not invent download URLs or magnetogram filenames.
* Do not infer Carrington-rotation alignment from `#STARTTIME` arithmetic; defer to
  `SWMFSOLAR/Scripts/change_awsom_param.py`.
* Do not classify a magnetogram type from filename when the FITS header disagrees;
  surface the discrepancy.
* Do not silently accept an ADAPT realization — the realization is a sweep axis (1..12)
  unless the user pinned one.

## Cluster-bound notes

* GONG QRII hourly maps (`mrzqs*`) are 360×180 latitude-longitude maps in Gauss.
  CCMC SOFIE+MFLAMPA workflows route them through `HARMONICS.exe` to produce `mf.dat`
  inside the run-directory's `SC/` folder. The `#HARMONICSFILE` line should resolve to
  `SC/mf.dat`.
* ADAPT FITS bundles ship 12 realizations (`NAXIS3=12`); selecting one is a sweep
  decision the skill surfaces but does not pick.
