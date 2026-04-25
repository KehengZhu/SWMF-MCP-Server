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
* IDL snapshot, log, animation, transform, slicing, and graphics-export workflows
* coupling architecture explanation and Mermaid diagrams
* output artifact layout and interpretation context
* postprocessing failure triage (before handing off to `swmf-debug`)

Not in scope: general failure diagnosis, PARAM semantics, build/run workflow.

## Immediate Load Rules

If the request mentions IDL plotting, `read_data`, `plot_data`, `plot_func`,
`show_data`, `animate_data`, `plotmode`, `func`, IDL log plotting, graphics
export, or asks to list plotting procedures:
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
Prefer an existing extracted run directory over an archive when both are
present. For `Run_Max_RP_CME3`, use `SWMFSOLAR/Run_Max_RP_CME3/run01`; treat
`Run_Max_RP_CME3.tar.gz` only as a fallback/source archive.
Run-dir inspection now includes concise PARAM-derived run-intent evidence
(session timeline, control settings, and `#SAVEPLOT` essentials) and should be
used before inferring IDL plotting cadence.

For IDL procedures:
```
get_evidence(query=<procedure-or-task>, mode="keyword", goal="IDL procedure signature and usage")
```
For IDL workflow detail:
```
get_evidence(query=<func/plotmode/transform/export term>, mode="keyword", goal="IDL visualization manual detail")
```
If a run directory or output file is named:
```
inspect_artifact(artifact_type="run_dir"|"result", path=<path>)
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
Do not directly read whole runlogs unless the user explicitly requests raw log
content; after inspection, use only bounded excerpts needed to verify findings.
If conflicting evidence → hand off to `swmf-debug`.

## Authority Order

1. Direct tool output tied to source files or runtime artifacts
2. Deterministic IDL catalog evidence returned by `get_evidence`
3. Direct source/doc reads from `share/IDL`, `docs/idl.md`, coupling sources, output artifacts named by v2 tools
4. Heuristic source evidence

Never let heuristic search override direct v2 artifact evidence.
For coupling precision follow-up:
```
get_evidence(mode="keyword", goal="coupling registry detail")
```
Use only the files or symbols named by the v2 result for any direct reads.
