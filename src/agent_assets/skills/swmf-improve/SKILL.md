---
name: swmf-improve
description: "Use when the task is to grow the SWMF replication rules layer from paper-replication outcomes. Drives one cycle of: replicate a paper from the curated eval set, score the attempt against the A–E rubric, classify each residual gap to a fix-source lane, draft rules with non-reference provenance, regress across all eval papers, auto-merge low-risk lanes or file proposals for human review. Pre-requisite: the eval set under `eval/papers/` contains the named paper with `paper.pdf` and `reference/PARAM.in`."
---

# swmf-improve

Outer loop that wraps `swmf-replicate` with score → classify → propose →
regress → merge. The goal is to grow `rules/` without learning from the
eval references.

## When to use

* "Run one improvement cycle on eclipse2024."
* "Process the new paper I added to the eval set."
* "Re-check whether v3's residual gap can be closed by mineable rules."

## Do not use when

* No eval entry exists for the named paper → user must drop `paper.pdf`
  and `reference/PARAM.in` under `eval/papers/<name>/` first.
* User wants a single replication, not the improvement loop → use
  `swmf-replicate` directly.
* User wants to score an attempt against a reference without proposing
  rules → run Stage 2 only (see "Partial invocation" below).

## Required inputs

* `paper_name` — directory name under `eval/papers/`.
* The eval entry must contain `paper.pdf` and `reference/PARAM.in`.
* Optional: `--no-merge` to stop after Stage 4 (propose) without running
  regression / merge. Useful while debugging.

If the eval entry is missing, the skill stops and reports what to add.
It does not invent paths or fall back to other paper directories.

## The contamination tripwire (read this first)

The meta-agent's one inviolable rule:

> **No proposed rule's `provenance.source` may resolve under any
> `eval/papers/*/reference/` directory.**

The reference is allowed *only* as the existence signal that a gap is
present (Stage 2 diff). It is **never** an acceptable fix source. Every
rule must cite shipped SWMF/SWMFSOLAR source, a paper DOI + page, an
archetype catalog entry, a mined corpus YAML, or expert testimony. If
the only signal an agent has for a value is the reference itself, the
gap routes to the `reference-only` or `expert-knowledge` lane, not to a
rule proposal.

The agent enforces this before writing each proposed rule and re-checks
before any merge. Violations are filed under `eval/proposals/rejected/`
with the offending source path quoted.

## Five-stage workflow

### Stage 1 — Replicate

Invoke `swmf-replicate` with:

* `intent="paper"`
* `paper_path = eval/papers/<paper_name>/paper.pdf`
* The replicate skill's own `swmf_root` and target paths — pass through
  whatever the user has configured globally. The replicate skill is
  *not* told about `eval/papers/<paper_name>/reference/`; that path is
  this skill's responsibility, not the inner replicator's.

Cache the generated `paper_spec.json` under
`eval/papers/<paper_name>/cache/paper_spec.json` so re-runs reuse it.
If the cache exists and the PDF is unchanged, pass the cached spec to
`swmf-replicate` (skipping its own Stage 1 extraction).

Outputs land under `eval/papers/<paper_name>/runs/<YYYY-MM-DD>/attempt/`:
`PARAM.in`, `REPORT.md`, `CONFIG.sh`, `job.<cluster>`.

### Stage 2 — Score (apply the rubric)

Read `docs/replication_eval_criteria.md`. Apply each criterion to the
attempt:

**A. Schema and structural validity (binary).**
* Run `Scripts/TestParam.pl` at the nproc counts named in the attempt's
  `REPORT.md` (typically 3 counts spanning the intended job range).
  Record exit codes.
* Run `swmf inspect --type param --path attempt/PARAM.in --check-rules`.
  Record `rule_check_summary.{block,warn,info}`.
* Verify `component_map` matches the paper's components.
* Verify build-vs-PARAM consistency: read `CONFIG.sh` for `e=<Name>`;
  every command required for that equation set (cross-reference
  `rules/required_floors/equation_set.yaml`) must be present in
  the PARAM.
* Verify `external_references` resolve.
* Verify session structure (`#STOP` per session, `#END` terminating).

**B. Paper-spec coverage (graded).**
* Read the attempt's `REPORT.md` and pull the provenance table.
* Cross-check: every numerical value the paper states has at least one
  `spec:` provenance entry; every command in the PARAM has a provenance
  tag drawn from `spec | template | recipe | default | practice |
  derivation | gap`.
* Verify the `inferred | assumed` block exists and is non-trivial.
* Verify the `gap` list exists.

**C. Reference-diff: physics-command parity (graded, needs reference).**
* Run `swmf compare --left attempt/PARAM.in --right eval/papers/<name>/reference/PARAM.in`.
  This returns the per-command diff (`missed`, `extra`, value mismatches).
* Categorize each diff record using the rubric's category table:
  - **physics-blocking** (`#HEATCONDUCTION`, `#SEMIIMPLICIT`,
    `#ANISOTROPICPRESSURE`, `#CURLB0`, `#COORDSYSTEM`)
  - **numerical-scheme** (`#SCHEME` flux/limiter, `#TIMESTEPPING`,
    `#LIMITER` flags)
  - **boundary-domain** (`#OUTERBOUNDARY`, `#GRID`, `#LIMITRADIUS`)
  - **operator-knowledge value** (`#POYNTINGFLUX`, `#CHROMOBC`,
    `#MINIMUMTEMPERATURE`, `#CORONALHEATING` reflection params)
  - **cosmetic / diagnostic** (`#ECHO`, `#TEST`, `#SATELLITE`,
    `#SAVEPLOT` formatting)
  - **style-alternative** (`#AMRCRITERIARESOLUTION` vs
    `#AMRCRITERIALEVEL`, `#HARMONICSFILE` vs `#LOOKUPTABLE B0`)
* Categorization is judgment: weigh the command's role in the physics
  being solved, not its alphabetic order or frequency.

**D. Reference-diff: numerical-value parity.**
* For commands present in both, compare argument values:
  - **Exact** — numerical equality.
  - **Tolerant** — within rule-defined tolerance (e.g. `#POYNTINGFLUX`
    ±20 %; check `rules/physical_constraints.yaml` for tolerances).
  - **Operator-knowledge mismatch** — practitioner-tunable parameter
    (Poynting flux, CHROMOBC, surface-wave reflection).
  - **Structural** — wrong sign, wrong order of magnitude. Always a
    hard fail.

**E. Run-cycle readiness (binary).**
* Magnetogram staged or fetch-scripted.
* Jobscript matches the named cluster (`#SBATCH` / `#PBS` tokens).
* Allocation placeholder called out in REPORT.
* Run-dir layout documented.
* Build target named.

Write the score to `runs/<date>/score.md` (markdown table per criterion)
and `runs/<date>/gap_list.md` (one record per categorized gap).

### Stage 3 — Classify (route each gap to a lane)

For each gap in `gap_list.md`, decide which lane the fix must come from. Per
the Option-2 refactor (see plan Part C2) the lane taxonomy is **6 lanes**
mutually exclusive, prioritized in order:

| Order | Lane | Signal to look for | Fix lands in | Auto-fix? |
|---|---|---|---|---|
| 1 | **xml_lookup** | Agent emitted the command but never ran `swmf inspect --type xml --xml-scope 'commandgroup:...'` for its commandgroup (audit_violation in launch gate, or absent from `xml_audit_record`) | `swmf-replicate/SKILL.md` ladder strengthening + audit gate tightening | ✅ (skill-prompt patch, regression-gated) |
| 2 | **crosswalk** | Paper used a physics phrase that did not map to any command name (agent surfaced a gap with no candidate); the phrase + the correct command are both known | `rules/crosswalks/<topic>.yaml` (new entry) | ✅ |
| 3 | **convention** | Multiple SWMF commands were valid for the same job; agent picked the wrong one for this archetype | `rules/conventions.yaml` (new tie-breaker entry) | ✅ |
| 4 | **recipe** | Session ladder / AMR pattern / equation-set choice diverges from archetype norm; the recipe needs an update | `rules/case_recipes/<archetype>.md` | ✅ |
| 5 | **paper_extraction** | Paper-stated value missing from `paper_spec.json` because the extractor missed it (low confidence, hidden in a table, etc.) | `swmf-replicate` Stage 1 spec-extraction prompt | ✅ (skill-prompt patch, regression-gated) |
| 6 | **expert_review** | None of the above fits; the value is operator preference, or the lane is genuinely ambiguous | Queue to `eval/expert_queue.md` for human conversation | ❌ |

Classification procedure (run **in order**, stop at first match):

1. Read `runs/<date>/attempt/REPORT.md` and look at the `xml_audit_record`
   field from the launch gate. If the missed command's commandgroup is
   NOT in `groups_read` → `xml_lookup`.
2. Re-read the paper section for the affected physics topic. If the paper
   uses a phrase that does not appear in any `rules/crosswalks/*.yaml`
   `phrases:` field, and the correct command is known from the reference
   → `crosswalk`.
3. Check whether the reference uses a different but equivalent SWMF
   command for the same job (e.g. `#AMRCRITERIARESOLUTION` vs
   `#AMRCRITERIALEVEL`). If yes → `convention`.
4. Check `rules/case_recipes/<archetype>.md`. If the recipe does not
   describe the session structure the reference uses → `recipe`.
5. Read `eval/papers/<name>/cache/paper_spec.json`. If the paper body
   names the value but the spec is missing it → `paper_extraction`.
6. Otherwise → `expert_review`.

The old `wiring`, `corpus-derivable`, and `source-derivable` lanes have been
folded: corpus-mined intersections are gone (they hid `#CURLB0` in Liu et
al. 2026); PARAM.XML-derivable knowledge belongs in `required_floors/` or
PARAM.XML itself, not in a rules-layer derivation; and the wiring lane
was a symptom of mined rules silently failing — which can no longer
happen now that the agent reads PARAM.XML directly under audit-gate
enforcement.

Write `runs/<date>/improvement_plan.md`: one section per gap with the
category from Stage 2, the lane from Stage 3, the proposed-fix source,
and a one-paragraph proposed action.

### Stage 4 — Propose (draft rules or skill-prompt patches)

For each gap whose lane permits auto-fix (lanes 1–5), draft the appropriate
artifact:

**Lane 1 — xml_lookup** (skill-prompt patch):
```markdown
# patch — strengthen swmf-replicate audit gate
Target file: src/agent_assets/skills/swmf-replicate/SKILL.md
Diff: add a checkpoint requiring `swmf inspect --type xml --xml-scope 'commandgroup:<X>' --run-dir <run directory>`
before authoring the <Y> block. Pass the SAME --run-dir to this xml read
and to the `swmf inspect --type param --check-xml-audit --run-dir <run directory>`
launch check so the audit gate (persisted to <run_dir>/.swmf_ai/audit.json) can
correlate the recorded commandgroup reads with the launch check.
```

**Lane 2 — crosswalk** (new YAML entry):
```yaml
# rules/crosswalks/<topic>.yaml — appended entry
crosswalks:
  - id: <slug>
    phrases:
      - "<phrase exactly as it appears in the paper>"
    commands:
      - "#<COMMAND>.<parameter>"
    xml_group: "<COMPONENT>:<GROUPNAME>"
    archetypes: [<archetype-id>]
    notes: <one-line non-obvious rationale>
    provenance:
      lane: crosswalk
      added_by: swmf-improve
      added_for_eval: <paper-name>
      added_on: <YYYY-MM-DD>
```

**Lane 3 — convention** (new entry in `rules/conventions.yaml`).
**Lane 4 — recipe** (markdown edit to `rules/case_recipes/<archetype>.md`).
**Lane 5 — paper_extraction** (skill-prompt patch to `swmf-replicate`
Stage 1, identical shape to lane 1).

**Provenance / contamination check (mandatory).** Before writing the
artifact to disk, verify that the proposed entry does NOT include literal
text or numeric values extracted from any path under
`eval/papers/*/reference/`. Compute the absolute path of any cited
source and check whether it is a descendant of any reference directory.
If so:

* Do not write the rule / patch.
* Write `eval/proposals/rejected/<date>-<gap>.md` with the offending
  source, the gap it was trying to close, and a note that the lane
  should have routed to `expert_review` instead. Update the
  classification.

For lane 6 (`expert_review`) gaps, append an entry to
`eval/expert_queue.md` using the template at the top of that file. Do
not draft a rule.

Write all drafted artifacts to `runs/<date>/proposals/` first (not directly
into `rules/` or `src/agent_assets/skills/`). They move into the live
tree only after Stage 5 gates pass.

### Stage 5 — Regress + merge

For each proposed rule:

1. Create a worktree: `git worktree add ../swmf-improve-wt-<gap> HEAD`.
2. Copy the proposed rule into the worktree's `rules/` tree.
3. Re-run Stages 1–2 on every paper under `eval/papers/` (train +
   holdout). Run in parallel where feasible (one worktree per paper).
4. Compute deltas: `score_after.composite - score_before.composite`
   per paper.
5. Run `pytest tests/` in the worktree.
6. **Auto-merge** iff all of:
   - target paper improves in C or D categories
   - no other paper regresses in A, C, or D
   - holdout paper score is unchanged or improves
   - `pytest tests/` exits 0
7. If auto-merge: copy the rule from the worktree into `rules/`, write
   `eval/proposals/<date>-<gap>.md` with `status: auto-merged` and the
   delta table.
8. If not auto-merge: write `eval/proposals/<date>-<gap>.md` with
   `status: pending-human-review` and the delta table. The rule stays
   in `runs/<date>/proposals/` until a human reviews it.
9. Clean up the worktree: `git worktree remove ../swmf-improve-wt-<gap>`.

The delta table per proposal:

| Paper | A.before | A.after | C.before | C.after | D.before | D.after | Verdict |
|---|---|---|---|---|---|---|---|
| eclipse2024 (target) | PASS | PASS | 2 missed | 1 missed | 7 op | 7 op | improves |
| paper-2 (train) | PASS | PASS | 3 missed | 3 missed | 4 op | 4 op | unchanged |
| paper-3 (holdout) | PASS | PASS | 1 missed | 1 missed | 2 op | 2 op | unchanged |

## Output contract

After `/swmf-improve <paper-name>` completes:

```
eval/papers/<paper-name>/runs/<YYYY-MM-DD>/
├── attempt/
│   ├── PARAM.in
│   ├── REPORT.md
│   ├── CONFIG.sh
│   └── job.<cluster>
├── score.md
├── gap_list.md
├── improvement_plan.md
└── proposals/
    ├── <gap-1>.yaml           drafted rule (pre-regression)
    └── <gap-2>.yaml
eval/proposals/
├── <YYYY-MM-DD>-<gap-1>.md    auto-merged or pending review
└── rejected/
    └── <YYYY-MM-DD>-<gap-3>.md  if any provenance violation occurred
```

The terminal message summarizes:

```
swmf-improve cycle on <paper-name>:
  attempt scored: A=PASS, B=22/24, C=2 missed (1 physics, 1 op), D=7 op-mismatch, E=PASS
  gaps classified: 1 xml_lookup, 2 crosswalk, 1 convention, 1 paper_extraction, 1 expert_review
  proposals drafted: 5
  auto-merged: 4
  pending review: 1 (see eval/proposals/<date>-<gap>.md)
  expert queue: +1 entry (see eval/expert_queue.md)
```

## Partial invocation

The skill accepts three reduced modes for development / CI / regression:

* `--only=eval` — runs Stage 1 + Stage 2 only and writes `score.md` and
  `gap_list.md`, then stops. The same mode used by CI to confirm no
  refactor regresses any paper in `eval/papers/`. No proposals, no merges.
* `--only=eval --all` — runs `--only=eval` over **every** paper in
  `eval/papers/` (plus the holdout) and emits a single score matrix per
  invocation. Wire into pytest as a slow-tier test.
* `--no-merge` — runs through Stage 4 (proposals drafted, queues
  written) but skips Stage 5. The proposals stay under
  `runs/<date>/proposals/` and are not regression-tested.

## Cross-paper discipline

Every cycle re-evaluates **all** eval papers, including holdout. The
holdout is the load-bearing check: a rule that improves the target but
degrades the holdout is exactly the contamination signal — auto-merge
rejects it. The holdout is rotated per the policy in
`eval/papers/holdout.txt`.

If the eval set has fewer than 2 papers, the skill warns at the start
of every cycle. With only 1 paper, the cross-paper regression
collapses to a tautology and the holdout signal is meaningless. Curate
a second paper before relying on auto-merge.

## Invariants

* The skill never reads any file under `eval/papers/*/reference/`
  except to run `swmf compare` in Stage 2. The reference is
  evidence of the gap, not a source for the fix.
* `provenance.source` must resolve outside `eval/papers/*/reference/`.
  This is enforced twice: at proposal-write time and at pre-merge
  re-check.
* No rule is written directly into `rules/`. Proposals are written to
  `runs/<date>/proposals/` and moved into `rules/` only by the merge
  step in Stage 5.
* Expert-knowledge and reference-only gaps never produce auto-fixes.
  They produce queue entries (operator) or flagged proposals (human
  review).
