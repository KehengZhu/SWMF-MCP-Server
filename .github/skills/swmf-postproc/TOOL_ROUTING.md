# Tool Routing Matrix

Use this matrix after classifying the request family.

## `output_inventory`
Preferred first tools:
- `swmf_collect_run_context`
- `swmf_compare_run_artifacts` when two outputs or runs are involved

## `artifact_comparison`
Preferred first tools:
- `swmf_compare_run_artifacts`
- `swmf_collect_run_context`

## `visualization_planning`
Preferred first tools:
- `swmf_collect_run_context`
- `swmf_find_examples`

## `idl_inventory`
Preferred first tool:
- `swmf_list_idl_procedures(category="plotting")`

Disallowed first tool:
- `swmf_search_source`

## `idl_usage_guidance`
Preferred first tool:
- `swmf_explain_idl_procedure`

Then consult:
- `share/IDL/General/procedures.pro`
- `share/IDL/General/funcdef.pro`
- concrete example files

## `coupling_architecture_explanation`
Preferred first tool:
- `swmf_get_coupling_info`

Disallowed first tool:
- build/readiness tools used only for environment inspection
- heuristic source search without first collecting coupling evidence

## `postprocess_failure_triage`
Preferred first tools:
- `swmf_extract_first_error`
- `swmf_extract_stacktrace`
- `swmf_collect_run_context`

If the request turns into diagnosis with conflicting evidence, hand off to `swmf-debug`.