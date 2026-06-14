---
name: swmf-compare
description: "Use when two SWMF things must be contrasted: run vs run, PARAM file vs PARAM file, output vs output, or config vs config."
---

# swmf-compare

## When to use
- "What changed between run A and run B?"
- "Why does my modified PARAM.in behave differently?"
- "The second run crashed but the first didn't — what's different?"
- "Compare these two output directories"
- Any request to diff, contrast, or explain differences between two artifacts

## Do not use when
- Only one artifact is under investigation → `swmf-debug` (if failed) or `swmf-analyze`
- User wants architecture explanation → `swmf-explain`
- User wants to configure a new case → `swmf-configure`

## Evidence order

1. **Compare artifacts first**:
   ```bash
   swmf compare --left <baseline_path> --right <modified_path> \
     --comparison-type param|log|run_dir|auto \
     --question "<user question>"
   ```
   Read `differences` for structural/value changes. When `--comparison-type run_dir`
   and both sides have a `PARAM.in`, the response includes a `param_diff` entry with a
   per-session command-name diff plus a unified text diff — surface this before falling
   back to file-list deltas.
   Do not directly read whole runlogs unless the user explicitly requests raw
   log content; use bounded excerpts only after tool output names a need.

2. **Inspect the anomalous side** (if one side has errors or a crash):
   ```bash
   swmf inspect --type log|param|run_dir --path <anomalous_path>
   ```
   The param inspector returns structural primitives only (sessions, includes,
   component map, external refs, parser errors); read the PARAM.in directly
   when you need to interpret the failing session or command flow.

3. **Source grounding** (only if differences involve non-obvious config or code effect):
   ```bash
   swmf get-evidence --query "<changed_entity>" --mode keyword --goal "impact of difference"
   ```

4. **IDL visualization comparison** (only when the user asks how to visualize or
   plot the difference):
   - inspect named result files with `swmf inspect --type result --path <path>`
   - normalize broad plotting prompts into `func`, `plotmode`, `transform`, `slice`,
     `compare`, or `animate_data`
   - load `support/swmf-postproc/IDL_VISUALIZATION.md` for the comparison,
     transform, overplot, and export policy
   - if the user asks for plot/image/movie artifacts, use the IDL-first
     generated `.pro` workflow from `swmf-postproc`; do not hand-render the
     comparison in Python/SVG unless IDL fails and the user accepts that fallback

5. Grep: only if Steps 1–4 name a file that evidence missed; restrict to evidence paths.

## Helper skills allowed

* `swmf-debug` — if the anomalous side crashed and needs full failure protocol
* `swmf-params` — if differences involve PARAM schema or validation
* `swmf-postproc` / `swmf-analyze` — if comparison involves output visualization
* `swmf-exact-lookup` — for specific changed symbol confirmation
* `swmf-validation` — when one side is a reference (paper figure, observation, CCMC
  quick-look) rather than another SWMF artifact
* for broad IDL visualization, analysis, or output-comparison plotting, route
  through `swmf-postproc` instead of inventing IDL commands from diffs alone

## Outputs

* differences listed by location: `left_value` vs `right_value`
* each difference classified: "added", "removed", "changed", "structural"
* runtime consequence linked to difference when evidence supports it
* confirmed diffs (from `swmf compare`) vs inferred effects separated
* `uncertainty.known_unknowns` surfaced when present
