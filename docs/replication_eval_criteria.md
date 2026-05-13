# Replication Evaluation Criteria

How to score a paper-replication attempt produced by `swmf-replicate`.
The goal is a repeatable rubric that distinguishes **agent quality** from
**evaluator luck** — and that scales to papers other than eclipse2024.

> This rubric is consumed by `swmf-improve` (Stage 2). The skill reads
> this document and applies the criteria to each attempt; criteria stay
> authoritative here, mechanization lives in the skill. See
> `src/agent_assets/skills/swmf-improve/SKILL.md`.

A replication attempt is a directory containing at minimum:

* `PARAM.in` (the produced parameter file)
* `CONFIG.sh` (the SWMF build invocation)
* `job.<cluster>` (the submission script)
* `REPORT.md` (the agent's self-report, including the `inferred | assumed`
  block and `gap` list)
* one of: a reference `PARAM.in.reference` (gold answer), or a published
  run that can be cited and diffed against.

If `PARAM.in.reference` is absent, only the **A** and **B** criteria apply.
**C** and **D** require a reference.

## A. Schema and structural validity (binary, must pass)

These are go/no-go gates. Any failure here is reported as a hard regression
even if the rest of the artifact is good.

| Check | How | Pass condition |
|---|---|---|
| Schema | `Scripts/TestParam.pl` at ≥3 nproc counts spanning the intended job range | exit 0 at every count |
| Rule check | `inspect_artifact(artifact_type="param", path=PARAM.in, check_rules=True)` | `rule_check_summary.block == 0` |
| Component map | `inspect_artifact` `component_map` field | matches the components named in the paper |
| Build vs PARAM consistency | `e=<Name>` in `CONFIG.sh` vs commands in `PARAM.in` | every required-command for that equation set is present |
| External references | `inspect_artifact` `external_references` | every `#INCLUDE` and `#LOOKUPTABLE` target resolves or is named in `inferred | assumed` |
| Sessions terminate | grep `#STOP` / `#RUN` / `#END` | one `#STOP` per session, one terminating `#END` |

Failure example: v2 built with `e=AwsomAnisoPi` but `PARAM.in` lacked the
Ehot stack — fails "Build vs PARAM consistency" even though it passed
`TestParam.pl`.

## B. Paper-spec coverage (graded, no reference needed)

Score what the agent extracted from the paper, independent of whether the
extraction is correct.

| Check | How | Pass / partial / fail |
|---|---|---|
| Paper-stated values cited | grep `REPORT.md` provenance table for `spec:paper:` tags | every numerical value the paper names has at least one `spec:` provenance entry |
| Paper-stated commands present | cross-check `paper_spec.json::numerics_phrases` against `PARAM.in` | every phrase maps to a present command, or appears in `gap` |
| `inferred | assumed` block exists and is non-trivial | read `REPORT.md` | block lists everything the paper does not say |
| `gap` list exists and is non-trivial | read `REPORT.md` | block lists everything the agent could not decide |
| Provenance per command | every `#COMMAND` in `PARAM.in` has a tag in REPORT | 100 % coverage; tags are `spec:` / `template:` / `recipe:` / `default:` / `practice:` / `derivation:` / `gap:` |

A high B score with a low C score means the agent is honest about its
uncertainty; a low B score means the agent silently assumed values the
paper did or did not name.

## C. Reference-diff: physics-command parity (graded, needs reference)

Treat `PARAM.in.reference` as the gold answer and compute:

```
missed = commands in reference not in attempt
extra  = commands in attempt not in reference
```

Score by category. Categories matter more than raw count — one missing
`#HEATCONDUCTION` is worse than three extra cosmetic `#LOOKUPTABLE`s.

| Category | Examples | Weight |
|---|---|---|
| **Physics-blocking misses** | `#HEATCONDUCTION`, `#SEMIIMPLICIT`, `#ANISOTROPICPRESSURE`, `#CURLB0`, `#COORDSYSTEM` | very high — these change the physics solved |
| **Numerical-scheme misses** | `#SCHEME` flux/limiter, `#TIMESTEPPING`, `#LIMITER` flags | high — change the numerical answer |
| **Boundary / domain misses** | `#OUTERBOUNDARY`, `#GRID` root blocks, `#LIMITRADIUS` | high — change the domain |
| **Operator-knowledge value misses** | `#POYNTINGFLUX`, `#CHROMOBC`, `#MINIMUMTEMPERATURE`, `#CORONALHEATING` reflection params | medium — change the steady state but not the structure |
| **Cosmetic / diagnostic misses** | `#ECHO`, `#TEST`, `#SATELLITE`, `#SAVEPLOT` formatting | low — observable-only |
| **Style-alternative misses** | `#AMRCRITERIARESOLUTION` vs `#AMRCRITERIALEVEL`, `#HARMONICSFILE` vs `#LOOKUPTABLE B0`, `#GRIDRESOLUTION` vs `#GRIDLEVEL` | low if the alternative is documented in `inferred | assumed`; medium otherwise |

A replication is **physics-equivalent** if its physics-blocking,
numerical-scheme, and boundary-domain misses are all zero. v2 was not
physics-equivalent; v3 is not yet (still missing `#ANISOTROPICPRESSURE` and
`#CURLB0`).

## D. Reference-diff: numerical-value parity (graded, needs reference)

For commands that appear in both, compare argument values.

| Match level | Description | Action |
|---|---|---|
| Exact | numerical equality | OK |
| Tolerant | difference within rule-defined tolerance (e.g. `#POYNTINGFLUX` ±20 %) | OK, log |
| Operator-knowledge mismatch | the parameter is the kind a practitioner tunes (Poynting flux, CHROMOBC, surface-wave reflection) | flag for Track D in the improvement plan |
| Structural mismatch | wrong sign, wrong order of magnitude | hard fail; almost always a paper-extraction or build bug |

Report per-parameter, not per-command — one `#POYNTINGFLUX` with the right
shape but the wrong value is different from `#OUTERBOUNDARY` with the
wrong boundary type on one face.

## E. Run-cycle readiness (binary, no reference needed)

Independent of physics correctness, does the package launch?

| Check | How | Pass condition |
|---|---|---|
| Magnetogram staged or fetch-scripted | `ls magnetogram/` and read `CLUSTER_COMMANDS.md` | a FITS file is present locally, or a documented fetch command exists |
| Jobscript matches cluster | inspect `job.<cluster>` headers | scheduler tokens (`#SBATCH` / `#PBS`) match the named cluster |
| Allocation placeholder called out | grep `REPORT.md` for the allocation flag | listed as an outstanding-user-action item |
| Run-dir layout described | read `run_dir_layout.md` | every file the PARAM references has a place in the layout |
| Build target named | read `CONFIG.sh` | the build flag matches the archetype's expected `e=<Name>` |

## Composite score

Report as a table per attempt:

```
A (schema/structural)    : PASS | FAIL (list failures)
B (paper coverage)       : X / Y items
C (physics parity)       : missed P-physics, P-numerical, P-boundary, P-operator, P-cosmetic, P-style
D (numerical-value)      : exact / tolerant / op-mismatch / structural counts
E (run-cycle readiness)  : PASS | FAIL (list failures)
```

A replication is:
* **shippable** if A and E pass.
* **physics-equivalent to reference** if A, E, and the high-weight C
  categories are clean.
* **paper-faithful** if B is ≥ 90 % and D shows no structural mismatches.

eclipse2024 v3 is shippable but not yet physics-equivalent. The Track A and B
fixes in the improvement plan target the gap between shippable and
physics-equivalent.

## Anti-overfitting discipline

Three rules to prevent the eval from leaking into the prototype:

1. **No single-paper eval is sufficient.** Every change to the prototype
   must be re-evaluated on at least two paper-replication targets. If only
   one is available, the change is provisional.
2. **No rule may be added to the prototype that cites the reference
   `PARAM.in` of any in-eval paper.** Rules must derive from shipped SWMF
   source, shipped SWMFSOLAR templates, paper text, or expert testimony —
   never from a reference answer.
3. **Reference files must be physically isolated.** Keep
   `PARAM.in.reference`, paper-figure assets, and prior chat transcripts in
   a directory the agent's `swmf_root` does not see. The current
   `Xianyu26Paper/` layout (replication sub-dirs are agent-visible; the
   parent dir holds the reference) is the right shape.

Violating any of these turns a rising eval score from evidence of
improvement into evidence of contamination, which is much harder to
detect later than to prevent now.

## Comparing attempts (v2 → v3 example)

When scoring a sequence of attempts on the same paper, report the deltas:

```
Criterion              v2          v3          Delta
A.schema_pass          PASS        PASS        =
A.build_param_consist  FAIL(5)     FAIL(1)     +4 closed
B.coverage             18 / 24     22 / 24     +4 items
C.physics_blocking     5 missed    2 missed    +3 closed
C.numerical_scheme     1 mismatch  0 mismatch  +1 closed
C.operator_knowledge   7 mismatch  7 mismatch  =
D.value_op_mismatch    7 params    7 params    =
E.runcycle_ready       PASS        PASS        =
```

A real improvement shows non-zero deltas in A, C, or D categories that the
intervening change targeted. Improvements only in B (paper-coverage) without
matching A/C/D deltas often indicate the agent is getting more verbose, not
more correct.
