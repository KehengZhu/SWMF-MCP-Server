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
   ```
   compare_artifacts(
     left  = <baseline_path>,
     right = <modified_path>,
     comparison_type = "param" | "log" | "run_dir" | "auto",
     question = <user question>
   )
   ```
   Read `differences` for structural/value changes.

2. **Inspect the anomalous side** (if one side has errors or a crash):
   ```
   inspect_artifact(artifact_type="log"|"param"|"run_dir", path=<anomalous_path>)
   ```

3. **Source grounding** (only if differences involve non-obvious config or code effect):
   ```
   get_evidence(query=<changed_entity>, mode="hybrid", goal="impact of difference")
   ```

4. Grep: only if Steps 1–3 name a file that evidence missed; restrict to evidence paths.

## Helper skills allowed

* `swmf-debug` — if the anomalous side crashed and needs full failure protocol
* `swmf-params` — if differences involve PARAM schema or validation
* `swmf-postproc` / `swmf-analyze` — if comparison involves output visualization
* `swmf-exact-lookup` — for specific changed symbol confirmation

## Outputs

* differences listed by location: `left_value` vs `right_value`
* each difference classified: "added", "removed", "changed", "structural"
* runtime consequence linked to difference when evidence supports it
* confirmed diffs (from `compare_artifacts`) vs inferred effects separated
* `uncertainty.known_unknowns` surfaced when present
