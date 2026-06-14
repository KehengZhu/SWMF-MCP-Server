---
name: swmf-architecture
type: support
description: "Support skill. Answers questions about SWMF component roles, coupling relationships, control flow, and system-level architecture. Called by swmf-explain and sometimes swmf-debug."
---

# swmf-architecture (Support)

This is a **support skill**. It is not chosen directly by the agent.
`swmf-explain` (and rarely `swmf-debug`) consult it for architecture questions.

## Purpose

Answer one thing: how SWMF components relate, couple, and interact at the
system level.

## Scope

* component roles and responsibilities
* coupling pairs and coupling mechanism (CON timing, shared variables)
* control flow between components
* architecture summaries

Not in scope: PARAM semantics, build steps, failure diagnosis.

## Tool Protocol

```bash
swmf get-context \
  --question "<architecture question>" \
  --scope <components if named> \
  --task-type architecture \
  --detail normal   # use "deep" for multi-component ambiguous questions
```

Then for each key entity returned:
```bash
swmf get-evidence \
  --query "<entity>" \
  --mode hybrid \
  --scope <component> \
  --top-k 8 \
  --goal "architecture explanation"
```

Precision follow-up:
* `swmf get-evidence --mode keyword --goal "coupling registry detail"` on the specific
  coupling symbols or files returned by `swmf get-context`
* direct source reads only for files named by the swmf CLI output

## Output Contract

* component roles cited from evidence
* coupling mechanism named and evidence path cited
* confirmed claims separated from inferred claims
* `uncertainty.known_unknowns` surfaced when present
