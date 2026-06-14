---
name: swmf-explain
description: "Use when the question is broad, conceptual, cross-component, or asks 'how/why/where' at system level. Explains SWMF architecture, component roles, coupling, and control flow."
---

# swmf-explain

## When to use
- "How does SWMF work?"
- "How does GM couple to IE?"
- "What is CON responsible for?"
- "How does the timestep manager interact with components?"
- Any question asking how or why something works at the system level
- Any question where the relevant area of the codebase is unknown

## Do not use when
- User wants to configure a specific case → `swmf-configure`
- User wants to build → `swmf-build`
- User wants to run → `swmf-run`
- Something failed → `swmf-debug`
- User wants to interpret outputs → `swmf-analyze`
- User wants to compare two things → `swmf-compare`

## Evidence order

1. `swmf get-context --question ... --task-type architecture --detail normal`
   — orientation, entities, relevant components and files
2. `swmf get-evidence --mode keyword --query <entity> --goal "architecture explanation"`
   — grounding for each key entity from Step 1
3. Read specific files only from paths returned in evidence
4. Grep: only if Steps 1–2 both miss a specific named token; restrict to evidence paths

## Helper skills allowed

* `swmf-architecture` — for deep coupling or control-flow questions
* `swmf-params` — if the explanation requires understanding a PARAM command

## Outputs

* which components are involved (cited from evidence)
* coupling mechanism or control flow described
* evidence path + snippet for each major claim
* confirmed claims vs inferred claims separated
* what is uncertain and what check would resolve it
