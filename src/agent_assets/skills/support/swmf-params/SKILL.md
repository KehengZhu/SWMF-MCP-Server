---
name: swmf-params
type: support
description: "Support skill. Answers questions about PARAM command meaning, PARAM.in structure, PARAM.XML schema, include resolution, component maps, and validation. Called by swmf-configure, swmf-debug, and swmf-run."
---

# swmf-params (Support)

This is a **support skill**. It is not chosen directly by the agent.
`swmf-configure` consults it for PARAM meaning and validation.
`swmf-debug` consults it when the failure is PARAM-related.

## Purpose

Answer one thing: what does a PARAM command mean, is a PARAM.in valid, and
where do schema and source behavior differ.

## Scope

* command definition and schema (from `PARAM.XML`)
* `PARAM.in` structural validation
* `#INCLUDE` chain resolution
* `#COMPONENTMAP` layout
* external input files required by PARAM
* schema vs runtime source behavior divergence

Not in scope: build steps, run execution, failure diagnosis.

## Tool Protocol

For command meaning:
```
get_evidence(
  query = <param_command>,
  mode = "keyword",
  goal = "param definition"
)
```

For structural validation:
```
inspect_artifact(
  artifact_type = "param",
  path = <PARAM.in_path>,
  question = <question>
)
```

For source behavior (schema vs runtime divergence):
```
get_evidence(
  query = <param_command>,
  mode = "hybrid",
  goal = "runtime source behavior"
)
```

Authoritative validation (outside MCP):
* Run `Scripts/TestParam.pl -n=<nproc> <PARAM.in>` directly from the SWMF root

## Authority Order

1. `TestParam.pl` output (run directly from SWMF root)
2. `PARAM.XML` schema (via `get_evidence(mode="keyword", goal="param schema")`)
3. Deterministic parsing (`inspect_artifact(artifact_type="param", ...)`)
4. Heuristic source evidence (`get_evidence(mode="hybrid")`)

Never let heuristic search override `TestParam.pl` or `PARAM.XML`.

## Output Contract

* `param_family`: one of `command_definition`, `file_validation`,
  `include_resolution`, `component_layout`, `schema_vs_source_behavior`, `example_lookup`
* `authoritative_evidence`
* `heuristic_evidence` when used
* `verified_claims`
* `unverified_claims`
* `conflicts` when schema and source disagree
