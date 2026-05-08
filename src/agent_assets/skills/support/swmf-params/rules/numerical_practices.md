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
