Your current tree mixes **task skills**, **retrieval skills**, **execution skills**, and **specialist subskills** in a way that will make routing fuzzy:

* `swmf-build-run` and `swmf-workflow` overlap.
* `swmf-debug` and `swmf-debug-run` overlap.
* `swmf-param-specialist` and `swmf-exact-lookup` partly overlap.
* `swmf-postproc` and `swmf-compare` partly overlap.
* `swmf-architecture` and `swmf-implementation` can overlap unless one is explicitly conceptual and the other code-grounded.

The main problem is that some skills are named by **user intent** (“debug”, “compare”), while others are named by **method** (“exact-lookup”), and others by **knowledge scope** (“architecture”, “param-specialist”). That usually confuses agents.

## Clean design principle

Make skills follow one hierarchy:

**1. Entry skills = task-oriented**
These are what the agent should choose first.

**2. Support skills = internal helpers**
These should usually not be selected directly unless the task clearly demands them.

So the agent first answers: “What job am I doing?” not “What retrieval trick should I use?”

## Recommended redesign

I would reshape your set into this:

### Entry skills

* `swmf-explain`
* `swmf-configure`
* `swmf-build`
* `swmf-run`
* `swmf-debug`
* `swmf-analyze`
* `swmf-compare`

### Support skills

* `swmf-architecture`
* `swmf-implementation`
* `swmf-params`
* `swmf-postproc`
* `swmf-exact-lookup`

That means:

* **Explain** = architecture / “how does this work?”
* **Configure** = params, setup, `Config.pl`, case preparation
* **Build** = compile / setup build targets
* **Run** = execution guidance and run-state reasoning
* **Debug** = failure diagnosis
* **Analyze** = outputs, interpretation, derived insight
* **Compare** = run-vs-run, config-vs-config, output-vs-output

Then keep the others as helper skills that these entry skills call mentally.

## What to merge

I would merge like this:

* `swmf-build-run` → split into `swmf-build` and `swmf-run`
* `swmf-workflow` → remove as a top-level skill; fold into build/run/configure guidance
* `swmf-debug-run` → remove; fold into `swmf-debug`
* `swmf-param-specialist` → rename to `swmf-params`
* `swmf-postproc` stays, but as support under `swmf-analyze` and `swmf-compare`

## What each skill should own

### `swmf-explain`

Use when the question is broad, conceptual, cross-component, or asks “how/why/where” at system level.

Owns:

* component roles
* coupling
* control flow
* architecture summaries

Should consult:

* `swmf-architecture`
* `swmf-implementation`
* context/evidence MCP as needed

### `swmf-configure`

Use when the task is about preparing or changing a case.

Owns:

* parameter meaning
* `PARAM.in`
* `PARAM.XML`
* `Config.pl`
* module-specific configuration guidance

Should consult:

* `swmf-params`
* `swmf-exact-lookup`

### `swmf-build`

Use when the task is about compile/build configuration.

Owns:

* build targets
* compile flags
* setup/build scripts
* build troubleshooting

### `swmf-run`

Use when the task is about how to execute or what execution procedure is appropriate.

Owns:

* run guidance
* launch sequence
* script entrypoints
* run environment expectations

### `swmf-debug`

Use when something is broken or suspicious.

Owns:

* logs first
* params second
* code lookup third
* evidence-backed diagnosis

Should consult:

* `swmf-implementation`
* `swmf-exact-lookup`
* `swmf-params`

### `swmf-analyze`

Use when the user wants interpretation of outputs.

Owns:

* result reading
* diagnostics from outputs
* field interpretation
* postprocessing workflow guidance

Should consult:

* `swmf-postproc`

### `swmf-compare`

Use when two things must be contrasted.

Owns:

* run comparisons
* param diffs
* output diffs
* regression-style reasoning

Should consult:

* `swmf-postproc`
* `swmf-analyze`

## How the agent knows which skill to use

Give every entry skill a tiny routing contract in `SKILL.md`:

* **When to use**
* **When not to use**
* **Inputs it expects**
* **What evidence it should gather**
* **Which support skills it may rely on**

Example:

```md
# swmf-debug

Use when:
- run failed
- output is wrong
- coupling is missing
- build succeeded but behavior is incorrect

Do not use when:
- user only wants conceptual explanation
- user is only asking how to configure a case from scratch

Preferred evidence order:
1. logs
2. PARAM.in / PARAM.XML
3. workflow guidance
4. exact code lookup
5. architecture context if cross-component

Outputs:
- likely cause
- evidence
- uncertainty
- next diagnostic step
```

That is much better than hoping the name alone is enough.

## Skill selection policy

The agent should choose in this order:

### 1. Pick one primary entry skill

Only one should own the answer.

### 2. Pull in support skills as needed

Not multiple competing top-level skills.

### 3. Use MCP for evidence, not for deciding the whole plan

Skills decide the plan.

A simple router:

* “how does X work?” → `swmf-explain`
* “how do I set/configure X?” → `swmf-configure`
* “how do I build?” → `swmf-build`
* “how do I run?” → `swmf-run`
* “why did this fail?” → `swmf-debug`
* “what does this output mean?” → `swmf-analyze`
* “what changed / which is different?” → `swmf-compare`

## What `swmf-exact-lookup` should be

This should not feel like a peer to `swmf-debug` or `swmf-build`.

It should be a support skill with a narrow role:

* exact identifiers
* file/path lookup
* error string lookup
* narrow confirmation after broader reasoning

So it becomes “precision helper,” not “top-level way of thinking.”

## A cleaner tree

I would aim for this:

```text
skills/
├── swmf-explain/
├── swmf-configure/
├── swmf-build/
├── swmf-run/
├── swmf-debug/
├── swmf-analyze/
├── swmf-compare/
├── support/
│   ├── swmf-architecture/
│   ├── swmf-implementation/
│   ├── swmf-params/
│   ├── swmf-postproc/
│   └── swmf-exact-lookup/
└── SWMF_CORE_DISCIPLINE.md
```

If you do not want a `support/` subdirectory, at least label them clearly inside each skill.

## What should go into `SWMF_CORE_DISCIPLINE.md`

This should be global rules shared by all skills:

* prefer evidence over speculation
* exact lookup for exact tokens
* semantic/context tools only for broad questions
* grep is allowed as fallback
* do not answer operational questions without artifacts when available
* one primary skill per task
* support skills are helpers, not co-owners

This file should be short and strict.

## Collaboration with your minimal MCP interface

This fits your earlier interface well:

* `get_context` mainly used by `swmf-explain`, sometimes `swmf-debug`
* `get_evidence` used by almost all entry skills
* `get_workflow_guidance` used by `swmf-configure`, `swmf-build`, `swmf-run`
* `inspect_artifact` used by `swmf-debug`, `swmf-analyze`
* `compare_artifacts` used by `swmf-compare`

So the mapping becomes clean:

* **skills = task policy**
* **MCP = evidence and guidance**
* **indexes = hidden retrieval backend**

## Concrete plan

### Phase 1

Rename and merge skills:

* merge `swmf-debug-run` into `swmf-debug`
* split `swmf-build-run` into `swmf-build` and `swmf-run`
* rename `swmf-param-specialist` to `swmf-params`
* demote `swmf-workflow` to helper content or remove it

### Phase 2

Create a routing header in every entry skill:

* use when
* don’t use when
* evidence order
* helper skills allowed

### Phase 3

Standardize all support skills:

* each one only answers one kind of question
* none should act like a full workflow owner

### Phase 4

Add a single router rule for the agent:

* choose one primary entry skill by user intent
* use support skills only to fill gaps
* use MCP tools for proof

### Phase 5

Test on 10 representative queries:

* architecture
* configure module
* build case
* run case
* debug crash
* debug coupling
* explain parameter
* analyze output
* compare runs
* exact symbol lookup

Track where routing is ambiguous. If two skills could both plausibly be primary, your boundaries are still too fuzzy.

## My strongest recommendation

Do **not** organize the top layer by internal method like `exact-lookup`, `workflow`, or `implementation`.
Organize it by **what the user is trying to get done**.

That is the cleanest way to make skill selection reliable.
