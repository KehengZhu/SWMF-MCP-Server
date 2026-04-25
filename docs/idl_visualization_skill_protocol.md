# IDL Visualization Skill and MCP Protocol

## Purpose

This protocol defines how IDL visualization support belongs inside the SWMF
skill/MCP model.

The design follows `docs/skill_mcp_protocol.md`:

- `swmf-analyze` is the entry skill for user-facing visualization tasks.
- `swmf-postproc` is the support skill that owns IDL-specific policy.
- MCP tools return evidence only.
- The public MCP surface remains `get_context`, `get_evidence`,
  `inspect_artifact`, and `compare_artifacts`.

No public `idl_*` MCP tool should be added unless the four-tool surface cannot
return deterministic evidence cleanly.

## Source Basis

The IDL workflow policy is grounded in `docs/idl.md`, especially:

- IDL path/startup setup with `IDL_PATH`, `IDL_STARTUP`, and `idlrc`
- `read_data` for reading snapshots into `x`, `w`, and header variables
- regular-grid transformations for generalized or unstructured grids
- data comparison with multiple files and `compare`
- `plot_data` and `show_data` for plotting loaded or freshly read data
- `func` strings for variables, predefined functions, expressions, and vector pairs
- `plotmode` strings for 1D plots, 2D scalar plots, vector plots, modifiers, and color tables
- domain restriction, slicing, animation, log plotting, and graphics export

## Skill Structure

### Entry Skill: `swmf-analyze`

Use for:

- "How do I plot this output?"
- "How do I visualize this SWMF result in IDL?"
- "Which `func` or `plotmode` should I use?"
- "What does this output field mean?"
- "What postprocessing workflow applies to this run?"

Responsibilities:

- inspect the run directory or result file when an artifact is named
- decide whether the task is output interpretation, IDL plotting, or broader postprocessing
- call `swmf-postproc` for IDL visualization details
- compose the final workflow and separate facts from inference

### Support Skill: `swmf-postproc`

Use only under an entry skill. It owns:

- IDL procedure discovery policy
- snapshot/log/animation plotting policy
- `func` and `plotmode` evidence policy
- transform, slice, and export guidance
- answer contracts for IDL inventory and usage answers

It does not own:

- general run failure diagnosis
- PARAM configuration changes
- build/run workflow
- comparison policy except when `swmf-compare` asks for postprocessing context

## IDL Evidence Order

For a user request involving a run directory or output file:

1. `inspect_artifact(artifact_type="run_dir"|"result", path=<path>)`
2. Normalize the prompt before retrieval:
   - named procedure or workflow: `plot_data`, `show_data`, `read_data`, `animate_data`, `plot_log_data`, `read_log_data`
   - inventory request: `list IDL plotting procedures`
   - manual detail: `func`, `plotmode`, `transform`, `slice`, `export`
   - if the prompt is broad, do not pass it through unchanged to `get_evidence`
3. `get_evidence(query=<normalized procedure-or-task>, mode="keyword", goal="IDL procedure signature and usage")`
4. `get_evidence(query=<normalized func/plotmode/transform/export term>, mode="keyword", goal="IDL visualization manual detail")`
5. direct reads only from files named by evidence

For procedure inventory:

1. `get_evidence(query="list IDL plotting procedures", mode="keyword", goal="IDL procedure signature and usage")`
2. optional narrowed `get_evidence` query for a named procedure or category
3. direct source reads only for named `share/IDL/**` files

For postprocessing entrypoint discovery:

1. `get_evidence(query="IDL postprocessing", task_type="analysis", goal="IDL visualization entrypoints")`
2. `inspect_artifact` only if the user also names a local artifact

## Supporting MCP Tool Design

### `inspect_artifact`

Required evidence:

- run-directory inventory
- PARAM-derived run intent from `PARAM.in` when present (session timeline, control settings, and `#SAVEPLOT` cadence/forms/variables)
- output/result file presence
- result-file type classification
- log presence when relevant
- uncertainty when binary result contents are not inspected

Tool boundary:

- may say a file is an IDL-like output artifact
- must not decide which IDL plotting workflow is best

### `get_evidence`

Required evidence:

- deterministic IDL catalog rows for procedure inventories
- deterministic IDL procedure signatures for named procedures
- source paths and line numbers for procedures
- documentation/source snippets for `func`, `plotmode`, transforms, slicing, animation, logs, and export
- workflow entrypoint evidence when `task_type="analysis"`

Implementation rule:

- IDL catalog evidence should be exposed through `get_evidence`, not a new public tool.
- Evidence items should use `type="idl"` and metadata such as
  `metadata.kind="idl_procedure_signature"` or
  `metadata.kind="idl_procedure_catalog_row"`.
- Metadata should include `relative_path`, `why_relevant`, and category when known.

Tool boundary:

- may return signatures, categories, snippets, and source locations
- must not return "recommended next action" or workflow advice

### `get_context`

Use only for broad orientation, such as asking where IDL postprocessing lives.
It is not authoritative for a specific procedure signature or case artifact.

### `compare_artifacts`

Use when the task is comparing two outputs, PARAM files, logs, or run
directories. IDL-specific visualization of the comparison remains skill policy.

## Workflow Inference Rules

The agent, not MCP, infers:

- whether to use `read_data` plus `plot_data`, `show_data`, or `animate_data`
- whether a log workflow should use `read_log_data` and `plot_log_data`
- whether an irregular grid requires a regular-grid transform before a requested plot mode
- whether a requested quantity is a raw variable, predefined `funcdef.pro` function, expression, or vector pair
- whether export setup is needed

For artifact-generating visualization requests, the agent should use the
IDL-first export ladder:

- generate a case-local `analysis/<name>.pro` command script
- execute it with `idl`, capturing `analysis/<name>.idl.log`
- use a SWMF macro-first driver: let IDL read plot files and render with
  `read_data`, `plot_data`, `show_data`, `animate_data`, or log procedures
- convert IDL PostScript/EPS output to PNG with `magick` or `convert` only
  after IDL succeeds
- use Python/SVG/manual binary rendering only after IDL fails and the user
  accepts a non-IDL fallback

The generated `.pro` file should mainly set documented common-block values such
as `filename`, `func`, `plotmode`, `plottitle`, `multiplot`, transform, range,
and export settings, then call SWMF IDL entrypoints. Do not replace those
entrypoints with direct `contour`, `vector`, `triangulate`, `tvrd`, custom
readers, or graphics primitives unless evidence shows the SWMF macros cannot
express the requested output and the user accepts that tradeoff.

If the normalized retrieval still returns no IDL evidence, retry with the exact
procedure name from the file header or with `list IDL plotting procedures`.

## Distill Protocol

Use this protocol when a chat history, transcript, or session export asks for
evaluation of IDL visualization behavior and improvement proposals. The goal is
to identify the root cause and the smallest general fix, not to optimize only
the one visible task.

### 1. Reconstruct the Intended Workflow

From the chat history, extract:

- the user's original goal and requested output artifact
- the selected primary skill and any support skill that should have been loaded
- the MCP calls made, their factual outputs, and whether evidence was normalized
- shell commands or local inspections that happened after MCP evidence
- the final user-visible result, including whether files were generated
- points where the agent switched strategy, stalled, guessed, or retried

Classify each step as evidence gathering, workflow inference, execution,
verification, or fallback. This keeps tool failures separate from skill policy
failures.

### 2. Evaluate Success and Failure

Judge the session against the IDL skill/MCP contract:

- Did the agent inspect artifacts before choosing variables, frames, or format?
- Did it use normalized `get_evidence` queries for `func`, `plotmode`,
  procedures, export, transforms, logs, or scripts?
- Did MCP remain evidence-only, without recommendations or next actions?
- Did the skill infer the workflow from evidence instead of broad search output?
- For artifact generation, did the agent generate and run IDL `.pro` code before
  attempting Python/SVG/manual binary rendering?
- Was the generated `.pro` a SWMF macro-first driver that configured documented
  entrypoints such as `read_data`, `plot_data`, `show_data`, `animate_data`,
  `plot_log_data`, or `slice_data`, rather than hand-written direct graphics?
- Did the final answer separate deterministic facts, inferences, completed
  artifacts, failed commands, and unknowns?

When a task succeeded slowly, distinguish "correct but inefficient" from
"wrong workflow." When a task failed, distinguish missing evidence, missing
skill instruction, missing MCP evidence shape, runtime environment failure, and
agent execution mistake. If the agent wrote low-level IDL graphics while SWMF
macros could have handled the request, classify that as a skill/execution
ladder failure, not merely a stylistic difference.

### 3. Root-Cause Pattern

Prefer one concise root-cause statement with supporting observations:

- **Skill gap**: the skill did not say what to do, what to avoid, or how to
  choose among valid IDL workflows.
- **MCP evidence gap**: the skill needed deterministic facts that existing MCP
  outputs did not expose, such as frame grouping, plot-file header fields, or
  procedure/manual snippets.
- **Boundary violation**: MCP returned advice, or the agent expected MCP to
  choose a workflow.
- **Execution ladder gap**: the agent lacked a clear order for artifact
  generation, verification, export conversion, and fallback.
- **Macro-first gap**: the agent used Python plotting, custom parsers, or
  hand-written IDL graphics instead of configuring existing SWMF IDL macros.
- **Prompt/answer contract gap**: the expected answer did not require the
  fields needed to audit what happened.
- **Environment gap**: IDL or conversion tools failed despite correct skill
  behavior.

Do not propose many unrelated fixes. If multiple issues appear, identify the
highest-leverage cause that would have prevented the most wasted work.

### 4. Propose General Improvements

Each proposed improvement must be generalized beyond the specific run, file, or
plot. Use this shape:

- **Skill change**: what instruction, decision matrix entry, guardrail, answer
  contract, or gold prompt should change.
- **MCP change, only if needed**: what evidence field should be added to
  `inspect_artifact`, `get_evidence`, `get_context`, or `compare_artifacts`.
- **Boundary check**: why the MCP change is evidence-only and why workflow inference remains in the skill.
- **Acceptance test**: one protocol, skill-layout, or MCP unit test that would
  fail before the fix and pass after it.

Prefer compact skill instructions over copying large manual sections. Prefer
extending existing MCP tools over adding public `idl_*` tools. Add a new public
tool only if the change gate in this document is satisfied. For IDL rendering
failures, first ask whether a stronger SWMF macro-first skill instruction would
have prevented the problem; add MCP fields only when the skill lacks factual
evidence, not when the agent ignored available procedures.

### 5. Ask Immediately When Intent Is Ambiguous

If the chat history does not reveal what kind of improvement the user wants,
ask before proposing a detailed plan. Ask especially when choosing between:

- stricter skill instructions versus new MCP evidence fields
- enforcing IDL execution versus documenting a non-executing advisory workflow
- optimizing speed versus maximizing diagnostic detail
- changing answer contracts versus changing implementation behavior
- adding tests only versus changing runtime tool output

The question should name the tradeoff and its consequence. Do not ask questions
whose answers can be discovered from the transcript, repository, or MCP output.

### 6. Output Shape

For a distilled improvement proposal, include:

- `observed_behavior`
- `successes`
- `failures_or_waste`
- `root_cause`
- `generalized_improvement`
- `skill_changes`
- `mcp_changes_if_needed`
- `tests_or_gold_prompts`
- `open_question`, only when user preference is required

Keep the proposal concrete enough that another agent can implement it directly,
but avoid task-specific filenames or one-off commands unless they are used only
as examples.

## Answer Contracts

For IDL inventory answers:

- authority level
- entrypoints
- helpers or supporting routines
- source paths
- verification note

For IDL usage answers:

- authoritative procedure
- artifact assumptions
- function definition evidence
- plotmode evidence
- copy-paste-ready IDL example
- uncertainty

For IDL plot workflows:

- target artifact
- read step
- `func` choice
- `plotmode` choice
- optional transform or slice
- copy-paste-ready IDL example
- known unknowns

## Evaluation Tasks

Use these prompts as the initial gold set:

- "List the IDL plotting procedures in SWMF."
- "How do I plot density from this run directory with IDL?"
- "How do I use `plot_data` with `func='bx;bz'`?"
- "What `plotmode` should I use for streamlines on an irregular 2D grid?"
- "How do I animate multiple frames from an IDL plot file?"
- "How do I plot a quantity from a SWMF log file in IDL?"
- "How do I transform an unstructured grid to a regular grid before plotting?"
- "How do I cut a 3D result down to a 2D plane or coarsen vectors with `triplet`?"
- "How do I compare two IDL plot files and plot `w=w1-w0`?"
- "How do I export an IDL plot to PDF and save an animation as MP4?"
- "How do I turn my IDL plotting commands into a reusable `@script` or `pro` file?"

Concrete `Run_Max_RP_CME3` evaluation:

- Prompt: "animate IH results (z=0 cut, visualize U overlayed with bx by vectors) in Run_Max_RP_CME3"
- First resolve the existing run directory `SWMFSOLAR/Run_Max_RP_CME3/run01`;
  prefer it over `Run_Max_RP_CME3.tar.gz`, which is only a fallback/source archive.
- First MCP call:
  `inspect_artifact(artifact_type="run_dir", path="Run_Max_RP_CME3", question="animate IH z=0 .out snapshots")`
- If the relative path is missing, `inspect_artifact` should return
  `path_search_candidates` that include the real `.../SWMFSOLAR/Run_Max_RP_CME3/run01`.
- Normalized evidence calls include
  `get_evidence(query="animate_data", mode="keyword", goal="IDL procedure signature and usage")`,
  `get_evidence(query="func", mode="keyword", goal="IDL visualization manual detail")`,
  and `get_evidence(query="plotmode", mode="keyword", goal="IDL visualization manual detail")`.
- The final shell setup should include:
  `cd /Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01/IH`
  and `cat z=0_var_3_t*.out > z=0_var_3.outs`.
- The final IDL sketch should include `filename='z=0_var_3.outs'`,
  `func='u bx;by'`, `plotmode='contbar vectorover'`, and `animate_data`.
- For a first/middle/last still-image export, the final workflow should include
  generated `analysis/z0_u_bxy_export.pro`, an `idl` command that runs it, an
  `analysis/z0_u_bxy_export.idl.log` transcript, and PS/EPS-to-PNG conversion
  after IDL succeeds.
- The answer should say IDL was not executed unless the environment was
  explicitly inspected and an IDL command actually ran.

For each task, record:

- selected primary skill
- first MCP tool
- whether deterministic IDL catalog evidence was returned
- whether shell fallback was needed
- whether MCP emitted advice instead of evidence
- whether the final answer separated certainty from inference

## Change Gate

Before adding any new public MCP surface for IDL, verify all are true:

- the evidence is deterministic or structurally extractable
- `get_evidence` and `inspect_artifact` cannot express it cleanly
- at least two skills need the same evidence
- the new output is evidence-only
- the new tool will not overlap with existing public tools

If any condition fails, refine the skill or extend the existing tool output
shape instead.
