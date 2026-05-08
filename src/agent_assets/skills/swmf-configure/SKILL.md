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
- User wants to **replicate** an entire run from a paper, structured spec, or prior run
  directory → `swmf-replicate`. `swmf-configure` handles edits to a single PARAM; full
  case replication is multi-step and lives in the entry skill.

## Evidence order

1. For PARAM command meaning:
   ```
   get_evidence(query=<param_command>, mode="keyword", goal="param definition")
   ```
2. For structural primitives (rule evaluation, include resolution, component map,
   external-ref resolution) on a PARAM.in:
   ```
   inspect_artifact(artifact_type="param", path=<PARAM.in_path>, check_rules=True)
   ```
   For PARAM intent (sessions, control cadence, `#SAVEPLOT` meaning), read the
   PARAM.in file directly. The inspector returns structural primitives only.
3. For configuration scripts or `Config.pl` discovery:
   ```
   get_evidence(query=<config goal>, goal=<config goal>, module=<component>, task_type="configuration")
   ```
4. For runtime schema vs source divergence:
   ```
   get_evidence(query=<param_command>, mode="hybrid", goal="runtime source behavior")
   ```
5. Authoritative validation: run `Scripts/TestParam.pl` directly from the SWMF root (not via MCP)

## Helper skills allowed

* `swmf-params` — for deep PARAM schema, validation, include resolution
* `swmf-exact-lookup` — when exact command location or definition is needed
* `swmf-cme-setup` — when a `#CME` block, GL/SPHEROMAK/Cone choice, or eruption-session
  structure is involved.
* `swmf-magnetogram` — when `#HARMONICSFILE`, `#FDIPS`, or magnetogram input files are
  involved.

## Outputs

* PARAM command meaning cited from `PARAM.XML` or evidence
* structural validation findings (if a PARAM.in was provided)
* configuration workflow evidence from `get_evidence(task_type="configuration")`
* workflow metadata on returned items:
  * `metadata.kind`
  * `metadata.relative_path`
  * `metadata.why_relevant`
* verified claims vs unverified claims separated
* any conflicts between schema and source behavior named explicitly
