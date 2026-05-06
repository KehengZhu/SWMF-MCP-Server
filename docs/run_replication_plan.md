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

### 5.4 Extension interface: `swmf-params` rules directory

The `swmf-params` support skill owns a rules directory the user grows over time. This is the **single backstop** for everything the agent does not yet know about valid PARAM construction. Both MCP and the skill consume from it:

```
src/agent_assets/skills/support/swmf-params/rules/
  physical_constraints.yaml   # deterministic if/then rules, evaluated by MCP
  numerical_practices.md      # narrative best practices, loaded by the skill
  case_recipes/
    awsom_steady_sc.md        # multi-session structure for steady-state SC
    awsom_cme_eruption.md     # background → eruption session reshaping
    sofie_mflampa.md          # SOFIE+MFLAMPA SEP follow-up structure
    geospace_gmie.md          # geospace coupling case (future)
```

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

#### 5.4.4 Maintenance contract

- Adding a new rule: append to `physical_constraints.yaml`. No code change.
- Adding a new narrative practice: append to `numerical_practices.md`. No code change.
- Adding a new case archetype: add a new file under `case_recipes/`. No code change.
- Schema changes to `physical_constraints.yaml` (new predicate types): require MCP code change in `inspect_artifact(artifact_type="param")` rule evaluator. Treat these as MCP API changes and version them.

This is the user's primary leverage point. Every time the agent silently fills in a value during replication and the user disagrees, the fix belongs here.

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

1. Skill picks the **closest-precedent template** from SWMFSOLAR `Param/` or a prior run, and the matching **case recipe** from `swmf-params/rules/case_recipes/`.
2. Agent reads the template directly. Agent reads the case recipe to understand the target multi-session skeleton.
3. Agent enumerates the **delta**: what command blocks must be added, removed, reordered, or have their values changed; which session boundaries shift.
4. For each delta item, agent gathers evidence: PARAM.XML schema (authoritative), prior-run example (precedent), `physical_constraints.yaml` and `numerical_practices.md` (rules and narrative).
5. Agent **writes PARAM.in directly** via Edit/Write at the assembled run directory path. Composition is workflow reasoning; this is agent territory.
6. Where a sub-block within the construction is itself a sweep (e.g. plugging the GL flux-rope numbers from the spec into the new `#CME` block), the agent may shell `change_param.py` for that sub-step after the structural edit is in place.
7. Validation gate (§6.5.5) runs.

The skill output contract requires the agent to record:

- which template was the base,
- which case recipe was followed,
- the structural delta (added/removed/reordered command blocks, session changes),
- per-value provenance (spec-stated | prior-run | template-default | rule-derived | user-confirmed),
- explicit list of values the agent inferred and could not source (these become user-approval items).

The agent **must not** invent numerical values. If a spec is silent on a parameter and no template/recipe/rule supplies it, the skill reports the gap and asks the user.

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

---

## 7. Phased Rollout

Each phase has one entry-deliverable and an exit criterion that is testable from a small gold prompt set.

### 7.1 Phase 1 — Skill scaffolding + jobscript inspection + rules skeleton + gate

**Deliverable**:

- `swmf-replicate` entry skill (skeleton with intents and evidence order, including the §6.5 PARAM-generation step and the §6.5.5 launch gate).
- `swmf-jobscript` support skill.
- `inspect_artifact(artifact_type="jobscript")` extension.
- `compare_artifacts(comparison_type="run_dir")` PARAM-delta extension.
- **Rules directory skeleton** under `src/agent_assets/skills/support/swmf-params/rules/` with:
  - `physical_constraints.yaml` containing 5–10 seed rules covering the most common AWSoM/CME pitfalls (the user authors these; the skill ships with a starter set).
  - `numerical_practices.md` with a few seed entries.
  - `case_recipes/awsom_cme_eruption.md` derived from `Run_Max_RP_CME3/run01`.
- `inspect_artifact(artifact_type="param")` extended with `check_rules=True` consuming the YAML.
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
- The rules directory (`physical_constraints.yaml` + `numerical_practices.md` + `case_recipes/`) is the user's extension interface for domain knowledge. New rules require zero MCP code change.
- A mandatory pre-launch gate runs MCP rule checks, `Scripts/TestParam.pl`, a PARAM diff, and explicit user approval. Hard-blocks on `severity=block` rule violations or schema errors.
- Operational logic (download, build, submit, postproc) stays in SWMFSOLAR scripts the agent shells; MCP only inspects results.
- Validation against papers/observations is skill-level, not MCP-level. Reference comparison is presented to the user; MCP does not adjudicate.
