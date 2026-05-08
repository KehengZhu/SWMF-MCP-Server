---
name: swmf-validation
type: support
description: "Support skill for validating a SWMF run against an external reference (paper figure, observation trace, CCMC quick-look). Loaded by swmf-replicate, swmf-analyze, and swmf-compare when one side is a reference rather than another SWMF artifact."
---

# swmf-validation (Support)

`swmf-replicate`, `swmf-analyze`, and `swmf-compare` consult this skill whenever
one side of a comparison is a **reference** — a paper figure, an observation
trace (OMNI / STEREO / DSCOVR), a CCMC quick-look panel — rather than another
SWMF artifact. It does not compare runs against each other; that is
`swmf-compare` with `compare_artifacts(comparison_type="run_dir"|"result"|"log")`.

## When to use

* "Does my run match Figure 6 of Sokolov 2023?"
* "Compare the modeled L1 density against OMNI for 2023-02-24."
* "Does this LASCO C2 base-difference movie agree with the CCMC quick-look?"
* "Validate the MFLAMPA flux against the SEPMOD reference panel."
* Any request where the user names a paper, observation source, or CCMC quick-look
  as the comparison target.

## Do not use when

* Both sides are SWMF runs → `swmf-compare`.
* User wants postprocessing/IDL rendering with no reference comparison → `swmf-postproc`.
* Failure-mode investigation → `swmf-debug`.
* User asks how to set up the run → `swmf-replicate` (validation runs after the run completes).

## Inputs (from agent intake)

* Reference descriptor: paper figure (paper path + figure id), observation source
  (instrument/spacecraft + time range), or CCMC quick-look path/URL.
* Modeled run directory.
* Optional: numerical metric requested (RMSE, correlation), spatial/temporal slice
  the comparison should target.

## Evidence order

1. **Run output inventory** — discover what the modeled run produced:
   ```
   inspect_artifact(artifact_type="run_dir", path=<modeled_run>)
   ```
   Read `component_output_artifacts` to see which `#SAVEPLOT` groups landed
   on disk. The agent maps the reference target (e.g. "LASCO C2 base difference")
   to the corresponding SC IDL plot group.

2. **Per-output inspection** — for each candidate modeled output:
   ```
   inspect_artifact(artifact_type="result", path=<modeled_output_file>)
   ```
   Surface the file format, header variables, snapshot count.

3. **Reference-side inspection (when the reference is also a SWMF-typed artifact)** —
   e.g. the CCMC delivered a `Run information_CCMC.md` plus matching IDL output
   files, or another run directory shipped with the paper:
   ```
   inspect_artifact(artifact_type="ccmc_spec", path=<ref_spec>)
   inspect_artifact(artifact_type="result",    path=<ref_idl_out>)
   inspect_artifact(artifact_type="run_dir",   path=<ref_run_dir>)
   compare_artifacts(comparison_type="result"|"log"|"run_dir",
                     left=<reference>, right=<modeled>)
   ```
   `compare_artifacts(comparison_type="run_dir")` already returns a `param_diff`
   block when both sides have `PARAM.in`; surface that before falling back to
   file-list deltas.

4. **Paper-spec or paper_spec normalization** — when the reference is a paper:
   ```
   inspect_artifact(artifact_type="paper_spec", path=<paper_spec.json>)
   ```
   Use `paper_spec_summary` to identify named figures/diagnostics; treat
   `confidence_per_field` as the priority order for what to validate first.

5. **Observation-trace comparison** — when the reference is an in-situ trace
   (OMNI, STEREO, DSCOVR, ACE):
   * The agent shells SWMFSOLAR's `Scripts/compare_insitu.py` (loaded via
     `swmf-swmfsolar`) — that script owns the OMNI download and overlay.
   * If a numerical metric is requested, compute it from the resulting CSV/IDL
     trace; do not put metric arithmetic in MCP.

6. **IDL rendering hand-off** — for any visual side-by-side:
   ```
   (route through swmf-postproc)
   ```
   `swmf-postproc` owns the IDL `.pro` workflow and the comparison/transform/
   overplot policy. Do not invent IDL commands here.

## Validation methods (allowed `comparison_method` values)

* `deterministic_diff` — both sides are SWMF-typed artifacts (run_dir / result /
   log) and `compare_artifacts` produced a structural diff. The lowest-judgment
   class.
* `numerical_metric` — a defined scalar (RMSE on density at L1, peak-arrival
   delta in hours, integrated SEP fluence ratio). Computed by the agent (or
   `compare_insitu.py`); MCP does not adjudicate.
* `idl_overlay` — `swmf-postproc` produced a side-by-side panel/animation.
   The user confirms the visual match; the skill records `pending_user_review`
   until they do.
* `user_visual_confirmation` — paper figure / quick-look case where no numerical
   metric exists. Skill emits a side-by-side and waits for the user to mark
   `matched` or `divergent`. Never auto-classified.

## Output contract

For each validation target the skill returns:

* `target_id` — short label (e.g. `lasco_c2_base_diff`, `omni_density_l1`).
* `reference_artifact` — `{kind: "paper_figure"|"observation_trace"|"ccmc_quicklook"|"run_artifact",
  path_or_descriptor: str, identifier: str}`. For paper figures the identifier
  is the paper figure number; for observations it is the instrument/time range.
* `modeled_artifact` — `{path: <run-local path>, kind: <SAVEPLOT group | log | postproc bundle>}`.
* `comparison_method` — one of `deterministic_diff | numerical_metric | idl_overlay |
  user_visual_confirmation`.
* `result` — one of `matched | divergent | pending_user_review`. `matched` and
  `divergent` carry a short notes field; `pending_user_review` is the default
  for visual methods until the user adjudicates.
* `metric` — when `comparison_method=numerical_metric`, includes
  `{name, value, units, threshold, passed}`.
* `evidence_paths` — file paths inspected on each side (modeled + reference).
* `provenance_lane` — `confirmed | inferred | assumed`, mirroring the
  `swmf-replicate` output contract so a paper-derived target can be traced back
  to the spec field that drove it.
* `uncertainty.known_unknowns` — explicit list (instrument calibration drift,
   missing OMNI coverage, paper-figure resolution).

The skill must aggregate per-target results into a single object with a
`summary` ("3 matched, 1 divergent, 2 pending_user_review") so the entry skill
(`swmf-replicate` / `swmf-analyze` / `swmf-compare`) can present a single
status block.

## Boundary (carry forward from §4.3.3)

This skill does **not** classify a paper figure as "matched" by image
inspection alone. It drives an IDL-rendered local equivalent and asks the
user to confirm visually unless a numerical metric is available.

`compare_artifacts(comparison_type="reference")` does **not** exist in the
public MCP surface (rejected in plan §5.1). Reference comparison crosses
domains (image ↔ observation trace ↔ simulated trace) and is judgmental;
keeping it skill-side preserves the deterministic-MCP boundary.

## Helper skills allowed

* `swmf-postproc` — for any IDL rendering / overlay / animation work.
* `swmf-swmfsolar` — for `compare_insitu.py` and other OMNI/STEREO comparison
  scripts.
* `swmf-analyze` — for output structure interpretation when the run is the
  side under question.
* `swmf-compare` — when the reference is itself a SWMF artifact (e.g. a CCMC-
  shipped run directory).

## Anti-patterns

* **Image-similarity-as-deterministic-evidence.** Do not claim a paper-figure
  match by image hashing. Visual comparison is presented to the user.
* **Re-implementing OMNI download.** SWMFSOLAR `compare_insitu.py` already
  owns the in-situ comparison pipeline; defer there via `swmf-swmfsolar`.
* **MCP-as-reference-fetcher.** Network I/O for paper PDFs, OMNI series, or
  CCMC quick-looks is shell-side. MCP only inspects the resulting local files.
* **Silently dropping low-confidence paper fields.** Every `paper_spec` field
  with low `confidence_per_field` carries into the validation output as a
  `provenance_lane=inferred` target with `uncertainty.known_unknowns` populated;
  it does not vanish because the score was low.
* **Auto-classifying `pending_user_review` as `matched`.** A visual method
  stays `pending_user_review` until the user explicitly says it matched.
