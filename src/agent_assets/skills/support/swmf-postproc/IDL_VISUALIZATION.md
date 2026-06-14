# IDL Visualization Playbook

Use this playbook only as a support policy for `swmf-analyze` or
`swmf-compare`. The entry skill owns the final answer; this file defines how to
gather and normalize IDL visualization evidence.

## Supported Intents

- IDL setup and startup path guidance
- snapshot reading with `read_data`
- quick read-and-plot workflows with `show_data`
- plotting loaded snapshots with `plot_data`
- animation or multi-snapshot workflows with `animate_data`
- log and satellite plotting with `read_log_data`, `plot_log_data`, or `show_log_data`
- `func` selection, derived quantities, vector pairs, and `funcdef.pro` lookup
- `plotmode` selection for 1D, 2D scalar, vector, stream, contour, polar, and overplot modes
- non-regular grid handling, regular-grid transforms, slices, cuts, and graphics export
- listing IDL plotting procedures and separating entrypoints from helpers

## Not In Scope

- diagnosing failed IDL execution beyond basic artifact observations
- changing SWMF output configuration; hand back to `swmf-configure`
- comparing two completed plots or runs; use `swmf-compare`
- inventing IDL function definitions without evidence from `funcdef.pro` or docs

## Evidence Order

1. If a run directory or output file is named:
   `swmf inspect --type run_dir|result --path <path>`
2. Normalize the prompt before retrieval:
   - named procedure or workflow: `plot_data`, `show_data`, `read_data`, `animate_data`, `plot_log_data`, `read_log_data`
   - inventory request: `list IDL plotting procedures`
   - manual detail: `func`, `plotmode`, `transform`, `slice`, `export`
   - if the prompt is broad, do not pass it through unchanged to `swmf get-evidence`
3. For named procedures or procedure inventories:
   `swmf get-evidence --query "<normalized procedure-or-inventory-task>" --mode keyword --goal "IDL procedure signature and usage"`
   - for animations, normalize to
     `swmf get-evidence --query "animate_data" --mode keyword --goal "IDL procedure signature and usage"`
4. For `func`, `plotmode`, transform, slicing, animation, log plotting, or export details:
   `swmf get-evidence --query "<normalized specific-term>" --mode keyword --goal "IDL visualization manual detail"`
5. For postprocessing entrypoints:
   `swmf get-evidence --query "IDL postprocessing" --task-type analysis --goal "IDL visualization entrypoints"`
6. Direct file reads are allowed only for files named by evidence, normally:
   `share/IDL/General/procedures.pro`, `share/IDL/General/funcdef.pro`,
   examples under `share/IDL/**`, or `docs/idl.md`.

## swmf CLI Evidence Contract

IDL evidence from the swmf CLI must stay factual:

- procedure name, kind, signature, keywords, category, source path, and line
- run-directory inventory and result-file type
- documentation snippets for `read_data`, `plot_data`, `show_data`, `animate_data`, `func`, `plotmode`, transforms, and export
- example file paths and exact snippets
- uncertainty such as missing IDL catalog, missing output path, or uninspected runtime behavior

If a vague request arrives, the support skill should first rewrite it into one
of the normalized retrieval forms above. If the normalized query still returns
no IDL evidence, fall back to the artifact name, a term from the file header, or
an exact procedure name mentioned in docs.

The swmf CLI must not emit recommended workflows, next tools, or plotting advice. The
agent infers the workflow from this playbook and the evidence.

## Decision Matrix

- Quick single plot: `show_data`.
- Controlled single snapshot: `read_data` followed by `plot_data`.
- Controlled single snapshot export: generated `.pro` script with `read_data`, `set_device`, `plot_data`, and `close_device`.
- Multiple selected snapshot exports: generated `.pro` script that loops over files with `read_data`, `set_device`, `plot_data`, and `close_device`.
- Multiple frames or files: `animate_data`.
- Multiple frames, full frame series, or movies: generated `.pro` script with `animate_data`.
- Logfile columns: `read_log_data` followed by `plot_log_data`, or `show_log_data`.
- Derived logfile quantities: read the log as 1D data with `read_data`, then use `plot_data`.
- Structured 3D slice scan: `read_data`, configure `func`/`plotmode`, then `slice_data`.

## IDL-First Execution Ladder

For requests that ask Codex to create a plot, image, movie, or export artifact,
use IDL as the renderer by default and use SWMF IDL macros before custom
graphics:

1. Inspect the named run directory or result file with the swmf CLI. Use the evidence only
   to identify the artifact, variables, output groups, and example filenames;
   do not manually reconstruct the plotted data unless IDL cannot run. Never
   open or parse SWMF output files with common command-line tools; use IDL/SWMF
   procedures for the data.
2. Retrieve deterministic IDL evidence for the chosen SWMF entrypoint and for
   `func`, `plotmode`, and `export`.
3. Create an `analysis/` directory next to the relevant output files and write a
   case-local `.pro` command script there. Put local plot choices near the top:
   `workdir`, `files`, `func`, `plotmode`, `plottitle`, `outbase`,
   `autorange`, `showxtitle`, and `showytitle`.
   For Codex-generated exports, prefer a command-style `analysis/<name>.pro`
   driver over a reusable procedure unless arguments or reuse are required.
   The script should be a macro driver that sets documented variables and then
   calls `read_data`, `plot_data`, `show_data`, `animate_data`,
   `plot_log_data`, or `slice_data`.
4. Execute the script with `idl`, capturing the transcript as
   `analysis/<outbase>.idl.log`, for example:
   `printf '@analysis/z0_u_bxy_export\nexit\n' | idl > analysis/z0_u_bxy_export.idl.log 2>&1`
5. Verify expected `.ps`, `.eps`, `.pdf`, `.png`, or movie outputs exist before
   presenting them as completed artifacts.
6. Only use Python, SVG, manual Fortran-record plotting, or hand-written IDL
   direct graphics (`contour`, `vector`, `triangulate`, `tvrd`, custom readers)
   as a last resort after IDL macro execution fails or evidence shows the SWMF
   macros cannot express the requested output, and the user explicitly accepts
   that fallback; do not hand-write
   binary readers or direct graphics before the macro path fails. Do not check for Python plotting libraries before trying the
   IDL path.

Assume `idl` is the preferred deployed renderer for IDL visualization tasks. Do
not spend the main workflow proving IDL installation up front; if execution
fails, inspect the log and then check `IDL_PATH`, `IDL_STARTUP`, and `idlrc`.
Use `retall` only as an interactive recovery command after a failed nested IDL
macro leaves the prompt inside a procedure. Use `set_default_values` to restore
SWMF IDL defaults before rerunning a macro in the same session.

## Workflow Policy

For IDL environment and startup setup:

1. If you can find idl executable, then run idl. 
2. If you cannot find idl, write the script as .pro file and give commands for user
   to execute them manually.

For artifact triage:

1. Distinguish snapshot plot files from time-series logs:
   - `.out` is normally one snapshot, unless the header says otherwise.
   - `.outs` is a concatenated multi-snapshot plot file suitable for `animate_data`.
   - `.log` and `.sat` are log/satellite time series for log workflows.
2. Inspect result files before naming variables. SWMF IDL plot files may be ASCII,
   `real4`, `real8`, or long-header `REAL4`/`REAL8`; use header fields for
   `headline`, `it`, `time`, `gencoord`, `ndim`, `neqpar`, `nw`, `nx`, coordinate
   names, variable names, and parameter names.
3. Treat `.out` files that cannot be decoded as IDL plot files as generic result
   files; state the uncertainty instead of inventing variables.

For a snapshot plot:

1. Establish the target artifact: run directory, `*.out`, `*.outs`, `*.idl`, or log/satellite file.
2. Confirm the IDL entrypoint:
   - use `read_data` then `plot_data` when data is already chosen or multiple settings matter
   - use `show_data` for quick read-or-reread-and-plot
   - use `animate_data` for multiple frames, movies, or time evolution
   - use log procedures for `.log` or satellite time-series data
3. Map the requested quantity to `func`:
   - raw variable names come from the plot-file header
   - predefined names must be confirmed in `funcdef.pro` or `docs/idl.md`
   - expressions are acceptable if grounded in available variables and scalar parameters
   - vector pairs use semicolon syntax such as `ux;uy` or `bx;bz`
4. Select `plotmode` from data dimensionality and grid constraints:
   - 1D: `plot`, `plot_io`, `plot_oi`, `plot_oo`
   - 2D scalar: contour, filled contour, colorbar, polar, `tv`, surface, or shade modes
   - 2D vector: stream, vector, arrow, or velovect modes
   - irregular or generalized grids: prefer contour, filled contour, stream, or vector unless evidence shows a regular transform
5. Add transform or slice setup only when the user asks for it or the artifact requires it.
6. Add graphics export setup only when the user asks for saved files.

For log and satellite data:

1. Use `read_log_data` when the task is selecting existing log columns by name.
2. Use `plot_log_data` after `read_log_data`, or `show_log_data` for quick
   read-and-plot behavior.
3. Use `read_data` on a log only when the user needs derived quantities,
   expressions, or normal `plot_data` behavior for 1D data.
4. Ground log function names in `wlognames`, `show_log_data` prompts, or artifact
   evidence; do not assume a column exists.

For an animation from many single-snapshot plot files:

1. Distinguish `*.out` from `*.outs`: a `*.out` file is one snapshot, while a
   `*.outs` file is the multi-snapshot input expected by `animate_data`.
2. Locate the component output directory and select the desired cut pattern, for
   example `IH/z=0_var_3_t*.out`.
3. If multiple matching `*.out` files are found and no matching `*.outs` file
   exists, propose concatenating them first:
    `cat z=0_var_3_t*.out > z=0_var_3.outs`
4. Then generate a `.pro` file and run `animate_data` with
   `filename='z=0_var_3.outs'`.
5. For non-interactive export, set `showmovie='n'`. Use `savemovie='ps'` for
   robust frame export, or `savemovie='png'` only when IDL image output is known
   to work in the environment.

For transforms and non-regular grids:

1. A negative `ndim` or `gencoord=1` signals generalized/unstructured grid handling.
2. Use `transform='regular'`, `transform='polar'`, `transform='unpolar'`,
   `transform='sphere'`, or `transform='my'` only when supported by manual evidence
   and the requested plot mode benefits from regular coordinates.
3. Configure regular-grid transforms with `nxreg`, `xreglimits`, and
   `dotransform`; use `wreg`/`xreg` when plotting transformed data.
4. If two files must be compared after transform, keep separate arrays such as
   `x1`, `w1`, `xreg1`, `wreg1` and form differences like `w=w1-w0` or
   `wreg=wreg1-wreg0`. If resolutions differ, use `coarsen` only when evidence
   supports the dimensions.

For domain selection, cuts, and vectors:

1. For flat 2D plots, `!x.range` and `!y.range` are the broadest domain limits;
   reset them with `!x.range=0` and `!y.range=0`.
2. For transformed regular grids, use `xreglimits` to limit the transformed
   domain.
3. For structured grids, use `cut=grid(...)`; use `triplet(...)` or
   `quadruplet(...)` to coarsen and subset index ranges.
4. For vector and streamline placement, use `velpos` and `velvector`; reset with
   `velpos=0` to return to random positions.
5. Use `rcut` to remove data inside a circular/spherical inner radius; `body` in
   `plotmode` only covers that region visually.

For structured 3D slicing:

1. Read the snapshot first with `read_data`; then configure `func`, `plotmode`,
   `slicedir`, `firstslice`, `dslice`, and `nslicemax`.
2. Use `slice_data` to animate or scan slices.
3. If slicing aborts and overwrites `x`/`w`, use `slice_data_restore`.

For comparison and multi-file plotting:

1. Use `animate_data` when comparing multiple plot files or frames with common
   `func`, `plotmode`, and `plottitle` settings.
2. Use per-file arrays such as `filename`, `func_file`, `plotmode_file`, and
   `plottitle_file` when files require different rendering.
3. Use the IDL `compare` workflow or explicit differences (`w=w1-w0`,
   `wreg=wreg1-wreg0`) only after the files have compatible variables and grids.

For multiplot, overplot, and animation storage:

1. Use `multiplot` to control subplot rows, columns, fill order, and starting
   slot; use `showxtitle`/`showytitle` when axis labels must appear on all panels.
2. Use the `over` plotmode modifier, such as `streamover`, `vectorover`, or
   `arrowover`, to draw a later function on an earlier scalar plot.
3. Use `nplotstore` with `max` or `mean` plotmode modifiers when the task asks for
   stored-frame maxima or averages.

For export:

1. For a single plot, wrap `plot_data` or a one-frame `animate_data` call with
   `set_device,'file.eps'` and `close_device`; use `close_device,/pdf` or
   `close_device,pdf='convert',/delete` only when the conversion tool exists.
2. For animation frames, set `savemovie='ps'`, `'png'`, `'tiff'`, `'jpeg'`, or
   `'bmp'`.
3. For video export, set `savemovie='mp4'`, `'mov'`, or `'avi'`, and optionally
   `videofile` and `videorate`, before `animate_data`.
4. When the user asks for PNG output and IDL generates PostScript, convert after
   IDL succeeds:
   `magick -density 180 input.ps -background white -alpha remove input.png`
   Use `convert` only if `magick` is unavailable.
5. Keep the IDL transcript in `analysis/<outbase>.idl.log` and report failed IDL
   execution from that log instead of switching silently to another renderer.

For reusable IDL scripts:

1. Use `@script` for command scripts that run in the current IDL session.
2. Use `.r script` to compile a `.pro` file containing procedures/functions.
3. Write a true `pro name` routine when arguments, local variables, or reuse
   matter; keep case-local filenames and plot choices near the top.

State that `u` is the IDL speed function from `funcdef`, while `Bx` and `By`
are header variables from the IH z=0 files. Mention
`func='u bx;by'` with `plotmode='contbar streamoverbody'` for the standard
speed-plus-Bx/By streamline example. Mention `plotmode='contbar ovelovect'`
only as a denser vector alternative.
For three selected frames, prefer the `files` loop with `read_data` and
`plot_data`; for a full series, use the `.outs` file with `animate_data`.

## Required Answer Shapes

For `idl_inventory`, include:

- `authority_level`
- `entry_points`
- `helpers_or_supporting_routines`
- `source_paths`
- `verification_note`

For `idl_usage_guidance`, include:

- `authoritative_procedure`
- `artifact_assumptions`
- `function_definition_evidence`
- `plotmode_evidence`
- `copy_paste_ready_example`
- `uncertainty`

For `idl_plot_workflow`, include:

- `target_artifact`
- `read_step`
- `func_choice`
- `plotmode_choice`
- `optional_transform_or_slice`
- `generated_pro_script`
- `idl_execution_command`
- `export_files`
- `copy_paste_ready_example`
- `known_unknowns`

## Guardrails

- Do not treat helper routines as the main plotting interface.
- Do not state a variable exists in the output unless it came from artifact inspection, file header evidence, or explicit user input.
- Do not claim IDL is installed or runnable unless the environment was inspected.
- Do not substitute Python/SVG/manual binary plotting for IDL unless IDL failed
  and the user accepted that fallback.
- Prefer commands that can be pasted into an IDL session; label shell setup separately.
- If evidence conflicts, say what is deterministic and what is inferred.
