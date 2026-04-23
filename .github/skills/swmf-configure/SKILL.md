---
name: swmf-configure
description: "Use when the task is about preparing or changing a SWMF case: PARAM.in, PARAM.XML, Config.pl, module-specific configuration, or case setup."
---

# swmf-configure

## When to use
- "How do I set `#TIMESTEP` for this case?"
- "What PARAM commands does GM accept?"
- "Is my PARAM.in valid?"
- "How do I configure module X?"
- "What does `#COMPONENTMAP` do?"
- Any task about preparing or modifying a PARAM file or case configuration

## Do not use when
- User asks how/why something works at the architecture level → `swmf-explain`
- User asks how to build → `swmf-build`
- User asks how to run → `swmf-run`
- Something failed during a run → `swmf-debug`
- User wants to change source behavior → consult `swmf-implementation` (support)

## Evidence order

1. For PARAM command meaning:
   ```
   get_evidence(query=<param_command>, mode="keyword", goal="param definition")
   ```
2. For structural validation of a PARAM.in:
   ```
   inspect_artifact(artifact_type="param", path=<PARAM.in_path>)
   ```
3. For configuration scripts or `Config.pl` discovery:
   ```
   get_workflow_guidance(goal=<config goal>, module=<component>, task_type="configuration")
   ```
4. For runtime schema vs source divergence:
   ```
   get_evidence(query=<param_command>, mode="hybrid", goal="runtime source behavior")
   ```
5. Authoritative validation: run `Scripts/TestParam.pl` directly from the SWMF root (not via MCP)

## Helper skills allowed

* `swmf-params` — for deep PARAM schema, validation, include resolution
* `swmf-exact-lookup` — when exact command location or definition is needed

## Outputs

* PARAM command meaning cited from `PARAM.XML` or evidence
* structural validation findings (if a PARAM.in was provided)
* configuration script entrypoints with `relative_path` and `why_relevant`
* verified claims vs unverified claims separated
* any conflicts between schema and source behavior named explicitly
