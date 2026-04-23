# IDL Visualization Playbook

Use this playbook for:
- listing IDL plotting procedures
- explaining how to use `plot_data`, `plot_func`, `show_data`, or `animate_data`
- mapping a requested plotted quantity such as `U` to its definition in `funcdef.pro`
- giving in-repo examples for SWMF plotting workflows

## Authority Order
1. `get_evidence(mode="keyword", goal="IDL procedure")`
2. `get_evidence(mode="keyword", goal="IDL plotting procedure entry points")`
   narrowed to the returned procedure or category candidates
3. Direct reads from `share/IDL/General/procedures.pro` only when named by v2 evidence
4. Direct reads from `share/IDL/General/funcdef.pro` only when named by v2 evidence
5. Direct reads from example files under `share/IDL/**` only when named by v2 evidence

## Allowed First Tools
### Inventory questions
Examples:
- "list all idl plotting procedures in SWMF"
- "which plotting macros exist"

First tool:
```
get_evidence(mode="keyword", goal="IDL plotting procedure entry points")
```

Precision follow-up:
- a second `get_evidence(mode="keyword", goal="IDL plotting category detail")`
  query narrowed to the returned candidate procedures or files

Follow-up discipline:
- Treat the returned `category` as a candidate label, not final truth.
- Verify representative items with narrowed `get_evidence` queries or direct
  source reads on named files.
- Split the final answer into `entry_points` and `helpers_or_supporting_routines`.

### Usage questions
Examples:
- "how do I plot func U"
- "how do I use plot_func for SC z=0"

First tool:
```
get_evidence(mode="keyword", query=<procedure_name>, goal="IDL procedure signature and usage")
```
Precision follow-up:
- `get_evidence(mode="keyword", goal="IDL procedure signature and usage detail")`

Then gather, in order:
1. Relevant section in `procedures.pro`
2. Relevant section in `funcdef.pro` if a function string or variable semantics are involved
3. One or more concrete example files from `share/IDL/**`

## Required Evidence Patterns
### Listing procedures
Always identify:
- `entry_points`
- `helpers_or_supporting_routines`
- `source_paths`
- `verification_note`

Typical entry points include:
- `plot_data`
- `show_data`
- `animate_data`
- `plot_func`
- `plot_log`

Helpers such as formatting, prompting, or utility transforms must not be presented as if they are the main user-facing plotting interface.

### Explaining `func`
If the user asks about plotting a quantity like `U`, confirm it in `funcdef.pro`.

Minimum required explanation:
- where the plotting procedure consumes `func`
- how the function name is interpreted
- the specific definition of the requested quantity
- one copy-paste-ready example from the repo or a repo-grounded adaptation

## Zero-Result Recovery Rule
If `get_evidence` returns zero results:
- do not retry with near-duplicate queries
- move to direct source reads or example files only if the first v2 result named them

## Final Answer Requirements
For inventory answers include:
- `authority_level`
- `entry_points`
- `helpers_or_supporting_routines`
- `source_paths`
- `verification_note`

For usage answers include:
- `authoritative_procedure`
- `function_definition_evidence`
- `example_files`
- `assumptions`
- `copy_paste_ready_example`
