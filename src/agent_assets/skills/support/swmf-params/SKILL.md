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
Standalone MFLAMPA SEP-physics commands (`#ADVECTION`, `#DIFFUSION`, `#MOMENTUMBC`,
`#FOCUSEDTRANSPORT`, `#TURBULENTSPECTRUM`, momentum/pitch-angle grid, end BCs) →
`swmf-mflampa`. This skill owns only how MFLAMPA is *wired into a SOFIE run* (the
`#FIELDLINE` registry and `SC→SP`/`IH→SP` coupling cadence), not the SP-side kinetics.

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
```bash
swmf get-evidence --query <param_command> --mode keyword --goal "param definition"
```

For structural primitives (rule evaluation, include + external-ref resolution,
component map, parser-level errors):
```bash
swmf inspect --type param --path <PARAM.in_path> --question <question> --check-rules
```

The param inspector returns structural primitives only. For session intent, control
cadence, `#SAVEPLOT` meaning, or any other semantic interpretation of the PARAM,
**read the PARAM.in file directly**. Do not call this command to "summarize" a PARAM.

For run-level PARAM intent from an existing case:
```bash
swmf inspect --type run_dir --path <run_dir_path>
```
Then read the run-local `PARAM.in` directly for intent.

For source behavior (schema vs runtime divergence):
```bash
swmf get-evidence --query <param_command> --mode hybrid --goal "runtime source behavior"
```

Authoritative validation (outside the swmf CLI):
```
Scripts/TestParam.pl -n=<nproc> <PARAM.in>   (from SWMF root)
```

## Authority Order

1. `TestParam.pl` output (run directly from SWMF root)
2. `PARAM.XML` schema (via `swmf get-evidence --mode keyword --goal "param schema"`)
3. Deterministic parsing (`swmf inspect --type param --check-rules`)
4. Heuristic source evidence (`swmf get-evidence --mode keyword`)

Never let heuristic search override `TestParam.pl` or `PARAM.XML`.

## Rules Directory

The `rules/` directory is the user-owned domain knowledge base, reshaped in
the Option-2 refactor to the narrow waist: only what PARAM.XML and the SWMF
manual cannot say.

| Lane | File(s) | Purpose |
| ---- | ------- | ------- |
| CONSTRAIN | `physical_constraints.yaml` | if/then validation rules for the swmf CLI |
| CROSSWALK | `crosswalks/*.yaml` | paper-phrase → command/parameter mappings |
| RECIPE | `case_recipes/*.md` | multi-session skeletons per archetype |
| CONVENTION | `conventions.yaml` + `conventions.md` | tie-breakers when multiple commands are valid |
| FLOOR | `required_floors/*.yaml` | equation-set / archetype required commands, attested to PARAM.XML or Fortran |
| CORRECTION | `xml_corrections.md`, `manual_corrections.md` | known-stale XML / manual entries |
| CATALOG | `archetypes.yaml` | archetype labels with one-line descriptions |
| TEMPLATES (pointers) | `templates/INDEX.md` + `discovery.md` | pointers to *sets* of shipped PARAMs across SWMF |
| STATISTICAL | `corpus_frequency/*_typical.yaml` | warn-tier value envelopes; **not** authoritative |
| DERIVE | `derivations/*.yaml` | spec → PARAM value formulas (e.g. GL→SPHEROMAK) |

### Authoring ladder (for `swmf-replicate`)

For every PARAM value emitted, walk the ladder in order. First match wins.
**Step 4 (XML) is mandatory** for every physics-substantive PARAM block —
the audit gate enforces this.

| Step | Lane | Provenance tag |
| ---- | ---- | -------------- |
| 1 | spec field, direct | `spec` |
| 2 | recipe slot | `recipe:<id>` |
| 3 | template survey — value seen across shipped PARAM set | `template_survey:<path>` |
| 4 | **PARAM.XML default / `<parameter>` schema** | `xml:<commandgroup>` |
| 5 | manual worked example (cross-checked against XML) | `manual:<file>` |
| 6 | crosswalk maps paper phrase → command | `crosswalk:<id>` |
| 7 | convention breaks a tie | `convention:<id>` |
| 8 | derivation computes the value | `derivation:<id>` |
| 9 | nothing supplies the value | `gap` (user prompt) |

Validation rules and `TestParam.pl` run on the result **after** authoring; they are
not part of the authoring ladder. The XML audit gate
(`swmf inspect --type param --check-xml-audit --run-dir <run directory>`) refuses launch
if any commandgroup containing an emitted command was never read this session.
The audit gate persists recorded command-group reads to
`<run_dir>/.swmf_ai/audit.json`, so the SAME `--run-dir <run directory>` must be passed
to BOTH every `swmf inspect --type xml --xml-scope 'commandgroup:...'` read AND this
`swmf inspect --type param --check-xml-audit` launch check; otherwise the gate cannot
correlate the reads with the launch check.

### What's NOT here anymore

- `defaults/*.yaml` — folded into the matching `case_recipes/<archetype>.md`.
- `defaults/mined/*_required.yaml` — deleted. Statistical "required" lists
  were the file class that hid `#CURLB0` from the Liu et al. 2026
  replication. Required commands now come from `required_floors/`
  (PARAM.XML-attested) or PARAM.XML directly.
- `templates/*.yaml` (forked PARAM-template manifests) — replaced by
  `templates/INDEX.md` pointing at sets of shipped PARAMs across SWMF.
- `numerical_practices.md` — folded into `conventions.md`.

The corpus boundary is load-bearing: any rule entry that cites a literal
value from `eval/papers/*/reference/` is rejected by the contamination
tripwire in `swmf-improve` Stage 5.

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
* `heuristic_evidence` — when `swmf get-evidence` was used, with confidence level
* `verified_claims` — facts derivable from structural parsing or schema
* `unverified_claims` — inferences or defaults that were applied
* `conflicts` — when schema and source behavior disagree
* `rule_violations` — list of fired `physical_constraints.yaml` rules with severity
* `gaps` — PARAM values that no ladder step could supply (require user input)
* `provenance_map` — for each emitted PARAM value, the ladder step that supplied it
