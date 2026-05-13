# awsom_cme_eruption — case recipe

Multi-session skeleton for an AWSoM (or AWSoM-R) CME run with SC + IH coupling, no SP.
Derived from the shipped templates `SWMFSOLAR/Param/PARAM.in.awsomr.CME` and
`SWMFSOLAR/Param/PARAM.in.awsom.CME`.

The recipe is **structure**, not values. Numbers are template- or spec-supplied; this
document specifies which command goes in which session, where session boundaries fall,
and what each session toggles.

## Two-PARAM split

This archetype produces **two** PARAM.in files:

| File | Role | `#TIMEACCURATE` | `#CME` | Restart |
| ---- | ---- | --------------- | ------ | ------- |
| `PARAM.expand.start`   | steady-state background | `F` | absent | writes `SC/restartOUT/`, `IH/restartOUT/` |
| `PARAM.expand.restart` | time-accurate eruption  | `T` | present in SC, session 1 | reads `SC/restartIN/restart.H`, `IH/restartIN/restart.H` |

A merged single-PARAM is rejected by this recipe — see `numerical_practices.md`.

## `PARAM.expand.start` session ladder (background)

Four sessions, ladder iteration counts come from `defaults/session_ladders.yaml`
(scale by grid resolution; do not invent).

| Session | Toggles | Role |
| ------- | ------- | ---- |
| 1 | SC only; `#DOAMR` enabled; initial `#GRIDLEVEL` ramp | initial AMR in SC |
| 2 | SC only; `#DOAMR` disabled | freeze SC AMR before coupling |
| 3 | `#COMPONENT IH T`; `#COUPLE1 SC->IH` enabled | enable IH and SC↔IH coupling |
| 4 | IH `#DOAMR` enabled then disabled in a final tail | enable IH AMR, then freeze |

Final session ends with `#SAVERESTART` cadence already declared at session 1; the run
terminates when `#STOP MaxIter` is reached.

## `PARAM.expand.restart` session ladder (eruption)

Three to four sessions:

| Session | `#TIMEACCURATE` | `#CME` UseCme | `#STOP` | Role |
| ------- | --------------- | ------------- | ------- | ---- |
| 1 | T | T | `tSimulationMax = cme_traveling_time` | seed and propagate the FR through SC/IH |
| 2 | T | F | `tSimulationMax = (smoothing_factor) * cme_traveling_time` | relaxation tail; keep eruption-quality output |
| 3 (optional) | T | F | tail extension | extra IH-only follow-up if spec asks |

Both PARAMs include the same `#STARTTIME`, `#HARMONICSFILE`, `#HARMONICSGRID`,
`#POYNTINGFLUX`, `#CORONALHEATING`, `#PLASMA` blocks. Differences are concentrated in:

* `#TIMEACCURATE` (F → T)
* presence of `#INCLUDE RESTART.in` and `#INCLUDE SC/restartIN/restart.H`,
  `#INCLUDE IH/restartIN/restart.H`
* presence of `#CME`, `#FIELDLINE`/`#PARTICLELINE` (when applicable)
* `#SAVEPLOT` blocks for the CCMC quick-look set

## Where each command lives

| Command | start | restart | Component | Session |
| ------- | ----- | ------- | --------- | ------- |
| `#DESCRIPTION` | yes | yes | global | 1 |
| `#STARTTIME` | yes | yes | global | 1 |
| `#TIMEACCURATE` | F (1) | T (1) | global | 1 |
| `#COMPONENTMAP` | yes | yes | global | 1 |
| `#SAVERESTART` | yes | yes | global | 1 |
| `#INCLUDE RESTART.in` | no | yes | global | 1 |
| `#HARMONICSFILE` | yes | yes | SC | 1 |
| `#HARMONICSGRID` | yes | yes | SC | 1 |
| `#POYNTINGFLUX` | yes | yes | SC | 1 |
| `#CORONALHEATING` | yes | yes | SC | 1 |
| `#PLASMA` | yes | yes | SC and IH | 1 |
| `#FIELDLINETHREAD` | yes | yes | SC | 1 |
| `#GRIDBLOCKALL` | yes | yes | SC and IH | 1 |
| `#AMRREGION CMEbox` | yes | yes | SC | 1 |
| `#DOAMR` | yes (toggled) | yes | SC, IH | 1..end |
| `#TIMESTEPPING` | yes | yes | SC, IH | 1 |
| `#SCHEME` | yes | yes | SC, IH | 1 |
| `#COUPLE1` SC→IH | yes (s≥3) | yes | global | 3+ |
| `#CME` | no | yes (UseCme=T) | SC | 1 |
| `#CME UseCme=F` | no | yes | SC | 2 |
| `#SAVEPLOT` quick-look | minimal | full | SC, IH | 1 |
| `#STOP` | per session | per session | global | each |
| `#RUN` | session boundaries | session boundaries | global | between |
| `#END` | last session | last session | global | last |

## Decision points the recipe leaves to spec/template

* Magnetogram source (ADAPT vs GONG vs HMI) — spec.
* Specific FR parameters (`LongitudeCme`, `LatitudeCme`, `OrientationCme`, `Radius`,
  `BStrength`, `uCme`) — spec.
* Spheromak shape (`Stretch`, `ApexHeight`, `iHelicity`, `DecayCme`) — `defaults/cme_eruption.yaml`.
* Iteration counts — `defaults/session_ladders.yaml` keyed by grid resolution.
* `#AMRREGION CMEbox` bounds — `derivations/geometric.yaml::cmebox_from_fr_and_cone`.
* `#AMRREGION coneIH_CME` rotation — `derivations/geometric.yaml::coneih_rotation_from_fr`.
* Lookup tables (`RadCoolCorona`, `TR`, `los_tbl`, etc.) — copied from template verbatim.

## Anchored on shipped templates

`SWMFSOLAR/Param/PARAM.in.awsomr.CME` is the canonical AWSoM-R CME exemplar for this
archetype; `SWMFSOLAR/Param/PARAM.in.awsom.CME` is the AWSoM-AnisoPi variant. The
authoring ladder diffs the emerging PARAM against both via the
`secondary_precedents` slot in `templates/awsom_cme.yaml`.
