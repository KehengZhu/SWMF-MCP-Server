---
name: swmf-analyze
description: "Use when the user wants to interpret SWMF outputs: what results mean, diagnostics from output files, field interpretation, or postprocessing workflow guidance."
---

# swmf-analyze

## When to use
- "What do these output files contain?"
- "How do I plot the result?"
- "What does this field value mean?"
- "How do I run the postprocessing?"
- "Are my results physically reasonable?"
- Any task about reading, interpreting, or processing simulation outputs

## Do not use when
- User wants to compare two runs → `swmf-compare`
- Something failed → `swmf-debug`
- User wants to configure → `swmf-configure`
- User wants to run → `swmf-run`

## Evidence order

1. `inspect_artifact(artifact_type="run_dir", path=<run_dir>)`
   — output file inventory and layout
2. `get_evidence(mode="keyword", goal="output format or field definition")`
   — field semantics, output variable definitions
3. `get_workflow_guidance(goal="postprocessing", task_type="analysis")`
   — postprocessing scripts and entrypoints

## Helper skills allowed

* `swmf-postproc` — for IDL visualization details and coupling architecture context
* `swmf-exact-lookup` — for specific field name or procedure confirmation

## Outputs

* what output artifacts were found (from `inspect_artifact`)
* field/variable definitions cited from evidence
* postprocessing entrypoints with `relative_path`
* what is certain vs uncertain about the interpretation
* for IDL: load `swmf-postproc/IDL_VISUALIZATION.md` for full protocol
