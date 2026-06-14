---
name: swmf-swmfsolar
type: support
description: "Support skill. Owns the SWMFSOLAR project as the canonical operational driver: Makefile targets, Scripts/, JobScripts/, Param/, ParamListScripts/. Loaded by swmf-replicate, swmf-build, and swmf-run when an AWSoM/SOFIE/CME workflow is in scope."
---

# swmf-swmfsolar (Support)

This is a **support skill**. `swmf-replicate`, `swmf-build`, and `swmf-run` consult it
when the operational machinery for solar/CME runs is in scope. The skill exists so the
agent does not rediscover SWMFSOLAR via `swmf get-evidence` on every call.

## Purpose

Answer one thing: which SWMFSOLAR Makefile target, Script, JobScript, or Param template
handles the request, and what are its required arguments and known constraints.

## Scope

* **Makefile targets** (`SWMFSOLAR/Makefile`):
  * `compile`, `adapt_run_w_compile`, `adapt_run` — build + first run.
  * `rundir_local`, `rundir_realizations` — assemble run directories.
  * `run` — submit (after `rundir_*`).
  * `check_postproc`, `check_compare_*` — postprocess + compare to references.
* **Scripts** (`SWMFSOLAR/Scripts/`):
  * `change_awsom_param.py` — magnetogram alignment, ADAPT realization handling. Use
    this rather than rolling your own `#STARTTIME`/Carrington arithmetic.
  * `change_param.py` — pure template-fill: `add_commands`, `remove_commands`,
    `replace_commands`, `change_param_value`. **Sweep mode only**; cannot insert blocks
    that aren't already in the template.
  * `download_ADAPT.py` — FTP fetch for ADAPT FITS bundles.
  * `sub_runs.py` — multi-realization submission orchestration.
  * `watch_runlog.py` — periodic monitor; surfaces progress and detect failure.
  * `compare_insitu.py` — observation comparison helper.
* **`JobScripts/`** — per-cluster templates, drives `swmf-jobscript`.
* **`Param/`** — canonical PARAM templates, drives `swmf-replicate` template selection.
* **`ParamListScripts/`** — sweep configurations.
* **`Run_Max_*` directories** — anchored prior runs.

Not in scope: building SWMF directly (defer to `swmf-build`); arbitrary Python script
debugging; cluster submission credentials.

## Tool Protocol

1. `swmf get-evidence --query "<task>" --task-type configuration|run|analysis --goal "SWMFSOLAR entrypoint"`
   — to discover which Makefile target or Script handles the request.
2. `swmf inspect --type param --path SWMFSOLAR/Param/<template> --check-rules`
   — when comparing a template against the current rules.
3. `swmf inspect --type jobscript --path SWMFSOLAR/JobScripts/<file>`
   — for cluster submission templates.
4. Direct reads only of files named by evidence.

## Authority Order

1. `SWMFSOLAR/Makefile` (when the agent is checking what target a `make` invocation
   maps to).
2. Script `--help` / argparse help text via `swmf get-evidence`.
3. `SWMFSOLAR/README` and `SWMFSOLAR/Prompts.txt` for narrative context (lower
   authority; cite explicitly).
4. Path-pattern inference (lowest authority; surface as `inferred`).

## Output Contract

* `entrypoint` — Makefile target or Script path.
* `entrypoint_kind` — `make` | `script` | `jobscript` | `template` | `param_list`.
* `arguments` — required arguments with brief descriptions when extractable from
  `--help`.
* `constraints` — known limitations (e.g. `change_param.py` sweep-only).
* `evidence_paths` — files cited.
* `version_drift_warning` — `True` whenever the Makefile target the agent suggests
  cannot be located in the current `SWMFSOLAR/Makefile`. Flagged so the user can pin a
  newer/older SWMFSOLAR checkout.

## Quick reference (evidence pointers, not advice)

* Build + run-dir for AWSoM steady state: `make compile`, then `make rundir_local`.
* Build + run-dir for ADAPT realization sweep: `make adapt_run` (handles 1..12 ADAPT
  layers via `change_awsom_param.py`).
* Submit: `make run` or, for explicit cluster submission, `sbatch <jobscript>`.
* Postprocess + compare: `make check_postproc RESDIR=<name>` then
  `make check_compare_*`.

## Multi-realization ensemble (Phase 4)

A 12-realization ADAPT ensemble is produced by `rundir_realizations` as
sibling directories `${SIMDIR}/run01/`, `run02/`, …, `run12/`. The Makefile
chain is:

* `make rundir_local` — calls `rundir_realizations` after `change_awsom_param.py`
  and `copy_param`. Each `runNN/` gets `PARAM.in`, `SC/HARMONICS.in`,
  `SC/FDIPS.in`, `job.long`, and the realization-specific `map_NN.out`.
* `make run` — iterates the realization list and submits each `job.long`
  (`sbatch` on Frontera/Derecho, `qsub`/`./qsub.pfe.pbspl.pl` on Pleiades).
* `Scripts/sub_runs.py` — alternative submission orchestrator with finer
  control (chunked submissions, restart loops). The skill defers there for
  non-default submission patterns.
* `make check_postproc RESDIR=<name>` — aggregates `runNN/SWMF.SUCCESS` runs
  into `Results/${RESDIR}/runNN/`; failed realizations are appended to
  `error_postproc.log`. The agent reads that log to know which realizations
  to resubmit without re-running the whole ensemble.

Inspection: `swmf inspect --type run_dir --path <SIMDIR>` surfaces
a `run_dir_ensemble` finding when ≥2 `runNN/` siblings are present. The
finding carries `realization_count`, per-realization status (`completed` |
`killed` | `in_progress_or_crashed` | `prepared` | `missing_executable`), and
an aggregate count tally. Use this to monitor a 12-realization run without
shelling each `runNN/` individually.

## Restart workflow (Phase 4)

The canonical SWMF restart driver is **`SWMF/share/Scripts/Restart.pl`**, not a
SWMFSOLAR-local script. Surface it as the entrypoint when the user asks about
restart. Common modes:

* `Restart.pl -c` — check restart files exist and are consistent.
* `Restart.pl -i <restart_tree>` — link restart files **in** before submission
  (steady-state → eruption transition for CME runs).
* `Restart.pl -o <restart_tree>` — collect a restart **out** snapshot tree.
* `Restart.pl -r=<seconds> -k=<n>` — repeat mode: keep `n` restart trees,
  rotate every `<seconds>`. Used for long runs where the user wants periodic
  checkpoints without filesystem blow-up.

For two-PARAM CME cases (background → eruption), the workflow is:

1. Submit start PARAM (steady-state). Wait for `SWMF.SUCCESS`.
2. Confirm `SC/restartOUT/` and `IH/restartOUT/` populated.
3. `Restart.pl -i SC/restartOUT IH/restartOUT` to wire them as restart input
   for the next session (or rely on `#INCLUDE RESTART.in` in the restart
   PARAM, which is the SWMFSOLAR convention).
4. Swap PARAM.in for the eruption variant. Resubmit.

The `swmf-replicate` launch gate enforces step 2 (it reads
`restart_inventory` from the run-dir inspector); steps 3–4 are agent shell
calls.

## Anti-patterns

* Do not hardcode SWMFSOLAR Makefile rules inside skill prose; cite the Makefile target
  and let the agent run `make`.
* Do not reimplement `download_ADAPT.py` inside the swmf CLI. Network calls and retries belong in
  the shell.
* Do not assume a specific Makefile target name across SWMFSOLAR versions; surface the
  evidence path so the user can verify, and set `version_drift_warning=True` when the
  expected target is absent.
* Do not silently switch between AWSoM and AWSoM-R variants; the build flags differ
  (`u=Awsom` vs `u=AwsomR`) and the choice belongs to the spec or the recipe.
