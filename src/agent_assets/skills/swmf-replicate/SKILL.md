---
name: swmf-replicate
description: "Use when the task is to replicate a SWMF run end-to-end: from a paper, a structured spec (CCMC), or a prior run directory. Drives spec normalization, build, run-dir assembly, PARAM.in generation, pre-launch validation gate, submission, monitoring, postprocessing, and validation."
---

# swmf-replicate

End-to-end replication of a SWMF run. Single entry skill, three intents declared via input
contract: `intent="paper"`, `intent="structured_spec"`, `intent="prior_run"`.

## When to use

* "Run this paper's case from scratch."
* "Replicate this CCMC run locally."
* "Reproduce `Run_Max_RP_CME3/run01` on Frontera."
* "Build a new run for the 2023-02-24 CME like this paper says."

## Do not use when

* User wants to interpret an *existing* run → `swmf-analyze`.
* User wants to compare two existing runs without producing a new one → `swmf-compare`.
* User wants to debug a failed run → `swmf-debug`.
* User asks "how does AWSoM-CME work?" without intent to run → `swmf-explain`.
* User only wants to configure/edit PARAM in an existing case → `swmf-configure`.

## Required inputs (from agent intake)

* One of: paper file path, structured-spec file path, prior run directory path.
* Target environment: `cluster=frontera|pleiades|derecho|local`.
* Optional: target SWMF source path; output root.

If any of these is missing the skill asks the user once; it does not invent.

## Evidence order

1. **Spec inspection.**
   * `prior_run`: `inspect_artifact(artifact_type="run_dir", path=<dir>)` for layout +
     `component_output_artifacts`, then **read the run-local `PARAM.in` directly** for
     run intent (sessions, control cadence, save-plot meaning, command flow). The
     param inspector is structural-only; do not call it for intent reasoning.
   * `structured_spec`: `inspect_artifact(artifact_type="ccmc_spec", path=<file>)`. The
     parser surfaces typed fields (`run_id`, `model`, `event_time_utc`, `fr_type`,
     `fr_params`, `cone_params`, `cme_params`, `mflampa_params`, `metadata`,
     `input_files_listed`, `output_files_listed`, `quicklook_targets`). Treat absent
     fields as `gap`, never invent.
   * `paper`: see *Paper intent* below. The agent extracts a structured
     `paper_spec.json` from paper text, asks the user to confirm, then calls
     `inspect_artifact(artifact_type="paper_spec", path=<paper_spec.json>)`. After
     this step the workflow merges with the `structured_spec` path — same
     archetype detection, same template/recipe/derivation/default ladder, same
     launch gate.
2. **Archetype detection.** From the normalized spec compute the case archetype tuple
   `(model, components, has_CME, has_MFLAMPA, has_threaded_gap)`. Common results:
   * `awsom_cme_eruption` — AWSoM/AWSoM-R + CME, no SP. Anchored on
     `SWMFSOLAR/Run_Max_RP_CME3/run01`.
   * `sofie_mflampa_cme` — AWSoM-R + SaMhd + CME + MFLAMPA SP. Anchored on
     `examples/CCMC_run_weihao/`.
3. **Template discovery.** Load
   `support/swmf-params/rules/templates/<archetype>.yaml`. The manifest carries
   `start_template`, `restart_template`, `required_flag_overrides`, `recipe`, and
   `secondary_precedents`. If no manifest exists, fall back to
   `get_evidence(query="<archetype> PARAM template", task_type="configuration", goal="PARAM template selection")`
   and tag `template_choice.provenance="inferred"`.
4. **Magnetogram and harmonics evidence.**
   * `inspect_artifact(artifact_type="magnetogram", path=<fits|map>)` when a file is
     named or downloaded. The inspector reports format, map_type, CR, observation_time,
     realization_count, and grid.
   * Hand off to `swmf-magnetogram` for the alignment policy.
   * `get_evidence(query="ADAPT magnetogram download", task_type="configuration", goal="magnetogram acquisition entrypoint")`
     when nothing is named — the entrypoint is `SWMFSOLAR/Scripts/download_ADAPT.py`.
5. **Build evidence.** Hand off to `swmf-build`; the canonical `Config.pl` flags for the
   archetype come from `rules/defaults/build_flags.yaml` (provenance `default:<id>`)
   unless the spec or template manifest overrides them.
6. **Job assembly.**
   * `inspect_artifact(artifact_type="jobscript", path=<file>)` on the chosen template.
   * `get_evidence(query="job script <cluster>", task_type="run", goal="cluster submission template")`
     if no template is named.
7. **PARAM.in generation.** Classify as **sweep** vs **construction** per §6.5 of
   `docs/run_replication_plan.md`:
   * **Sweep**: template structure is correct; only parameter values change. Agent shells
     `SWMFSOLAR/Scripts/change_param.py` with a typed dict. Use this for prior-run
     replication and for ADAPT-realization studies over an existing case.
   * **Construction** (Phase 2): template is the closest precedent but its *structure*
     must change. Follow the procedure below.
8. **Pre-launch validation gate** (mandatory; see *Launch Gate* below).
9. **Launch.** Agent shells `sbatch`/`qsub`/`mpirun`. Skill output records the launch
   command and job id. For two-PARAM CME archetypes, `launch_command` is a list:
   submit start → wait for `SWMF.SUCCESS` and confirm `SC/restartOUT/` + `IH/restartOUT/`
   populated → swap PARAM.in for the restart variant → resubmit.
10. **Monitoring.** Agent shell + periodic `inspect_artifact(artifact_type="run_dir")` and
    `inspect_artifact(artifact_type="runlog")`.
11. **Postprocessing and visualization.** Hand off to `swmf-analyze`; `swmf-postproc`
    owns IDL execution.
12. **Validation.** Hand off to `swmf-validation` (Phase 3).

## Paper intent (Phase 3)

Triggered when `intent="paper"`. The agent (LLM) reads the paper PDF/preprint;
**MCP does not parse PDFs** (anti-pattern: MCP-as-PDF-parser, plan §9.2).

1. **Extract.** From the paper text (and any tables/figures the user pasted),
   the agent produces a structured normalization with the same shape as
   `ccmc_spec`:

   ```jsonc
   {
     "run_id":          "<paper-derived id, e.g. sokolov2023_2023-02-24>",
     "model":           "AWSoM-R + MFLAMPA",
     "model_version":   null,
     "event_time_utc":  "2023-02-24T20:30:00+00:00",
     "fr_type":         "GL",
     "fr_params":       { "longitude_deg": ..., "latitude_deg": ..., ... },
     "cone_params":     { ... },
     "cme_params":      { "speed_km_s": ..., "mass_g": ... },
     "mflampa_params":  { ... },
     "metadata":        { "magnetogram_source": "ADAPT", "carrington_rotation": 2266 },
     "input_files_listed":  [],
     "output_files_listed": [],
     "quicklook_targets":   ["LASCO_C2_base_difference_movie", "OMNI_density_L1"],
     "source_paper_path":   "/abs/path/to/paper.pdf",
     "confidence_per_field": {
       "fr_type":          "high",
       "fr_params":        "medium",
       "event_time_utc":   "high",
       "magnetogram_source": "low"
     }
   }
   ```

   * Mirror `ccmc_spec` keys exactly so downstream archetype/recipe/derivation
     logic does not branch on intent.
   * `confidence_per_field` is the agent's own self-rating
     (`high|medium|low`, or 0–1). Low-confidence fields drive earlier user
     prompts and stricter gating downstream.
   * If a field is silent in the paper, **omit it** rather than guessing;
     the inspector reports it under `paper_spec_missing_fields`.

2. **User confirmation before compute.** The agent presents the extracted JSON
   to the user before any compute (download, build, run-dir assembly) is
   consumed. The user edits or accepts; the agent writes the file to
   `<workspace>/paper_spec.json`.

3. **Inspect.** Call
   `inspect_artifact(artifact_type="paper_spec", path=<paper_spec.json>)`.
   Surface:
   * `paper_spec_summary` — the typed fields as MCP loaded them.
   * `paper_spec_provenance` — `source_paper_path` + `confidence_per_field`.
   * `paper_spec_missing_fields` — canonical fields absent from the JSON.
   * `paper_spec_files` / `paper_spec_quicklook` — when listed.
   * `paper_spec_parse_errors` — any JSON/YAML loader errors.

4. **Merge with structured-spec path.** Treat `paper_spec_summary` exactly like
   `ccmc_spec_summary` from this point on:
   * archetype detection,
   * template manifest load,
   * authoring ladder (with `spec` provenance pointing to `paper_spec`,
     **not** `ccmc_spec`),
   * launch gate.

5. **Provenance discipline.** Every PARAM value whose `param_provenance` is
   `spec` carries a sub-tag `spec:paper:<field>` for paper intent (vs
   `spec:ccmc:<field>` for structured_spec). Low-confidence paper fields
   propagate into the launch gate's `inferred|assumed` block alongside
   `derivation:gl_to_spheromak_typecme`-class translations.

6. **Validation hand-off.** Each entry in `quicklook_targets` becomes a
   target for `swmf-validation` after the run finishes. `paper_spec_files` and
   `quicklook_targets` are the canonical inputs to the validation plan.

Anti-patterns specific to paper intent:

* **Inventing missing fields.** If `paper_spec_missing_fields` lists a
  required key, surface it as a `gap` and ask the user — do not infer from
  "physical reasonableness".
* **Lossy paper extraction.** Confidence-per-field is mandatory; "I read the
  paper, here's a JSON" without confidence labels prevents the launch gate
  from flagging weak inputs.
* **PDF parsing in MCP.** `inspect_artifact(artifact_type="paper_spec")` only
  loads the JSON/YAML the agent already wrote. The PDF is the agent's input.

## Construction mode (Phase 2)

Triggered when the chosen template's structure does not match the spec. Most paper- and
CCMC-driven replications are construction jobs. Steps:

1. **Resolve archetype** from the normalized spec.
2. **Load the template manifest**
   `support/swmf-params/rules/templates/<archetype>.yaml`. The manifest names the
   start+restart template pair, required flag overrides, and the recipe pointer.
3. **Read the case recipe** under `support/swmf-params/rules/case_recipes/`. The recipe
   defines the multi-session skeleton: which command appears in which session, where
   `#TIMEACCURATE` flips, where `#CME` opens, where `UseCme=F` closes the seed, where
   the relaxation tail starts.
4. **Walk the authoring ladder per emitted PARAM value.** For every value the agent
   would write, walk this ladder and record the supplying step as the value's
   provenance:

   | Step | Lane | Provenance tag |
   | ---- | ---- | -------------- |
   | 1 | spec field, direct (`fr_longitude`, `event_time_utc`, etc.) | `spec` |
   | 2 | derivation matches and computes (`rules/derivations/*.yaml`) | `derivation:<id>` |
   | 3 | recipe specifies a session-structural slot (`rules/case_recipes/*.md`) | `recipe:<id>` |
   | 4 | template carries the value as-is | `template:<path>` |
   | 5 | default applies (`rules/defaults/*.yaml`) | `default:<id>` |
   | 6 | narrative practice resolves a tie (`rules/numerical_practices.md`) | `practice:<entry>` |
   | 7 | nothing supplies the value | `gap` → user prompt |

5. **Two-PARAM split.** For CME archetypes (`awsom_cme_eruption`,
   `sofie_mflampa_cme`), produce **both** `PARAM.expand.start` (background) and
   `PARAM.expand.restart` (eruption + relaxation). Verify the restart PARAM's
   `#INCLUDE RESTART.in`, `#INCLUDE SC/restartIN/restart.H`, `#INCLUDE
   IH/restartIN/restart.H` references. The recipe `case_recipes/<archetype>.md`
   specifies which command lives in which file.
6. **Direct PARAM authoring.** Agent writes both PARAM files via Edit/Write at the
   assembled run-dir path. `change_param.py` is **not** sufficient — it cannot insert
   `#CME`, reshape sessions, or reorder commands. Where a sub-block is itself a sweep
   (e.g. plugging FR numbers into a new `#CME` block after the structural edit), the
   agent may shell `change_param.py` for that sub-step.
7. **Surface translations.** Any value whose provenance is
   `derivation:gl_to_spheromak_typecme` (or any other `surface_as: inferred`
   derivation) must appear in the launch gate's `inferred|assumed` block. The skill
   refuses launch until the user confirms each.
8. **Surface gaps.** Every `gap` value is presented as a user-approval item. Closing a
   gap is a YAML edit in `rules/derivations/` or `rules/defaults/` — record this
   suggestion in the skill output so the next replication does not re-prompt.
9. **Run the launch gate** (next section).

Anti-pattern: re-prompting the user for the same `gap` across runs. If a gap recurs,
promote it into the rules directory (a derivation if it's a function of the spec, a
default if it's archetype-keyed, a recipe entry if it's structural).

## Authoring ladder (per emitted PARAM value)

For every PARAM value the agent writes during construction, walk this ladder. The first
step that supplies the value wins; the agent records the supplying step as that value's
provenance:

| Step | Lane | Provenance tag |
| ---- | ---- | -------------- |
| 1 | spec field, direct | `spec` |
| 2 | derivation matches and computes (`rules/derivations/*.yaml`) | `derivation:<id>` |
| 3 | recipe specifies a session-structural slot (`rules/case_recipes/*.md`) | `recipe:<id>` |
| 4 | template carries the value as-is (`rules/templates/*.yaml`) | `template:<path>` |
| 5 | default applies (`rules/defaults/*.yaml`) | `default:<id>` |
| 6 | narrative practice resolves a tie (`rules/numerical_practices.md`) | `practice:<entry>` |
| 7 | nothing supplies the value | `gap` → user prompt |

The agent **must not** invent numerical values. Every `gap` entry surfaces as a
user-approval item; closing one is a YAML edit in the rules directory so the next
replication does not re-prompt.

## Launch Gate (mandatory)

Launch is blocked unless every check below passes:

1. `inspect_artifact(artifact_type="param", path=<PARAM.in>, check_rules=True)` — the
   structural primitive call. **Block on any `severity=block` violation.** `warn` and
   `info` surface but do not block. The agent has already read PARAM.in directly for
   intent reasoning earlier in the workflow; this step is purely the rule-eval check.
2. Agent shells `Scripts/TestParam.pl -n=<nproc> <PARAM.in>` from the SWMF root. **Block
   on any error** — this is the schema authority.
3. PARAM diff vs base template via `compare_artifacts(comparison_type="param")` (or the
   `param_diff` block of `compare_artifacts(comparison_type="run_dir")` when both runs
   are assembled), with evidence citation per change, presented to the user.
4. The skill output's `inferred|assumed` value list is presented to the user.
5. User approval is recorded (timestamp + hash of approved PARAM.in).

Steps 3–5 are skill-level (the gate is enforced by skill policy, not MCP). MCP only
supplies the deterministic checks in step 1 and the diff in step 3; step 2 is a shell
call.

## Helper skills

* `swmf-configure` — for PARAM construction details.
* `swmf-build` — for build orchestration.
* `swmf-run` — for run-dir readiness and submission.
* `swmf-analyze` — for postprocessing and IDL.
* `swmf-compare` — for prior-run parity check.
* `swmf-jobscript` — for cluster jobscript inspection.
* `swmf-magnetogram` (Phase 2) — for magnetogram input handling.
* `swmf-cme-setup` (Phase 2) — for CME initiation policy.
* `swmf-validation` — for run-vs-reference comparison (paper figure / OMNI /
  CCMC quick-look).
* `swmf-swmfsolar` (Phase 2) — for SWMFSOLAR Makefile/Scripts navigation.

## Output contract

Required fields in the final answer:

* `intent` — one of `paper|structured_spec|prior_run`.
* `normalized_spec` — structured representation of model, event time, magnetogram source,
  B0 method, FR type and parameters, target diagnostics, target cluster.
* `template_choice` — picked PARAM template plus evidence path and `provenance` tag
  (`manifest` if loaded from `rules/templates/`, else `inferred`).
* `case_recipe` — pointer to the recipe followed (for construction mode).
* `external_inputs` — magnetogram file, harmonics file, restart source, with provenance
  (downloaded vs reused vs inferred).
* `build_plan` — `Config.pl` invocations and `make` targets, with evidence citations.
* `assembled_run_dir` — path of the constructed run directory and its readiness diff vs
  `swmf-run` checks.
* `param_provenance` — for each emitted/changed PARAM value, the supplying lane tag from
  the authoring ladder (`spec` | `derivation:<id>` | `recipe:<id>` | `template:<path>` |
  `default:<id>` | `practice:<entry>` | `gap`).
* `gaps` — explicit list of `gap` values requiring user input.
* `launch_gate` — record of every step in *Launch Gate* (rule_violations summary,
  TestParam.pl exit, PARAM diff path, user approval timestamp, approved-PARAM hash).
* `launch_command` — exact command actually executed (or `"not executed"` with reason).
  For two-PARAM CME cases this expands to a list (start submission, restart submission).
* `job_status_chain` — list of `(timestamp, status, evidence_path)` entries.
* `postproc_plan` — `PostProc.pl` invocation + IDL targets.
* `validation_plan` — references to paper figures or CCMC quick-look targets, mapped to
  local artifacts.
* Explicit separation of **confirmed** vs **inferred** vs **assumed** for every
  decision-altering field.
* `uncertainty.known_unknowns`.

## Anti-pattern guard

The skill must not:

* invent magnetogram URLs, paper-extracted parameters, or cluster commands without
  evidence;
* use `change_param.py` for structural changes (insert `#CME`, reshape sessions,
  reorder commands);
* emit a single merged PARAM for a CME case (use the start+restart pair);
* silently translate spec fields (e.g. spec `FR_type=GL` → PARAM `TypeCme=SPHEROMAK`)
  without surfacing the translation to the user;
* invent values to satisfy a `severity=block` rule — surface the gap instead;
* re-prompt the user for the same `gap` across runs without recording it as a candidate
  YAML entry for `rules/derivations/` or `rules/defaults/`.

## Multi-realization ensembles (Phase 4)

ADAPT magnetograms ship with 12 realization layers. SWMFSOLAR's
`rundir_realizations` Makefile target produces 12 sibling run-dirs
(`run01/` … `run12/`), each with the same PARAM but a realization-specific
`SC/map_NN.out`. The skill orchestrates ensembles via this target — it does
**not** roll its own loop.

* **Assembly**: `make rundir_local MODEL=AWSoMR PFSS=HARMONICS REALIZATIONS=1,...,12`
  (the SWMFSOLAR Makefile fans out the 12 layers).
* **Submission**: `make run MACHINE=<cluster>` from the parent directory
  (per-cluster scheduler logic lives in the Makefile + `JobScripts/`).
  `Scripts/sub_runs.py` is the alternative entrypoint when chunked submission
  or restart loops are needed.
* **Monitoring**: `inspect_artifact(artifact_type="run_dir", path=<SIMDIR>)`
  surfaces a `run_dir_ensemble` finding with per-realization status and an
  aggregate `{completed, killed, in_progress_or_crashed, prepared,
  missing_executable, total}` tally. Use this to drive the next action
  (postproc the completed ones, resubmit the failed ones) without scanning
  each realization individually.
* **Postproc**: `make check_postproc RESDIR=<name>` aggregates successful
  realizations into `Results/${RESDIR}/runNN/`; failures are listed in
  `error_postproc.log`. The agent reads that log to know which realizations
  to retry.
* **Resubmission of failed realizations only**: shell-side. The skill output
  records which realizations need retry and why (cluster signature from the
  log inspector); the agent shells targeted resubmissions rather than
  re-running the full ensemble.

The `swmf-replicate` output's `assembled_run_dir`, `launch_command`, and
`job_status_chain` fields all become **lists** for ensemble runs (one entry
per realization). The launch gate runs once on the shared PARAM.in plus once
per realization-specific `map_NN.out` — gate failures on a single realization
do not block submission of the others, but are recorded.

## Restart workflow (Phase 4)

The canonical restart driver is `SWMF/share/Scripts/Restart.pl`. The skill
surfaces it as the entrypoint and never reimplements restart linking. Two
common scenarios:

1. **Background → eruption (two-PARAM CME)**. After the start PARAM completes
   with `SWMF.SUCCESS`:
   * `inspect_artifact(artifact_type="run_dir", path=<run>)` confirms
     `restart_inventory` shows `SC/restartOUT` and `IH/restartOUT` populated.
   * Either the restart PARAM uses `#INCLUDE RESTART.in` (SWMFSOLAR
     convention) and the framework picks up `SC/restartIN`/`IH/restartIN`
     symlinks automatically, or the agent shells
     `share/Scripts/Restart.pl -i <tree>` to wire them.
   * Swap PARAM.in for the restart variant; resubmit.
2. **Long-run checkpointing**. `share/Scripts/Restart.pl -r=<seconds> -k=<n>`
   rotates `n` restart trees every `<seconds>` of wallclock. The skill does
   not invoke this — the user opts in via the recipe.

The launch gate enforces:

* `restart_inventory.framework` includes `RESTART.in` for the restart-side
  PARAM, **or** the restart PARAM declares `#INCLUDE RESTART.in`.
* `restart_inventory.components` shows non-empty `restartOUT` (background
  side) or `restartIN` (eruption side) directories.

If either check fails, the gate reports `restart_state=missing` and refuses
to launch the eruption submission until the user confirms (or the start
submission is rerun).

## Cluster-boundary recovery (Phase 4)

When a realization crashes on the cluster boundary (walltime exceeded, OOM,
license server hiccup, node failure) rather than on a SWMF-side numerical
issue, `inspect_artifact(artifact_type="log", path=<runlog>)` surfaces a
`cluster_failure_signatures` finding listing one or more of:

* `walltime_exceeded` → `recovery_family=resubmit_with_longer_walltime`
* `oom_killed` → `recovery_family=increase_memory_or_reduce_decomp`
* `module_load_failure` → `recovery_family=fix_module_environment`
* `license_failure` → `recovery_family=license_server_or_compiler_check`
* `mpi_rank_signal` → `recovery_family=investigate_failing_rank`
* `file_quota_exceeded` → `recovery_family=free_disk_or_change_workdir`
* `node_failure` → `recovery_family=resubmit_after_node_drained`
* `signal_term` → `recovery_family=scheduler_terminated_job`

The skill maps each signature to a recovery action *suggestion*, but the
recovery itself is shell-side (resubmit, request more memory, reload module).
MCP only reports — it does not modify the jobscript or resubmit. Hand off to
`swmf-debug` for non-cluster-boundary failures (failure family
`runtime_crash_stop`, `numerical_physics_anomaly`, etc.).

## Phase scope

* **Phase 1** — `intent="prior_run"` end-to-end up to the launch gate (sweep mode).
  Jobscript inspection wired. Rules directory minimal but functional.
* **Phase 2 (current)** — `intent="structured_spec"` end-to-end up to the launch gate.
  CCMC spec parser, magnetogram inspector, and full SOFIE+MFLAMPA recipe + derivations
  + defaults active. Construction-mode authoring fully documented; the agent can take a
  CCMC spec and produce both `PARAM.expand.start` and `PARAM.expand.restart` against
  the gate.
* **Phase 3** — `intent="paper"` end-to-end up to the launch gate via
  `inspect_artifact(artifact_type="paper_spec")`. `swmf-validation` reference
  comparison wired (paper figure / observation trace / CCMC quick-look).
* **Phase 4 (current)** — multi-realization ensemble support
  (`run_dir_ensemble` finding + ensemble-aware launch/monitor/postproc),
  restart workflow integration via `share/Scripts/Restart.pl`, and
  cluster-boundary failure-signature recovery
  (`cluster_failure_signatures` finding driven by the log inspector).

The skill always stops before actual launch in this prototype: the launch gate runs and
reports state, the user reviews the diff and the inferred values, and the agent surfaces
the launch command without executing it.
