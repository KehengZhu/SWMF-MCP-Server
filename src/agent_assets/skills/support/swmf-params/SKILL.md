---
name: swmf-params
type: support
description: >-
  Support skill. Authoritative PARAM.in expert for SWMF solar/heliosphere runs.
  Answers questions about PARAM command meaning, PARAM.in structure, PARAM.XML schema,
  include resolution, component maps, session ladders, multi-component coupling
  cadences, CME block construction, SOFIE/AWSoM model distinction, and validation.
  Called by swmf-configure, swmf-replicate, swmf-cme-setup, swmf-debug, and swmf-run.
---

# swmf-params (Support)

This is a **support skill**. It is not chosen directly by the agent.
Entry skills that call it:
- `swmf-configure` — for PARAM meaning, construction, and validation.
- `swmf-replicate` — for authoring ladder, session structure, and pre-launch gate.
- `swmf-cme-setup` — for CME block parameters, multi-session structure, and GL→SPHEROMAK translation.
- `swmf-debug` — when the failure is PARAM-related.
- `swmf-run` — when run-dir inspection surfaces a PARAM question.

## Purpose

Answer questions about:
- what a PARAM command does and what schema it expects
- whether a PARAM.in is structurally valid and rule-consistent
- how to build a PARAM.in from a spec (authoring ladder)
- which values belong to which model variant (AWSoM vs AWSoM-R vs SOFIE)
- how multi-session PARAMs are structured for steady-state vs CME eruption cases

## Scope

* command definition and schema (from `PARAM.XML`)
* `PARAM.in` structural validation and `#INCLUDE` chain resolution
* `#COMPONENTMAP` layout and component-rank assignment
* external input files required by PARAM (harmonics, lookup tables, trajectory files)
* schema vs runtime source behavior divergence
* authoring ladder: spec → derivation → recipe → template → default → practice → gap
* model variant knowledge: AWSoM, AWSoM-R, SOFIE (SaMhd), SOFIE+MFLAMPA
* CME block construction: GL→SPHEROMAK translation, multi-session session boundaries
* session termination: MaxIter (steady state) vs TimeMax (time-accurate)

Not in scope: build steps, run execution, job submission, failure diagnosis.

## Model Variant Quick Reference

### AWSoM
- Config.pl: `e=Awsom` or `e=AwsomAnisoPi`
- Inner boundary: 1.0 Rs; `OUTERBOUNDARY TypeBc1 = user`
- HARMONICSGRID: `rSourceSurface=25`, `IsLogRadius=T`, `MaxOrder=180`, `nR=400`
- GRIDGEOMETRY: `spherical_genr` + `SC/Param/grid_awsom.dat`
- No CURLB0 / B0SOURCE / ALIGNBANDU

### AWSoM-R
- Config.pl: `u=AwsomR, e=Awsom` (or `e=AwsomR`)
- Inner boundary: 1.0 Rs; `OUTERBOUNDARY TypeBc1 = fieldlinethreads`
- HARMONICSGRID: same as AWSoM (`rSourceSurface=25`, `IsLogRadius=T`)
- Has `#FIELDLINETHREAD` and `#PLOTTHREADS`
- No CURLB0 / B0SOURCE / ALIGNBANDU

### SOFIE (SaMhd)
- Config.pl: `u=AwsomR, e=AwsomSA`
- Inner boundary: **1.1 Rs**; `OUTERBOUNDARY TypeBc1 = fieldlinethreads`
- HARMONICSGRID: `rSourceSurface=2.5`, `IsLogRadius=F`, `MaxOrder=90`, `nR=100`
- GRIDGEOMETRY: `spherical_lnr`
- Has `#FIELDLINETHREAD`, `#CURLB0`, `#B0SOURCE`, `#ALIGNBANDU` (all three required)

### SOFIE + MFLAMPA
- All SOFIE above, plus `SP/MFLAMPA` component
- Requires `#FIELDLINE` registry, `#COUPLE1 SC→SP` and `IH→SP` at 120 s cadence
- IH `#GRIDBLOCKALL` = 2400000 (much larger than non-MFLAMPA runs)
- `#PARTICLELINE` required in both SC and IH
- SP requires `#GRIDNODE`, `#ORIGIN`, `#MOMENTUMBC`, `#USEFIXEDMFPUPSTREAM`, `#DORUN`

## Key Command Groups

### Global control
`#COMPONENTMAP`, `#TIMEACCURATE`, `#STARTTIME`, `#SAVERESTART`, `#STOP`, `#RUN`, `#END`,
`#INCLUDE`, `#DESCRIPTION`, `#TEST`, `#CPUTIMEMAX`, `#COMPONENT`

### SC/IH coupling
`#COUPLE1`, `#COMPONENT` (enable/disable), `#FIELDLINE` (for SP)

### Magnetogram / B0
`#HARMONICSFILE`, `#HARMONICSGRID`, `#CURLB0`, `#B0SOURCE`, `#ALIGNBANDU`, `#HELIOUPDATEB0`,
`#ROTATEHGR`, `#ROTATEHGI`

### Grid and AMR
`#GRIDBLOCKALL`, `#GRIDGEOMETRY`, `#GRID`, `#LIMITRADIUS`, `#COORDSYSTEM`,
`#GRIDRESOLUTION`, `#AMRREGION`, `#AMRCRITERIARESOLUTION`, `#DOAMR`, `#COARSEAXIS`

### Physics
`#POYNTINGFLUX`, `#CORONALHEATING`, `#HEATPARTITIONING`, `#RADIATIVECOOLING`,
`#PLASMA`, `#MINIMUMTEMPERATURE`, `#MINIMUMPRESSURE`, `#MINIMUMRADIALSPEED`,
`#NONCONSERVATIVE`, `#DIVB`, `#RESCHANGE`, `#FIELDLINETHREAD`, `#PLOTTHREADS`,
`#USERSWITCH`, `#CHROMOBC`, `#TRANSITIONREGION`

### Numerics
`#TIMESTEPPING`, `#SCHEME`, `#LIMITER`, `#TIMESTEPLIMIT`, `#SUBCYCLING`

### Boundaries
`#OUTERBOUNDARY`, `#INNERBOUNDARY`, `#BUFFERGRID`, `#BODY`, `#RESTARTOUTFILE`

### CME-specific
`#CME` (TypeCme, UseCme, DoAddFluxRope, tDecayCme, LongitudeCme, LatitudeCme,
OrientationCme, BStrength, iHelicity, Radius, Stretch, ApexHeight, uCme)

### Output
`#SAVEPLOT`, `#SAVELOGFILE`, `#SAVEINITIAL`, `#SAVETECPLOT`, `#SATELLITE`,
`#LOOKUPTABLE`, `#PARTICLELINE`

### MFLAMPA/SP
`#GRIDNODE`, `#ORIGIN`, `#MOMENTUMBC`, `#USEFIXEDMFPUPSTREAM`, `#DORUN`,
`#TRACESHOCK`, `#DIFFUSION`, `#USEDATETIME`, `#LOWERENDBC`, `#UPPERENDBC`,
`#ADVECTION`, `#SAVEPLOT` (mh2d, mhtime)

## Tool Protocol

For command meaning:
```
get_evidence(
  query = <param_command>,
  mode = "keyword",
  goal = "param definition"
)
```

For structural primitives (rule evaluation, include + external-ref resolution,
component map, parser-level errors):
```
inspect_artifact(
  artifact_type = "param",
  path = <PARAM.in_path>,
  question = <question>,
  check_rules = True
)
```

The param inspector returns structural primitives only. For session intent, control
cadence, `#SAVEPLOT` meaning, or any other semantic interpretation of the PARAM,
**read the PARAM.in file directly**. Do not call this tool to "summarize" a PARAM.

For run-level PARAM intent from an existing case:
```
inspect_artifact(
  artifact_type = "run_dir",
  path = <run_dir_path>
)
```
Then read the run-local `PARAM.in` directly for intent.

For source behavior (schema vs runtime divergence):
```
get_evidence(
  query = <param_command>,
  mode = "hybrid",
  goal = "runtime source behavior"
)
```

Authoritative validation (outside MCP):
```
Scripts/TestParam.pl -n=<nproc> <PARAM.in>   (from SWMF root)
```

## Authority Order

1. `TestParam.pl` output (run directly from SWMF root)
2. `PARAM.XML` schema (via `get_evidence(mode="keyword", goal="param schema")`)
3. Deterministic parsing (`inspect_artifact(artifact_type="param", check_rules=True)`)
4. Heuristic source evidence (`get_evidence(mode="hybrid")`)

Never let heuristic search override `TestParam.pl` or `PARAM.XML`.

## Rules Directory

The `rules/` directory is the user-owned domain knowledge base.

| Lane | File(s) | Purpose |
| ---- | ------- | ------- |
| CONSTRAIN | `physical_constraints.yaml` | if/then validation rules for MCP |
| NARRATIVE | `numerical_practices.md` | best practices and failure patterns |
| STRUCTURE | `case_recipes/*.md` | multi-session skeletons per archetype |
| ANCHOR | `templates/*.yaml` | template-pair manifests per archetype |
| DERIVE | `derivations/*.yaml` | spec → PARAM value formulas |
| DEFAULT | `defaults/*.yaml` | operational defaults when spec is silent |
| MINED | `defaults/mined/*.yaml` | auto-generated by `scripts/mine_param_corpus.py` from the shipped corpus; never hand-edited |
| CATALOG | `archetypes.yaml` | archetype labels with one-line descriptions; LLM matches paper text against the `description` field |

### Authoring ladder (for `swmf-replicate`)

For every PARAM value emitted, walk the ladder in order. First match wins.

| Step | Lane | Provenance tag |
| ---- | ---- | -------------- |
| 1 | spec field, direct | `spec` |
| 2 | derivation match | `derivation:<id>` |
| 3 | recipe slot | `recipe:<id>` |
| 4 | template carries it | `template:<path>` |
| 5 | default applies | `default:<id>` |
| 6 | narrative practice resolves a tie | `practice:<entry>` |
| 7 | nothing supplies the value | `gap` (user prompt required) |

Validation rules and `TestParam.pl` run on the result **after** authoring; they are
not part of the authoring ladder.

### Available defaults files

- `defaults/ops_guards.yaml` — `#CPUTIMEMAX`, `#MINIMUMPRESSURE`, `#MINIMUMTEMPERATURE`, `#HELIOUPDATEB0`
- `defaults/cme_eruption.yaml` — SPHEROMAK shape, couple cadence, savePlot entries for CME runs
- `defaults/session_ladders.yaml` — iteration count ladders per archetype
- `defaults/build_flags.yaml` — `Config.pl` flags per archetype
- `defaults/sofie_cme.yaml` — SOFIE session timing, GRIDBLOCKALL, HARMONICSGRID, COUPLE1 cadences, FIELDLINE registry
- `defaults/awsom_steady.yaml` — AWSoM steady-state session ladder, HARMONICSGRID, SCHEME progression, DIVB, RESCHANGE

### Mined defaults (auto-generated)

`defaults/mined/` holds the output of `scripts/mine_param_corpus.py`. Files in
this directory are **regenerated atomically** by re-running the miner; do not
hand-edit. Per-paper curation continues to land in the un-namespaced
`defaults/*.yaml` files.

- `defaults/mined/<archetype>_required.yaml` — command-intersection across the
  shipped PARAMs that match `<archetype>`. Use as the diff target when
  authoring a new PARAM for that archetype.
- `defaults/mined/<archetype>_typical.yaml` — per-command, per-key value
  envelope (min/max/mode/values_seen) across the same group. Seeds range
  rules in `physical_constraints.yaml` with deterministic numbers.
- `defaults/mined/equation_set_required.yaml` — `Config.pl -o=…:e=<Name>` →
  required `#COMMAND` set, derived from the `NameVar_V` declarations in
  `srcEquation/ModEquation<Name>.f90`. The var → command mapping is
  hand-curated inside the miner (`_VAR_TO_COMMANDS`).
- `defaults/mined/mining_report.md` — coverage report: PARAMs grouped per
  archetype, unmatched files, skipped files. Human-readable; not consumed by
  any tool.

The corpus boundary is load-bearing: the miner only ingests `SWMF/Param/`,
`SWMFSOLAR/Param/`, `SWMFSOLAR/ParamListScripts/`, and equation modules.
Anything under `SWMFSOLAR/Run_*/` is rejected with a hard error
(`scripts/mine_param_corpus.py::_reject_if_run_dir`).

### Available derivation files

- `derivations/geometric.yaml` — CMEbox bounds, coneIH rotation, MFLAMPA ORIGIN/GRIDNODE, Poynting flux, coronal heating
- `derivations/spheromak_shape.yaml` — GL→SPHEROMAK TypeCme translation

### Available case recipes

- `case_recipes/awsom_cme_eruption.md` — AWSoM/AWSoM-R CME eruption (start + restart)
- `case_recipes/sofie_mflampa_cme.md` — SOFIE + MFLAMPA CME eruption (start + restart)
- `case_recipes/awsom_steady_sc.md` — AWSoM/AWSoM-R/SOFIE steady-state SC+IH background

## Output Contract

* `param_family`: one of `command_definition`, `file_validation`, `include_resolution`,
  `component_layout`, `schema_vs_source_behavior`, `example_lookup`,
  `authoring_guidance`, `model_variant_distinction`
* `authoritative_evidence` — citations to PARAM.XML, TestParam.pl output, template paths
* `heuristic_evidence` — when `get_evidence` was used, with confidence level
* `verified_claims` — facts derivable from structural parsing or schema
* `unverified_claims` — inferences or defaults that were applied
* `conflicts` — when schema and source behavior disagree
* `rule_violations` — list of fired `physical_constraints.yaml` rules with severity
* `gaps` — PARAM values that no ladder step could supply (require user input)
* `provenance_map` — for each emitted PARAM value, the ladder step that supplied it
