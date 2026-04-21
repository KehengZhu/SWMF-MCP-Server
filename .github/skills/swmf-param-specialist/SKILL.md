---
name: swmf-param-specialist
description: "Use for any SWMF PARAM.in request: command meaning, schema interpretation, validation, include resolution, external inputs, component maps, and disagreements between PARAM.XML and source behavior."
---

# SWMF Param.in Specialist

## Purpose
Own PARAM.in understanding for SWMF.
This skill should answer what a command means, whether a PARAM file is structurally valid,
which external files are required, and where schema behavior and source behavior diverge.

## Use This Skill For
- Explaining a PARAM command or component setting
- Validating PARAM structure and external inputs
- Resolving `#INCLUDE` chains and `#COMPONENTMAP`
- Comparing PARAM.XML schema against source evidence
- Turning colleague knowledge into stable PARAM facts later

## First Classification
Classify the request into one of these Param families before answering:
- `command_definition`
- `file_validation`
- `include_or_reference_resolution`
- `component_layout`
- `schema_vs_source_behavior`
- `example_lookup`

State the family explicitly at the start of the answer.

## Evidence Workflow
1. Gather authoritative schema or structure evidence first.
2. Only then gather heuristic source evidence when the request asks about runtime behavior.
3. Keep schema claims and source-behavior claims separate.
4. If execution-sensitive validation matters, use the authoritative validator.

## MCP Evidence Map

### Authoritative or deterministic tools
- `swmf_explain_param`
- `swmf_validate_param`
- `swmf_run_testparam`
- `swmf_validate_external_inputs`
- `swmf_collect_param_context`
- `swmf_resolve_param_includes`
- `swmf_extract_component_map`

### Reference tools
- `swmf_get_param_schema`
- `swmf_get_param_command`
- `swmf_get_param_trace`
- `swmf_find_examples`
- `swmf_get_component`
- `swmf_list_components`

### Heuristic source evidence
- `swmf_search_source`
- `swmf_lookup_source_symbol`
- `swmf_get_knowledge_index_status`

## Authority Discipline
Authority tiers for this skill:
1. Verbatim source context and direct tool output tied to a file/line
2. `TestParam.pl` validation output
3. `PARAM.XML` schema and resource-backed command metadata
4. Deterministic MCP parsing output (`validate_param`, `collect_param_context`, `extract_component_map`)
5. Heuristic source search results
6. Human notes and examples

Rules:
- Never let heuristic search override `TestParam.pl` or `PARAM.XML`.
- Never claim a PARAM command is accepted at runtime from search evidence alone.
- When schema and source differ, report both explicitly as `schema_contract` and `source_behavior_evidence`.

## Output Contract
Always include:
- `param_family`
- `authoritative_evidence`
- `heuristic_evidence` when used
- `verified_claims`
- `unverified_claims`
- `conflicts` when schema and source disagree
- `recommended_next_check`

## Collaboration Rules
- Hand off to `swmf-build-run` when the request turns into build or run preparation.
- Hand off to `swmf-debug` when validation fails and root-cause narrowing is needed.
- Hand off to `swmf-implementation` when the user wants to change PARAM-related source behavior.
- Hand off to `swmf-postproc` when the request moves from setup semantics into output interpretation.

## Anti-patterns
- Do not generate a runnable workflow from heuristic search alone.
- Do not skip `swmf_run_testparam` when the request is validation-sensitive.
- Do not collapse `PARAM.XML`, examples, and source references into one undifferentiated answer.