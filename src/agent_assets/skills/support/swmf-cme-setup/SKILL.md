---
name: swmf-cme-setup
type: support
description: "Support skill. Owns CME initiation policy: GL vs Titov-Démoulin vs SPHEROMAK vs cone; how spec FR fields map to PARAM #CME parameters; multi-session structure (background → eruption → relaxation); two-PARAM start+restart split. Loaded by swmf-replicate and swmf-configure."
---

# swmf-cme-setup (Support)

This is a **support skill**. `swmf-replicate` and `swmf-configure` consult it when a CME
initiation is involved. Detailed structure for the most common archetypes lives in
`support/swmf-params/rules/case_recipes/`.

## Purpose

Answer one thing: given a CME spec, what `TypeCme` family applies, what `#CME`
parameters need values, what is the multi-session structure of the eruption PARAM, and
which translations between spec labels and PARAM values must surface to the user.

## Scope

* `TypeCme` family selection: GL → SPHEROMAK (operational standard), TitovDemoulin/TD,
  Cone.
* Required `#CME` parameters per type and their spec sources.
* Two-PARAM split (background + restart) and the inter-file references.
* Multi-session toggling of `UseCme` (T in seed session, F in relaxation tail).
* Spec → PARAM derivation walk-through for `#AMRREGION CMEbox`, `#AMRREGION
  coneIH_CME`, and the relaxation `#STOP`.
* Interaction with `#HELIOUPDATEB0`, `#FIELDLINETHREAD`, `#ALIGNBANDU` (SaMhd) blocks.

Not in scope: PARAM validation (defer to `swmf-params`); magnetogram input handling
(defer to `swmf-magnetogram`); cluster submission.

## Tool Protocol

1. Read the recipe(s) under
   `support/swmf-params/rules/case_recipes/` that match the resolved archetype:
   * `awsom_cme_eruption.md` for AWSoM/AWSoM-R CME without SP.
   * `sofie_mflampa_cme.md` for SOFIE+MFLAMPA SEP runs.
2. Load the matching template manifest from
   `support/swmf-params/rules/templates/<archetype>.yaml`.
3. Load relevant derivations and defaults:
   * `derivations/geometric.yaml` — CMEbox, coneIH, MFLAMPA #ORIGIN.
   * `derivations/spheromak_shape.yaml` — TypeCme translation rule.
   * `defaults/cme_eruption.yaml` — SPHEROMAK shape, ops guards, couple cadence.
   * `defaults/session_ladders.yaml` — iteration counts.
4. Schema lookups via:
   ```
   get_evidence(query="#CME", mode="keyword", goal="param definition")
   ```
   ```
   get_evidence(query="GL flux rope", task_type="configuration", goal="CME initiation")
   ```
5. Direct reads only of files named by evidence
   (`SWMFSOLAR/Param/PARAM.in.awsomr.CME`,
   `SWMFSOLAR/Run_Max_RP_CME3/run01/PARAM.in`,
   `examples/CCMC_run_weihao/Weihao_Liu_011326_SH_1_PARAM.expand.{start,restart}`).

## Authority Order

1. Spec values (direct).
2. Derivations in `rules/derivations/` whose `applies_when` matches.
3. Recipe-specified slot values in `rules/case_recipes/`.
4. Template-carried values from the chosen template.
5. Defaults in `rules/defaults/`.
6. Schema (`PARAM.XML`) for command meaning.

Never let `get_evidence` heuristic results override a derivation rule that fires.

## Output Contract

* `case_archetype` — resolved archetype name (e.g. `sofie_mflampa_cme`).
* `type_cme_chosen` — value emitted into the `#CME` block, with provenance:
  * `spec` if the spec named TypeCme directly.
  * `derivation:gl_to_spheromak_typecme` if the agent translated `GL → SPHEROMAK` via
    the rule.
  * `gap` if neither covers the case (user prompt).
* `type_cme_translation_surfaced` — `True` whenever the value differs from the spec's
  literal `FR_type` field (e.g. `GL → SPHEROMAK`); user must confirm before launch.
* `cme_block` — full set of emitted `#CME` parameters with per-value provenance:
  `LongitudeCme`, `LatitudeCme`, `OrientationCme`, `Radius`, `BStrength`, `uCme`
  (typically `spec`), `Stretch`, `ApexHeight`, `iHelicity`, `DecayCme` (typically
  `default:spheromak_shape_defaults`).
* `session_structure` — list of session entries with role, `#TIMEACCURATE`, `UseCme`,
  `#STOP` source.
* `two_param_split` — `True` for AWSoM/AWSoM-R/SOFIE CME; the launch_command will be a
  pair (start submission, restart submission).
* `dependent_blocks` — list of co-required blocks the recipe activates (e.g.
  `#HELIOUPDATEB0`, `#AMRREGION coneIH_CME`).
* `gaps` — any value the ladder could not source. Each gap is a candidate YAML entry
  for `derivations/` or `defaults/`.

## Anti-patterns

* Do not silently translate spec `FR_type=GL` to PARAM `TypeCme=SPHEROMAK` without
  surfacing the translation. The `swmf-params/rules/derivations/spheromak_shape.yaml`
  rule emits `surface_as: inferred` for exactly this reason.
* Do not produce a single merged PARAM.in for a CME case. Use the start+restart pair
  from the recipe and orchestrate a two-stage submission.
* Do not invent SPHEROMAK shape parameters when neither template nor recipe provides
  them; the defaults are operational, not physical, and a recipe-anchored value is
  preferred when one exists.
* Do not use `change_param.py` to insert `#CME` into a steady-state template; that is a
  structural change (see `swmf-replicate` §6.5).
* Do not set `UseCme=T` in the relaxation session — only the seed session.
