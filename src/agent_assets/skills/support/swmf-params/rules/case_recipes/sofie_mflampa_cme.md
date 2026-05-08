# sofie_mflampa_cme — case recipe

Multi-session skeleton for an AWSoM-R + Stream-Aligned MHD (SaMhd) CME run with SC + IH
coupling and MFLAMPA SP coupling. Anchored on `examples/CCMC_run_weihao/` (the CCMC
"Weihao_Liu_011326_SH_1" standard answer). The closest shipped templates are
`SWMFSOLAR/Param/PARAM.in.sofie.CCMC` (background) and
`SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA` (eruption + SEP).

The recipe is **structure**, not values. Numbers are template- or spec-supplied.

## Two-PARAM split (mandatory)

This archetype produces **two** PARAM files:

| File | Role | `#TIMEACCURATE` | `#CME` | SP component | Restart |
| ---- | ---- | --------------- | ------ | ------------ | ------- |
| `PARAM.expand.start`   | steady-state SC + IH background | `F` | absent | absent | writes `SC/restartOUT/`, `IH/restartOUT/` |
| `PARAM.expand.restart` | time-accurate eruption + SEP    | `T` | present in SC, session 1 | active (`SP/MFLAMPA`) | reads `SC/restartIN/restart.H`, `IH/restartIN/restart.H` |

A merged single-PARAM is rejected by this recipe.

## Component map

* `start`: `SC 0 -1 1`, `IH 0 -1 1` (no SP).
* `restart`: `SC 0 -1 1`, `IH 0 -1 1`, `SP 0 224 1` (rank-bounded SP component because
  MFLAMPA does not scale to the full job width).

## Build flags

| Component | Config.pl flags | Lane |
| --------- | --------------- | ---- |
| layout    | `-v=Empty,SC/BATSRUS,IH/BATSRUS,SP/MFLAMPA` (or `-v=SC/BATSRUS,IH/BATSRUS,SP/MFLAMPA`) | `defaults/build_flags.yaml::sofie_mflampa_cme_layout` |
| SC        | `-o=SC:u=AwsomR,e=AwsomSA,ng=2,g=8,8,4` | `defaults/build_flags.yaml::sofie_mflampa_cme_sc` |
| IH        | `-o=IH:u=AwsomR,e=AwsomSA,ng=2,g=4,4,4` | `defaults/build_flags.yaml::sofie_mflampa_cme_ih` |
| SP        | `-o=SP:g=20000` | `defaults/build_flags.yaml::sofie_mflampa_cme_sp` |

## `PARAM.expand.start` session ladder (background)

Five-session SC-then-IH ladder. Iteration counts come from
`defaults/session_ladders.yaml::sofie_mflampa_steady_ladder`; scale proportionally for
denser/coarser grids and verify in the runlog.

| Session | Toggles | Role |
| ------- | ------- | ---- |
| 1 | SC only; `#DOAMR T`; initial `#GRIDRESOLUTION` ramp; `#MINIMUMRADIALSPEED T` | initial AMR in SC, build threaded gap |
| 2 | SC only; `#DOAMR F`; `#MINIMUMRADIALSPEED F` | freeze SC AMR before coupling |
| 3 | `#COMPONENT IH T`; `#COUPLE1 SC->IH Dn=1`; activate IH | enable IH, couple every step |
| 4 | `#COUPLE1 SC->IH Dn=-1`; `#COMPONENT SC F`; `#DOAMR T` in IH | freeze SC, run IH AMR alone |
| 5 | `#DOAMR F` in IH | freeze IH AMR; tail iterations |

Session terminators are all `#STOP MaxIter=<value>` with `TimeMax=-1.0`.

## `PARAM.expand.restart` session ladder (eruption + SEP)

| Session | `#TIMEACCURATE` | `#CME` UseCme | `#STOP TimeMax` | Role |
| ------- | --------------- | ------------- | --------------- | ---- |
| 1 | T | T | `cme_traveling_time` | seed FR in SC; propagate; couple SC↔IH↔SP |
| 2 | T | F | `(smoothing_factor) * cme_traveling_time` | relaxation tail; SEP follow-up |

Session 1 is opened with the SP component active and the `#FIELDLINE` registry between
SC, IH, SP. The SP component holds `#GRIDNODE`, `#ORIGIN`, `#MOMENTUMBC`,
`#USEFIXEDMFPUPSTREAM`, `#USEDATETIME` blocks; cadences come from spec values.

## Where each command lives

| Command | start | restart | Component | Session |
| ------- | ----- | ------- | --------- | ------- |
| `#DESCRIPTION` | yes | yes | global | 1 |
| `#STARTTIME` | yes | absent (covered by restart.H + `#INCLUDE RESTART.in`) | global | 1 |
| `#TIMEACCURATE` | F (1) | T (1) | global | 1 |
| `#COMPONENTMAP` | yes (SC, IH) | yes (SC, IH, SP) | global | 1 |
| `#SAVERESTART` | yes (DnSaveRestart=20000) | F | global | 1 |
| `#INCLUDE RESTART.in` | absent | yes | global | 1 |
| `#GRIDNODE` | absent | yes | SP | 1 |
| `#ORIGIN` | absent | yes (spec lon/lat min/max + ROrigin=2.5) | SP | 1 |
| `#MOMENTUMBC` | absent | yes (SpectralIndex, EfficiencyInj from spec) | SP | 1 |
| `#USEFIXEDMFPUPSTREAM` | absent | yes (MeanFreePath0 from spec) | SP | 1 |
| `#FIELDLINE` | absent | yes (RScMin=1.105, RScMax=21, RIhMin=19, RIhMax=640) | global | 1 |
| `#COUPLE1 SC→SP`/`IH→SP` | absent | yes (Dt=120 s) | global | 1 |
| `#HARMONICSGRID` | yes | yes | SC | 1 |
| `#HARMONICSFILE` | yes (`SC/mf.dat`) | yes (`SC/mf.dat`) | SC | 1 |
| `#POYNTINGFLUX` | yes (spec ratio × 1e6) | yes (spec ratio × 1e6) | SC, IH | 1 |
| `#CORONALHEATING` | yes (spec value × 1e5) | yes (spec value × 1e5) | SC, IH | 1 |
| `#CME` | absent | yes (UseCme=T) | SC | 1 |
| `#HELIOUPDATEB0` | absent | yes (DtUpdateB0=300) | SC | 1 |
| `#AMRREGION CMEbox` | yes (spec FR + cone) | absent | SC | 1 |
| `#AMRREGION coneIH_CME` | absent | yes (spec rotation) | IH | 1 |
| `#SAVEPLOT` quick-look | minimal (1 file in SC, 2 in IH) | full (CME diagnostics, LASCO C2, EUVI, AIA where requested) | SC, IH | 1+ |
| `#CPUTIMEMAX` | absent | yes (default 44 h) | global | 1 |
| `#STOP` | per session | per session | global | each |
| `#RUN`/`#END` | session boundaries | session boundaries | global | between |

## Decision points the recipe leaves to spec/template/derivation

* Magnetogram FITS source (GONG / ADAPT / HMI) — spec.
* `#STARTTIME` value — spec event time.
* FR fields (`LongitudeCme`, `LatitudeCme`, `OrientationCme`, `Radius`, `BStrength`,
  `uCme`) — spec.
* `TypeCme` translation from spec `FR_type` — `physical_constraints.yaml::cme_typecme_matches_spec_fr_type`
  surfaces the discrepancy; the user confirms `GL → SPHEROMAK` translation before
  launch.
* SPHEROMAK shape (`Stretch`, `ApexHeight`, `iHelicity`, `DecayCme`) —
  `defaults/cme_eruption.yaml::spheromak_shape_defaults`.
* `#AMRREGION CMEbox` bounds — `derivations/geometric.yaml::cmebox_from_fr_and_cone`.
* `#AMRREGION coneIH_CME` rotation — `derivations/geometric.yaml::coneih_rotation_from_fr`.
* SP `#ORIGIN` lat/lon bounds — `derivations/geometric.yaml::mflampa_origin_from_spec_ranges`.
* SP `#MOMENTUMBC` `SpectralIndex`, `EfficiencyInj` — spec.
* `#USEFIXEDMFPUPSTREAM` `MeanFreePath0` — spec.
* Iteration counts — `defaults/session_ladders.yaml`.
* Operational guards (`#CPUTIMEMAX`, `#MINIMUMPRESSURE`, `#MINIMUMTEMPERATURE`,
  `#HELIOUPDATEB0`) — `defaults/ops_guards.yaml` and `defaults/cme_eruption.yaml`.
* Lookup tables (`RadCoolCorona`, `TR`, `los_tbl`, `los_Eit_cor`, `los_EuviA/B`, `aia`) —
  copied from template verbatim.

## Quick-look mapping (CCMC → SAVEPLOT entries)

When the spec lists CCMC quick-look targets, the eruption PARAM picks `#SAVEPLOT` blocks
from this table. Every entry is recipe-driven; the agent must not synthesize plot
strings outside this list.

| CCMC quick-look phrase | StringPlot | Component |
| ---------------------- | ---------- | --------- |
| Synthetic LASCO C2 brightness movie | `los ins idl_ascii soho:c2` | SC |
| Synthetic LASCO C2 running difference movie | `los ins idl_ascii soho:c2` (with run-difference postproc) | SC |
| Synthetic LASCO C3 movie | `los ins idl_ascii soho:c3` | SC |
| EUVI A / EUVI B / AIA panels | `los ins idl_ascii sta:euvi stb:euvi sdo:aia` | SC |
| In-situ comparison at Earth/STA/STB | `#SATELLITE MHD` block(s) for earth, sta, stb | SC, IH |
| 3D speed / shock surface movies in z=0/y=0/x=0 | `z=0 VAR idl`, `y=0 VAR idl`, `x=0 VAR idl` with `u bx;by` | SC, IH |
| Proton flux >10 MeV / >100 MeV at 1 AU | `#SAVEPLOT mh2d flux ascii Radius=215.0` | SP |
| Radial magnetic field (input) | derived from `#HARMONICSFILE` + post-prep IDL render | n/a |

Items not in this table are surfaced to the user as a `gap` rather than guessed.
