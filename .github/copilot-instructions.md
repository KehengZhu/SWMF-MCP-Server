# SWMF Copilot Instructions

This repository is the **Space Weather Modeling Framework (SWMF)** MCP server
prototype. SWMF is a multi-physics, multi-component simulation framework for
space weather research. The codebase is primarily Fortran, Perl, and Python.

Two MCP servers are active: `swmf-prototype` (SWMF tools) and the IDL server.

## SWMF Tool Discipline — Always Active

These rules apply to every SWMF-related request, regardless of which skill is
loaded:

### Mandatory pre-search gate

Before calling any grep, `rg`, glob, or direct file read to answer a question
about SWMF source behavior, architecture, coupling, or mechanisms:

1. Classify the question as one of: `source_understanding`, `exact_lookup`,
   `param_semantics_or_validation`, `build_or_run_readiness`,
   `failure_diagnosis`, or `postprocess_or_architecture`.
2. Call the designated first MCP tool for that family (see table below).
3. Only then read files, and only the files named in the tool's output.

**This gate is mandatory. Using grep before calling the first MCP tool is a
protocol violation.**

| Question family | First MCP tool |
|---|---|
| Source behavior / architecture / mechanisms | `get_context` or `get_evidence` |
| Coupling or component interaction | `get_context` |
| PARAM meaning or validation | `inspect_artifact` for local PARAM files, otherwise `get_evidence` |
| Build or run environment | `get_workflow_guidance` |
| Crash or wrong-result debug | `inspect_artifact` |
| IDL procedures or visualization | `get_evidence` |
| Artifact comparison | `compare_artifacts` |

### Authority order

1. Direct MCP tool output (runtime artifacts, exact source context)
2. Authoritative v2 tool output and repository evidence
3. Deterministic parsing and context-collection tools
4. Direct file inspection on files explicitly named by the v2 tool output
5. Grep or manual file inspection (only after the gate is passed)

### User experience rules

- Users should never need to name MCP tools or ask for semantic search.
- Surface answers in SWMF terms. Mention tool names only when the user asks or
  when the evidence path itself matters.

## Skill routing

For complex SWMF requests, load the appropriate skill FIRST:

- Source changes or implementation → `swmf-debug` with support from `swmf-implementation`
- PARAM.in questions → `swmf-configure` with support from `swmf-params`
- Build/run readiness → `swmf-build` or `swmf-run`
- Debugging crashes or wrong results → `swmf-debug`
- Post-processing or visualization → `swmf-analyze` with support from `swmf-postproc`

Each skill loads `../../SWMF_CORE_DISCIPLINE.md` as its shared parent protocol.
