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
1. `swmf inspect --type run_dir --path <run_dir>`
   - output file inventory and layout
   - use `run_dir_layout`, `postproc_state`,
     `component_artifact_inventory`, `restart_inventory`, and
     `component_output_artifacts` as the authority for artifact selection
   - after this, read the whole run-local `PARAM.in` yourself and understand
     the run intent, sessions, component setup, stops/runs, save cadence, and
     relevant command blocks before interpreting outputs
   - do not directly read whole runlogs or component directories unless tool
     evidence is missing/unreadable or the user asks for raw content
   - compact runlog status if logs are present; do not directly read whole
     runlogs unless the user explicitly requests raw log content
   - if deeper runlog investigation is needed, run
     `swmf inspect --type runlog --path <runlog>` on the specific
     runlog listed by run-dir inspection
2. `swmf get-evidence --mode keyword --goal "output format or field definition"`
   - field semantics, output variable definitions
3. `swmf get-evidence --query "postprocessing" --task-type analysis --goal "postprocessing"`
   - postprocessing scripts and entrypoints

### IDL visualization
1. If a run directory or output file is named, first run `swmf inspect --type run_dir|result --path <path>`
   - deterministic artifact type, output layout, and likely plot files
   - for `run_dir`, then read the run-local `PARAM.in` completely and reason
     from the actual file contents; do not rely on `swmf inspect` for
     PARAM semantics beyond brief presence/counts and output-artifact matching
   - for `run_dir`, use `run_dir_layout`, `postproc_state`,
     `component_artifact_inventory`, `restart_inventory`, and
     `component_output_artifacts` before reading raw artifacts
   - prefer an existing extracted run directory over an archive when both are present; treat a tarball alongside an extracted run as a fallback/source archive only
   - never open or parse `.out`, `.outs`, `.idl`, `.sav`, `.tec`, `.dat`, or
     other SWMF output files with common command-line tools (`cat`, `head`,
     `tail`, `grep`, Python binary readers, ad hoc parsers); use SWMF/IDL
     scripts and procedures selected from evidence
2. Normalize the user prompt before retrieval:
   - named procedure or workflow: `plot_data`, `show_data`, `read_data`, `animate_data`, `plot_log_data`, `read_log_data`
   - inventory request: `list IDL plotting procedures`
   - manual detail: `func`, `plotmode`, `transform`, `slice`, `export`
   - do not send a broad question such as "how do I visualize this" directly to `swmf get-evidence`
3. Run `swmf get-evidence --query <normalized IDL procedure or inventory task> --mode keyword --goal "IDL procedure signature and usage"`
   - deterministic IDL catalog evidence for named procedures or procedure lists
4. Run `swmf get-evidence --query <normalized func/plotmode/output-format term> --mode keyword --goal "IDL visualization manual detail"`
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
* `swmf-debug` — for clear runtime failures reported by run-dir or log evidence
* `swmf-exact-lookup` — for specific field name or procedure confirmation
* `swmf-validation` — when the comparison is against a paper figure, observation trace, or
  other non-SWMF reference rather than another SWMF artifact.

## Outputs

* what output artifacts were found (from `swmf inspect`)
* field/variable definitions cited from evidence
* postprocessing workflow evidence from `swmf get-evidence --task-type analysis`
* for IDL visualization:
  * artifact/file assumptions
  * PARAM-driven output intent (saved plot forms/areas/cadence when available from `swmf inspect --type run_dir`)
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
