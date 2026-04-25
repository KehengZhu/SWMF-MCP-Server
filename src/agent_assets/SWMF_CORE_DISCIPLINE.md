# SWMF Core Discipline

Shared global rules. Every SWMF skill must apply these before domain-specific rules.

---

## One primary skill per task

Choose one entry skill based on what the user is trying to get done:

| User intent | Entry skill |
|---|---|
| "how does X work?" | `swmf-explain` |
| "how do I set up / configure X?" | `swmf-configure` |
| "how do I build?" | `swmf-build` |
| "how do I run?" | `swmf-run` |
| "why did this fail?" | `swmf-debug` |
| "what does this output mean?" | `swmf-analyze` |
| "what changed / which is different?" | `swmf-compare` |

Support skills (`swmf-architecture`, `swmf-implementation`, `swmf-params`,
`swmf-postproc`, `swmf-exact-lookup`) are helpers. They do not own the answer.
An entry skill consults them to fill specific gaps.

---

## V2 MCP tool surface

These four tools are the only agent-facing retrieval interface. All backends
(catalog, semantic index, param parser, log extractor, script scanner) are
hidden inside them.

| Tool | Use for |
|---|---|
| `get_context` | Broad orientation, architecture, cross-component questions |
| `get_evidence` | Symbol/param/file lookup, code grounding, workflow evidence, evidence gathering |
| `inspect_artifact` | Deep inspection of a log, PARAM.in, XML, or run directory |
| `compare_artifacts` | Diff two PARAM files, logs, run outputs, or directories |

Default tool per task type:

* **explain** → `get_context` first, then `get_evidence`
* **configure** → `get_evidence(mode="keyword")` for PARAM meaning; `get_evidence(task_type="configuration")` for scripts
* **build / run** → `get_evidence(task_type="build"|"run")` first
* **debug** → `inspect_artifact` first
* **analyze** → `inspect_artifact` first, then `get_evidence(task_type="analysis")` when postprocessing entrypoints are needed
* **compare** → `compare_artifacts` first

Legacy helper tools are not part of the public MCP surface. Use the four v2
tools above for all agent-facing retrieval and artifact inspection.

---

## Evidence discipline

1. **Exact token in the query** → `get_evidence(mode="keyword")` first.
2. **Broad NL question** → `get_context` or `get_evidence(mode="hybrid")`.
3. **Local artifact available** → `inspect_artifact` or `compare_artifacts` before any search.
4. **Grep is a fallback**, not a first move. When allowed: restrict to file paths
   returned by the v2 tool, never the full SWMF tree.
5. **Do not answer operational questions without artifacts** when a run directory
   or log file is available.
6. **Do not let heuristic evidence override** validators, `PARAM.XML`, or
   `TestParam.pl` output.

## Runlog discipline

Do not directly read a whole `runlog*`, `.stdout`, `.stderr`, or large runtime
`.log` file unless the user explicitly asks for raw log content. Runtime logs
must be compacted through `inspect_artifact(artifact_type="log"|"run_dir", ...)`
or compared through `compare_artifacts` first.

After the tool response, direct reads are allowed only as bounded follow-up:
specific line ranges, `rg` for named diagnostics, or short `head`/`tail`
windows needed to verify a finding.

---

## Mandatory pre-search gate

Before any grep, directory walk, glob, or direct file read for a source,
architecture, or mechanism question, the agent **must**:

1. Call the designated first MCP tool for the request type.
2. Check whether the tool's output answers the question or names the files to read.

Only after this gate may the agent read specific files — and only from the
paths returned by the first tool.

**Skipping this gate is a protocol violation.**

---

## Response contract

Every answer must include:

* what was checked (which tool / artifact)
* what evidence supports the conclusion
* what remains uncertain
* what next check should happen if uncertainty matters

Do not name MCP tools to the user unless the user asks or the evidence path
itself is important.
