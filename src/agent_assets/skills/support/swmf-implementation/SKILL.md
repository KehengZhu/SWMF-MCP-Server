---
name: swmf-implementation
type: support
description: "Support skill. Handles source-level change preparation: invariant context, affected symbols, validation plan, patch-readiness gate. Called by swmf-debug and swmf-configure when a code change is needed."
---

# swmf-implementation (Support)

This is a **support skill**. It is not chosen directly by the agent.
`swmf-debug` consults it when a source patch is needed.
`swmf-configure` consults it when a PARAM or source behavior change is requested.

## Purpose

Prepare source-level changes safely: gather evidence, build invariant context,
define validation plan, and enforce patch-readiness gate before any edits.

## Scope

* affected source files and symbols
* invariant context for data structures
* validation artifacts and comparison path
* patch-readiness gate

Not in scope: failure diagnosis (that is `swmf-debug`), PARAM semantics
(that is `swmf-params`), workflow execution (that is `swmf-run`).

## Required Preconditions Before Editing

1. User intent is specific enough to identify the behavior to change.
2. Affected source files or symbols are identified (from `swmf get-evidence`).
3. Invariant context exists from swmf CLI evidence, artifact inspection, and named
   source reads after the swmf CLI gate.
4. Validation artifacts are identified.
5. At least one rollback-safe comparison path exists.

## Tool Protocol

```bash
swmf get-context --task-type architecture
```
Only when the affected surface is broad or ambiguous.

```bash
swmf get-evidence --mode keyword --goal "source context for <change>"
```
For exact source files and surrounding interfaces.

```bash
swmf inspect --type param|run_dir --path ...
```
For relevant PARAM.in or run directory context.

Precision follow-up:
* `swmf get-evidence --mode keyword --goal "invariant-sensitive symbols and interfaces"`
  for exact source symbols and nearby interfaces
* `swmf inspect --type param --question "PARAM implications for this change"`
  when PARAM side effects matter
* direct source reads only for files explicitly named by the swmf CLI output

## Output Contract

* `requested_behavior`
* `affected_symbols_or_files`
* `invariant_block`
* `validation_plan`
* `patch_readiness` (true only when all preconditions are met)

## Guardrails

* Do not patch before invariant context exists.
* Do not accept heuristic search as the only evidence for a source change.
* Do not treat a requested behavior as complete until validation evidence is defined.
