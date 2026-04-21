# IDL Visualization Playbook

Use this playbook for:
- listing IDL plotting procedures
- explaining how to use `plot_data`, `plot_func`, `show_data`, or `animate_data`
- mapping a requested plotted quantity such as `U` to its definition in `funcdef.pro`
- giving in-repo examples for SWMF plotting workflows

## Authority Order
1. `swmf_list_idl_procedures(category="plotting")`
2. `swmf_explain_idl_procedure`
3. Direct reads from `share/IDL/General/procedures.pro`
4. Direct reads from `share/IDL/General/funcdef.pro`
5. Direct reads from example files under `share/IDL/**`
6. Heuristic tools such as `swmf_search_source` only if the authoritative path leaves a gap

## Allowed First Tools
### Inventory questions
Examples:
- "list all idl plotting procedures in SWMF"
- "which plotting macros exist"

First tool:
- `swmf_list_idl_procedures(category="plotting")`

Follow-up discipline:
- Treat the returned `category` as a candidate label, not final truth.
- If the result set contains obvious helpers or generic utilities, verify representative items with `swmf_explain_idl_procedure` or direct source reads before presenting them as primary plotting entry points.
- Split the final answer into `entry_points` and `helpers_or_supporting_routines`.

### Usage questions
Examples:
- "how do I plot func U"
- "how do I use plot_func for SC z=0"

First tool:
- `swmf_explain_idl_procedure`

Then gather, in order:
1. Relevant section in `procedures.pro`
2. Relevant section in `funcdef.pro` if a function string or variable semantics are involved
3. One or more concrete example files from `share/IDL/**`

Only use heuristic search if the above do not answer the question.

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
If `swmf_search_source` or another heuristic retrieval step returns zero results:
- do not retry with near-duplicate natural-language queries first
- instead move back to `swmf_explain_idl_procedure`, direct source reads, or example files

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