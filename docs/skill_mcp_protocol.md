# SWMF Skill-MCP Protocol

## Purpose

This document defines a general design protocol for the SWMF skill/MCP model.

The target model is:

- MCP tools stay minimal.
- MCP tools return evidence only.
- Skills own task policy.
- The agent infers workflow from skill policy plus evidence.
- New skills and new MCP tools are added through a disciplined pipeline.

This is intended for early-stage development, where interface clarity matters
more than feature count.

## Core Principle

Treat the system as three layers with strict responsibilities:

1. MCP tools
   - return evidence
   - do not recommend actions
   - do not choose plans
   - do not act like weak agents

2. Skills
   - define task policy
   - define evidence order
   - define output contract
   - define when a tool should or should not be used

3. Agent
   - selects the primary skill
   - uses MCP evidence through the skill protocol
   - infers the workflow
   - writes the final reasoning and answer

If a layer starts doing another layer's job, the model becomes harder to
control and easier to confuse.

## Non-Goals

This design explicitly avoids:

- MCP tools that suggest workflows
- MCP tools that recommend next steps
- many narrow public tools with overlapping purposes
- skills that act like retrieval wrappers instead of task policies
- tool outputs that force the agent into one hard-coded answer path

## Contract by Layer

### MCP Tool Contract

Every public MCP tool should satisfy all of the following:

- returns local evidence or deterministic artifact facts
- has a narrow, stable contract
- does not prescribe actions
- does not prescribe tool order
- does not return "recommended workflow" or "next tool"
- does not hide uncertainty
- is useful across multiple skills

Good MCP output:

- script path
- usage block
- accepted flags found in source/help text
- run directory artifact presence
- PARAM structure
- job script scheduler and task counts
- code/doc snippets
- file inventories
- exact source locations

Bad MCP output:

- "you should run X next"
- "the workflow is probably A -> B -> C"
- "use this tool next"
- "the best fix is ..."

### Skill Contract

Each skill should define:

- when to use
- when not to use
- required inputs
- evidence order
- allowed fallback behavior
- required answer structure
- helper skills allowed

A skill is a task policy, not a bag of retrieval hints.

### Agent Contract

The agent should:

1. choose one primary skill
2. follow that skill's evidence order
3. call MCP only for evidence
4. infer workflow from evidence and skill policy
5. answer with explicit certainty vs inference

## Minimal Public MCP Surface

The public MCP interface should stay small and general.

A good default public surface is:

- `get_context`
- `get_evidence`
- `inspect_artifact`
- `compare_artifacts`

But these should be interpreted strictly:

- `get_context`
  - orientation only
  - broad repo/task grounding
  - not authoritative for case-local questions

- `get_evidence`
  - retrieval only
  - source/doc/schema snippets
  - workflow evidence when `task_type` is set

- `inspect_artifact`
  - deterministic inspection of one artifact
  - logs, PARAM, run_dir, build output, result files

- `compare_artifacts`
  - deterministic differences
  - not causal explanation by itself

## Workflow Evidence

Workflow discovery is a `get_evidence` use case, not a separate tool.
There is no dedicated workflow retrieval surface.

Use `task_type="configuration"|"build"|"run"|"analysis"` and an optional
`module` hint when the question is about entrypoints, scripts, or
postprocessing affordances. The returned evidence should stay evidence-only and
may include workflow metadata on each item:

- `metadata.kind`
- `metadata.relative_path`
- `metadata.why_relevant`

It should not contain:

- `suggested_steps`
- `recommended_next_action`
- `recommended_next_tool`
- `best_workflow`

## Gold Rule for Tool Design

If the output sounds like advice, it probably belongs in a skill or the agent,
not in MCP.

If the output sounds like a fact extractable from local sources, it belongs in
MCP.

## Skill-MCP Workflow Protocol

For any task, the system should follow this pipeline:

1. Intent classification
   - choose one primary entry skill

2. Skill policy activation
   - read the skill's evidence order and answer contract

3. Evidence collection
   - call MCP tools in the order defined by the skill

4. Evidence normalization
   - separate deterministic facts from heuristic evidence

5. Workflow inference
   - agent infers likely sequence, dependencies, and decision points

6. Answer composition
   - agent answers using:
     - evidence-backed claims
     - explicit inferences
     - explicit uncertainty

The workflow is inferred at step 5, not emitted by MCP at step 3.

## Evidence Authority Model

Not all evidence should have equal authority.

Use this authority ladder:

1. Deterministic artifact inspection
   - `inspect_artifact`
   - direct structured parsing
   - file existence/layout facts

2. Authoritative source/schema evidence
   - `PARAM.XML`
   - script help text
   - source-defined usage blocks

3. Source/doc retrieval
   - `get_evidence`
   - code/doc snippets

4. Broad orientation
   - `get_context`

Skills should explicitly state when lower-authority evidence is not enough.

Example:

- run readiness should not rely on `get_context`
- PARAM validation should not rely only on semantic retrieval
- build/run script usage should not rely on generic search if usage text is
  available directly from the script

## Design Pattern for Skills

Entry skills should be task-oriented.

Examples:

- `swmf-explain`
- `swmf-configure`
- `swmf-build`
- `swmf-run`
- `swmf-debug`
- `swmf-analyze`
- `swmf-compare`

Support skills should be helper-oriented.

Examples:

- `swmf-architecture`
- `swmf-params`
- `swmf-implementation`
- `swmf-postproc`
- `swmf-exact-lookup`

Entry skills decide the evidence plan.
Support skills refine one part of that plan.

## Design Pattern for MCP Tools

Public MCP tools should be broad but typed.

Prefer:

- one tool with a stable typed output

over:

- many tools that each answer one tiny narrow case

Example:

Prefer one `inspect_artifact` with stable artifact types over separate public
tools like:

- `inspect_log`
- `inspect_param`
- `inspect_run_dir`
- `inspect_build_output`

Keep implementation-specific helpers private unless multiple skills truly need
them as a public contract.

## How to Add a New Skill

When adding a skill, use this pipeline.

### Step 1: Define the task boundary

Write:

- what user intent activates it
- what intents it should reject
- what final output shape it must produce

### Step 2: Define the evidence contract

For each required output field, ask:

- what evidence is needed
- which existing MCP tool should provide it
- what authority level is required

### Step 3: Identify MCP gaps

If a required field cannot be produced cleanly by existing MCP tools:

- decide whether the gap is deterministic and reusable
- only then add or extend an MCP tool

### Step 4: Write the evidence order

The skill should define:

1. first MCP call
2. follow-up MCP call
3. fallback MCP call
4. when direct file reads are allowed

### Step 5: Add evaluation tasks

For the new skill, create a small gold set of representative prompts and check:

- correct primary skill selection
- correct first MCP tool
- low shell fallback rate
- no invented workflow from MCP output

## How to Add or Change an MCP Tool

Use this gate before adding a public tool.

Add or change a tool only if all are true:

1. at least one skill needs the same evidence repeatedly
2. the evidence is deterministic or structurally extractable
3. existing tools force too much heuristic reasoning or shell fallback
4. the new contract will remain understandable to agents

If any of these fail, do not add a public tool.

Instead:

- improve a private helper
- refine a skill
- keep the logic inside the agent

## Preferred Evolution Strategy

When you find a weakness, fix in this order:

1. clarify skill policy
2. improve existing tool output shape
3. expose a private helper through an existing public tool
4. add a new public tool only as a last resort

This keeps the MCP interface small.

## Concrete Guidance for Build and Run

Build and run are the clearest examples of why evidence-only MCP matters.

### Build Skill Needs

`swmf-build` needs evidence such as:

- build entry scripts
- `Config.pl` locations
- Makefile locations
- usage/help text
- accepted flags
- required environment variables
- build log errors
- compile/link error excerpts

The skill, not MCP, should infer:

- which command the user likely needs
- what order to run commands in
- how to adapt to the user's goal

### Run Skill Needs

`swmf-run` needs evidence such as:

- run directory readiness
- job script paths
- scheduler type
- task count hints
- launch script usage
- restart-related files
- PARAM presence
- status markers like `SWMF.SUCCESS`

The skill, not MCP, should infer:

- whether the case is ready to launch
- what launch path fits the user's environment
- which missing artifact matters most

## Concrete Guidance for IDL Visualization

IDL visualization is part of `swmf-analyze`, with `swmf-postproc` as the
support skill. The detailed protocol lives in
`docs/idl_visualization_skill_protocol.md`.

IDL support should not add public `idl_*` MCP tools by default. Procedure
catalog rows, procedure signatures, source locations, and manual snippets are
evidence returned through `get_evidence`. Run-directory and result-file facts
are evidence returned through `inspect_artifact`.

The skill, not MCP, should infer:

- whether to use `read_data` plus `plot_data`, `show_data`, or `animate_data`
- which `func` string matches the user's requested quantity
- which `plotmode` fits the data dimensionality and grid constraints
- whether a regular-grid transform, slice, log workflow, or graphics export is needed

## Response Schema Philosophy

Tool schemas should optimize for agent reasoning, not human readability.

That means:

- typed fields first
- free-text summary second
- evidence paths and snippets always included
- explicit uncertainty always included

Preferred shape:

```json
{
  "ok": true,
  "summary": "...",
  "typed_fields": "...",
  "evidence": [],
  "uncertainty": {
    "known_unknowns": []
  }
}
```

Avoid schema shapes that force the agent to scrape prose.

## Evaluation Protocol

Evaluate the system at the skill-MCP boundary, not just by final answer quality.

For each gold task, measure:

- was the correct primary skill chosen
- was the correct first MCP tool chosen
- did MCP return the needed evidence fields
- did the agent have to fall back to shell/grep
- did MCP output advice instead of evidence
- did the final answer clearly separate fact from inference

Track these failure types:

- wrong skill
- wrong first tool
- missing evidence fields
- generic evidence instead of local evidence
- workflow advice leaking from MCP
- agent forced into ad hoc shell recovery

## Anti-Patterns

Avoid these patterns:

- tool proliferation
- overlapping public tools
- MCP tools with embedded reasoning policy
- skills that just mirror tool names
- retrieval-first design for deterministic tasks
- returning "recommended_next_tools" in public MCP contracts

Private helpers may contain orchestration logic.
Public MCP tools should not.

## Recommended Development Sequence

Use this sequence as the general development pipeline.

### Phase 1: Freeze the philosophy

- keep MCP evidence-only
- keep skills policy-oriented
- keep one primary skill per task

### Phase 2: Normalize current tools

For each public tool:

- remove advisory fields
- ensure typed evidence fields exist
- ensure uncertainty is explicit

### Phase 3: Tighten current skills

For each skill:

- make evidence order explicit
- define fallback rules
- define final answer contract

### Phase 4: Add missing deterministic evidence

Only extend tools where a skill repeatedly lacks evidence.

Typical first targets:

- script usage extraction
- job script inspection
- stronger PARAM validation
- stronger local run/build artifact inspection

### Phase 5: Add skill-level evaluations

Create a gold prompt set per skill and log:

- chosen skill
- tool sequence
- shell fallbacks
- evidence sufficiency

### Phase 6: Expand cautiously

Only after the current skills are stable:

- add new entry skills
- add new support skills
- add new public MCP tools if still justified

## Repository-Level Rule

When deciding whether something belongs in MCP, ask:

"Is this reusable evidence extraction, or is this workflow reasoning?"

- reusable evidence extraction -> MCP
- workflow reasoning -> skill/agent

That rule should stay stable even as the system grows.

## Short Version

The design target is:

- minimal MCP
- evidence-only MCP
- policy-rich skills
- one primary skill per task
- workflow inferred by the agent
- deterministic facts before heuristic retrieval
- add tools only when multiple skills need the same reusable evidence

If this rule is followed consistently, the model should scale to more skills
without making the MCP interface noisy or confusing.
