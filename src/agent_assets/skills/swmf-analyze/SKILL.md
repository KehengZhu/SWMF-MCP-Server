---
name: swmf-analyze
description: "Use when the user wants to interpret SWMF outputs: what results mean, diagnostics from output files, field interpretation, or postprocessing discovery."
---

# swmf-analyze

## When to use
- "What do these output files contain?"
- "How do I plot the result?"
- "How do I visualize this output with IDL?"
- "Which `func` or `plotmode` should I use?"
- "What does this field value mean?"
- "How do I run the postprocessing?"
- "Are my results physically reasonable?"
- Any task about reading, interpreting, or processing simulation outputs

## Do not use when
- User wants to compare two runs → `swmf-compare`
- Something failed → `swmf-debug`
- User wants to configure → `swmf-configure`
- User wants to run → `swmf-run`

## Evidence order

### Output interpretation
1. `inspect_artifact(artifact_type="run_dir", path=<run_dir>)`
   - output file inventory and layout
2. `get_evidence(mode="keyword", goal="output format or field definition")`
   - field semantics, output variable definitions
3. `get_evidence(query="postprocessing", task_type="analysis", goal="postprocessing")`
   - postprocessing scripts and entrypoints

### IDL visualization
1. If a run directory or output file is named, first call `inspect_artifact(artifact_type="run_dir"|"result", path=<path>)`
   - deterministic artifact type, output layout, and likely plot files
   - prefer an existing extracted run directory over an archive when both are present; for `Run_Max_RP_CME3`, use `SWMFSOLAR/Run_Max_RP_CME3/run01` and treat `Run_Max_RP_CME3.tar.gz` only as a fallback/source archive
2. Normalize the user prompt before retrieval:
   - named procedure or workflow: `plot_data`, `show_data`, `read_data`, `animate_data`, `plot_log_data`, `read_log_data`
   - inventory request: `list IDL plotting procedures`
   - manual detail: `func`, `plotmode`, `transform`, `slice`, `export`
   - do not send a broad question such as "how do I visualize this" directly to `get_evidence`
3. Call `get_evidence(query=<normalized IDL procedure or inventory task>, mode="keyword", goal="IDL procedure signature and usage")`
   - deterministic IDL catalog evidence for named procedures or procedure lists
4. Call `get_evidence(query=<normalized func/plotmode/output-format term>, mode="keyword", goal="IDL visualization manual detail")`
   - `func`, `plotmode`, transformation, slicing, save/export, or output-format evidence
5. Load `support/swmf-postproc/IDL_VISUALIZATION.md`
   - detailed policy for composing the plotting workflow
6. For requests to create plot/image/movie artifacts, follow the support
   skill's IDL-first execution ladder:
   - generate a case-local `analysis/<name>.pro`
   - run it with `idl` and capture `analysis/<name>.idl.log`
   - convert IDL PostScript/EPS output to PNG only after IDL succeeds
   - do not switch to Python/SVG/manual binary plotting unless IDL fails and the
     user accepts that fallback

## Helper skills allowed

* `swmf-postproc` — for IDL visualization details and coupling architecture context
* `swmf-exact-lookup` — for specific field name or procedure confirmation

## Outputs

* what output artifacts were found (from `inspect_artifact`)
* field/variable definitions cited from evidence
* postprocessing workflow evidence from `get_evidence(task_type="analysis")`
* for IDL visualization:
  * artifact/file assumptions
  * authoritative IDL entrypoint or procedure
  * required `read_data`/`show_data`/`plot_data` sequence
  * relevant `func` and `plotmode` semantics
  * generated `.pro` script path, `idl` execution command, IDL log path, and
    export files when artifact generation was requested
  * copy-paste-ready IDL command sketch when evidence is sufficient but execution
    was not requested or not possible
  * the normalized query form used for retrieval, when the original prompt was vague
* workflow metadata on returned items:
  * `metadata.kind`
  * `metadata.relative_path`
  * `metadata.why_relevant`
* what is certain vs uncertain about the interpretation
* for IDL: load `swmf-postproc/IDL_VISUALIZATION.md` for full protocol
