---
name: swmf-build
description: "Use when the task is about compiling, setting up build targets, build configuration, or build troubleshooting."
---

# swmf-build

## When to use
- "How do I build SWMF with GM and IE?"
- "What compile flags do I need?"
- "How do I run Config.pl for a new component set?"
- "Build failed — what went wrong?"
- Any task about compiling or build configuration

## Do not use when
- User wants to configure PARAM or case settings → `swmf-configure`
- User wants to run the simulation → `swmf-run`
- Something failed at runtime → `swmf-debug`

## Evidence order

1. `get_evidence(query=<build goal>, task_type="build", goal=<build goal>)`
   — discovers Config.pl, Makefile targets, and build entrypoints
2. `inspect_artifact(artifact_type="run_dir"|"build_output", path=...)`
   — for build output inspection or troubleshooting
3. `get_evidence(mode="keyword", goal="build flags or component selection")`
   — for specific build options or component lookup

## Helper skills allowed

* `swmf-params` — if a PARAM.in must be valid before building
* `swmf-exact-lookup` — for specific symbol or flag confirmation

## Outputs

* workflow evidence items from `get_evidence(task_type="build")`
* workflow metadata on returned items:
  * `metadata.kind`
  * `metadata.relative_path`
  * `metadata.why_relevant`
* build findings when troubleshooting (from `inspect_artifact`)
* next step clearly stated (what command to run and why)
