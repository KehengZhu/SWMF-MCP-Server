---
name: swmf-jobscript
type: support
description: "Support skill. Owns scheduler-aware policy for SWMF job scripts (SLURM on Frontera/local, PBS on Pleiades/Derecho, plain mpirun for laptops). Loaded by swmf-run and swmf-replicate."
---

# swmf-jobscript (Support)

This is a **support skill**. It is not chosen directly by the agent. `swmf-run` and
`swmf-replicate` consult it when a candidate job script is in scope, or when picking a
jobscript template for a target cluster.

## Purpose

Answer one thing: given a job script (or a cluster name), what does the scheduler
actually request — nodes, tasks-per-node, walltime, executable invocations, postproc
hooks, FDIPS/HARMONICS pre-stage — and what placeholders need substitution before
submission.

## Scope

* SLURM directives (`#SBATCH`) and PBS directives (`#PBS`).
* MPI launchers (`ibrun`, `mpirun`, `mpiexec`, `srun`, `aprun`) and their executable
  arguments.
* Pre-stage executables (`FDIPS.exe`, `HARMONICS.exe`).
* Postprocessing hook (`PostProc.pl` invocation, `PostProc.STOP` marker).
* Substitution placeholders (`{{...}}`, `<PLACEHOLDER>`, `amapNN` job-name patterns,
  `JOBNAME`, `RUNTIME`, `ALLOCATION`).

Not in scope: PARAM validation, build orchestration, runtime debugging.

## Tool Protocol

For one named jobscript:

```bash
swmf inspect --type jobscript --path <jobscript_path>
```

For discovering candidate templates by cluster:

```bash
swmf get-evidence --query "job script <cluster>" --task-type run --goal "cluster submission template"
```

The skill calls inspect first and `swmf get-evidence` only when no candidate is named.

## Authority Order

1. `swmf inspect --type jobscript` — deterministic parse of the file.
2. `swmf get-evidence --task-type run` — discovery of templates and conventions.
3. `swmf-swmfsolar` (Phase 2) — for canonical Makefile/JobScripts dependencies.

Never let `swmf get-evidence` override `swmf inspect` for a file the user actually has.

## Output Contract

* `scheduler` — one of `slurm | pbs | local | unknown`.
* `directives` — list of `{key, value, line, raw}` entries verbatim from the script.
* `nodes`, `tasks_per_node`, `total_ranks`, `walltime` — typed dimensional fields.
* `executable_invocations` — ordered list of `{line, launcher, executable, nproc,
  rank_offset, raw}`. Order matters: a CME run typically pre-stages FDIPS, then runs
  PostProc.pl on rank 0, then SWMF.exe on the remaining ranks.
* `swmf_invoked`, `fdips_invoked`, `harmonics_invoked`, `postproc_present` — booleans.
* `substitution_tokens` — placeholder names the user must replace before submitting.
* `evidence_paths` — the inspected file plus any evidence items returned by
  `swmf get-evidence` calls.
* `verified_claims` vs `unverified_claims`.

## Cluster cheatsheet (evidence pointers, not advice)

The skill answers each as a cited pointer rather than a recipe:

* Frontera (TACC): SLURM, `ibrun` launcher with `-n` and `-o` rank offsets. See
  `SWMFSOLAR/JobScripts/job.FDIPS.frontera`.
* Pleiades (NASA): PBS, `mpiexec`. See `SWMFSOLAR/JobScripts/job.FDIPS.pfe`.
* Derecho (NCAR): PBS, intel module quirks. See
  `SWMFSOLAR/JobScripts/job.FDIPS.derecho`.
* Local: plain `mpirun -np <N> ./SWMF.exe > runlog`.

## Anti-patterns

* Do not invent `#SBATCH` or `#PBS` directives the inspector did not return.
* Do not collapse the executable order; SWMF runs after FDIPS pre-stage and PostProc
  on rank 0.
* Do not silently substitute placeholders. Surface them and ask the user.
