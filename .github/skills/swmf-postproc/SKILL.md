---
name: swmf-postproc
description: Use for SWMF postprocessing, output inspection, artifact comparison, and visualization planning. This skill should consume evidence and resources rather than recreate workflow-heavy MCP tools.
---

# SWMF Postproc

## Purpose
Own postprocessing and output interpretation for SWMF.
This skill should help the model inspect outputs, compare artifacts, identify available plotting interfaces, and plan visualization or analysis steps from evidence.

## Use This Skill For
- Understanding run outputs and artifact layout
- Comparing outputs across runs or revisions
- Planning analysis and visualization steps
- Inspecting available IDL procedures and output-related source references
- Narrowing postprocessing failures before handing off to Debug

## Boundaries
- Do not recreate a large postprocess execution tool surface.
- Prefer resource lookup and evidence collection over command synthesis.
- If the request becomes a failure investigation, hand off to `swmf-debug`.

## Request Families
- `output_inventory`
- `artifact_comparison`
- `visualization_planning`
- `postprocess_failure_triage`

## MCP Evidence Map
- `swmf_collect_run_context`
- `swmf_compare_run_artifacts`
- `swmf_extract_first_error`
- `swmf_extract_stacktrace`
- `swmf_search_source`
- `swmf://idl/procedures`
- `swmf://idl/{procedure}`
- `swmf://examples/{name}`
- `swmf://knowledge/symbol/{name}`

## Process
1. Determine whether the request is about output layout, comparison, visualization, or failure triage.
2. Collect run/output evidence first.
3. Use IDL and example resources to ground any visualization advice.
4. Keep planning grounded in available artifacts and indexed procedures.

## Output Contract
Always include:
- `postproc_family`
- `available_artifacts`
- `comparison_findings` when relevant
- `visualization_evidence`
- `missing_inputs`
- `next_steps`

## Collaboration Rules
- Ask `swmf-debug` for error diagnosis or ambiguous failures.
- Ask `swmf-build-run` for run-environment context when output layout depends on setup choices.
- Ask `swmf-implementation` when the user wants to add new diagnostics or output behavior.
- Ask `swmf-param-specialist` when visualization expectations depend on PARAM-controlled output settings.

## Anti-patterns
- Do not claim a visualization workflow exists without resource or source evidence.
- Do not infer runtime correctness from plots alone when artifacts disagree.
- Do not treat postprocessing output shape as proof of physical correctness.