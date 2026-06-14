# conventions.md — human-readable rationale for the tie-breakers in `conventions.yaml`

Folded from the legacy `numerical_practices.md`, scoped down to the entries
that survive after Part B's rules-layer narrowing. The rule of thumb: if the
practice is just "PARAM.XML says X," it belongs in PARAM.XML and is not
duplicated here. If the practice is "when X and Y are both valid, archetype Z
prefers X because of stability / convention / coupling," that belongs here.

## AWSoM SC-only steady state

* **Time-stepping default**: `#TIMESTEPPING nStage=2 cfl=0.8` is the operating
  default. When raising `#GRIDLEVEL` for the first few iterations, halve `cfl`
  until the initial transient damps; otherwise inner-boundary Alfvén-wave
  reflection can blow up the threaded-field-line region.

* **AMR criteria form**: prefer the `dphi`-based `#AMRCRITERIARESOLUTION` over
  `#AMRCRITERIALEVEL`. The dphi form maps cleanly to paper-supplied angular
  resolutions.

* **AMR session split**: when the paper describes refinement at distinct
  iteration counts (e.g. 20k / 40k / 60k), use a three-session split with
  progressive `#AMRCRITERIARESOLUTION` rather than a single block. The single
  block is convenient shorthand but evaluates every criterion at every AMR
  pass.

* **Non-conservative pressure**: SC-only AWSoM steady state typically uses
  `#NONCONSERVATIVE UseNonConservative=T` to avoid shock-induced heating in
  the low corona. SC+IH runs prefer `F`. Paper overrides.

* **Axis boundary**: under `spherical_genr`, axes (`Bc3`–`Bc6`) take `float`
  in the FDIPS reference workflow. Some harmonics templates use `periodic`;
  both run, but `float` matches the conservative reference for steady state.

* **5th-order tail**: the Chen 2016 path uses `#SCHEME nOrder=5 + Linde + mc3
  + #SCHEME5 MP5` in a final session, with `#LOWORDERREGION` shielding the
  outer shell. mc3 is Koren (`ModFaceValue.f90` confirms).

## AWSoM-R + SOFIE coupling

* **Required co-occurrence**: AWSoM-R requires `#FIELDLINETHREAD` and
  `#PLOTTHREADS` together. Removing one while keeping the other is a silent
  failure mode.

* **Build flags**: SOFIE+MFLAMPA SC requires `u=AwsomR` AND `e=AwsomSA` (or
  `AwsomAnisoPi`). Missing `u=AwsomR` silently builds plain AWSoM; most cases
  will run but produce subtly wrong wind speeds.

## CME eruption sessions

* **Two-file split**: the standard AWSoM/AWSoM-R CME PARAM is split across
  `PARAM.expand.start` (background) and `PARAM.expand.restart` (eruption).
  The eruption PARAM `#INCLUDE`s the SC and IH `restartIN/restart.H`. A
  single merged PARAM has no checkpoint and is operationally fragile.

* **`#CME` block placement**: must live inside `#BEGIN_COMP SC` … `#END_COMP
  SC`. Placing it outside is silently ignored.

* **Second session**: set `UseCme=F` to disable the seeding once the rope has
  been launched.

## SC↔IH and IH↔SP coupling cadence

* For SC↔IH coupling in CME runs, `#COUPLE1 Dn=1` (every step) is the
  operating norm during the eruption window. Increasing it smears the shock
  arrival.

* SC,IH ↔ SP (MFLAMPA) couples on `Dt=120 s` for standard CCMC operations.

## Output cadence

* For CCMC quick-look products (LASCO, EUVI, AIA, in-situ), `DtSavePlot=3600`
  produces one-frame-per-hour matching the standard answer. Below this
  cadence inflates output volume by 10× without improving the science panel.

## Magnetogram alignment

* `#STARTTIME` should match the magnetogram's observation time.
  `change_awsom_param.py` in SWMFSOLAR handles rotation alignment; do not
  roll your own arithmetic on longitude shifts.

---

This file is consumed as prose by the agent during the **convention** lane of
the swmf-replicate ladder. Machine-readable predicates that the rule-checker
can evaluate live in `conventions.yaml`. Keep them in sync.
