---
name: swmf-postproc
type: support
description: "Support skill. Provides deep postprocessing knowledge: IDL visualization, coupling architecture, output artifact inspection. Called by swmf-analyze and swmf-compare."
---

# swmf-postproc (Support)

This is a **support skill**. Entry skills `swmf-analyze` and `swmf-compare`
consult it for IDL visualization, coupling architecture, and output artifacts.

## Purpose

Provide specialized postprocessing knowledge that entry skills need but do not
own directly.

## Scope

* IDL procedure discovery and usage guidance
* coupling architecture explanation and Mermaid diagrams
* output artifact layout and interpretation context
* postprocessing failure triage (before handing off to `swmf-debug`)

Not in scope: general failure diagnosis, PARAM semantics, build/run workflow.

## Immediate Load Rules

If the request mentions IDL plotting, `plot_data`, `plot_func`, `show_data`,
`read_data`, or asks to list plotting procedures:
- Read `IDL_VISUALIZATION.md`
- Read `ANSWER_CONTRACTS.md`

If the request mentions coupling, couplers, component relationships, or asks
for a Mermaid diagram:
- Read `COUPLING_ARCHITECTURE.md`
- Read `ANSWER_CONTRACTS.md`

## Tool Protocol

For output inventory:
```
inspect_artifact(artifact_type="run_dir", path=<run_dir>)
```

For IDL procedures:
```
get_evidence(mode="keyword", goal="IDL procedure signature and usage")
```
Precision follow-up:
```
get_evidence(mode="keyword", goal="IDL procedure detail or category narrowing")
```
Use only the files or procedures named by the v2 result for any direct reads.

For coupling architecture:
```
get_context(question=<coupling question>, task_type="architecture")
```
Precision follow-up:
```
get_evidence(mode="keyword", goal="coupling registry detail")
```
Use only the files or symbols named by the v2 result for any direct reads.

For postprocess failure:
```
inspect_artifact(artifact_type="log"|"run_dir", path=...)
```
If conflicting evidence → hand off to `swmf-debug`.

## Authority Order

1. Direct tool output tied to source files or runtime artifacts
2. Direct source/doc reads from `share/IDL`, coupling sources, output artifacts named by v2 tools
3. Heuristic source evidence

Never let heuristic search override direct v2 artifact evidence.
For coupling precision follow-up:
```
get_evidence(mode="keyword", goal="coupling registry detail")
```
Use only the files or symbols named by the v2 result for any direct reads.
