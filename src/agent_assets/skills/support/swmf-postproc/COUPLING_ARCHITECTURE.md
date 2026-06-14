# Coupling Architecture Playbook

Use this playbook for:
- explaining how SWMF components are coupled
- describing the coupler architecture
- producing Mermaid diagrams of component relationships
- answering broad architecture questions about component interaction paths

## Allowed First Tool
First tool:
- `swmf get-context --question "<coupling question>" --task-type architecture`

Precision follow-up when registry detail is needed:
- `swmf get-evidence --mode keyword --goal "coupling registry detail"`

Do not begin broad coupling questions with build/run readiness tools or heuristic source search.

## Evidence Order
1. `swmf get-context` (returns coupling entities and evidence)
2. `swmf get-evidence --mode keyword --goal "coupling registry detail"` if entity-level
   registry detail is needed
3. Direct source reads only when the swmf CLI payload names a specific file and still
   leaves a material gap
4. Heuristic source evidence only for additive context

## Required Distinctions
Always separate these concepts explicitly:
- `registry_components`: components that exist in the registry
- `implemented_directed_links`: dispatch links actually implemented in coupler logic
- `compile_time_gates`: links guarded by compile-time conditions
- `runtime_enablement_notes`: whether a compiled link must still be enabled by runtime settings

Never compress those four layers into a single undifferentiated statement such as “all components are coupled.”

## Mermaid Rules
- Use a directed graph
- Represent source-to-target dispatch direction explicitly
- If a component appears only in the registry or only as a target in the evidence, say so in the prose
- Do not invent symmetric links unless the evidence shows both directions
- Add a short legend or note when compile-time or runtime gating materially changes interpretation

## Final Answer Requirements
Always include:
- `registry_components`
- `implemented_directed_links`
- `compile_time_gates`
- `runtime_enablement_note`
- `mermaid_diagram`

If the available evidence does not establish one of these fields, mark it as unresolved rather than guessing.
