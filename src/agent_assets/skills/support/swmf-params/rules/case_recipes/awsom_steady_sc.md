# awsom_steady_sc — case recipe

Multi-session skeleton for an AWSoM (or AWSoM-R) steady-state solar-wind run.
Covers two layouts: **SC+IH** (full solar wind background for CME) and **SC-only**
(coronal structure studies where the domain ends at ~24 Rs and no heliospheric
propagation is needed).

The recipe is **structure**, not values. Numbers come from `defaults/awsom_steady.yaml`;
this document specifies which command goes in which session and what each session toggles.

## Purpose

**SC+IH layout**: Produce a steady-state solar wind background to be used before a CME
eruption. The `PARAM.expand.start` produced here must converge before
`PARAM.expand.restart` can start.

**SC-only layout**: Produce a steady-state corona for coronal structure or heating studies
where the simulation domain ends at the SC outer boundary (~24 Rs) and no IH component
is needed. Use this layout when the science target is coronal topology, white-light
synthesis, open flux, or DEM — not in-situ solar wind at L1/STEREO.

## Single-PARAM structure

The steady-state background is one PARAM file (`PARAM.expand.start`). Unlike the eruption
PARAM, it does not split across two files.

## Layout decision

Choose the layout before writing `#COMPONENTMAP` or `Config.pl` flags:

| Condition | Layout |
| --------- | ------ |
| CME background; downstream `PARAM.expand.restart` will follow | **SC+IH** |
| Science target is coronal topology, white-light, open flux, DEM; no in-situ output needed | **SC-only** |
| Domain explicitly ends at ≤ 24 Rs in the spec | **SC-only** |
| Spec or prior run has `#SATELLITE earth/sta/stb` as primary output | **SC+IH** |

If ambiguous, default to **SC+IH** and note the assumption.

## Build flags

| Layout | Config.pl flags |
| ------ | --------------- |
| SC+IH | `./Config.pl -v=Empty,SC/BATSRUS,IH/BATSRUS` |
| SC+IH SC physics | `./Config.pl -o=SC:u=Awsom,e=AwsomAnisoPi,g=6,8,8,nG=3` (or `u=AwsomR,e=AwsomSA`) |
| SC+IH IH physics | `./Config.pl -o=IH:u=Awsom,e=AwsomAnisoPi,g=8,8,8,nG=3` (must match SC variant) |
| SC-only | `./Config.pl -v=Empty,SC/BATSRUS` |
| SC-only SC physics | same SC line as above |

Anchored on `SWMFSOLAR/Param/PARAM.in.awsom.STITCH` (SC-only precedent) and
`SWMFSOLAR/Param/PARAM.in.awsom` (SC+IH precedent).

## Session ladder — SC+IH layout

| Session | Active comps | Toggles | `#STOP` | Role |
| ------- | ------------ | ------- | ------- | ---- |
| 1 | SC | `#DOAMR T`; `#MINIMUMRADIALSPEED T`; limiter=`minmod`; `#GRIDGEOMETRY` + `#GRID` + `#LIMITRADIUS` (first session only) | `MaxIter=1000` | initial AMR in SC, build threaded gap |
| 2 | SC | `#SCHEME mc3+1.2` | `MaxIter=70000` | converge SC wind with better limiter |
| 3 | SC | `#MINIMUMRADIALSPEED F`; `#DOAMR F` | `MaxIter=80000` | freeze SC AMR before IH coupling |
| 4 | SC + IH | `#COMPONENT IH T`; `#COUPLE1 SC→IH Dn=1` (one-step coupling) | `MaxIter=80001` | activate IH; one coupling step to pass SC state |
| 5 | IH only | `#COMPONENT SC F`; `#DOAMR T` in IH | `MaxIter=83000` | IH AMR ramp |
| 6 | IH only | `#DOAMR F` in IH | `MaxIter=85000` | freeze IH AMR |
| (optional) 7–10 | SC → SC+IH → IH | higher-order scheme `nOrder=5` + `mp5` limiter | per run | high-accuracy tail if needed |

Sessions 7–10 (from `PARAM.in.awsom`) activate a 5th-order SCHEME for SC and then
re-couple IH. Include only if the user requires high-order convergence; omit for standard
CCMC runs.

## Session ladder — SC-only layout

| Session | Active comps | Toggles | `#STOP` | Role |
| ------- | ------------ | ------- | ------- | ---- |
| 1 | SC | `#DOAMR T`; `#MINIMUMRADIALSPEED T`; limiter=`minmod`; `#GRIDGEOMETRY` + `#GRID` + `#LIMITRADIUS` (first session only) | `MaxIter=1000` | initial AMR in SC |
| 2 | SC | `#SCHEME mc3+1.2` | `MaxIter=80000` | converge SC corona |
| 3 (optional) | SC | `#MINIMUMRADIALSPEED F`; `#DOAMR F` | `MaxIter=80000` | freeze AMR (merge with session 2 if AMR already off) |
| 4 (optional) | SC | 5th-order: `#SCHEME Linde` + `nOrder=5` + `TypeLimiter=mc3` → switch to `mp5` | `MaxIter=90000` | high-accuracy tail for white-light / DEM quality |

Session 4 (high-order tail) is required when the science target is white-light synthesis,
AIA EUV, or DEM. It corresponds to the 10k final iterations with the MP5+Suresh-Huynh
limiter used in Liu et al. 2026 (§2.3). Skip it for convergence-only runs.

There are no IH sessions. Drop all `#COUPLE1`, `#BUFFERGRID`, `#BODY`, `#DIVB`,
`#INNERBOUNDARY buffergrid`, and `#COMPONENT IH` commands entirely.

## Where each command lives

Commands marked **SC-only: omit** must not appear in a SC-only PARAM.in.

| Command | Session | Component | SC+IH | SC-only |
| ------- | ------- | --------- | ----- | ------- |
| `#DESCRIPTION` | 1 | global | required | required |
| `#COMPONENTMAP` | 1 | global | `SC 0 -1 1`, `IH 0 -1 1` | `SC 0 -1 1` only |
| `#TIMEACCURATE` | 1 | global | `F` | `F` |
| `#STARTTIME` | 1 | global | magnetogram observation time | same |
| `#SAVERESTART` | 1 | global | `DnSaveRestart=20000, DtSaveRestart=-1` | same |
| `#ROTATEHGR` / `#ROTATEHGI` | 1 | global | `-1` to auto-align | same |
| `#TEST init_axes` | 1 | global | required for SC/IH axis init | required |
| `#GRIDBLOCKALL` | 1 | SC (IH when present) | both comps | SC only |
| `#GRIDGEOMETRY` | 1 | SC | `spherical_genr` + `SC/Param/grid_awsom.dat` | same |
| `#GRID` | 1 | SC, IH | SC: ±100 Rs, IH: ±250 Rs | SC only |
| `#LIMITRADIUS` | 1 | SC | `rMin=1.0, rMax=24.0` | same |
| `#RESTARTOUTFILE one` | 1 | SC (IH when present) | both comps | SC only |
| `#COORDSYSTEM` | 1 | IH | `HGC` or `HGI` | **omit** |
| `#PLASMA` | 1 | SC (IH when present) | both comps | SC only |
| `#HARMONICSFILE` | 1 | SC | required | required |
| `#HARMONICSGRID` | 1 | SC | required | required |
| `#POYNTINGFLUX` | 1 | SC | spec-derived | spec-derived (see Table 2 for multi-map studies) |
| `#CORONALHEATING` | 1 | SC (IH when present) | both comps | SC only |
| `#HEATPARTITIONING` | 1 | SC (IH when present) | both comps | SC only |
| `#RADIATIVECOOLING` | 1 | SC | `T`; requires radcool + TR LOOKUPTABLE | same |
| `#LOOKUPTABLE radcool` | 1 | SC | `SC/Param/RadCoolCorona_8.0.dat` | same |
| `#LOOKUPTABLE TR` | 1 | SC | `SC/Param/TR.dat` | same |
| `#COARSEAXIS` | 1 | SC | `nCoarseLayer=2` (AWSoM-R); `3` (SOFIE) | same |
| AMR regions | 1 | SC | see *AMR variants* below | see *AMR variants* below |
| `#DOAMR` | 1 → 3 | SC (IH when present) | T → F; IH: T at s4, F at s6 | SC only; T → F at session 3 |
| `#MINIMUMRADIALSPEED` | 1 → 3 | SC | T → F at session 3 | same |
| `#TIMESTEPPING` | 1 | SC (IH when present) | `nStage=2, cfl=0.8` | SC only |
| `#SCHEME` | 1 | SC (IH when present) | see defaults/awsom_steady.yaml | SC only; session 4 switches to `nOrder=5, mp5` |
| `#LIMITER` | 1 | SC | `UseLogRhoLimiter=T, UseLogPLimiter=T` | same |
| `#MINIMUMTEMPERATURE` | 1 | SC | `TminDim=5e4, TeMinDim=5e4` | same |
| `#MINIMUMPRESSURE` | 1 | SC | `1E-9`; IH: `1E-14` | SC `1E-9` only |
| `#NONCONSERVATIVE` | 1 | SC (IH when present) | `F` | SC only |
| `#RESCHANGE` | 1 | SC (IH when present) | `T` | SC only |
| `#SAVELOGFILE` | 1 | SC (IH when present) | both comps | SC only |
| `#OUTERBOUNDARY` | 1 | SC | `user, float, periodic×4` | same |
| `#USERSWITCH` | 1 | SC | `+init +ic` | same |
| `#SAVEPLOT` | 1 | SC (IH when present) | x=0, y=0, z=0 VAR idl; LOS; slg | SC only; add LOS and EUV tables for coronal study |
| `#SATELLITE` | 1 | SC, IH | earth, sta, stb .dat files | SC only or **omit** if no in-situ target |
| `#LOOKUPTABLE AiaXrt/euv/EuviA/EuviB` | 1 | SC | LOS synthesis tables | required for EUV/white-light output |
| `#SAVEINITIAL` | 1 | SC | `T` | same |
| `#INNERBOUNDARY buffergrid` | 4 | IH | SC+IH only | **omit** |
| `#BUFFERGRID` | 4 | IH | SC+IH only | **omit** |
| `#BODY` | 4 | IH | SC+IH only | **omit** |
| `#DIVB` | 4 | IH | SC+IH only | **omit** |
| `#COUPLE1 SC→IH` | 4 | global | `Dn=1` then `-1` | **omit** |
| `#COMPONENT IH T/F` | 4 / 5 | global | SC+IH only | **omit** |
| `#STOP` | each | global | MaxIter per defaults ladder | same |
| `#RUN` | boundaries | global | required | required |
| `#END` | last | global | required | required |

## AMR variants

### Standard (SC+IH and SC-only CME background)

Two named regions placed in session 1 and left active until `#DOAMR F`:

| Region | Type | Parameters | Target resolution |
| ------ | ---- | ---------- | ----------------- |
| `InnerShell` | `shell0` | `RadiusInner=1.0, Radius=1.7` | highest near inner boundary |
| `earthcone` | `cone` | half-angle ~10°, toward Earth | high resolution along Sun-Earth line |
| `cmebox` (optional) | `brick0` | lon/lat bounds around active region | pre-refine CME source region |

`#AMRCRITERIARESOLUTION`: 3 criteria for SC (add a 4th/5th for cmebox when present).

### Coronal eclipse study (SC-only, Liu et al. 2026 pattern)

Four refinement levels applied in sequence as iteration count increases. AMR is driven by
`#AMRCRITERIARESOLUTION` resolution thresholds, not gradient-based criteria. Regions are
placed in session 1; the AMR sequence is controlled by `#DOAMR` toggling across sessions.

| Level | Region name | Type | Bounds | Target resolution | When applied |
| ----- | ----------- | ---- | ------ | ----------------- | ------------ |
| 1 | (global) | whole domain | — | 2.8° | initial mesh |
| 2 | (global refine) | whole domain | — | 1.4° | after ~20k iterations (factor-2 uniform refinement) |
| 3 | `OuterCorona` | `shell0` | `RadiusInner=1.0, Radius=5.5` | 0.7° | same AMR pass as level 2 |
| 4 | `LowCoronaEquatorial` | constrained shell | `r=[1.01, 1.2] Rs`, `lat=[-30°, 30°]` | 0.35° | same AMR pass; resolves low-corona active-region belt |

`LowCoronaEquatorial` covers the full longitude range (0°–360°) and a ±30° latitude
band. In SWMF this can be expressed as a `brick0` region aligned in spherical coordinates
or as a shell-with-latitude-bounds if the BATSRUS version supports it; check the available
`#AMRREGION` type keywords in the current SWMF source before writing the block.

`#AMRCRITERIARESOLUTION` for this variant: 4 criteria, one per level, ordered from
coarsest (global 1.4°) to finest (`LowCoronaEquatorial` 0.35°).

Anchored on Liu et al. 2026 §2.3 (ApJ 997:243). No prior SWMFSOLAR template uses this
exact 4-level pattern; treat parameter values as **confirmed** (from paper) but
SWMF-command translation as **inferred** until `TestParam.pl` validates.

## Decision points the recipe leaves to spec/template

* **SC+IH vs SC-only** — see *Layout decision* table above. Mark choice as `confirmed`
  if the spec explicitly states the domain extent or absence of IH; otherwise `inferred`.
* **AMR variant** — `standard` (default) or `coronal_eclipse` (when science target is
  coronal topology/heating and the spec matches the Liu et al. 2026 setup). Mark as
  `inferred` unless the paper/spec explicitly describes the 4-level scheme.
* Magnetogram source (ADAPT vs GONG vs HMI) and its date — spec.
* `#STARTTIME` — spec event time.
* `#ROTATEHGR` / `#ROTATEHGI` — `-1` for auto-rotation to align magnetogram; omit if
  the prior run did not rotate (check `PARAM.in` from prior run).
* `#POYNTINGFLUX` — spec-derived via `derivations/geometric.yaml::poyntingflux_from_spec_ratio`.
  For multi-map ensemble studies, use per-map calibrated (S_A/B)_⊙ values from the spec
  (e.g. Liu et al. 2026 Table 2 gives explicit values for 4 maps).
* `#CORONALHEATING` `LperpTimesSqrtBSi` — spec-derived.
* `#AMRREGION cmebox` bounds — optional for SC+IH CME background; if CME source region
  is known, apply `derivations/geometric.yaml::cmebox_from_fr_and_cone`.
* High-order tail (session 4, SC-only) — include when science target is white-light,
  AIA EUV, or DEM; omit for convergence studies.
* Iteration counts per session — `defaults/awsom_steady.yaml::awsom_steady_session_ladder`.
* Lookup tables — copied from template verbatim.

## AWSoM vs SOFIE differences in the background PARAM

| Feature | AWSoM / AWSoM-R | SOFIE (SaMhd) |
| ------- | --------------- | ------------- |
| Inner BC radius | 1.0 Rs | 1.1 Rs |
| `OUTERBOUNDARY TypeBc1` | `user` | `fieldlinethreads` |
| `HARMONICSGRID.rSourceSurface` | 25 | 2.5 |
| `HARMONICSGRID.IsLogRadius` | T | F |
| `HARMONICSGRID.MaxOrder` | 180 | 90 |
| `GRIDGEOMETRY` | `spherical_genr` + grid_awsom.dat | `spherical_lnr` |
| `#CURLB0` / `#B0SOURCE` / `#ALIGNBANDU` | absent | required |
| `COARSEAXIS.nCoarseLayer` | 2 | 3 |

## Anchored from template

`SWMFSOLAR/Param/PARAM.in.awsom` — full 10-session AWSoM SC+IH steady-state ladder.
`SWMFSOLAR/Param/PARAM.in.awsom.STITCH` — SC-only AWSoM precedent (`Config.pl -v=Empty,SC/BATSRUS`; `rMax=24.0`). Use for SC-only layout structure even though STITCH is time-accurate; drop `#STITCH`/`#STITCHREGION` and change `#TIMEACCURATE` to `F`.
`SWMFSOLAR/Param/PARAM.in.sofie.CCMC` — SOFIE (SaMhd) 5-session steady-state background.
