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

## Local CLI surface

Retrieval and artifact inspection run through one local command, `swmf`,
invoked via the shell. (The absolute launcher path is given at the top of this
instruction file; run it as `swmf <subcommand>`.) Each subcommand prints a JSON
result to stdout. All backends (catalog, keyword index, PARAM parser, log
extractor, script scanner) are hidden inside them. Semantic / embedding
retrieval has been removed; every search uses the catalog keyword (BM25)
backend.

| Command | Use for |
|---|---|
| `swmf get-context` | Broad orientation, architecture, cross-component questions |
| `swmf get-evidence` | Symbol/param/file lookup, code grounding, workflow evidence, evidence gathering |
| `swmf inspect` | Deep inspection of a log, PARAM.in, PARAM.XML, run directory; **`--type xml --xml-scope 'commandgroup:<name>'` is the primary authoring channel before writing a physics-substantive PARAM block** |
| `swmf compare` | Diff two PARAM files, logs, run outputs, or directories |

Default command per task type:

* **explain** → `swmf get-context` first, then `swmf get-evidence --mode keyword`
* **configure** → `swmf inspect --type xml --xml-scope 'commandgroup:...'` for PARAM-command syntax/defaults; `swmf get-evidence --task-type configuration` for scripts
* **build / run** → `swmf get-evidence --task-type build|run` first
* **debug** → `swmf inspect` first
* **analyze** → `swmf inspect` first, then `swmf get-evidence --task-type analysis` when postprocessing entrypoints are needed
* **compare** → `swmf compare` first
* **replicate (authoring)** → `swmf inspect --type xml --xml-scope 'commandgroup:...'` is **mandatory** for every physics-substantive PARAM block; the audit gate enforces this at the launch step

### XML audit gate: pass a consistent `--run-dir`

The audit gate persists which command groups were read to
`<run_dir>/.swmf_ai/audit.json`. For it to correlate the reads with the launch
check, **pass the same `--run-dir <your run directory>` to every
`swmf inspect --type xml --xml-scope 'commandgroup:...'` read AND to the
`swmf inspect --type param --check-xml-audit` launch check.** Reads recorded
under a different (or missing) `--run-dir` will not count, and the launch will
be blocked.

---

## Evidence discipline

1. **Exact token in the query** → `swmf get-evidence --mode keyword` first.
2. **Broad NL question** → `swmf get-context` or `swmf get-evidence --mode keyword`.
3. **Local artifact available** → `swmf inspect` or `swmf compare` before any search.
4. **Grep is a fallback**, not a first move. When allowed: restrict to file paths
   returned by the `swmf` command, never the full SWMF tree.
5. **Do not answer operational questions without artifacts** when a run directory
   or log file is available.
6. **Do not let heuristic evidence override** validators, `PARAM.XML`, or
   `TestParam.pl` output.

## Runlog discipline

Do not directly read a whole `runlog*`, `.stdout`, `.stderr`, or large runtime
`.log` file unless the user explicitly asks for raw log content. Runtime logs
must be compacted through `swmf inspect --type log|run_dir ...` or compared
through `swmf compare` first.

After the tool response, direct reads are allowed only as bounded follow-up:
specific line ranges, `rg` for named diagnostics, or short `head`/`tail`
windows needed to verify a finding.

---

## Mandatory pre-search gate

Before any grep, directory walk, glob, or direct file read for a source,
architecture, or mechanism question, the agent **must**:

1. Run the designated first `swmf` command for the request type.
2. Check whether the command's output answers the question or names the files to read.

Only after this gate may the agent read specific files — and only from the
paths returned by the first command.

**Skipping this gate is a protocol violation.**

---

## Response contract

Every answer must include:

* what was checked (which command / artifact)
* what evidence supports the conclusion
* what remains uncertain
* what next check should happen if uncertainty matters

Do not name `swmf` commands to the user unless the user asks or the evidence
path itself is important.
