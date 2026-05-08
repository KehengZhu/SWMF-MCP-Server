# SWMF Run Replication Plan

## 1. Goal and Scope

### 1.1 Goal

Extend the existing skill+MCP system so an agent can **replicate a SWMF run end-to-end** from a high-level specification. End-to-end means: parse the specification, assemble a run environment (magnetogram, harmonics/FDIPS, includes, jobscript), produce a working `PARAM.in`, build the right SWMF executable, submit and monitor the run on the available cluster, postprocess outputs, visualize, and validate against a reference (paper figure or CCMC quick-look).

### 1.2 Scope

- Source specifications:
  1. A scientific paper (PDF/markdown/text), where the agent must extract the physical scenario, infer parameters, run, visualize, and compare to paper figures.
  2. A structured run specification (e.g. CCMC `Run information _ CCMC.md`), where parameters are explicit and the agent must mechanically translate them into a SWMF run.
  3. An existing prior run directory (e.g. `SWMFSOLAR/Run_Max_RP_CME3/run01`) that should be reproduced (same code, same inputs, same output) or perturbed (same scenario, modified parameter set).
- Target domains: solar/heliosphere CME runs (AWSoM/AWSoMR/SOFIE), with later expansion to geospace and full SWMF couplings.
- Out of scope (Phase 1): autonomous paper PDF parsing without human approval; arbitrary cluster credential management.

### 1.3 Non-goals

- Building a paper-to-PARAM compiler inside MCP.
- Building a cluster orchestration layer inside MCP.
- Bypassing or duplicating SWMFSOLAR. The plan **wraps and codifies** SWMFSOLAR rather than reimplementing it.

---

## 2. Three Driving Scenarios

These three scenarios anchor every design decision below. If a proposed surface does not help all three, it is suspect.

### 2.1 Scenario A — Paper replication

> "Replicate the 2023/02/24 CME run from Sokolov et al. 2023 (or an analogous AWSoM-CME paper). Make a run that reproduces Figure 6 (synthetic LASCO C2 brightness)."

Walkthrough:

1. Agent ingests paper text/figures (user-provided file path or excerpt). Agent extracts: model (AWSoM-R, SOFIE, etc.), event time, magnetogram source (ADAPT/GONG/HMI), CME initiation method (GL flux rope, Titov-Démoulin, cone), key flux-rope parameters, target diagnostics (in-situ comparisons at L1/STA/STB, LASCO synthesis).
2. Agent normalizes to a structured **paper spec** artifact and asks the user to confirm before consuming compute.
3. From the structured spec, the workflow merges with Scenario B.
4. Validation: agent locates paper-style figures, generates equivalent IDL plots, and produces a side-by-side comparison.

### 2.2 Scenario B — CCMC (or other structured) spec replication

> "Run `Weihao_Liu_011326_SH_1` locally — SWMF-AWSoM, 2023-02-24 CME, GL flux rope, MFLAMPA SEP follow-up."

Walkthrough:

1. Agent reads `Run information _ CCMC.md` (or analog) into a structured **ccmc spec** artifact.
2. Agent picks the closest SWMFSOLAR PARAM template (`Param/PARAM.in.sofie.MFLAMPA` for this case; `Param/PARAM.in.awsom.CME` for non-SEP CME background+eruption).
3. Agent identifies required external inputs (magnetogram for 2023/02/24, ADAPT vs GONG fits cube, harmonics file).
4. Agent invokes SWMFSOLAR shell pipeline (`make compile`, `make rundir_local`, `make run`) — possibly via `swmf-replicate` skill — with the specific parameters injected.
5. Agent monitors job, postprocesses, runs the standard CCMC quick-look set (LASCO synthesis, in-situ comparison at STEREO-A/OMNI, MFLAMPA SEP plots).
6. Validation: compare modeled `earth.sat`/`sta.sat` against observation traces (or CCMC reference if downloadable).

### 2.3 Scenario C — Prior run directory replication

> "Reproduce `SWMFSOLAR/Run_Max_RP_CME3/run01` from scratch on Frontera with the same magnetogram and same flux-rope parameters."

Walkthrough:

1. Agent inspects the prior run directory using `inspect_artifact(artifact_type="run_dir")`. Reads `PARAM.in` directly per existing skill protocol.
2. Agent extracts the run's *intent*: components, scheme flags, magnetogram file, harmonics file, GL flux-rope block, sessions, save cadence, satellite list.
3. Agent re-derives the build configuration from `PARAM.in` (`#COMPONENTMAP`, `#COMPONENT`, scheme flags) and the SWMFSOLAR Makefile patterns.
4. Agent assembles a fresh run directory mirroring the prior one and submits the job.
5. Validation: when the new run completes, `compare_artifacts(comparison_type="run_dir", left=<old>, right=<new>)` reports structural/diff parity. Optional output equivalence test on log files and selected `.out` snapshots.

---

## 3. Layer Assignment (Skill / MCP / Shell)

This is the protocol-level decision the rest of the plan depends on.

### 3.1 Rule restated

- **MCP** = deterministic, reusable evidence extraction.
- **Skill** = task policy: when, in what order, with what answer contract.
- **Agent (with shell)** = workflow inference and execution against the real environment.

### 3.2 Concrete assignment for replication

| Concern | Layer | Justification |
| --- | --- | --- |
| Parsing a paper PDF/markdown into a structured spec | Agent (LLM reasoning) + skill output contract | Heuristic extraction; not deterministic; agent-strength task. |
| Parsing a CCMC-style structured spec | Skill normalizes; MCP optionally inspects via `inspect_artifact(artifact_type="ccmc_spec")` for deterministic field surfacing | Structured Markdown/JSON is parseable; multiple skills will reuse. |
| Choosing the PARAM template (AWSoM vs SOFIE vs CME) | Skill (`swmf-replicate`) | Workflow reasoning. |
| Discovering candidate templates | MCP (`get_evidence(task_type="configuration", goal="param template")`) | Retrieval, evidence-only. |
| Composing PARAM.in for a new case (insert `#CME` block, add/reshape sessions, reorder commands, change scheme) | Agent writes PARAM.in directly via Edit/Write, guided by template + PARAM.XML + rules directory | `change_param.py` cannot do structural changes (see §6.5). Composition is workflow reasoning → agent territory. |
| Mechanical parameter sweep over a fixed template structure (e.g. ADAPT realization 1..12, scanning `PoyntingFluxPerBSi`) | Agent shells `change_param.py` from SWMFSOLAR | Deterministic substitution; the script's actual sweet spot. |
| Inspecting a candidate `PARAM.in` for validity | MCP (`inspect_artifact(artifact_type="param", check_rules=True)`) — structural + rule-based | Existing tool extended to consume the user-owned rules directory (§5.4). Stays evidence-only. |
| Authoritative schema validation | Agent shells `Scripts/TestParam.pl` from SWMF root | Already exists; the canonical PARAM.XML check. |
| Discovering jobscript templates | MCP (`get_evidence`) for retrieval; MCP (`inspect_artifact(artifact_type="jobscript")`) for one named file | Multiple skills (`swmf-run`, `swmf-replicate`, future `swmf-resubmit`) need the same evidence: scheduler, node count, tasks-per-node, executable invocation, postproc hooks. **Justified extension.** |
| Magnetogram file: download / locate / classify | Agent shells `download_ADAPT.py`; MCP optionally classifies via `inspect_artifact(artifact_type="magnetogram")` for deterministic header facts (CR number, time, type, resolution) | Download is a network operation; do not put HTTP in MCP. Classification is deterministic file inspection. |
| Building SWMF for the right components | Agent shells `Config.pl` and `make` | Existing `swmf-build`, no change needed. |
| Submitting jobs (sbatch/qsub) | Agent shell | Cluster auth and side-effects belong outside MCP. |
| Monitoring jobs | Agent shell (`squeue`, `qstat`, `tail runlog*`); MCP can re-inspect `run_dir`/`runlog` after each poll | Existing surfaces suffice. |
| Postprocessing | Agent shells `PostProc.pl`; MCP inspects result tree | Existing pattern, no change. |
| IDL visualization | Existing `swmf-postproc` protocol | Already specified. |
| Comparing run vs reference run | MCP `compare_artifacts(comparison_type="run_dir")` already supports it | No change required initially. |
| Comparing model output vs paper figure or observation | Skill (`swmf-validation`) drives; agent uses existing `compare_artifacts` for log/result diffs and IDL for figure overlays. **No new MCP tool.** | Image-level visual comparison is judgmental and cross-domain; not deterministic in the MCP sense. |
| Paper-PDF retrieval | Agent + skill (load file) | Neither deterministic enough nor SWMF-local enough for MCP. |

### 3.3 Why not new public MCP tools (`assemble_param`, `submit_job`, `fetch_external_data`)

Apply the change gate from `skill_mcp_protocol.md` §"How to Add or Change an MCP Tool":

- `assemble_param`: would embed workflow ("merge template + spec + magnetogram path"). That is policy, not evidence. **Reject.** SWMFSOLAR's `change_param.py` is the deterministic step the agent shells; MCP only inspects the resulting `PARAM.in`.
- `submit_job`: side-effecting, environment-dependent, never reusable as evidence. **Reject.**
- `fetch_external_data`: network calls, secrets, retries, server-side semantics. **Reject.** Reuse `download_ADAPT.py` and similar scripts; MCP only inspects the local artifact afterwards.

Each of these would also bloat the public surface. The protocol explicitly favors broad-typed inspection over many narrow tools.

---

## 4. New / Modified Skills

### 4.1 New entry skill: `swmf-replicate`

Single entry skill, **two intents** declared inside via input contract: `intent="paper" | "structured_spec" | "prior_run"`. Justification for one skill not three: same answer contract, same evidence ladder after spec normalization, same hand-offs to `swmf-build`/`swmf-run`/`swmf-analyze`. Splitting would duplicate policy.

#### 4.1.1 When to use

- "Run this paper's case from scratch."
- "Replicate this CCMC run locally."
- "Reproduce `Run_Max_RP_CME3/run01` on Frontera."
- "Build a new run for the 2023-02-24 CME like this paper says."

#### 4.1.2 When not to use

- User wants to interpret an *existing* run → `swmf-analyze`.
- User wants to compare two existing runs without producing a new one → `swmf-compare`.
- User wants to debug a failed run → `swmf-debug`.
- User asks "how does AWSoM-CME work?" without intent to run → `swmf-explain`.

#### 4.1.3 Required inputs (from agent intake)

- One of: paper file path, structured-spec file path, prior run directory path.
- Target environment: `cluster=frontera|pleiades|derecho|local`.
- Optional: target SWMF source path; output root.

#### 4.1.4 Evidence order

1. Spec inspection.
   - For `prior_run`: `inspect_artifact(artifact_type="run_dir", path=<dir>)` then read the run-local `PARAM.in` directly (existing pattern from `swmf-run`).
   - For `structured_spec`: `inspect_artifact(artifact_type="ccmc_spec", path=<file>)` (new, see §5).
   - For `paper`: skill prompts the agent to produce a structured `paper_spec` JSON and confirm with the user; agent then optionally writes that spec to a file and calls `inspect_artifact(artifact_type="paper_spec", path=<file>)` to surface the deterministic fields it contains.
2. Template discovery.
   - `get_evidence(query="AWSoM CME PARAM template" or similar normalized term, task_type="configuration", goal="PARAM template selection")`.
3. Magnetogram and harmonics evidence.
   - `inspect_artifact(artifact_type="magnetogram", path=<fits|map>)` when a file is named or downloaded.
   - `get_evidence(query="ADAPT magnetogram download", task_type="configuration", goal="magnetogram acquisition entrypoint")` when nothing is named — returns SWMFSOLAR's `download_ADAPT.py` as the entrypoint.
4. Build evidence.
   - Hand off to `swmf-build`; reuse its evidence order.
5. Job assembly.
   - `inspect_artifact(artifact_type="jobscript", path=<file>)` (new) on the chosen template.
   - `get_evidence(query="job script <cluster>", task_type="run", goal="cluster submission template")` if no template is named.
6. PARAM.in generation (per §6.5).
   - Classify as **sweep** vs **construction**.
   - For sweep: agent shells `change_param.py` with a typed dict over the chosen template.
   - For construction: agent writes PARAM.in directly, guided by template + PARAM.XML + `swmf-params/rules/`.
7. Pre-launch validation gate (per §6.5).
   - `inspect_artifact(artifact_type="param", path=<PARAM.in>, check_rules=True)` — structure + rule violations.
   - Agent shells `Scripts/TestParam.pl` — schema authority.
   - PARAM diff vs base template surfaced with evidence citation per change.
   - `inspect_artifact(artifact_type="run_dir", path=<assembled>)` and `inspect_artifact(artifact_type="jobscript", path=<assembled>/job.*)`.
   - **Hard rule**: launch is blocked if any rule with `severity=block` fails or `TestParam.pl` errors. User approval is recorded before submission.
8. Launch.
   - Agent shells `sbatch`/`qsub`/`mpirun`. Skill output contract requires the agent to record the launch command and job id.
9. Monitoring.
   - Agent shell + periodic `inspect_artifact(artifact_type="run_dir")` and `inspect_artifact(artifact_type="runlog")`.
10. Postprocessing and visualization.
    - Hand off to `swmf-analyze` for IDL; the support skill `swmf-postproc` already owns this. No new policy here.
11. Validation.
    - Hand off to new support skill `swmf-validation` (§4.3.3).

#### 4.1.5 Output contract

Required fields:

- `intent` — one of `paper|structured_spec|prior_run`.
- `normalized_spec` — the structured representation, with explicit fields surfaced (model, event time, magnetogram source/file, B0 method, FR type, FR params, target diagnostics, target cluster).
- `template_choice` — picked PARAM template plus evidence path (e.g. `SWMFSOLAR/Param/PARAM.in.awsom.CME`).
- `external_inputs` — magnetogram file, harmonics file, restart source, with provenance (downloaded vs reused vs inferred).
- `build_plan` — `Config.pl` invocations and `make` targets, with citations to evidence.
- `assembled_run_dir` — path of the constructed run directory and its readiness diff vs `swmf-run` checks.
- `launch_command` — exact command actually executed (or "not executed" with reason).
- `job_status_chain` — list of (timestamp, status, evidence path) entries.
- `postproc_plan` — `PostProc.pl` invocation + IDL targets.
- `validation_plan` — references to paper figures or CCMC quick-look targets, mapped to local artifacts.
- Explicit separation of **confirmed** vs **inferred** vs **assumed** for every field.
- `uncertainty.known_unknowns` — e.g. unknown magnetogram CR alignment, unverified flux-rope sign convention, paper figure quality.

#### 4.1.6 Helper skills allowed

- `swmf-configure` (for PARAM construction details).
- `swmf-build` (for build orchestration).
- `swmf-run` (for run-dir readiness and submission ladder).
- `swmf-analyze` (for postprocessing and IDL).
- `swmf-compare` (for prior-run parity check).
- `swmf-magnetogram` (new support, §4.2).
- `swmf-jobscript` (new support, §4.3.1).
- `swmf-cme-setup` (new support, §4.3.2).
- `swmf-validation` (new support, §4.3.3).
- `swmf-swmfsolar` (new support, §4.3.4).

#### 4.1.7 Anti-pattern guard

The skill must not invent magnetogram URLs, paper-extracted parameters, or cluster commands without evidence; if a field is inferred from paper text, it must be marked inferred and listed under `uncertainty.known_unknowns` until validated against either a SWMFSOLAR template, a structured spec, or a prior run.

### 4.2 New support skill: `swmf-magnetogram`

Owns the policy of "what is a valid magnetogram input for SWMF, where do you get it, how is it referenced from PARAM/HARMONICS/FDIPS." Loaded by `swmf-replicate` and `swmf-configure` when a magnetogram is involved.

- Scope: ADAPT vs GONG vs HMI vs MDI; FITS vs `.dat` (`map_NN.out`) vs harmonics coefficient files; how `HARMONICS.in`, `FDIPS.in`, and `#HARMONICSFILE` reference them.
- Tool protocol:
  1. `get_evidence(query="magnetogram", task_type="configuration", goal="magnetogram entrypoint and file conventions")`.
  2. `inspect_artifact(artifact_type="magnetogram", path=<file>)` (new artifact type, §5.1).
  3. Direct reads only of files named by evidence.
- Output contract: file type, time/CR coverage, expected SWMF reference path, downstream PARAM commands that consume it.

### 4.3 New support skills

#### 4.3.1 `swmf-jobscript`

Owns scheduler-aware policy: SLURM (Frontera/local), PBS (Pleiades/Derecho), local mpirun. Loaded by `swmf-run` and `swmf-replicate`.

- Tool protocol:
  1. `inspect_artifact(artifact_type="jobscript", path=<file>)` (new, §5.2).
  2. `get_evidence(query="job script <cluster>", task_type="run", goal="cluster submission template")`.
- Output contract: scheduler, node count, tasks-per-node, total ranks, walltime, executable invocation order (FDIPS → SWMF → PostProc), substitution points (jobname, runtime, allocation).

#### 4.3.2 `swmf-cme-setup`

Owns CME initiation policy specifically: GL vs Titov-Démoulin vs cone; what fields each requires; how `#CME` block parameters map to physical quantities; how multi-session PARAM (background → eruption → relaxation) is structured.

- Tool protocol:
  1. `get_evidence(query="#CME", mode="keyword", goal="param definition")`.
  2. `get_evidence(query="GL flux rope", task_type="configuration", goal="CME initiation")`.
  3. Direct reads only of files named by evidence (e.g. `Param/PARAM.in.awsom.CME`, `Run_Max_RP_CME3/run01/PARAM.in`).
- Output contract: TypeCme value chosen, parameter mapping table from spec to PARAM block, multi-session structure with #STOP boundaries justified.

#### 4.3.3 `swmf-validation`

Owns "compare run output against reference" policy: paper figure vs IDL render, observation traces (OMNI, STEREO) vs satellite output, CCMC quick-look vs local equivalent.

- Tool protocol:
  1. `inspect_artifact(artifact_type="run_dir", path=<run>)` for output inventory.
  2. `inspect_artifact(artifact_type="result", path=<file>)` for individual outputs.
  3. `compare_artifacts(comparison_type="result"|"log"|"run_dir", left=<reference>, right=<modeled>)`.
  4. Hand-off to `swmf-postproc` for IDL overlay/animation rendering.
- Output contract: list of validation targets; for each, `reference_artifact`, `modeled_artifact`, `comparison_method` (deterministic diff, IDL overlay, statistical metric), and `result` (matched / divergent with notes).
- Explicit boundary: this skill does not classify a paper figure as "matched" by image inspection alone; it drives an IDL-rendered equivalent and asks the user to confirm visually unless a numerical metric is available.

#### 4.3.4 `swmf-swmfsolar`

Owns "the SWMFSOLAR project is the canonical operational driver — these are its scripts and Makefile targets."

- Scope: Makefile targets (`adapt_run_w_compile`, `adapt_run`, `compile`, `rundir_local`, `rundir_realizations`, `run`, `check_postproc`, `check_compare_*`); Scripts (`change_awsom_param.py`, `change_param.py`, `download_ADAPT.py`, `sub_runs.py`, `watch_runlog.py`, `compare_insitu.py`); JobScripts directory; Param directory; ParamListScripts directory.
- Tool protocol:
  1. `get_evidence(query="<task>", task_type="configuration|run|analysis", goal="SWMFSOLAR entrypoint")`.
  2. Direct reads only of files named by evidence.
- Output contract: which SWMFSOLAR Makefile target/script handles the request, its required arguments, and its known constraints.
- Justification: SWMFSOLAR encapsulates years of operational know-how; the alternative (each skill rediscovering it) wastes evidence calls. Treating it as a first-class support skill makes the dependency explicit.

### 4.4 Modifications to existing skills

- `swmf-configure`: add a section "When the target is a full case replication, defer to `swmf-replicate`." Add reference to `swmf-cme-setup` and `swmf-magnetogram` as helpers when CME or magnetogram fields appear.
- `swmf-run`: add `swmf-jobscript` as a helper. Add a sentence requiring `inspect_artifact(artifact_type="jobscript")` when a candidate job file is named.
- `swmf-analyze`: add `swmf-validation` as a helper for "compare to paper / observation" requests.
- `swmf-compare`: add `swmf-validation` as a helper when one side is a reference (paper/observation) rather than a SWMF artifact.
- `swmf-build`: no change in evidence order; add a note that for AWSoM/SOFIE replication, `swmf-swmfsolar` provides canonical Config.pl and `make` patterns.

---

## 5. MCP Changes (Accept/Reject Table)

Apply the gate from `skill_mcp_protocol.md`. The preferred shape is **extending `inspect_artifact` with new artifact types** rather than adding new public tools.

### 5.1 Accept/Reject

| Proposal | Decision | Rationale |
| --- | --- | --- |
| Extend `inspect_artifact` with `artifact_type="magnetogram"` | **Accept** | Deterministic header fields (FITS keywords, CR number, time, type, latitude/longitude grid, file format). Used by `swmf-magnetogram`, `swmf-replicate`, `swmf-cme-setup`. Existing `inspect_artifact` already handles other binary-adjacent files; adding magnetogram is a typed extension, not a new contract. |
| Extend `inspect_artifact` with `artifact_type="jobscript"` | **Accept** | Multiple skills (`swmf-run`, `swmf-jobscript`, `swmf-replicate`) repeatedly need scheduler/nodes/tasks-per-node/walltime/executable invocations. Pure regex/structural extraction. Authority-1 fact source per the evidence ladder. |
| Extend `inspect_artifact` with `artifact_type="ccmc_spec"` | **Accept** | Deterministic Markdown table parsing. Avoids each skill re-parsing the same file. Returns typed fields: model, event time, FR_type, FR params, MFLAMPA params, expected outputs. |
| Extend `inspect_artifact` with `artifact_type="paper_spec"` | **Accept (narrow)** | Only on a JSON/YAML structured spec the agent has written from paper text. The MCP tool surfaces fields and presence/absence; it does **not** parse the PDF itself. This keeps MCP deterministic. |
| Extend `inspect_artifact` with `artifact_type="param_template"` | **Reject** | A PARAM template *is* a PARAM file; existing `artifact_type="param"` handles it. Adding a new type would overlap. Use `param` and let the skill interpret "template-ness" via path. |
| Extend `inspect_artifact` with `artifact_type="result_bundle"` | **Reject** | A post-processed `RESULTS/<name>/` tree is a `run_dir` variant. Existing `run_dir` already documents the post-processed layout. Add a field if needed (e.g. `is_postproc_bundle: true`); do not branch types. |
| Extend `get_evidence` with `task_type="replication"` | **Conditional accept (Phase 2)** | Replication evidence is mostly union of existing `configuration|run|analysis` task types. Initially route through those. Add `replication` only if telemetry shows the agent fragmenting calls; if accepted, it should aggregate entrypoints from SWMFSOLAR Makefile, change_param scripts, download_ADAPT, and sub_runs. |
| Extend `get_evidence` with `task_type="validation"` | **Conditional accept (Phase 2)** | Same reasoning; initial implementation routes through `analysis`. Promote if `swmf-validation` repeatedly needs aggregated reference-comparison evidence. |
| Extend `compare_artifacts` with `comparison_type="reference"` | **Reject** | A reference comparison crosses domains (image, observation series, simulated trace) and is judgmental. Keep `compare_artifacts` as deterministic diff between like-typed artifacts. The skill drives reference comparison using existing types plus IDL. |
| Extend `compare_artifacts` so `comparison_type="run_dir"` reports parameter-level deltas (not just file-list deltas) | **Accept** | Deterministic; reuses existing `param` comparator on each side's `PARAM.in`. Surfaces PARAM-level differences for "replicate this prior run" parity checks. |
| Extend `inspect_artifact(artifact_type="param")` with `check_rules=True` that loads `support/swmf-params/rules/physical_constraints.yaml` and reports rule violations | **Accept** | Pure if/then evaluation against a user-owned YAML file; deterministic; no judgment in MCP code. The user grows the rule set over time without touching MCP. Multiple skills (`swmf-replicate`, `swmf-configure`, `swmf-cme-setup`) need this same gate. See §5.4. |
| New public MCP tool `assemble_param` | **Reject** | Workflow logic. Lives in `change_param.py` (shell) under skill orchestration. |
| New public MCP tool `submit_job` | **Reject** | Side-effecting, cluster-bound. Skill-level orchestration via shell. |
| New public MCP tool `fetch_external_data` | **Reject** | Network. Use `download_ADAPT.py` and analogues; MCP only inspects results. |

### 5.2 New typed fields required

For accepted artifact types, the typed fields each must return:

#### 5.2.1 `inspect_artifact(artifact_type="magnetogram")`

```
{
  "ok": bool,
  "summary": str,
  "format": "fits|map_out|harmonics_dat|unknown",
  "carrington_rotation": int|null,
  "observation_time": iso_string|null,
  "map_type": "ADAPT|GONG|HMI|MDI|other|unknown",
  "realization_count": int|null,            # ADAPT often 12
  "grid": {"nlon": int|null, "nlat": int|null},
  "file_size_bytes": int,
  "evidence": [{path, line_range_or_keyword}],
  "uncertainty": {"known_unknowns": [...]}
}
```

#### 5.2.2 `inspect_artifact(artifact_type="jobscript")`

```
{
  "ok": bool,
  "summary": str,
  "scheduler": "slurm|pbs|local|unknown",
  "directives": [{key, value, line}],
  "nodes": int|null,
  "tasks_per_node": int|null,
  "total_ranks": int|null,
  "walltime": str|null,
  "executable_invocations": [{cmd, args, line}],
  "postproc_present": bool,
  "fdips_invoked": bool,
  "harmonics_invoked": bool,
  "substitution_tokens": [str],            # e.g. amap01 placeholders
  "evidence": [...],
  "uncertainty": {...}
}
```

#### 5.2.3 `inspect_artifact(artifact_type="ccmc_spec")`

```
{
  "ok": bool,
  "summary": str,
  "run_id": str|null,
  "model": str|null,
  "event_time_utc": iso|null,
  "fr_type": str|null,
  "fr_params": {longitude, latitude, orientation, radius, bstrength, ...},
  "cone_params": {...}|null,
  "cme_params": {...}|null,
  "mflampa_params": {...}|null,
  "input_files_listed": [str],
  "output_files_listed": [str],
  "quicklook_targets": [str],
  "evidence": [...],
  "uncertainty": {...}
}
```

#### 5.2.4 `inspect_artifact(artifact_type="paper_spec")`

Same shape as `ccmc_spec`, but with explicit `source_paper_path` and `confidence_per_field` (since fields originate from agent extraction, not deterministic source). MCP returns only what is *literally present in the JSON*; it does not invent.

#### 5.2.5 `compare_artifacts(comparison_type="run_dir")` PARAM delta extension

Add a `param_diff` block built by feeding both sides' `PARAM.in` into the existing param comparator. No new contract.

#### 5.2.6 `inspect_artifact(artifact_type="param", check_rules=True)` rule-evaluation extension

Adds a `rule_violations` block to the existing `param` output:

```
{
  ...existing param fields...
  "rules_loaded_from": "src/agent_assets/skills/support/swmf-params/rules/physical_constraints.yaml",
  "rule_violations": [
    {
      "rule_id": str,                       # e.g. "poyntingflux_awsom_range"
      "severity": "block|warn|info",
      "command": str,                       # e.g. "#POYNTINGFLUX"
      "param_name": str|null,               # e.g. "PoyntingFluxPerBSi"
      "observed_value": str,
      "expected": str,                      # human-readable expectation from the rule
      "reason": str,                        # the rule's stated reason
      "evidence_line": int|null
    }
  ],
  "rule_check_summary": {"block": int, "warn": int, "info": int}
}
```

MCP only reports; it does not prescribe a fix. The skill (and ultimately the user) decide what to do with each violation. New rules require zero MCP code change — only edits to the YAML and (optionally) accompanying narrative in the rules directory.

### 5.3 Boundary-keeping notes

Each new artifact type **must not** return:

- `recommended_next_tool`
- `recommended_workflow`
- `suggested_steps`
- "you should now run X"

Output is fact-only. The skill draws conclusions.

### 5.3.1 Slim PARAM inspector (post-Phase-2 refactor)

`inspect_artifact(artifact_type="param")` is reduced to **structural primitives only**.
Its job is to emit machine-readable structure that the rule evaluator, the diff routine,
and the include/external-reference resolver consume. It is no longer a summarizer.

Removed findings (the agent reads PARAM.in directly for these):

- `session_commands` — per-session command lists.
- `param_session_timeline` — sessions with key-command events.
- `param_control_settings` — control-command summary.
- `param_saveplot_blocks` — `#SAVEPLOT` semantic extraction.

Retained findings (genuinely structural, agent can't reliably produce from raw text):

- `param_structure` — session count, command-map count, include count, external-ref
  count, parser errors/warnings.
- `include_files` — resolved `#INCLUDE` references with on-disk presence.
- `component_map` — `#COMPONENTMAP` rows expanded to typed `(component, proc0, procend,
  stride, nthread)` tuples; required components.
- `external_references` — referenced files with on-disk presence and ambiguities.
- `validation_note` — parser errors at the structural level.
- `rule_violations` — when `check_rules=True`; YAML-driven, see §5.4.

Run-directory inspection (`artifact_type="run_dir"`) keeps its internal use of
`_extract_param_semantics` because the `component_output_artifacts` finding maps
`#SAVEPLOT` intent to discovered output-file groups. That is structural extraction
across the run tree, not a summary handed back to the agent for intent reasoning.

**Skill protocol implication**: when a skill needs PARAM intent (sessions, control
cadence, save-plot intent, command flow), it reads the PARAM file directly. It calls
`inspect_artifact(artifact_type="param")` only when one of the retained primitives is
needed: rule evaluation (`check_rules=True`), include/external-ref resolution, or as
input to `compare_artifacts(comparison_type="param"|"run_dir")`. The existing
`swmf-analyze` policy ("read the run-local PARAM.in completely and reason from the
actual file contents") is now the cross-skill default.

Rationale: PARAM.in files are short (typically 200–700 lines, well within the agent
context budget), structured, and human-readable by design. An LLM reads PARAM intent
better than a fixed-schema summarizer. MCP duplicating that summary cost tokens, locked
in one interpretation, and competed with the agent's own reading. The structural
primitives that remain are operations the agent genuinely cannot do reliably from raw
text (typed value extraction for rule evaluation, set-level diff between two PARAMs,
filesystem-grounded include resolution).

This refactor is post-Phase-2 cleanup, not part of any phase's deliverables. It does
not change the public surface of `inspect_artifact` (still one tool, same artifact
types) — only the shape of the `findings` array for `artifact_type="param"`.

### 5.4 Extension interface: `swmf-params` rules directory

The `swmf-params` support skill owns a rules directory the user grows over time. This is the **single backstop** for everything the agent does not yet know about valid PARAM construction — and, equally important, everything the spec does not supply but a working PARAM still needs. Both MCP and the skill consume from it:

```
src/agent_assets/skills/support/swmf-params/rules/
  physical_constraints.yaml   # CONSTRAIN — if/then validation rules, evaluated by MCP
  numerical_practices.md      # narrative best practices, loaded by skill (tie-breaker)
  case_recipes/               # STRUCTURE — multi-session skeletons per archetype
    awsom_steady_sc.md
    awsom_cme_eruption.md
    sofie_mflampa_cme.md
    geospace_gmie.md          # future
  templates/                  # ANCHOR — template-pair manifests per archetype
    sofie_mflampa_cme.yaml
    awsom_cme.yaml
    awsomr_cme.yaml
  derivations/                # DERIVE — formulas mapping spec → PARAM values
    geometric.yaml            # CMEbox, coneIH rotation, MFLAMPA #ORIGIN, etc.
    spheromak_shape.yaml
    build_flags.yaml
  defaults/                   # DEFAULT — operational defaults for fields spec doesn't address
    cme_eruption.yaml
    session_ladders.yaml
    ops_guards.yaml           # CpuTimeMax, DtUpdateB0, MinimumPressure, etc.
```

The four lanes (constrain / derive / structure / default) plus the template anchor cover every value class the agent needs to produce. Each lane has the same maintenance contract: **append a YAML/MD file, no code change**. New predicate or expression types are the only changes that touch MCP code.

#### 5.4.1 `physical_constraints.yaml`

Pure if/then rules. No code. Schema (proposed):

```yaml
- id: poyntingflux_awsom_range
  applies_when: { command_present: "#POYNTINGFLUX" }
  require: { param_in_range: { name: PoyntingFluxPerBSi, min: 3.0e5, max: 1.5e6 } }
  severity: warn
  reason: "AWSoM tuning typically calibrated in this band; outside it solar wind speeds drift."

- id: cme_requires_starttime
  applies_when: { command_present: "#CME" }
  require: { command_present: "#STARTTIME" }
  severity: block
  reason: "GL/TD flux ropes are placed in HGI/HGR; without #STARTTIME the magnetogram alignment is undefined."

- id: timeaccurate_for_eruption_session
  applies_when: { session_index: 2, command_present: "#CME" }
  require: { param_equals: { name: DoTimeAccurate, value: T } }
  severity: block
  reason: "CME eruption must be time-accurate; steady-state will not propagate the rope."
```

Rule predicates that should be supported (deterministic, evaluable by inspecting PARAM.in alone):

- `command_present` / `command_absent`
- `param_equals` / `param_in_range` / `param_in_set`
- `command_co_occurs_with` / `command_excludes`
- `session_index` constraint (rule applies only in session N)
- `command_order_before` (X must appear before Y)

Predicates that require external evidence (magnetogram time, GPU vs CPU build, cluster) live in **case recipes** (narrative) instead, because they cross artifact boundaries and become judgmental.

#### 5.4.2 `numerical_practices.md`

Narrative best practices loaded by the `swmf-params` skill and surfaced through the skill's output. Examples of content the user will accumulate here:

- "For AWSoM SC, prefer `Sokolov` flux in IH and `Rusanov` in SC near the inner boundary; document the exception when overriding."
- "When `#GRIDLEVEL` increases, halve `cfl` for the first few iterations to avoid initial-transient blow-up."
- "GPU builds require `nStage=1` for some scheme combinations; check the GPU AWSoM template before assuming 2-stage."

The skill output contract requires the agent to cite which entries it applied or considered, even when they are narrative.

#### 5.4.3 `case_recipes/`

One markdown file per case archetype. Each recipe specifies the **multi-session skeleton** and the **decision points** within it: which commands appear in which session, where `#STOP`/`#TIMEACCURATE`/`#SAVERESTART` flip, what gets coupled at session boundaries. These are the documents `swmf-replicate` reads when classifying a PARAM job as "construction" (§6.5) and deciding which template to mutate.

A recipe is *not* a template. It documents the structure; the template instantiates it for one parameterization.

#### 5.4.4 `templates/` — ANCHOR

YAML manifests pairing a case archetype with its closest-precedent template(s) and required overrides. The skill loads `templates/<archetype>.yaml` immediately after archetype detection.

```yaml
# templates/sofie_mflampa_cme.yaml
id: sofie_mflampa_cme_pair
case_archetype: sofie_mflampa_cme
start_template: SWMFSOLAR/Param/PARAM.in.sofie.CCMC
restart_template: SWMFSOLAR/Param/PARAM.in.sofie.MFLAMPA
required_flag_overrides:
  - target: config_pl_sc
    from: "u=Awsom"
    to: "u=AwsomR"
    why: "Spec implies AWSoM-R via 2-temperature SaMhd; no shipped template carries this combination."
  - target: config_pl_ih
    from: "u=Awsom"
    to: "u=AwsomR"
recipe: case_recipes/sofie_mflampa_cme.md
secondary_precedents:
  - SWMFSOLAR/Param/PARAM.in.sofie.CME
  - SWMFSOLAR/Param/PARAM.in.awsomr.CME
  - SWMFSOLAR/Run_Max_RP_CME3/run01/PARAM.in
```

Without this file the agent re-derives template selection on every call via `get_evidence`; with it the answer is a single-file lookup. New archetypes are added by dropping a new YAML.

A `templates/<archetype>.yaml` is required for any archetype the user wants the agent to produce confidently. If none exists, `swmf-replicate` falls back to evidence-based template discovery and the answer's `template_choice` field is tagged `provenance=inferred` rather than `provenance=manifest`.

#### 5.4.5 `derivations/` — DERIVE

YAML files describing **how to compute** PARAM values from spec inputs and template-resolved context. Each entry has `applies_when` (precondition), `produces` (output sites + expressions), `assumptions` (values the user may want to override), and `evidence` (where the rule was learned). The skill loads every YAML in `derivations/`; the agent (LLM) evaluates each entry whose precondition matches.

```yaml
# derivations/geometric.yaml
- id: cmebox_from_fr_and_cone
  applies_when:
    case_archetype: [sofie_mflampa_cme, awsom_cme_eruption]
    spec_has: [fr_longitude, fr_latitude, cone_opening_lon, cone_opening_lat]
  produces:
    target: amr_region.CMEbox
    fields:
      Coord1MinBox: 1.1
      Coord1MaxBox: 22
      Coord2MinBox: "{fr_longitude} - {cone_opening_lon}/2"
      Coord2MaxBox: "{fr_longitude} + {cone_opening_lon}/2"
      Coord3MinBox: "{fr_latitude}  - {cone_opening_lat}/2"
      Coord3MaxBox: "{fr_latitude}  + {cone_opening_lat}/2"
  assumptions:
    - "Cone opening angles in spec are full angles, not half-angles."
    - "CMEbox radial extent fixed at 1.1–22 Rs (template default)."
  evidence: "CCMC weihao standard answer; SWMFSOLAR Run_Max_RP_CME3/run01."

- id: coneih_rotation_from_fr
  applies_when:
    case_archetype: [sofie_mflampa_cme, awsom_cme_eruption]
    spec_has: [fr_longitude, fr_latitude]
  produces:
    target: amr_region.coneIH_CME
    fields:
      xrotate: 0.0
      yrotate: "-{fr_latitude}"
      zrotate: "{fr_longitude}"
  evidence: "Standard SWMF AMRREGION conex rotated convention."

- id: mflampa_origin_from_spec_ranges
  applies_when:
    case_archetype: sofie_mflampa_cme
    spec_has: [mflampa_lon_min, mflampa_lon_max, mflampa_lat_min, mflampa_lat_max]
  produces:
    target: SP.#ORIGIN
    fields:
      ROrigin: 2.5
      LonMin: "{mflampa_lon_min}"
      LonMax: "{mflampa_lon_max}"
      LatMin: "{mflampa_lat_min}"
      LatMax: "{mflampa_lat_max}"

- id: relaxation_stop_from_smoothing
  applies_when:
    case_archetype: [sofie_mflampa_cme, awsom_cme_eruption]
    spec_has: [cme_traveling_time, smoothing_factor]
  produces:
    target: restart_PARAM.session_relaxation.#STOP.tSimulationMax
    expression: "{smoothing_factor} * {cme_traveling_time}"
  evidence: "CCMC weihao convention: relaxation tail = smoothing × CME time."
```

Predicate vocabulary the agent must understand (extendable list, but new predicates require an MCP/skill update if they introduce semantics the LLM cannot already evaluate):

- `case_archetype` — set match against the resolved archetype.
- `spec_has` — all listed spec fields are present in the normalized spec.
- `command_present` / `command_absent` — same as in `physical_constraints.yaml`.
- `cme_block_type` — match against resolved `TypeCme` (e.g. `SPHEROMAK`, `GL`, `TitovDemoulin`).
- `template_id` — applies only when a specific template manifest is in use.

Output expressions use `{spec_field}` and `{template_field}` for substitution and standard arithmetic operators. The agent (LLM) is the evaluator — no MCP code is needed unless predicates or operators are added.

Every derivation that fires must be reported in the skill output's per-value provenance (§4.1.5) as `provenance=derivation:<id>`.

#### 5.4.6 `defaults/` — DEFAULT

YAML files supplying **operational defaults** for fields the spec does not address and the template does not own. Apply only after spec / derivation / recipe / template have all failed to supply a value.

```yaml
# defaults/cme_eruption.yaml — operational scalar defaults
- id: spheromak_shape_defaults
  applies_when: { cme_block_type: SPHEROMAK }
  defaults:
    "#CME.Stretch": 0.6
    "#CME.ApexHeight": 0.72
    "#CME.iHelicity": 1
    "#CME.DecayCme": -1
  assumptions:
    - "iHelicity=1 corresponds to right-handed FR; surface for confirmation if observation suggests otherwise."
  evidence: "CCMC operational default; matches CCMC weihao standard answer."

- id: cme_ops_guards
  applies_when: { case_archetype: [sofie_mflampa_cme, awsom_cme_eruption] }
  defaults:
    "#CPUTIMEMAX.CpuTimeMax": "44 h"
    "#HELIOUPDATEB0.DtUpdateB0": 300
    "#COUPLE1.SC->SP.DtCouple": 120
    "#COUPLE1.IH->SP.DtCouple": 120

# defaults/session_ladders.yaml — iteration count ladders per archetype
- id: sofie_mflampa_steady_ladder
  case_archetype: sofie_mflampa_cme
  param_file: start
  ladder:
    - {session: 1, MaxIter: 70000, role: initial_AMR_in_SC}
    - {session: 2, MaxIter: 80000, role: freeze_SC_AMR}
    - {session: 3, MaxIter: 80001, role: enable_IH_couple}
    - {session: 4, MaxIter: 84000, role: enable_IH_AMR}
    - {session: 5, MaxIter: 85000, role: freeze_IH_AMR}
  scaling: "Tuned for the CCMC weihao grid resolution. Scale proportionally for denser/coarser grids and verify convergence in log file before relying."
  evidence: "Weihao_Liu_011326_SH_1 standard answer."
```

Defaults differ from derivations in two ways: (a) they do not require any spec input — they fire for the archetype alone; (b) they are explicitly overridable by a user value during the launch gate without surfacing as a discrepancy. Every applied default is reported as `provenance=default:<id>`.

The same `assumptions` field that flags caveats in derivations also applies here. A default with an `assumptions` block surfaces those notes during the launch gate even though the value itself does not block.

#### 5.4.7 The authoring ladder (how the lanes compose)

For every PARAM value the agent emits, the skill walks a fixed ladder. The first step that supplies the value wins; the agent records which step in the per-value provenance:

| Step | Lane | Provenance tag |
| --- | --- | --- |
| 1 | Spec field, direct (§6.7.1) | `spec` |
| 2 | Derivation matches and computes (§5.4.5) | `derivation:<id>` |
| 3 | Recipe specifies a session-structural slot value (§5.4.3) | `recipe:<id>` |
| 4 | Template carries the value as-is (§5.4.4 / §6.7.4) | `template:<path>` |
| 5 | Default applies (§5.4.6) | `default:<id>` |
| 6 | Narrative practice resolves a tie (§5.4.2) | `practice:<entry>` |
| 7 | Nothing supplies the value | `gap` → user prompt |

Validation rules (§5.4.1) and `Scripts/TestParam.pl` run on the *result* at the launch gate (§6.5.5); they are not part of authoring. The ladder is therefore "produce, then validate" — the four authoring lanes feed the ladder; the constraint lane is the gate.

Every step in the ladder is **append-only extendable**: adding a new derivation, default, recipe, or template manifest is a YAML drop. The user grows the system by closing one rung at a time on the cases that matter.

#### 5.4.8 Maintenance contract

- New validation rule: append to `physical_constraints.yaml`. No code change.
- New narrative practice: append to `numerical_practices.md`. No code change.
- New case archetype: add files under `case_recipes/`, `templates/`, and (where relevant) `defaults/`. No code change.
- New derivation: append a YAML entry to `derivations/<topic>.yaml`. No code change.
- New operational default: append a YAML entry to `defaults/<topic>.yaml`. No code change.
- New template-pair manifest: drop a YAML in `templates/`. No code change.
- Schema changes to predicate vocabulary (`physical_constraints.yaml`) or derivation expression operators: require MCP / skill code change. Treat as API changes and version them.

This is the user's primary leverage point. Every time the agent silently fills in a value during replication and the user disagrees, the fix belongs in one of the four lanes — not in the skill prompt and not in MCP code.

---

## 6. Workflow Protocol (Numbered Pipeline)

This is the canonical pipeline `swmf-replicate` follows. Each step states the layer.

1. **Intent classification** (agent + skill).
   - Determine `intent ∈ {paper, structured_spec, prior_run}`.
   - Determine target cluster, target SWMF root, target output root.

2. **Spec normalization** (skill + MCP).
   - For `paper`: agent extracts a structured `paper_spec` JSON; user confirms; `inspect_artifact(artifact_type="paper_spec")`.
   - For `structured_spec`: `inspect_artifact(artifact_type="ccmc_spec")`.
   - For `prior_run`: `inspect_artifact(artifact_type="run_dir")` plus direct read of `PARAM.in`.
   - Output: a single normalized internal representation.

3. **Reference selection** (skill + MCP).
   - Pick PARAM template from SWMFSOLAR `Param/`. Evidence: `get_evidence(task_type="configuration", goal="PARAM template")`.
   - Pick jobscript template from SWMFSOLAR `JobScripts/`. Evidence: `get_evidence(task_type="run")` + `inspect_artifact(artifact_type="jobscript")`.
   - For `prior_run`, the references are the prior run's own files.

4. **External-input acquisition** (agent shell).
   - Magnetogram: if available locally, classify via `inspect_artifact(artifact_type="magnetogram")`. If not, agent shells `download_ADAPT.py` (or analogous). After download, classify.
   - Harmonics: if FDIPS is the chosen B0 method, defer; harmonics file is generated during run-dir build (`HARMONICS.exe`). If pre-existing, classify.
   - Satellite trajectory files: agent shells SWMFSOLAR helpers if needed.

5. **Build** (skill `swmf-build`, agent shell).
   - Determine Config.pl options from PARAM (`#COMPONENTMAP`, scheme commands) and from SWMFSOLAR Makefile patterns (e.g. `Config.pl -o=SC:u=Awsom,e=AwsomAnisoPi,nG=3,g=6,8,8` for AWSoM).
   - Execute `make SWMF PIDL` and the auxiliary `make HARMONICS FDIPS` per SWMFSOLAR convention.

6. **Run-dir assembly** (agent shell, skill orchestration).
   - `make rundir RUNDIR=...` against SWMF source, or use SWMFSOLAR's `make rundir_realizations`.
   - Drop `PARAM.in`, `HARMONICS.in`/`FDIPS.in`, magnetogram, jobscript.
   - Inject specific parameters via `change_param.py` (CME flux-rope, Poynting flux, time, etc.).

7. **Pre-launch validation** (MCP).
   - `inspect_artifact(artifact_type="run_dir", path=<assembled>)`.
   - `inspect_artifact(artifact_type="param", path=<assembled>/PARAM.in, question="validate")`.
   - `inspect_artifact(artifact_type="jobscript", path=<assembled>/job.long)`.
   - Skill rule: do not launch if any artifact returns failure-class findings.

8. **Launch** (agent shell).
   - Issue cluster-appropriate command (`sbatch`, `qsub`, or `mpirun -np ... ./SWMF.exe`).
   - Record job id and submission command in skill output.

9. **Monitoring** (agent shell + MCP).
   - Periodic `inspect_artifact(artifact_type="run_dir")` to detect `SWMF.SUCCESS|SWMF.DONE|SWMF.KILL|core`.
   - `inspect_artifact(artifact_type="runlog", path=<latest>)` for compact status.
   - On failure family, hand off to `swmf-debug`.

10. **Postprocessing** (skill `swmf-analyze`, agent shell).
    - `PostProc.pl` (often executed inside the jobscript already).
    - For results bundle, `make check_postproc RESDIR=<name>` per SWMFSOLAR.

11. **Visualization** (skill `swmf-postproc`).
    - IDL `read_data`/`plot_data`/`animate_data` per existing protocol.
    - For CCMC-style quick-look: LASCO synthesis, in-situ comparison, MFLAMPA SEP plots, shock surface movies — each is an existing IDL workflow; the skill just selects the right `func`/`plotmode`.

12. **Validation** (skill `swmf-validation`).
    - For `prior_run` intent: `compare_artifacts(comparison_type="run_dir")` with PARAM-delta extension.
    - For `paper`/`structured_spec`: comparison against paper figures or observation traces is IDL-rendered and presented to the user; numerical metrics where available (e.g. RMSE on density at L1).

13. **Answer composition** (agent).
    - Apply the `swmf-replicate` output contract.
    - Separate confirmed/inferred/assumed; surface `uncertainty.known_unknowns`.

### 6.5 PARAM.in Generation Detail

PARAM.in generation is the highest-risk step in replication: a syntactically valid PARAM that runs to `SWMF.SUCCESS` but is physically wrong is the worst silent failure. This section pins down how the agent produces PARAM.in and what gates apply before launch.

#### 6.5.1 What `change_param.py` is good for, and what it is not

`SWMFSOLAR/Scripts/change_param.py` is four pure string-substitution functions: `add_commands`, `remove_commands`, `replace_commands`, `change_param_value`. All four require the template to **already contain** the structure with the right markers (`^`, `(tag)`); if a key isn't found the script exits.

What it cannot do:

- Insert a new command block that isn't in the template (e.g. add `#CME` to an AWSoM-steady template).
- Add or reshape sessions (`#RUN`/`#END` boundaries; flipping `#TIMEACCURATE`).
- Reorder commands (PARAM.XML enforces order).
- Resolve `#INCLUDE` chains.
- Validate anything (no schema awareness, no range checks).
- Choose a template; understand physics; generate from scratch.

It is sized for SWMFSOLAR's parameter-sweep workflow (template the same case 12 ways across ADAPT realizations), not case construction. The plan therefore uses it only where it fits.

#### 6.5.2 Two modes: sweep vs construction

The `swmf-replicate` skill classifies the PARAM job before generating:

- **Sweep**: the chosen template's structure is correct for the case; only parameter values change. Examples: ADAPT realization 1..12 of an existing CME case; scanning `PoyntingFluxPerBSi` for tuning; adjusting `#STOP` and `#SAVEPLOT` cadence.
- **Construction**: the chosen template is the closest precedent but its *structure* must change. Examples: starting from `PARAM.in.awsom.steady` and adding a `#CME` block plus an eruption session; adapting an SC-only template into an SC+IH coupled case; reshaping sessions for SOFIE+MFLAMPA.

Most paper- and CCMC-driven replications are **construction** jobs. Sweeps are common only when the user is rerunning a parameter study off an existing case.

#### 6.5.3 Sweep procedure

1. Skill confirms the template's structure already matches the spec (no missing command blocks; sessions correct).
2. Agent builds a typed dict of changes: `{ "PoyntingFluxPerBSi": "1.2e6", "POYNTINGFLUX(test)": "1.2e6", "STOP": "-1, 7200" }`.
3. Agent shells `change_param.py` (or imports the module) with the dict.
4. Validation gate (§6.5.5) runs.

The dict and the resulting diff are recorded in skill output. Failure modes are loud (the script `sys.exit`s on missing keys), which is desirable.

#### 6.5.4 Construction procedure

1. Skill resolves the **case archetype** from the normalized spec (e.g. `sofie_mflampa_cme`).
2. Skill loads `swmf-params/rules/templates/<archetype>.yaml` (§5.4.4) to obtain the template pair, required flag overrides, and recipe pointer. Falls back to evidence-based template selection if no manifest exists, marking the choice as `provenance=inferred`.
3. Agent reads the resolved template(s) and the case recipe (§5.4.3).
4. Agent enumerates the **delta**: command blocks to add, remove, reorder, or revalue; session boundaries that shift.
5. For each value the agent emits, it walks the **authoring ladder** (§5.4.7) and records the supplying step as the value's provenance: `spec` → `derivation` → `recipe` → `template` → `default` → `practice` → `gap`. Steps 2–6 are YAML-driven; the agent does not invent values.
6. Agent **writes PARAM.in directly** via Edit/Write at the assembled run-directory path. Both files (start + restart, §6.6) are produced when the archetype requires it.
7. Where a sub-block within the construction is itself a sweep (e.g. plugging the FR numbers from the spec into the new `#CME` block), the agent may shell `change_param.py` for that sub-step after the structural edit is in place.
8. Validation gate (§6.5.5) runs.

The skill output contract requires the agent to record:

- which template manifest (or evidence-derived template) was the base,
- which case recipe was followed,
- the structural delta (added/removed/reordered command blocks, session changes),
- per-value provenance using the §5.4.7 ladder tags (`spec` | `derivation:<id>` | `recipe:<id>` | `template:<path>` | `default:<id>` | `practice:<entry>` | `gap`),
- explicit list of `gap` values (these become user-approval items and represent extension opportunities — closing one is a YAML edit in `derivations/` or `defaults/`).

The agent **must not** invent numerical values. If a spec is silent on a parameter and the authoring ladder produces `gap`, the skill reports the gap and asks the user. Each closed gap is a candidate YAML entry the user can add to the rules directory so the next replication run does not re-ask.

#### 6.5.5 Pre-launch validation gate (mandatory)

Launch is blocked unless every item below passes:

1. `inspect_artifact(artifact_type="param", path=<PARAM.in>, check_rules=True)` — structural validity plus rule evaluation. **Block if any `severity=block` violation.** `warn` and `info` are surfaced but do not block.
2. Agent shells `Scripts/TestParam.pl` from SWMF root. **Block on any error.** This is the schema authority.
3. PARAM diff vs base template, with evidence citation per change, is presented to the user.
4. The skill output's "values agent inferred" list is presented to the user.
5. User approval is recorded (timestamp, hash of approved PARAM.in). The skill stores this as part of the launch evidence.

Steps 3–5 are skill-level (the gate is enforced by skill policy, not by MCP). MCP only supplies the deterministic checks in step 1; step 2 is a shell call; steps 3–5 are agent + user.

#### 6.5.6 Reliability honest assessment

Even with this gate, autonomous launch on novel cases is not safe. The plan assumes:

- For **prior-run replication**: parity is checkable (`compare_artifacts(comparison_type="run_dir")` with PARAM-delta) and the gate is sufficient.
- For **structured-spec replication**: the gate plus user approval is sufficient when the spec is complete.
- For **paper replication**: the gate is necessary but not sufficient. Every paper-derived value carries `confidence_per_field`, and the skill's default is to refuse autonomous launch and require explicit user confirmation. The user can override per session, but not as a durable instruction.

The rules directory (§5.4) is the user's leverage. Every silent-wrong-PARAM incident in practice should produce one of: a new rule in `physical_constraints.yaml`, a new entry in `numerical_practices.md`, or a new file under `case_recipes/`. The system gets safer over time without MCP changes.

### 6.6 Two-PARAM start+restart split

CCMC CME cases (and most AWSoM-R/SOFIE eruption runs) ship **two** PARAM.in files, not one. The skill must treat the pair as a single deliverable.

- **`PARAM.expand.start`** — steady-state background. SC+IH only, `#TIMEACCURATE F`, multi-session iteration ladder (initial AMR → freeze AMR → couple SC↔IH → IH AMR), terminating in `#SAVERESTART`. No `#CME` block.
- **`PARAM.expand.restart`** — time-accurate eruption. `#INCLUDE RESTART.in`, `#INCLUDE SC/restartIN/restart.H`, `#INCLUDE IH/restartIN/restart.H`. Adds `#CME` in SC, `#FIELDLINE`/`#PARTICLELINE` for SP, and the diagnostic `#SAVEPLOT` blocks (LASCO C2/C3, EUVI A/B, AIA, shock surface). Ends with the relaxation session.

Implications for `swmf-replicate`:

- Produce both PARAMs for any structured-spec or paper CME run.
- Plan a **two-stage submission**: build → submit start → wait for `SWMF.SUCCESS` and confirm `SC/restartOUT/` + `IH/restartOUT/` populated → swap PARAM.in for the restart variant → resubmit. The skill output's `launch_command` field expands to a list, not a single string.
- Restart linkage is by file convention (`#INCLUDE` against `restartIN/restart.H`); the skill verifies the start run produced these before swapping.
- `case_recipes/awsom_cme_eruption.md` must call out this split explicitly. A recipe that documents only one PARAM is incomplete.
- `compare_artifacts(comparison_type="run_dir")` PARAM-delta extension must compare like-to-like: start vs start, restart vs restart.

A merged single-PARAM is possible in principle but operationally fragile — any failure mid-eruption forces a full background re-run rather than a checkpointed restart. The split is the operational standard and the recipe enforces it.

### 6.7 Worked example: spec → PARAM mapping

Anchor case: `examples/CCMC_run_weihao/`. The directory contains the CCMC structured spec (`Run information_CCMC.md`), the standard-answer PARAM files (`Weihao_Liu_011326_SH_1_PARAM.expand.start`, `..._PARAM.expand.restart`), and the input magnetogram (`mrzqs230224t1904c2268_303.fits`). This is the **gold target** for the Phase 2 exit criterion (§7.2).

#### 6.7.1 Spec values that map directly into PARAM

| Spec field | PARAM site (file → command → param) | Notes |
| --- | --- | --- |
| Date `2023/02/24 20:29` | start → `#STARTTIME` | Direct |
| Poynting ratio `0.4` | start+restart → `#POYNTINGFLUX` PoyntingFluxPerBSi=`0.4e6` | Convention `0.4 → 0.4e6 J/m²/s/T` |
| Coronal Heating `1.5` | start+restart → `#CORONALHEATING` LperpTimesSqrtBSi=`1.5e5` | Convention `1.5 → 1.5e5` |
| FR Longitude `33` | restart → SC `#CME` LongitudeCme | Direct |
| FR Latitude `26` | restart → SC `#CME` LatitudeCme | Direct |
| FR_orientation `268.62` | restart → SC `#CME` OrientationCme | Direct |
| FR_radius `0.52` | restart → SC `#CME` Radius | Direct |
| FR_bstrength `20.98` | restart → SC `#CME` BStrength | Direct |
| CME speed `1276` | restart → SC `#CME` uCme | Direct |
| CME traveling time `43200` | restart → eruption-session `#STOP` tSimulationMax | Eruption phase end |
| MFLAMPA nLat/nLon `15`/`15` | restart → SP `#GRIDNODE` | Direct |
| MFLAMPA Lon/LatMin/Max | restart → SP `#ORIGIN` | Four values, direct |
| MFLAMPA MeanFreePath0 `0.3` | restart → SP `#USEFIXEDMFPUPSTREAM` | Direct |
| MFLAMPA SpectralIndex `5` | restart → SP `#MOMENTUMBC` SpectralIndex | Direct |
| MFLAMPA Efficiency `0.1` | restart → SP `#MOMENTUMBC` EfficiencyInj | Direct |
| Magnetogram FITS | start+restart → `#HARMONICSFILE SC/mf.dat` | FITS is the input; `mf.dat` is harmonics derived in-rundir before launch |

#### 6.7.2 Spec values requiring geometric derivation

| Spec input | Derived PARAM value | Derivation |
| --- | --- | --- |
| FR Lon/Lat + Cone opening (Lon=20.87, Lat=10.44) | start+restart → `#AMRREGION CMEbox` LongMin/Max=22.565/43.435, LatMin/Max=20.78/31.22 | `Lon ± OpeningLon/2`, `Lat ± OpeningLat/2`. Recipe documents whether opening is full or half-angle. |
| FR Lon/Lat | restart → `#AMRREGION coneIH_CME` yrotate=−Lat=−26, zrotate=Lon=33 | Convention: rotate cone axis to point at FR center. |
| Smoothing factor `2` × CME time `43200` | restart → final `#STOP` tSimulationMax=`86400` | Relaxation tail = (smoothing − 1) × CME time. |
| Quick Look list (LASCO C2 brightness/running diff/base diff; EUVI A/B; AIA; in-situ at STA/STB/Earth) | restart → SC `#SAVEPLOT` (`los ins idl_ascii soho:c2`, `... soho:c3`, `los ins idl_ascii sta:euvi stb:euvi sdo:aia`) plus three `#SATELLITE` MHD blocks for earth/sta/stb | Recipe-driven mapping from CCMC quick-look targets → plot block + lookup-table load. |

#### 6.7.3 Spec values that require explicit user judgment

| Spec field | Issue | Required handling |
| --- | --- | --- |
| FR_type `GL` | Standard PARAM uses `TypeCme=SPHEROMAK`, not `GL`. CCMC submission form labels both as "GL flux rope"; the operational SWMF model is SPHEROMAK with GL-shaped parameters. | Skill surfaces the discrepancy and requests user confirmation before launch. Add seed rule `cme_typecme_matches_spec_fr_type` to `physical_constraints.yaml` (severity=block when the translation is unconfirmed). |
| Cone opening angle convention | Spec lists "Cone opening angle: Longitude=20.87, Latitude=10.44" without specifying full vs half. CMEbox derivation above assumes full-angle (matches the standard answer). | Recipe documents the convention; surface in skill output as `cme_box.derivation_assumption=full_angle`. |
| Smoothing factor semantics | Spec says `Smoothing factor: 2`. Standard PARAM uses this as the multiplier on CME-time for relaxation tail; not all archetypes do. | Recipe-scoped convention; surface explicitly. |

#### 6.7.4 PARAM content not in spec at all (template- and recipe-supplied)

By count, the spec contributes ~25 values; the two PARAMs hold ~400 commands. Everything else is template- or recipe-derived:

- Component map and `Config.pl` options (`-v=SC/BATSRUS,IH/BATSRUS,SP/MFLAMPA`, `-o=SC:u=AwsomR,e=AwsomSA,ng=2,g=8,8,4`, IH variant, `-o=SP:g=20000`).
- Multi-session structure: 4 sessions for `start`, 4 sessions for `restart` (eruption → SC-relax → IH-only → tail).
- Session iteration counts (70000, 80000, 80001, 84000, 85000) — convergence-tuned, expert-set.
- AMR criteria, resolutions, and region geometry beyond the FR-derived box (`InnerShell`, `OuterShell`, `polar`, `IHbox`, `coneearth`).
- Grid roots, geometry types (`spherical_lnr` for SC, `roundcube` for IH with `rRound0=250`, `rRound1=375`), domain extents, buffer-grid sizing.
- Schemes (Sokolov, mc3, β=1.2, nStage=2, CFL=0.8) per component.
- Coupling cadences (`#COUPLE1` SC↔IH `Dn=1`; SC,IH↔SP `Dt=120 s`).
- Threaded field-line and SaMhd flags (`#FIELDLINETHREAD`, `#PLOTTHREADS`, `#ALIGNBANDU`).
- Lookup-table loads (RadCoolCorona, TR, los_tbl, los_Eit_cor, los_EuviA, los_EuviB).
- Restart cadence, log variables, plot variable lists, particle-line settings.
- SPHEROMAK shape parameters not in spec: `Stretch=0.6`, `ApexHeight=0.72`, `iHelicity=1`, `DecayCme=-1`.
- Operational guards: `CpuTimeMax=44 h`, `DtUpdateB0=300 s`, `MinimumPressure`, `MinimumTemperature`, `MinimumRadialSpeed`.

The skill must source each from one of: closest-precedent template, case recipe, prior run, or — if absent everywhere — an explicit user prompt. The list of "values agent could not source" is a required output field per §6.5.4.

### 6.8 Required agent abilities (capability inventory)

To execute §6.7 reliably, the agent (LLM + skill stack + MCP) must demonstrate:

1. **Structured-spec extraction.** Parse a CCMC-style markdown table into typed fields. → MCP `inspect_artifact(artifact_type="ccmc_spec")` (Phase 2).
2. **Closest-precedent template selection.** Given a normalized spec, identify the matching template family in SWMFSOLAR/Param/. Match on `(model, components, has_CME, has_MFLAMPA, has_threaded_gap)` tuples. → `swmf-replicate` evidence step 2.
3. **Two-PARAM structural reasoning.** Recognize that a CME case decomposes into background + restart and produce both with correct cross-file references. → §6.6 + `case_recipes/awsom_cme_eruption.md`.
4. **Multi-session reasoning.** Decide where session boundaries fall, what each session toggles (`#TIMEACCURATE`, `#DOAMR`, `#COMPONENT`, `#COUPLE1`), and how iteration counts ladder. The agent does not derive this from physics; it copies from the recipe and varies only what the spec demands. → `case_recipes/`.
5. **Geometric derivation.** Compute AMR-region bounds and cone-rotation Euler angles from FR longitude/latitude/cone-opening. Pure arithmetic; conventions (full/half angle, sign of rotation) live in the recipe. → recipe + agent math.
6. **Quick-look → diagnostic mapping.** Translate a CCMC "Quick Look Graphics" list into the corresponding `#SAVEPLOT` blocks and lookup-table loads. → recipe + `swmf-validation` reverse-mapping table.
7. **Discrepancy detection.** Identify when a spec field disagrees with the template default in a way that requires user confirmation (e.g. spec FR_type=GL vs template TypeCme=SPHEROMAK). → rules directory + skill output `confirmed|inferred|assumed` separation.
8. **Direct PARAM authoring.** Edit/Write structural changes on the assembled run-dir PARAM.in. `change_param.py` is not sufficient (§6.5.1).
9. **Pre-launch validation operation.** Drive `inspect_artifact(artifact_type="param", check_rules=True)`, shell `Scripts/TestParam.pl`, surface the diff vs base, and gate on results. → §6.5.5.
10. **Cluster-shell competence.** Run `Config.pl`, `make`, `sbatch`/`qsub`, `squeue`/`qstat`; recover from common failure modes (allocation, walltime, queue saturation). The skill does not embed credentials.
11. **Output inventory + IDL execution.** Locate post-processed outputs and drive existing `swmf-postproc` IDL workflows (LASCO synthesis, satellite traces, shock surface).
12. **Honest uncertainty reporting.** Every run-altering value is tagged `confirmed | inferred | assumed`, with `assumed` items blocking launch until the user confirms.
13. **Authoring-ladder execution.** For every emitted PARAM value, walk the §5.4.7 ladder (spec → derivation → recipe → template → default → practice → gap), evaluate `derivations/*.yaml` and `defaults/*.yaml` entries whose preconditions match, perform the simple arithmetic and substitution in their `produces`/`expression` fields, and tag the result with the supplying lane. Adding a new value class is a YAML drop, not a skill prompt edit.

What the agent cannot do, even with the full stack:

- Invent FR shape parameters (`Stretch`, `ApexHeight`) when neither spec nor precedent provides them. Surface as `assumed` with a specific user prompt.
- Pick AMR resolutions that diverge from the recipe. Resolution tuning is research; the skill stays on recipe rails or asks.
- Decide multi-session iteration counts for an unprecedented case archetype. Adding a new archetype is a `case_recipes/` authoring task — owned by the user.
- Validate physical correctness from a `Scripts/TestParam.pl` pass alone. Schema is necessary but not sufficient (§9.2).

---

## 7. Phased Rollout

Each phase has one entry-deliverable and an exit criterion that is testable from a small gold prompt set.

### 7.1 Phase 1 — Skill scaffolding + jobscript inspection + rules skeleton + gate

**Deliverable**:

- `swmf-replicate` entry skill (skeleton with intents and evidence order, including the §6.5 PARAM-generation step and the §6.5.5 launch gate).
- `swmf-jobscript` support skill.
- `inspect_artifact(artifact_type="jobscript")` extension.
- `compare_artifacts(comparison_type="run_dir")` PARAM-delta extension.
- **Rules directory skeleton** under `src/agent_assets/skills/support/swmf-params/rules/` covering all four lanes (§5.4):
  - `physical_constraints.yaml` — 5–10 seed validation rules for common AWSoM/CME pitfalls.
  - `numerical_practices.md` — a few seed narrative entries.
  - `case_recipes/awsom_cme_eruption.md` — derived from `Run_Max_RP_CME3/run01`.
  - `templates/awsom_cme.yaml` — pairs the prior-run as the template anchor for the AWSoM-CME archetype, with no flag overrides (Phase 1 sweep mode only).
  - `derivations/geometric.yaml` — at minimum `cmebox_from_fr_and_cone` and `coneih_rotation_from_fr` so the Phase 2 worked example (§6.7) has a foundation already in place.
  - `defaults/ops_guards.yaml` — `CpuTimeMax`, `MinimumPressure`, `MinimumTemperature` defaults shared across archetypes.
- Skill consumes `templates/`, `derivations/`, `defaults/` and walks the §5.4.7 authoring ladder; provenance tags appear in skill output for every emitted value.
- `inspect_artifact(artifact_type="param")` extended with `check_rules=True` consuming `physical_constraints.yaml`.
- All other support skills exist as stubs that delegate to `swmf-configure`/`swmf-run`/`swmf-analyze`.

**Exit criteria**:

- Agent given `prior_run="SWMFSOLAR/Run_Max_RP_CME3/run01"` and `cluster=frontera` produces a normalized spec, picks the prior PARAM as the template (sweep mode), identifies `job.frontera`, runs `inspect_artifact(artifact_type="jobscript")`, produces a build plan citing `SWMFSOLAR/Makefile` `compile` target, runs the launch gate, and reports approval state without actually launching.
- `inspect_artifact(artifact_type="param", check_rules=True)` correctly flags a deliberately broken PARAM (e.g. `#CME` without `#STARTTIME`) with `severity=block`.
- No public MCP advice fields leak.
- `compare_artifacts(comparison_type="run_dir")` returns a structured `param_diff` when both sides have `PARAM.in`.

**Gold prompts**:

1. "Reproduce `Run_Max_RP_CME3/run01` on Frontera. What's the build and submission plan? Stop before launch."
2. "Inspect `SWMFSOLAR/JobScripts/job.FDIPS.frontera` and tell me how many ranks it requests."
3. "Compare `Run_Max_RP/run01` and `Run_Max_RP_CME3/run01` and tell me which PARAM commands changed."
4. "Validate this PARAM.in against the rules" — including a synthetic broken case to confirm the gate triggers.

### 7.2 Phase 2 — Magnetogram + CME-setup + spec inspection + construction-mode generation

**Deliverable**: `swmf-magnetogram` and `swmf-cme-setup` support skills; `inspect_artifact(artifact_type="magnetogram")` extension; `inspect_artifact(artifact_type="ccmc_spec")` extension. SWMFSOLAR support skill (`swmf-swmfsolar`) added. **Construction-mode PARAM generation per §6.5.4** wired through `swmf-replicate`: the agent can take a CCMC spec, pick `Param/PARAM.in.awsom.steady` as base, follow `case_recipes/awsom_cme_eruption.md`, and produce a constructed PARAM.in that passes the gate.

**Exit criteria**:

- Agent given the CCMC markdown spec normalizes it, identifies needed magnetogram (date, type), classifies a local `mrzqs*.fits`, picks `Param/PARAM.in.sofie.MFLAMPA`, and produces a build plan including `Config.pl -v=Empty,SC/BATSRUS,IH/BATSRUS,SP/MFLAMPA` and `Config.pl -o=SC:u=Awsom,e=AwsomSA,...`.
- `inspect_artifact(artifact_type="magnetogram")` returns CR + time + type for a real `mrzqs190801t0014c2220_229.fits` from the repo root.
- `inspect_artifact(artifact_type="ccmc_spec")` returns typed fields for `Run information _ CCMC.md`.
- **Gold target — `examples/CCMC_run_weihao/`.** Given the CCMC spec, the magnetogram FITS, and the SWMFSOLAR template + recipe, the agent produces both `PARAM.expand.start` and `PARAM.expand.restart` candidates. `compare_artifacts(comparison_type="run_dir")` PARAM-delta against the bundled standard-answer PARAMs is run; every delta is classified per §6.7.4 / §6.8 as one of `expected (template-default) | needs-recipe-update | needs-rule-update | confirmed-user-judgment`. Zero deltas in the `direct-mapping` set of §6.7.1; geometric-derivation deltas (§6.7.2) match exactly modulo numeric tolerance; FR_type discrepancy (§6.7.3) is surfaced and blocks launch until user confirms.

**Gold prompts**:

1. "Set up the `Weihao_Liu_011326_SH_1` run from the CCMC spec for local Frontera execution."
2. "What magnetogram do I need for the 2023-02-24 CME, and where do I get it?"
3. "Translate the GL flux-rope parameters in this spec into a PARAM.in `#CME` block."

### 7.3 Phase 3 — Paper-spec normalization + validation

**Deliverable**: `paper_spec` artifact type; `swmf-validation` support skill; `swmf-replicate` `intent="paper"` path fully wired. Optional `task_type="replication"` and `task_type="validation"` for `get_evidence` if Phase 2 telemetry indicates fragmentation.

**Exit criteria**:

- Given a paper excerpt naming an event, the agent produces a `paper_spec.json`, hands it through `inspect_artifact`, and merges with the structured-spec path with no divergence.
- `swmf-validation` produces side-by-side IDL renders for at least one paper-figure-equivalent (e.g. synthetic LASCO C2 panel) given a completed run.
- Telemetry on Phases 1–2 has zero "MCP advice" leaks.

**Gold prompts**:

1. "Replicate the case described in this Sokolov 2023 PDF excerpt. Use Frontera."
2. "After the run finishes, validate the modeled L1 density against OMNI for the 2023-02-24 event."
3. "Render a LASCO C2 base-difference movie equivalent to Figure 6 of the paper."

### 7.4 Phase 4 — Resilience and parity at scale

**Deliverable**: hardened error handling on cluster boundaries; multi-realization support (`REALIZATIONS=1..12` from SWMFSOLAR Makefile) wrapped by skill; restart workflow integration with `Restart.pl`.

**Exit criteria**:

- Agent can launch and monitor a 12-realization ensemble.
- Agent can produce a "compare-to-CCMC" deliverable bundle for a non-trivial CME event without ad hoc shell recovery.

---

## 8. Open Questions and Risks

1. **Magnetogram licensing and provenance.** ADAPT/GONG/HMI policies differ; the skill must record source and timestamp explicitly. Risk: the agent picks a different magnetogram than the paper used and silently degrades parity. Mitigation: skill output requires `magnetogram.source_match_method` (paper-stated|inferred|user-confirmed).
2. **Carrington-rotation alignment.** Magnetograms are time-tagged but PARAM `#STARTTIME` may differ; SWMFSOLAR `change_awsom_param.py` handles this — the skill must defer there, not reimplement. Risk: agent rolls its own arithmetic.
3. **Paper-extraction reliability.** PDF/figure parsing is fragile. Risk: hallucinated parameters. Mitigation: every paper-derived field requires user confirmation; `confidence_per_field` is mandatory.
4. **Cluster authentication.** SSH keys, allocations, queue policies vary. The skill must not embed credentials. The agent shell handles auth; the skill output records cluster identity but not secrets.
5. **Cluster shell heterogeneity.** Frontera is `sbatch`+`ibrun`, Pleiades is `qsub`+`mpiexec`, Derecho is `qsub` with intel module quirks. The jobscript artifact type must surface scheduler unambiguously.
6. **SWMFSOLAR drift.** SWMFSOLAR is under active development; skill instructions that pin specific Makefile target names will rot. Mitigation: `swmf-swmfsolar` support skill is the single point of update.
7. **Restart vs cold-start parity.** CME runs typically require a converged background run as restart input. The skill must clearly distinguish "background available" from "must run background first" and route accordingly. Risk: launching CME run with no restart and silently producing nonsense.
8. **GPU vs CPU PARAM templates.** `*.gpu` templates exist (`PARAM.in.awsom.CME_gpu`) and require different `Config.pl` options. The skill must read target-environment hardware cues.
9. **Validation ambiguity.** "Match the paper" is judgmental. Risk: false-positive parity claims. Mitigation: numerical metrics where defined; otherwise explicit "visual, user-confirmed" classification.
10. **MFLAMPA coupling complexity.** SOFIE+MFLAMPA introduces SP component, field-line registry, and SEP physics tunables that go far beyond `Param/PARAM.in.awsom.CME`. Phase 2 must accept that this is a partial walkthrough and Phase 3 may need more.
11. **Output path conventions.** `Run_Max_RP_CME3/run01` shows IDL output files at the SC top level (not `SC/IO2/`); the run-dir inspector must already handle this, but `swmf-replicate` should verify before assuming `PostProc.pl` will tidy them.
12. **Token cost of evidence-order ladders.** Replication is multi-step; if every step calls multiple MCP tools, token use balloons. Mitigation: skill output contract requires *minimum-evidence answers* and discourages redundant retrieval.

---

## 9. Anti-patterns to Avoid

Carry forward the existing protocol's anti-patterns and add replication-specific ones.

### 9.1 Carried forward (still apply)

- Tool proliferation.
- Overlapping public tools.
- MCP tools with embedded reasoning policy.
- Skills that mirror tool names.
- Retrieval-first design for deterministic tasks.
- Returning `recommended_next_tools` in public MCP contracts.

### 9.2 New, replication-specific

- **MCP-as-HTTP-client.** Do not put ADAPT/GONG/CCMC fetch inside MCP. Network calls, retries, and authentication belong in shell scripts the agent invokes.
- **MCP-as-PDF-parser.** Do not build a paper-PDF parser inside MCP. The agent (LLM) extracts; MCP only inspects the resulting JSON.
- **MCP-as-job-submitter.** Do not allow MCP to launch jobs. Side-effects against clusters are agent-shell territory.
- **Skill-as-Makefile.** Do not encode SWMFSOLAR's Makefile rules inside a skill body. The skill points to the Makefile target and lets the agent run `make`.
- **Hidden parameter inference.** Do not let the skill silently fill in flux-rope parameters from "physical reasonableness." Every numeric value is either spec-stated, prior-run-derived, or user-confirmed.
- **Image-comparison-as-deterministic-evidence.** Do not allow `compare_artifacts` to claim a paper-figure match by visual similarity. Visual comparison is a user-facing presentation, not deterministic evidence.
- **One-skill-per-cluster.** Do not create `swmf-replicate-frontera`, `swmf-replicate-pleiades`. Cluster heterogeneity is jobscript-typed evidence, not a skill axis.
- **Spec-format-explosion.** Do not add a new artifact type for every paper or center spec format. Normalize to `paper_spec`/`ccmc_spec` and let the agent's spec normalizer absorb format differences.
- **Replication-via-grep.** Do not let the agent fall back to grepping SWMFSOLAR for parameter names when the structured normalized spec is incomplete. If a field is missing, the skill must ask the user.
- **`change_param.py` for structural changes.** Do not use `change_param.py` to insert a `#CME` block or reshape sessions. The script will silently no-op or hard-exit; either way the result is wrong. Structural edits are agent-written PARAM.in (§6.5.4).
- **Inventing values to satisfy a rule.** If a rule fires `severity=block` and the spec is silent on the offending field, the skill must surface the gap to the user — not pick a "reasonable" value to make the gate green.
- **Treating `Scripts/TestParam.pl` pass as physical correctness.** PARAM.XML conformance is necessary but not sufficient. A run can pass `TestParam.pl`, finish with `SWMF.SUCCESS`, and still be physically wrong. The rules directory and user approval are the substantive checks.
- **Silent semantic translation.** Do not silently translate a spec field through a model-specific identity (e.g. spec `FR_type=GL` → PARAM `TypeCme=SPHEROMAK`) without surfacing it. Translations of this kind belong in the rules directory and the skill output's `inferred` section, with explicit user confirmation before launch.
- **Producing a single PARAM for a CME case.** CCMC and most AWSoM-R CME runs are two-PARAM (background + restart). A skill that emits one merged PARAM either skips the steady-state background (physically wrong) or fuses sessions in a way that makes restart-from-checkpoint impossible (operationally wrong). See §6.6.
- **Hardcoding domain knowledge in the skill body.** Per-case derivations, template pairings, operational defaults, session ladders, and SPHEROMAK-shape conventions all belong in the `swmf-params/rules/` lanes (§5.4), not in the skill prompt or the agent's prose memory. A skill that knows "for SOFIE+MFLAMPA use sofie.CCMC + sofie.MFLAMPA" only because the prose says so is non-extensible: every new archetype forces a skill edit. The skill must consume `templates/`, `derivations/`, `defaults/` as data; the user authors new YAML to teach new cases.
- **Asking the user for the same gap on every run.** If a `gap` value (§5.4.7) recurs across runs, it should be promoted into the rules directory — a derivation if it's a function of the spec, a default if it's archetype-keyed, a recipe entry if it's structural. Re-prompting the user for the same value is a sign the system is not learning.

---

## 10. Judgment Calls (with alternatives considered)

Each marked decision the user should know was a tradeoff.

- **One `swmf-replicate` skill with intents instead of three separate skills.** Alternative considered: `swmf-paper-replicate`, `swmf-spec-replicate`, `swmf-rerun`. Rejected because the post-normalization workflow is identical and three skills would copy policy. Chosen because the answer contract is identical.
- **`swmf-swmfsolar` as a support skill.** Alternative considered: leave SWMFSOLAR as just-another-evidence-source through `get_evidence`. Rejected because the agent repeatedly needs its operational map (Makefile, Scripts, JobScripts) and rediscovering it wastes calls. Chosen as a support skill because it is a coherent unit of operational know-how, not a generic retrieval helper.
- **`magnetogram`/`jobscript`/`ccmc_spec`/`paper_spec` as artifact types instead of new public tools.** Alternative considered: a new `parse_spec` tool. Rejected because of the typed-artifact preference in `skill_mcp_protocol.md`. Chosen because each artifact type is deterministic and reuses the existing `inspect_artifact` contract shape.
- **No `task_type="replication"` initially.** Alternative considered: add immediately. Rejected because evidence is mostly union of `configuration|run|analysis`. Will be added in Phase 3 if telemetry shows fragmentation.
- **Validation does not get a new MCP comparison type.** Alternative considered: `compare_artifacts(comparison_type="reference")` with image hashing. Rejected because cross-domain comparison (image ↔ data trace ↔ simulated trace) is judgmental and would force MCP to embed criteria.
- **`paper_spec` requires the agent to write a JSON file first.** Alternative considered: have MCP accept paper text directly and parse it. Rejected because PDF/text parsing is not deterministic and would smuggle reasoning into MCP. Chosen pattern preserves the "MCP only sees structured artifacts" boundary.
- **CME initiation gets its own support skill (`swmf-cme-setup`).** Alternative considered: keep CME in `swmf-configure`. Rejected because CME initiation has its own decision tree (FR type → required PARAM block → multi-session structure) that is separable. Chosen because at least two entry skills (`swmf-replicate` and `swmf-configure`) need it.
- **PARAM.in for construction jobs is agent-written, not script-generated.** Alternative considered: make `change_param.py` (or a successor) the universal PARAM authoring tool. Rejected because the script is purely template-fill — it cannot insert command blocks, reshape sessions, or reorder commands, all of which are common in case construction. Chosen because composition is workflow reasoning (agent territory); `change_param.py` stays as the deterministic helper for sweep-mode work it was actually designed for.
- **Rules directory under `swmf-params/`, evaluated by MCP via YAML.** Alternative considered: encode rules inside MCP code, or inside the skill body as prose. Rejected because in-code rules require a code change for every domain-knowledge addition (high friction; user is the domain expert, not necessarily a Python author), and prose-only rules are not deterministically evaluable. Chosen YAML-driven design because the user owns the file, the format is reviewable, MCP evaluates without judgment, and the skill consumes the same directory for narrative content.

---

## 11. Short Checklist for Implementers

1. Read `docs/skill_mcp_protocol.md` and treat it as binding.
2. Read `docs/idl_visualization_skill_protocol.md` as the model for support-skill style.
3. Skim SWMFSOLAR top-level Makefile and Scripts/ before touching anything.
4. Phase 1 first; do not extend MCP beyond `jobscript` and the `run_dir` PARAM-delta until Phase 1 gold prompts pass.
5. For every proposed new field in `inspect_artifact`, write the typed shape *first* and verify it surfaces no advice.
6. For every new skill section, verify "When not to use" exists.
7. Run gold prompts before merging each phase; record skill chosen, first MCP tool, fallback rate, advice leaks.

---

## 12. Short Version

- One new entry skill `swmf-replicate` with three intents.
- Five new support skills: `swmf-magnetogram`, `swmf-jobscript`, `swmf-cme-setup`, `swmf-validation`, `swmf-swmfsolar`.
- MCP changes are typed extensions of `inspect_artifact` (`jobscript`, `magnetogram`, `ccmc_spec`, `paper_spec`, plus `check_rules=True` on `param`) and a `param_diff` block on `compare_artifacts(comparison_type="run_dir")`. No new public tools.
- PARAM.in generation is two modes (§6.5): **sweep** uses `change_param.py`; **construction** is agent-written directly, guided by template + PARAM.XML + the `swmf-params/rules/` directory.
- CME cases are **two-PARAM** (background + restart, §6.6); the skill produces both and orchestrates a two-stage submission.
- A spec contributes a small minority of PARAM content (§6.7: ~25 spec values vs ~400 PARAM commands). The agent maps spec → PARAM via direct fields, geometric derivations, and recipe-driven mappings; everything else comes from the closest-precedent template and the case recipe. Required agent abilities are inventoried in §6.8.
- The rules directory (§5.4) is the user's extension interface for domain knowledge, organized in four lanes — **constrain** (`physical_constraints.yaml`), **structure** (`case_recipes/`), **derive** (`derivations/`), **default** (`defaults/`) — anchored by template-pair manifests (`templates/`). Every PARAM value the agent emits is produced by walking the authoring ladder (§5.4.7) and tagged with the supplying lane. New domain knowledge is a YAML drop; only schema additions touch code.
- A mandatory pre-launch gate runs MCP rule checks, `Scripts/TestParam.pl`, a PARAM diff, and explicit user approval. Hard-blocks on `severity=block` rule violations or schema errors.
- The Phase 2 gold target is `examples/CCMC_run_weihao/`: agent reproduces both PARAM files against the bundled standard answers, with every delta classified.
- Operational logic (download, build, submit, postproc) stays in SWMFSOLAR scripts the agent shells; MCP only inspects results.
- **Slim PARAM inspector (§5.3.1)**: `inspect_artifact(artifact_type="param")` returns structural primitives only (sessions, includes, component map, external refs, parser errors, rule violations). The agent reads PARAM.in directly for intent reasoning. `inspect_artifact(param)` is invoked only for rule evaluation, compare, or include/external-ref resolution.
- Validation against papers/observations is skill-level, not MCP-level. Reference comparison is presented to the user; MCP does not adjudicate.
