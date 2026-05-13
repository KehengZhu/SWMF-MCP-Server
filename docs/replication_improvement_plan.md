# Replication-Agent Improvement Plan

Authored after the v2 → v3 eclipse-2024 evaluation cycle (`replication_v2/`,
`replication_v3/`). v3 closed the 5-command Ehot stack and added the minmod
warmup session that v2 explicitly overrode; the residual gap is two physics
commands (`#ANISOTROPICPRESSURE`, `#CURLB0`) plus an operator-knowledge
cluster (`#POYNTINGFLUX` value, `#CHROMOBC`, `#NONCONSERVATIVE`,
`#OUTERBOUNDARY` ϕ/λ treatment, surface-wave reflection, `#MINIMUMTEMPERATURE`,
`#GRID` root-block layout).

> Tracks A–D below map to lanes 1–6 of the `swmf-improve` Stage-3
> taxonomy (see `src/agent_assets/skills/swmf-improve/SKILL.md`):
>
> * Track A (equation-set wiring) → lane **wiring**
> * Track B (mineable corpus rules) → lane **corpus-derivable**
> * Track C (de-contaminate `_VAR_TO_COMMANDS`) → lane **source-derivable**
> * Track D (operator-knowledge rules) → lane **expert-knowledge**
>
> The meta-agent automates Tracks A–C across cycles; Track D remains
> bottlenecked on a human-operator conversation per the lane-policy in
> Stage 3.

This plan ranks the next improvements by leverage. It deliberately defers
contamination cleanup until the eval signal is strong enough to detect
regressions.

## Pre-requisite — break the eclipse2024 mono-eval

Every improvement from now on risks overfitting to eclipse2024 because that is
the only paper the prototype has been evaluated against. **Before adding any
new rules**, pick a second paper-replication target. Suitable candidates:

* Any AWSoM SC-only or SC+IH steady-state paper from a different group or year.
* A non-AWSoM target (SOFIE / SaMhd, AWSoM-R, MFLAMPA+CME) to exercise a
  different archetype.
* The CCMC public-archive runs (different magnetograms, same physics regime).

Acceptance: an unseen paper produces a `REPORT.md` whose `gap` list is
intelligible and whose `inferred | assumed` block is small. The eval criteria
in `replication_eval_criteria.md` apply to both papers symmetrically.

Without this second signal, "the gap got smaller" cannot be distinguished from
"the agent memorized the answer."

## Track A — Finish the equation-set wiring

**Status:** mechanical, no new domain knowledge, ~1 day.

**Symptom:** v3 fired the Ehot rule (5 commands landed) but not the Ppar rule
(`#ANISOTROPICPRESSURE` still missing). Both entries live in the same
`_VAR_TO_COMMANDS` dict in `scripts/mine_param_corpus.py`. The wiring is
single-variable-specific, not data-driven.

**Steps:**

1. Read `replication_v3/v3_chat.md` and confirm whether `Ppar` was ever
   queried against `equation_set_required.yaml`. If not, the bug is in the
   skill-side corpus-diff step.
2. In `swmf-replicate/SKILL.md` "Corpus diff (mandatory)", make the
   equation-set check **iterate every variable** in the build's `NameVar_V`
   that has an entry in `equation_set_required.yaml`. Do not predicate on
   archetype.
3. Add a regression test in `tests/test_replication_phase*.py`:
   `e=AwsomAnisoPi` build ⇒ Ppar-derived commands surfaced.
4. Re-run the eclipse2024 eval and confirm `#ANISOTROPICPRESSURE` appears.

**Closes:** `#ANISOTROPICPRESSURE`. Same fix shape should close future
equation-set-driven gaps automatically.

## Track B — Mineable operator commands

**Status:** corpus-derivable, ~2–3 days.

**Symptom:** `#CURLB0` and a few related B0-handling commands are present in
every shipped FDIPS/HARMONICS PARAM but missing from v3.

**Steps:**

1. Add a `b0_source → required_commands` lane to the miner. Inputs: presence
   of `#LOOKUPTABLE B0`, `#HARMONICSFILE`, `#HARMONICSGRID` in the source
   PARAM; outputs: commands that co-occur in ≥80 % of shipped PARAMs with
   that B0 source.
2. Emit `rules/defaults/mined/b0_source_required.yaml`.
3. Wire into the corpus-diff step in `swmf-replicate/SKILL.md`: after
   selecting the B0 source, intersect the emerging PARAM against the
   relevant `b0_source_required` entry.
4. Add a parallel lane for AMR style: `#AMRCRITERIALEVEL` + `#GRIDLEVEL`
   vs `#AMRCRITERIARESOLUTION` + `#GRIDRESOLUTION`. Don't pick one as
   canonical — let the chosen template's style carry, and surface the
   alternative in `inferred | assumed`.

**Closes:** `#CURLB0`, plus mass closure for any future B0 / AMR style gap.
Generalizes cleanly.

## Track C — De-contaminate `_VAR_TO_COMMANDS`

**Status:** static-analysis cleanup, ~1–2 weeks. **Defer until a second
paper-eval is in place** (otherwise improvements can't be detected).

**Symptom:** `_VAR_TO_COMMANDS` in `scripts/mine_param_corpus.py` is
hand-authored. The Ehot → 5-command mapping was reconstructed from
eclipse2024 knowledge during the v2 build, then back-derived from BATSRUS as
a sanity check. This is the contamination disclosed in the v3 prompt.

**Steps:**

1. Regex pass over `SWMF/SC/BATSRUS/src/Mod*.f90` and
   `share/Library/src/*.f90` to find command-handler gates of the form
   `if (index_in_NameVar_V('<var>') > 0) ... read_var('<#COMMAND>')` or
   `use_<var> = ...`.
2. Emit `rules/defaults/mined/var_to_commands.yaml` with provenance pointing
   at the BATSRUS file and line. Each entry: variable, required commands,
   source citation.
3. Delete the hand-authored `_VAR_TO_COMMANDS` dict; the miner consumes the
   generated YAML instead.
4. Re-run the miner and diff against the hand-authored output. Any deltas
   indicate either (a) over-curation in the original or (b) a mapping the
   regex missed; treat both as evidence to investigate, not noise.

**Closes:** the contamination disclosure. Does not directly add new
commands, but stops future improvements from quietly memorizing.

## Track D — Professor-knowledge rules

**Status:** requires SWMF operator input, ~one 2-hour conversation per batch
of 5–10 rules. **Highest residual ROI** but bottlenecked on a person.

**Symptom:** the operator-knowledge cluster from v3:

| Block | v3 | Reference | Why the agent gets it wrong |
|---|---|---|---|
| `#POYNTINGFLUX` value | `0.476e6` | `0.647e6` | Paper Table 2 has multiple rows; agent picked ADAPT-GONG row, reference uses a different row. Needs a rule mapping `(magnetogram_source, solar_activity) → row`. |
| `#CHROMOBC` (N, T) | `2e17, 5e4` | `5e17, 2e4` | Solar-max chromosphere differs from the AWSoM template default. |
| `#CORONALHEATING` rMin/reflection | `0.0, off` | `1.05, surface-wave T` | Surface-wave reflection at low corona is an operator-standard choice for steady-state runs; not in the shipped templates we mine. |
| `#NONCONSERVATIVE` | `F` | `T` | Operator preference for SC steady-state. |
| `#OUTERBOUNDARY` ϕ/λ | `periodic ×4` | `float ×5` | Operator preference; shipped template defaults to periodic. |
| `#GRID nRootBlock` | `2/2/1` | `2/4/2` | Operator-tuned for the eclipse2024 grid; not derivable from the template. |
| `#MINIMUMTEMPERATURE` | `5e4` | `2e4` | Operator floor. |

**Steps:**

1. Compile the list above (and equivalents from the second-paper eval) into a
   single agenda.
2. Single 2-hour conversation with an SWMF operator (Sokolov, Tóth, van der
   Holst, or any SWMFSOLAR practitioner). Capture each decision as a
   one-paragraph `practice:` or `derivations:` rule with a `Why:` line.
3. Land each rule in `rules/defaults/<topic>.yaml` or
   `rules/derivations/<topic>.yaml` per the lane policy in `rules/README.md`.
4. Cite the rule source as `expert:<name>:<date>` in the provenance tag, so
   future me can re-check.

**Closes:** ~half of the v3 residual gap. Does not generalize without effort
— each new physics regime needs its own operator pass.

## Recommended sequence

1. **Pick the second paper.** (1 day to find/scope, ongoing during everything
   below.)
2. **Track A** — finish the equation-set wiring. (~1 day.)
3. **Track B** — mineable B0/AMR-style rules. (~2–3 days.)
4. **Re-evaluate both papers.** (~1 day per paper.)
5. **Track D** — operator-knowledge conversation, batched. (~half-day prep,
   2-hour conversation, ~2 days landing the rules.)
6. **Re-evaluate both papers again.**
7. **Track C** — de-contaminate the var→commands map. Only after the eval
   signal is stable enough to detect regressions.

After step 6 the residual gap should be small, paper-specific, and clearly
labeled in `inferred | assumed` rather than silently wrong.

## Open question — `#AMRCRITERIARESOLUTION` `MaxResolution` in v3

v3 sets `MaxResolution = 0.35` (matches the finest target); v2 set it to
`2.8` (matches the coarsest). One Read of `PARAM.XML`'s `#AMRCRITERIARESOLUTION`
definition will resolve which is correct. If v3 is wrong, file as a regression
under Track A's regression-test suite.

## Out of scope

* Re-mining cadence as a scheduled job (capability_enrichment_plan.md §7
  item 5). Manual re-run on new SWMFSOLAR exemplars is sufficient.
* Per-paper delta lanes (capability_enrichment_plan.md §7 item 4). Defer
  until a third paper is in evaluation rotation.
* MCP public-surface changes. All improvements above land in skill/rule
  files; the MCP tool surface is unchanged.
