# Replication Evaluation: Liu et al. 2026 (2024 April 8 TSE)

This is an evaluation of one end-to-end run of the `swmf-replicate` skill against
a real paper-replication task. It compares what the agent produced against what
the paper's author actually used, and proposes concrete improvements to the
skill/MCP/rules stack.

- Workdir: `/Users/zkeheng/SWMFSoftware/Xianyu26Paper`
- Chat transcript: `replicate_chat_history.md`
- Agent output: `PARAM.in.awsom.eclipse2024` (481 lines, 4 sessions)
- Author reference: `PARAM.in.reference` (378 lines, 3 sessions; HipFT variant —
  only the magnetogram filename and `#POYNTINGFLUX` differ across the four
  models). **This file was placed in the workdir after the replication run as a
  gold answer; it was not visible to the agent during the run.** All references
  to it below are post-hoc oracle, not something the skill could have read.
- Run-dir skeleton: `Runs_eclipse2024_A/run01/`

## 1. What worked

- **Spec normalization.** `paper_spec.json` was produced cleanly with explicit
  `confidence_per_field` and a four-model table. The user confirmation gate
  fired correctly (single round trip on allocation / scope / strategy / scale).
- **Archetype + template discovery.** `awsom_steady_corona` archetype was
  named, `SWMFSOLAR/Param/PARAM.in.awsom` was identified as the closest
  precedent, and the choice was tagged `provenance=inferred` (no manifest
  exists). This matches §4.1.4 step 2 and §5.4.4.
- **Construction-mode classification.** The job was correctly flagged as
  "construction" rather than "sweep" (§6.5.2) since session structure and
  AMR cadence needed reshaping.
- **Magnetogram path.** `Scripts/download_ADAPT.py` was identified as the right
  fetcher; agent never invented URLs.
- **Schema gate ran end-to-end.** `Scripts/TestParam.pl -n=3584` was invoked
  and finished `EXIT=0`. The gate from §6.5.5 step 2 worked.
- **Honest local-vs-Frontera boundary.** When the user said "treat local as
  Frontera," the agent attempted compile, hit the no-Fortran-on-Mac wall, and
  pivoted to a placeholder rundir with 0-byte `.exe`s rather than faking
  artifacts. The skill output transparently flagged what was real and what was
  a placeholder.

## 2. What broke — physics-completeness failures in the generated PARAM

`Scripts/TestParam.pl` passed, but the generated PARAM is **physically
incomplete** for AWSoM with `AwsomAnisoPi`. Diff against `PARAM.in.reference`:

| Command (in reference, missing from generated) | What it does | Severity |
| --- | --- | --- |
| `#CURLB0 T 2.5 T` | Maintains curl-free B0 outside source surface; critical for FDIPS-initialized runs | block |
| `#ANISOTROPICPRESSURE F -1.0 1e5` | Required by `AwsomAnisoPi` equation set; sets relaxation time for pressure anisotropy | block |
| `#HEATCONDUCTION T spitzer` | Spitzer-Härm thermal conduction; AWSoM coronal physics depends on it | block |
| `#HEATFLUXREGION T 5.0 -8.0` | Regional control of collisional vs collisionless heat flux | block |
| `#HEATFLUXCOLLISIONLESS T 1.05` | Collisionless heat flux beyond rCollisionless; AWSoM solar wind acceleration | block |
| `#SEMIIMPLICIT T parcond` | Required to integrate heat conduction implicitly at AWSoM CFL | block |
| `#SEMIKRYLOV GMRES 1.0e-5 10` | Companion to `#SEMIIMPLICIT` — Krylov solver settings | block |
| `#COORDSYSTEM HGR` | Sets coord system explicitly (default may differ across builds) | warn |

Wrong-value findings (present in both, but generated has different numbers):

| Command | Generated | Reference | Impact |
| --- | --- | --- | --- |
| `#CHROMOBC` | `2e17 / 5e4` | `5e17 / 2e4` | Chromospheric density 2.5× lower, temperature 2.5× higher — changes wave injection footpoint thermodynamics |
| `#CORONALHEATING` 3rd–4th args | `rMinWaveReflection=0.0`, no `UseSurfaceWaveRefl` | `rMinWaveReflection=1.05`, `UseSurfaceWaveRefl=T` | Surface wave reflection is the dominant Alfvén-wave reflection mechanism in AWSoM corona; turning it off changes turbulence injection. |
| `#MINIMUMTEMPERATURE` | `5e4 / 5e4` | `2e4 / 2e4` | Floors solar wind temperature 2.5× higher |
| `#SCHEME` session 1 | `Linde / minmod` | `Sokolov / minmod` | Different Riemann solver; Sokolov is the SWMFSOLAR-AWSoM-steady canonical choice |

Both PARAMs pass `TestParam.pl` because schema (PARAM.XML) only enforces
syntax, command order, and value ranges — not physics-completeness. This is
explicitly called out in §9.2 "Treating `Scripts/TestParam.pl` pass as physical
correctness" anti-pattern, but in practice the skill had no way to detect any
of the eight missing commands above.

### Root cause analysis

1. **The agent anchored on the wrong precedent.** `Param/PARAM.in.awsom` is a
   minimal teaching template, not the operationally-used AWSoM-steady PARAM.
   The community-used precedent is closer to `PARAM.in.reference` — but no
   template manifest pointed at it. `templates/awsom_cme.yaml` exists in the
   Phase 1 plan but `templates/awsom_steady_corona.yaml` does not.
2. **Physics-requirement rules are missing.** Nothing in
   `physical_constraints.yaml` says "if `e=AwsomAnisoPi` is in the build,
   `#ANISOTROPICPRESSURE` must be present", or "if `#POYNTINGFLUX` is set,
   `#HEATCONDUCTION`+`#SEMIIMPLICIT`+`#HEATFLUXREGION`+`#HEATFLUXCOLLISIONLESS`
   must be present" — both are mechanical to encode and would have hard-blocked
   the launch gate.
3. **No equation-set → required-commands lookup.** Stock `Config.pl -o=SC:e=…`
   options imply a Fortran equation module which in turn requires specific PARAM
   commands. This mapping is documented nowhere the agent looked. It's
   structurally extractable from the source (each equation module declares its
   required ModH dependencies) and belongs in `defaults/equation_set_required.yaml`
   or in the recipe.
4. **Spec was silent on these fields.** The paper assumed AWSoM physics defaults
   without restating them. The agent honored the spec exactly and inherited
   nothing from the (unhelpful) anchor template. The authoring ladder dead-
   ended at `default` lane with no entries for "AWSoM coronal physics block."

## 3. What broke — build & run plan

- **Over-built.** Agent ran `Config.pl -v=Empty,SC/BATSRUS,IH/BATSRUS` and
  carried `#COMPONENTMAP IH 0 -1 1` + `#COMPONENT IH F`. Paper is SC-only;
  reference uses `-v=Empty,SC/BATSRUS` only. The agent's rationale ("build
  parity with SWMFSOLAR Makefile") is a SWMFSOLAR-convenience artifact, not a
  physical requirement, and it doubles compile time + binary size.
- **AMR strategy mismatch.** Paper described AMR targets in *degrees*; agent
  used `#AMRCRITERIARESOLUTION` (degree-based criterion). Reference used
  `#AMRCRITERIALEVEL` + `#GRIDLEVEL 2 initial` — the SWMFSOLAR-canonical form.
  Both can reach the same refinement, but the reference form is testable
  against existing AWSoM literature; the agent's form is novel for this case.
- **Session count: 4 vs 3.** Agent split scheme transitions across 4 sessions
  (session 3 = "AMR off + 2nd-order to iter 80k", session 4 = MP5). Reference
  used 3 sessions; AMR is disabled mid-session-2 by `#AMR -1` in the next
  session header. Both are valid; agent's is slightly easier to read but
  diverges from precedent without a documented reason.
- **`change_param.py` for sweep across models.** Plan correctly identified that
  Models A/H/L/N differ only in magnetogram + `#POYNTINGFLUX`, but the
  generated PARAM hard-codes Model A's `4.76e5` rather than templating it. A
  proper sweep-mode wrapper would emit one parameterized PARAM and have
  `make rundir_local POYNTINGFLUX=…` substitute. Agent did flag this as a
  follow-up, so it's a soft miss.
- **Jobscript scaling rationale was thin.** "Paper-class AMR runs warrant 64×56
  ranks × 24h" was inferred by analogy to an out-of-corpus personal run-dir
  (`SWMFSOLAR/Run_*/run01/job.frontera`). Those run-dirs are study artifacts,
  not part of SWMFSOLAR proper, and must not be used as exemplars. There is no
  evidence in the paper that 90k-iter AWSoM-SC steady needs 3584 ranks; this
  may be 2–4× oversize. The `inspect_artifact(jobscript)` tool extracted
  scheduler/nodes/tasks correctly, but the skill has no "right-size for
  workload" heuristic and pulled numbers from a non-canonical source.
- **`TestParam.pl` validation friction.** Two failed attempts before the agent
  set up a synthetic temp run-dir under `/tmp/testparam_eclipse2024/` with
  symlinked `SC/Param`. This pattern is reusable and should be canonized — see
  §4.5 below.

## 4. Recommended improvements

The goal is to close each rung of the §5.4.7 authoring ladder for the
`awsom_steady_corona` archetype, and to give the launch gate enough physics
awareness to catch the eight missing commands above.

### 4.1 New template manifest: `awsom_steady_corona.yaml`

`src/agent_assets/skills/support/swmf-params/rules/templates/awsom_steady_corona.yaml`:

```yaml
id: awsom_steady_corona_pair
case_archetype: awsom_steady_corona
start_template: SWMFSOLAR/Param/PARAM.in.awsom        # closest shipped precedent
restart_template: null                                 # cold-start; no restart pair
required_flag_overrides:
  - target: config_pl_sc
    from: "u=Awsom,e=AwsomAnisoPi,nG=3,g=6,8,8"
    to:   "u=Awsom,e=AwsomAnisoPi,nG=3,g=6,8,8"
    why: "Paper-canonical AwsomAnisoPi block size."
  - target: components
    from: "Empty,SC/BATSRUS,IH/BATSRUS"
    to:   "Empty,SC/BATSRUS"
    why: "SC-only domain (1.01-24 Rs); no IH propagation. Saves compile and binary."
recipe: case_recipes/awsom_steady_corona.md
secondary_precedents:
  - SWMFSOLAR/Param/PARAM.in.awsom.steady
  - SWMFSOLAR/Param/PARAM.in.sofie.CCMC
  - SWMFSOLAR/Param/PARAM.in.awsomr.CME
  # Authoritative sources only: shipped SWMF/SWMFSOLAR templates under
  # Param/ and ParamListScripts/. Personal study run-dirs under
  # SWMFSOLAR/Run_*/ are NOT part of SWMFSOLAR and must not be used.
```

The skill's evidence step 2 must read every listed secondary precedent before
construction, not just the start template. The secondary list is the place to
encode "look at the shipped PARAM that actually carries the full AWSoM physics
block" — `Param/PARAM.in.awsom` is a thin teaching template; the production
templates shipped under `SWMFSOLAR/Param/` (and the SOFIE CCMC variants) carry
the eight commands the teaching template omits.

### 4.2 New case recipe: `case_recipes/awsom_steady_corona.md`

Document the **required physics block** for AWSoM-AnisoPi steady runs as a
copy-paste skeleton. Specifically the eight commands missing from the agent's
output (§2), with the canonical values, plus a short explanation of why each
is required (e.g. "`#SEMIIMPLICIT parcond` because explicit Spitzer heat
conduction violates AWSoM CFL by orders of magnitude near the transition
region"). Also document:

- Session structure: 3 sessions (initial 2nd-order minmod ramp → 2nd-order mc3
  bulk → 5th-order MP5 tail), with AMR disabled mid-bulk via `#AMR -1` in the
  third session header. Document why this is preferred over an extra session.
- AMR convention: prefer `#AMRCRITERIALEVEL`+`#GRIDLEVEL` over
  `#AMRCRITERIARESOLUTION` for AWSoM-steady, citing every shipped AWSoM
  template that uses the level form.
- MP5 low-order shell radius: reference uses `5.5 → 24 Rs`, not `1.7 → 24 Rs`.
  Document both and the rationale (5.5 keeps mid-corona on MP5; 1.7 keeps only
  the chromosphere/TR on low-order).

### 4.3 New physical-constraint rules

Append to `physical_constraints.yaml`. These would have hard-blocked the
generated PARAM at the launch gate:

```yaml
- id: anisotropic_pressure_required_for_anisopi
  applies_when: { config_flag_present: "e=AwsomAnisoPi" }
  require: { command_present: "#ANISOTROPICPRESSURE" }
  severity: block
  reason: "AwsomAnisoPi equation set evolves anisotropic pressure; the corresponding control command must appear."

- id: awsom_requires_heat_conduction_stack
  applies_when: { command_present: "#POYNTINGFLUX" }
  require:
    all_of:
      - command_present: "#HEATCONDUCTION"
      - command_present: "#HEATFLUXREGION"
      - command_present: "#HEATFLUXCOLLISIONLESS"
      - command_present: "#SEMIIMPLICIT"
      - command_present: "#SEMIKRYLOV"
  severity: block
  reason: "AWSoM steady-state corona requires Spitzer + collisionless heat flux integrated semi-implicitly."

- id: fdips_implies_curlb0
  applies_when:
    all_of:
      - command_present: "#LOOKUPTABLE"
      - lookup_table_name: "B0"
      - file_pattern: "fdips_*.out"
  require: { command_present: "#CURLB0" }
  severity: warn
  reason: "FDIPS B0 is curl-free only inside rCurrentFreeB0; #CURLB0 must declare that radius."

- id: surface_wave_reflection_set_explicitly
  applies_when: { command_present: "#CORONALHEATING" }
  require: { command_value_set: { command: "#CORONALHEATING", param: "UseSurfaceWaveRefl" } }
  severity: warn
  reason: "AWSoM surface-wave reflection toggle is physics-relevant and should not be silently defaulted."
```

The first three predicates (`config_flag_present`, `lookup_table_name`,
`file_pattern`, `command_value_set`) are new — extending the predicate
vocabulary is a code change (§5.4.8), which is the only reason to touch MCP
here. The remaining work is YAML.

### 4.4 New derivations and defaults

`derivations/awsom_steady.yaml`:

```yaml
- id: chromobc_from_archetype
  applies_when:
    case_archetype: awsom_steady_corona
    spec_absent: [chromo_density_si, chromo_temperature_si]
  produces:
    target: "SC.#CHROMOBC"
    fields:
      NchromoSi: 5.0e17
      TchromoSi: 2.0e4
  evidence: "PARAM.in.reference (author-confirmed paper PARAM); also SWMFSOLAR AWSoM canonical."
```

`defaults/awsom_steady.yaml`:

```yaml
- id: awsom_physics_block_defaults
  applies_when: { case_archetype: awsom_steady_corona }
  defaults:
    "#ANISOTROPICPRESSURE":  { UseConstantTau: F, TauInstability: -1.0, TauGlobalSi: 1.0e5 }
    "#HEATCONDUCTION":       { UseHeatConduction: T, TypeHeatConduction: spitzer }
    "#HEATFLUXREGION":       { UseHeatFluxRegion: T, rCollisional: 5.0, rCollisionless: -8.0 }
    "#HEATFLUXCOLLISIONLESS":{ UseHeatFluxCollisionless: T, CollisionlessAlpha: 1.05 }
    "#SEMIIMPLICIT":         { UseSemiImplicit: T, TypeSemiImplicit: parcond }
    "#SEMIKRYLOV":           { TypeKrylov: GMRES, ErrorMaxKrylov: 1.0e-5, MaxMatvecKrylov: 10 }
    "#CURLB0":               { UseCurlB0: T, rCurrentFreeB0: 2.5, UseB0MomentumFlux: T }
    "#CORONALHEATING.rMinWaveReflection": 1.05
    "#CORONALHEATING.UseSurfaceWaveRefl": T
  evidence: "PARAM.in.reference + SWMFSOLAR/Param/PARAM.in.awsom canonical AWSoM block."
```

With these in place, the §5.4.7 ladder closes for every value the spec
doesn't supply, and the launch gate has both schema and physics teeth.

### 4.5 MCP improvement: `inspect_artifact(artifact_type="param")` resolves Param/

The Mac-local TestParam.pl friction (two failed attempts, one synthetic
`/tmp/testparam_eclipse2024/` setup with `ln -snf SC/Param`) suggests a small
MCP affordance: `inspect_artifact(artifact_type="param", path=…, run_dir_root=…)`
where `run_dir_root` synthesizes the symlinks needed for in-place schema
validation (so `Scripts/TestParam.pl` can resolve `SC/Param/grid_awsom.dat`).
This is structural / deterministic / used by every replication run; it fits
the MCP gate (§5.1 of the protocol). Alternatively, document the symlink
recipe in `case_recipes/_testparam_synthetic_rundir.md` — but the friction is
real enough that an MCP affordance is justified.

### 4.6 Skill update: read every shipped AWSoM PARAM, not just one anchor

The agent anchored on `Param/PARAM.in.awsom` (a thin teaching template) and
never consulted the production AWSoM PARAMs shipped elsewhere under
`SWMFSOLAR/Param/` (e.g. `PARAM.in.awsom.steady`, the SOFIE variants) — all of
which carry the eight-command physics block the teaching template omits.
Authoritative corpus sources are the shipped templates under `SWMF/Param/`,
`SWMFSOLAR/Param/`, and `SWMFSOLAR/ParamListScripts/` only; personal study
run-dirs under `SWMFSOLAR/Run_*/` are out of corpus. Add to `swmf-replicate`
evidence step 2:

> For each archetype, the template manifest's `secondary_precedents` list is
> mandatory reading before construction. Read every secondary precedent and
> diff it against the start template; commands present in secondaries but
> absent in the start template are physics-block candidates and must be
> resolved (either inherited or explicitly rejected with a documented reason).
> Tag findings with `provenance=secondary_precedent:<path>`.

This is the structural fix: the start template alone is never enough, and the
skill must compare against shipped production runs. (When a workdir happens to
contain author-confirmed PARAMs — e.g. a re-replication of a published case —
those should also be promoted as secondary precedents, but that is a bonus
case; the primary fix is to make the SWMFSOLAR-shipped production PARAMs
mandatory reading.)

### 4.7 Skill update: minimum-build principle

Add to `swmf-build` and to the build-evidence section of `swmf-replicate`:

> The `Config.pl -v=…` component list should match the PARAM's active
> components. If `#COMPONENT IH F` appears in the PARAM, drop IH from the
> build line. "Build parity with SWMFSOLAR Makefile" is not a valid reason to
> over-include components; the Makefile's `MODEL=AWSoM` target is a convenience
> default, not a constraint.

### 4.8 Skill update: jobscript right-sizing requires evidence

Currently the skill borrows node/wall-time numbers by analogy. Add to
`swmf-jobscript` and to §6 step 5:

> Job-scale parameters (`-N`, `--tasks-per-node`, `-t`) must be sourced from
> one of: (a) a precedent run for the **same archetype + grid resolution**
> (cite path), (b) a back-of-envelope cell-count × cost-per-cell × iter
> calculation surfaced in the skill output, or (c) explicit user input. Do not
> default to the largest available reference jobscript.

For the eclipse2024 case, an AWSoM-SC steady at AMR-target 0.35° in
[1.01, 1.2] Rs costs roughly 40M cells × 90k iter; reference Frontera AWSoM
production runs at this scale use 16–32 nodes × 56 tpn, not 64. The agent
chose 64 by analogy to an out-of-corpus personal study run-dir (heavier CME
run with IH); that comparison should not have been available to the agent in
the first place.

### 4.9 Skill update: explicit "local-as-staging" mode

The chat showed friction when the user said "treat local as Frontera." The
agent attempted `make compile`, failed on no-Fortran, and pivoted. Make this
explicit. Add to `swmf-replicate` required inputs:

```yaml
target_environment:
  cluster: frontera | pleiades | derecho | local
  build_locally: true | false
  submit: true | false
```

If `build_locally=false` and `submit=false`, the skill skips compile/run
steps and produces a **structural rundir with placeholders** as a first-class
deliverable — not a fallback after a build attempt. The chat already converged
on this mode; codifying it removes ~5 minutes of dead-end exploration per run.

### 4.10 Evaluation harness addition: physics-completeness check

Per §7.2 (Phase 2 exit criteria), the eclipse2024 case should be added to the
gold set as a **steady-state AWSoM** counterpart to the CCMC weihao CME case.
The agent runs blind (no author PARAM available); the oracle `PARAM.in.reference`
is used only by the harness to score the result. Exit metric:

- `param_diff` between agent output and the oracle shows zero deltas in the
  "physics block" set (the eight commands in §2), modulo command ordering.
- Numeric defaults (`#CHROMOBC`, `rMinWaveReflection`, `#MINIMUMTEMPERATURE`)
  match within 5% or are flagged for user confirmation in the skill output.
- The `inspect_artifact(param, check_rules=True)` call returns the three new
  `block`-severity rules from §4.3 firing on a deliberately-stripped PARAM,
  and zero firing on the oracle.
- Skill output's `provenance` ledger shows every physics-block command tagged
  `secondary_precedent:<path>` or `default:<id>` — never `gap`.

## 5. Summary of recommended changes

| Change | Layer | Effort | Payoff |
| --- | --- | --- | --- |
| `templates/awsom_steady_corona.yaml` | YAML drop | small | Closes anchor lane for AWSoM-steady |
| `case_recipes/awsom_steady_corona.md` | Markdown drop | medium | Documents required physics block + session structure |
| 4 new rules in `physical_constraints.yaml` | YAML + 2 new predicate types in MCP | medium (code touches predicate vocab) | Hard-blocks the eight-command physics gap |
| `derivations/awsom_steady.yaml` + `defaults/awsom_steady.yaml` | YAML drop | small | Closes derive + default lanes |
| `inspect_artifact(param, run_dir_root=…)` synthesis option | MCP code | small | Removes TestParam.pl-on-Mac friction |
| Make `secondary_precedents` mandatory reading + diff vs start template | Skill prose | small | Production AWSoM physics block flows into every replication |
| Minimum-build principle | Skill prose | small | Saves compile time and rules out IH-only bugs |
| Jobscript right-sizing requires evidence | Skill prose | small | Avoids 2-4× resource overshoot |
| `target_environment` input with `build_locally`/`submit` flags | Skill input contract | small | Removes the "build on Mac" dead end |
| Add eclipse2024 to Phase 2 gold set | Test harness | small | Catches the next physics-completeness regression |

None of these require new public MCP tools — the only MCP code change is two
new predicate types in `physical_constraints.yaml` evaluation
(`config_flag_present`, `lookup_table_name`/`file_pattern`/`command_value_set`).
Everything else is YAML, Markdown, or skill prose. This matches the
"YAML drop, no code" extension contract from §5.4.8.

## 6. Anti-patterns this run exposed

Add to §9.2 of `run_replication_plan.md`:

- **Anchoring on a teaching template without diffing against production
  precedents.** `Param/PARAM.in.awsom` is a minimal teaching template; the
  shipped production AWSoM PARAMs under `SWMFSOLAR/Param/` (the AWSoM-steady
  and SOFIE variants) carry the full physics block. The skill must diff
  start-template vs every listed secondary precedent before construction,
  treating commands present only in production precedents as physics-block
  candidates. Personal study run-dirs (e.g. anything under
  `SWMFSOLAR/Run_*/`) are out of corpus and must not be consulted.
- **Treating `TestParam.pl` pass as physics-completeness.** Already in §9.2
  but worth restating: this run produced a `TestParam.pl`-passing PARAM that
  is missing eight required physics commands. The rules directory is the
  substantive gate; schema is only the lower bound.
- **Equation-set–required commands not encoded.** If `Config.pl -o=SC:e=X` is
  chosen, the PARAM must contain X's required commands. This mapping is
  determinable from the source and belongs in `defaults/equation_set_required.yaml`.
- **Over-building "for SWMFSOLAR Makefile parity."** Carrying components the
  PARAM disables at runtime is a code smell, not a correctness requirement.
- **Jobscript scaling by analogy to the largest reference.** A 64-node × 24h
  envelope borrowed from a CME-with-IH run is not justification for a
  steady-state SC-only run. Right-sizing requires same-archetype precedent or
  back-of-envelope.
