---
name: swmf-postproc
description: Use for SWMF postprocessing, output inspection, artifact comparison, and visualization planning. This skill should consume evidence and resources rather than recreate workflow-heavy MCP tools.
---

# SWMF Postproc

## Purpose
Own postprocessing and output interpretation for SWMF.
This skill should help the model inspect outputs, compare artifacts, identify available plotting interfaces, and plan visualization or analysis steps from evidence.

`SKILL.md` is the entry router for this skill. For request-specific discipline, it must explicitly load the companion playbooks listed below before answering.

## Immediate Load Rules
If the request mentions IDL plotting, animation, procedures, `plot_data`, `plot_func`, `show_data`, `read_data`, or asks to list plotting procedures:
- Read `IDL_VISUALIZATION.md`
- Read `TOOL_ROUTING.md`
- Read `ANSWER_CONTRACTS.md`

If the request mentions coupling, couplers, component relationships, architecture, or asks for a Mermaid diagram of SWMF relationships:
- Read `COUPLING_ARCHITECTURE.md`
- Read `TOOL_ROUTING.md`
- Read `ANSWER_CONTRACTS.md`

If the request becomes failure-driven, ambiguous, or evidence from plots conflicts with logs or raw artifacts:
- Hand off to `swmf-debug`

## Use This Skill For
- Understanding run outputs and artifact layout
- Comparing outputs across runs or revisions
- Planning analysis and visualization steps
- Inspecting available IDL procedures and output-related source references
- Explaining authoritative IDL plotting interfaces and examples
- Explaining SWMF component coupling architecture from evidence
- Narrowing postprocessing failures before handing off to Debug

## Boundaries
- Do not recreate a large postprocess execution tool surface.
- Prefer resource lookup and evidence collection over command synthesis.
- Do not use heuristic source search as the first tool for IDL visualization questions when authoritative IDL catalog tools exist.
- Do not treat lexical IDL categories as final truth without checking whether a symbol is an entry point or helper.
- Do not answer broad coupling questions as build or run readiness questions.
- If the request becomes a failure investigation, hand off to `swmf-debug`.

## Request Families
- `output_inventory`
- `artifact_comparison`
- `visualization_planning`
- `idl_inventory`
- `idl_usage_guidance`
- `coupling_architecture_explanation`
- `postprocess_failure_triage`

## MCP Evidence Map
### Deterministic and authoritative tools
- `swmf_collect_run_context`
- `swmf_compare_run_artifacts`
- `swmf_list_idl_procedures`
- `swmf_explain_idl_procedure`
- `swmf_get_coupling_info`
- `swmf_find_examples`

### Supporting or heuristic tools
- `swmf_search_source`
- `swmf_lookup_source_symbol`
- `swmf_extract_first_error`
- `swmf_extract_stacktrace`

## Authority Discipline
When working under this skill, use this authority order unless a companion playbook narrows it further:
1. Direct tool output tied to source files or runtime artifacts
2. Resource-backed IDL catalog results
3. Direct source/doc reads from `share/IDL`, coupling sources, or output artifacts
4. Heuristic source search results

Rules:
- Never let heuristic search override direct IDL catalog evidence.
- Never present helper routines as primary visualization entry points without labeling them as helpers.
- Always distinguish `entry_points` from `helpers_or_supporting_routines` for IDL inventory answers.
- Always distinguish `registry_components`, `implemented_dispatch_links`, and `runtime_enablement_notes` for coupling answers.

## Process
1. Classify the request into one of the request families above.
2. Apply the Immediate Load Rules before using tools for IDL or coupling questions.
3. Use `TOOL_ROUTING.md` to select the allowed first tool for the family.
4. Collect authoritative evidence first, then add heuristic evidence only if needed.
5. Use `ANSWER_CONTRACTS.md` to shape the final response.
6. If evidence conflicts or the question turns into diagnosis, hand off to `swmf-debug`.

## Output Contract
Always include:
- `postproc_family`
- `available_artifacts`
- `comparison_findings` when relevant
- `visualization_evidence`
- `missing_inputs`
- `next_steps`

For IDL inventory, IDL usage, and coupling answers, the companion file `ANSWER_CONTRACTS.md` defines additional required sections and labels.

## Collaboration Rules
- Ask `swmf-debug` for error diagnosis or ambiguous failures.
- Ask `swmf-build-run` for run-environment context when output layout depends on setup choices.
- Ask `swmf-implementation` when the user wants to add new diagnostics or output behavior.
- Ask `swmf-param-specialist` when visualization expectations depend on PARAM-controlled output settings.

## Anti-patterns
- Do not claim a visualization workflow exists without resource or source evidence.
- Do not infer runtime correctness from plots alone when artifacts disagree.
- Do not treat postprocessing output shape as proof of physical correctness.
- Do not call `swmf_list_idl_procedures` without a category filter and then shell-parse a giant output blob if the question is specifically about plotting procedures.
- Do not retry zero-result heuristic searches with minor wording changes before checking the authoritative catalog, docs, or example files.
- Do not collapse coupling registry, dispatch implementation, and runtime enablement into one undifferentiated diagram.