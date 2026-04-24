# Plan: Enrich `inspect_artifact` run-directory inspection with `PARAM.in` context

## Problem

`inspect_artifact(artifact_type="run_dir")` currently reports run layout, status files, logs, job scripts, and output-file grouping, but it does not surface a structured understanding of what the run is configured to do in `PARAM.in`.  
The goal is to include deterministic `PARAM.in` interpretation (physical settings, sessions, and saved-plot configuration) directly in run-directory inspection so downstream skills (especially postprocessing) can reason from one artifact call.

## Proposed approach

1. Extend deterministic `PARAM.in` extraction used by `inspect_artifact(artifact_type="param")` to emit richer typed findings:
   - session structure and key command timeline
   - physical/control settings summary
   - `#SAVEPLOT` blocks (plot form/area/vars, save cadence, and related options)
2. Integrate this extraction into `inspect_artifact(artifact_type="run_dir")`:
   - when `PARAM.in` exists, inspect and attach a concise param summary plus structured findings
   - when missing/unreadable, add explicit finding with uncertainty
3. Use `PARAM.XML`/reference metadata where helpful for command normalization and confidence, while keeping outputs evidence-only.
4. Keep the public MCP tool surface unchanged and preserve existing run-dir findings for backward compatibility.
5. Add/extend tests and skill docs so run-dir inspections consistently expose PARAM-derived context.

## Todos

1. **audit-inspect-artifact-contract**
   - Confirm existing output shape and finding kinds in `inspect_artifact.py` and tests.
   - Identify backward-compatible extension points for new `param_*` finding kinds.

2. **implement-param-semantics-extraction**
   - Add focused extraction for:
     - physical/control settings from key PARAM commands
     - session-level command structure
     - `#SAVEPLOT` definitions and plot variable payloads
   - Keep parser deterministic and resilient to partial/malformed input.

3. **wire-param-into-run-dir-inspection**
   - Update `_inspect_run_dir` to detect `PARAM.in`, invoke param extraction, and append summarized findings.
   - Include enough detail for postprocessing skills without overwhelming payload size.

4. **align-skill-and-protocol-docs**
   - Update relevant skill docs (run/analyze/postproc/params) to state that run-dir inspection now includes PARAM-derived run-intent evidence.
   - Keep language aligned with evidence-only MCP protocol in `docs/skill_mcp_protocol.md`.

5. **add-regression-and-feature-tests**
   - Extend `tests/test_api_v2_phase1.py` for:
     - run-dir includes PARAM-based findings when `PARAM.in` exists
     - saved-plot extraction fields are present and stable
     - missing `PARAM.in` behavior remains explicit and non-fatal

## Notes and considerations

- Do not add a new public MCP tool; this is an `inspect_artifact` enhancement.
- Keep legacy finding kinds intact; only add new typed findings.
- Prefer reusable parser helpers over embedding complex PARAM logic directly in `_inspect_run_dir`.
- Ensure output remains factual (no prescribed workflow steps in tool payload).
- Scope decision confirmed: run-dir mode should include a concise PARAM summary plus saved-plot essentials by default; full PARAM detail remains in `artifact_type="param"`.
