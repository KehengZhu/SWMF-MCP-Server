# numerical_practices.md

Narrative best-practice notes loaded by the `swmf-params` skill. The skill output contract
requires citing which entries it applied or considered, even when narrative.

This file is append-only. Add a new bullet when a practice is confirmed or a past mistake
recurs; remove an entry only when it has been superseded.

---

## AWSoM/AWSoM-R steady-state convergence

* For AWSoM SC, `#TIMESTEPPING` of nStage=2 / cfl=0.8 is the operating default. When
  raising `#GRIDLEVEL` for the first few iterations, halve `cfl` until the initial
  transient damps; otherwise the inner-boundary Alfvén-wave reflection can blow up the
  threaded-field-line region.
* AWSoM-R requires the `#FIELDLINETHREAD` and `#PLOTTHREADS` blocks together. Removing one
  while keeping the other is a silent failure mode; the run will start but produce
  wrong-looking outputs near the inner boundary.

## CME eruption sessions

* The standard AWSoM/AWSoM-R CME PARAM is split across **two** files: a steady-state
  background (`PARAM.expand.start`) and a time-accurate eruption (`PARAM.expand.restart`).
  The eruption PARAM `#INCLUDE`s the SC and IH `restartIN/restart.H` produced by the
  background. Producing a single merged PARAM is operationally fragile (no checkpoint).
* The `#CME` block in the eruption PARAM lives inside `#BEGIN_COMP SC` ... `#END_COMP SC`.
  Placing it outside is silently ignored.
* In the second session of the eruption PARAM, set `UseCme=F` to disable the seeding once
  the rope has been launched. The shipped templates do this explicitly.

## Coupling cadence

* For SC↔IH coupling in CME runs, `#COUPLE1` `Dn=1` (every step) is the operating norm
  during the eruption window. Increasing it to skip steps will smear the shock arrival.
* SC,IH ↔ SP (MFLAMPA) couples on a `Dt=120 s` cadence in standard CCMC operations.

## #SAVEPLOT cadence

* For CCMC quick-look products (LASCO, EUVI, AIA, in-situ), `DtSavePlot=3600` produces a
  one-frame-per-hour movie that matches the standard answer. Cutting cadence below this
  inflates output volume by 10× without improving the science panel.

## #STARTTIME and magnetogram alignment

* `#STARTTIME` should match the magnetogram's observation time. `change_awsom_param.py`
  in SWMFSOLAR handles the rotation alignment; do not roll your own arithmetic on
  longitude shifts.

## Component build flags

* For AWSoM-R + SOFIE+MFLAMPA, the SC component requires `u=AwsomR` and `e=AwsomSA` (or
  `AwsomAnisoPi`). Missing the `u=AwsomR` flag silently builds plain AWSoM and most cases
  will run but produce subtly wrong wind speeds.
* GPU builds (`*.gpu` templates) require `nStage=1` for some scheme combinations; check the
  GPU AWSoM template before assuming 2-stage.

## AWSoM-R vs SOFIE (SaMhd) model distinction

* SOFIE enables stream-aligned MHD (SaMhd) via three co-occurring commands: `#CURLB0`,
  `#B0SOURCE`, and `#ALIGNBANDU` (`UseSaMhd=T`, `RSourceSaMhd=1.1`, `RMinSaMhd=5.5`).
  These are SaMhd-only; do not carry them into a plain AWSoM or AWSoM-R PARAM.
* The Config.pl flag that distinguishes SOFIE from plain AWSoM-R: `e=AwsomSA` (SaMhd).
  Plain AWSoM-R uses `e=Awsom` (Roe-scheme) or `e=AwsomR`; only `e=AwsomSA` activates
  the stream-aligned build.

## HARMONICSGRID: source-surface radius and grid

* **AWSoM / AWSoM-R**: `rSourceSurface=25`, `IsLogRadius=T`, `MaxOrder=180`, `nR=400`.
  The large source surface matches the SC outer boundary (~24 Rs) and is calibrated for
  the AWSoM threaded-field-line inner boundary at 1.0 Rs.
* **SOFIE (SaMhd)**: `rSourceSurface=2.5`, `IsLogRadius=F`, `MaxOrder=90`, `nR=100`.
  The PFSS source surface at 2.5 Rs is standard for SaMhd because the stream-aligned
  scheme reconstructs B0 from a 2.5 Rs PFSS field. Using `rSourceSurface=25` with
  `IsLogRadius=T` in a SOFIE PARAM is a copy-paste mistake that mis-aligns the
  threaded-field-line region.

## Inner boundary radius and boundary condition

* **AWSoM / AWSoM-R**: inner boundary at **1.0 Rs**, `OUTERBOUNDARY TypeBc1 = user`.
  The AMR `InnerShell` region is `RadiusInner=1.0, Radius=1.7`. `#GRIDBLOCKALL 200000`
  for standard runs.
* **SOFIE**: inner boundary at **1.1 Rs**, `OUTERBOUNDARY TypeBc1 = fieldlinethreads`.
  The AMR `InnerShell` region is `RadiusInner=1.1, Radius=1.7`. Do not set 1.0 for SOFIE
  — the SaMhd inner boundary routine assumes the 1.1 Rs base.

## GRIDBLOCKALL sizing

* SC: 120000–200000 blocks for standard AWSoM / AWSoM-R / SOFIE CME runs.
* IH: 160000 blocks for AWSoM / AWSoM-R CME runs (no MFLAMPA).
* IH: **2400000** blocks for SOFIE + MFLAMPA runs. MFLAMPA requires the full
  heliospheric domain at higher resolution to propagate SEPs to 1 AU; under-allocating
  causes an early "maximum block count exceeded" crash.

## SCHEME limiter progression (steady state)

* Session 1 (first SC steady-state): `minmod` (conservative; safe for initial ramp).
* Session 2 and later: upgrade to `mc3` + `LimiterBeta=1.2` for better resolution.
  The two-stage approach prevents numerical noise from the initial grid from blowing
  up the threaded-field-line region before AMR settles.
* IH when first activated (coupling activation session): start with `nOrder=1, Linde`
  (first-order flux). Upgrade to `nOrder=2, Linde, mc3` in the second AMR-enabled IH
  session.

## COORDSYSTEM in IH

* Time-accurate CME runs: `#COORDSYSTEM HGI`. The CME shock propagates outward in the
  heliocentric inertial frame; HGI is the natural IH frame for CME propagation.
* Steady-state background IH: `HGC` (rotating) is acceptable; `HGI` also works.
  The shipped SOFIE template uses HGI. Do not omit `#COORDSYSTEM` in IH — the default
  is model-version-dependent and a mismatch between SC and IH frames corrupts in-situ
  satellite output.

## GRIDGEOMETRY selection

* AWSoM (SC): `spherical_genr` with an external grid file (`SC/Param/grid_awsom.dat`).
  This is a non-uniform spherical mesh tuned for the AWSoM threaded boundary.
* SOFIE (SC): `spherical_lnr` (logarithmic-radial spherical geometry). Do not mix these;
  `spherical_genr` without the matching grid file will fail at startup.

## COARSEAXIS settings

* SOFIE background (`PARAM.in.sofie.CCMC`): `nCoarseLayer=3`.
* AWSoM-R CME (`PARAM.in.awsomr.CME`) and SOFIE eruption: `nCoarseLayer=2`.
  SOFIE uses a finer inner region and the background uses one more coarse layer to
  cover the 1.1–1.7 Rs AMR shell at sufficient resolution.

## PARTICLELINE for SOFIE MFLAMPA

* SOFIE eruption PARAMs include `#PARTICLELINE` in both SC and IH to enable seed
  particle tracing for MFLAMPA. The SC block must set `InitMode=import` and
  `UseBRAlignment=T`; the IH block sets `UseBRAlignment=F`.
  Omitting `#PARTICLELINE` in SC while keeping `#FIELDLINE` and `#COUPLE1` active
  causes SP to receive no particle seeds and produce zero flux output.

## Session termination: MaxIter vs TimeMax

* Steady-state sessions: `#STOP MaxIter=<value> TimeMax=-1.0`. Convergence is measured
  by iteration count; verify stability in the runlog before advancing.
* Time-accurate eruption sessions: `#STOP MaxIter=-1 TimeMax=<value>`. Physical elapsed
  simulation time is the hard constraint; MaxIter=-1 removes the iteration limit.
* Mixing (e.g. MaxIter=10000 + TimeMax=24h) terminates on whichever fires first —
  confirm this is intentional before finalizing the PARAM.

## SOFIE eruption session timing (nominal)

| Session | Simulation time | Role |
| ------- | --------------- | ---- |
| 1 | 1 h | seed FR; loose IH coupling (10 h cadence) |
| 2 | 4 h | turn off CME; tighten SC↔IH to 120 s |
| 3 | 13 h | CME exits SC; tight coupling 30 s |
| 4 | 4 d | IH-only propagation to 1 AU |

Extend session 3 to 17–20 h for fast CMEs (> 1500 km/s). Check IH `earth.sat`
output to confirm L1 arrival before stopping session 4.

## DIVB in IH

* `UseDivbDiffusion=T` in IH improves the polar/axial B-field quality and is the
  operational default for AWSoM / SOFIE runs. In SC it is typically `F`.
  `UseProjection` and `UseConstrainB` are `F` across all operational templates.

## LOOKUPTABLE files

* Required in every SC run with `#RADIATIVECOOLING T`: `radcool` (RadCoolCorona_8.0.dat)
  and `TR` (TR.dat). Both are in `SC/Param/`. Missing either causes a runtime error.
* LOS synthesis (LASCO, EUVI, AIA): `AiaXrt` (los_tbl.dat), `euv` (los_Eit_cor.dat),
  `EuviA` (los_EuviA.dat), `EuviB` (los_EuviB.dat) — required for synthetic LASCO C2
  and EUVI/AIA quick-look products.
