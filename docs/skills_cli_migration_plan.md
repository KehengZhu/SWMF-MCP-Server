# Migration plan: skills + MCP → skills + local CLI

> **Status: COMPLETE.** All phases implemented. Suite: 261 passed, 1 pre-existing
> failure (`test_weihao_restart_passes_via_include`, a params rule-check
> regression from the in-flight embeddings/rules refactor — unrelated to this
> migration and failing before it began). The MCP layer is fully removed; the
> `swmf` CLI + skills are the only surface.

## Goal

Replace the MCP-over-stdio interface with a local `swmf` console command that
skills invoke via Bash. All the intelligence (catalog, BM25 keyword index,
PARAM/XML/log parsers, XML audit gate) is kept verbatim. The MCP server, the
`mcp` dependency, and all per-agent MCP config are removed.

Rationale: the project runs entirely locally, so the client/server MCP transport
adds nothing but indirection. The four tool functions are already pure
`fn(args) -> dict`; `register(app)` is the only MCP-specific glue.

## Decisions (locked)

| Decision | Choice |
|---|---|
| MCP fate | **Full removal** — delete the server, drop the `mcp` dep, no MCP config |
| Script interface | **`swmf` CLI subcommands** (one console-script entrypoint), JSON to stdout |
| Audit gate state | **Persist to disk** under the run dir — keep the hard, machine-enforced gate |

## Architecture

```
BEFORE:  skill (md) ──MCP tool call──► FastMCP server (long-lived) ──► tool fn ──► dict
AFTER:   skill (md) ──Bash: swmf <cmd>──► cli.py (one-shot) ──────► tool fn ──► JSON to stdout
```

The four agent-facing tools and their CLI mapping:

| Function (today) | CLI subcommand |
|---|---|
| `get_context(question, scope, task_type, detail, swmf_root, run_dir)` | `swmf get-context` |
| `get_evidence(query, mode, scope, top_k, goal, task_type, module, swmf_root, run_dir)` | `swmf get-evidence` |
| `inspect_artifact(artifact_type, path, question, swmf_root, run_dir, check_rules, xml_scope, check_xml_audit)` | `swmf inspect` |
| `compare_artifacts(left, right, comparison_type, question, swmf_root, run_dir)` | `swmf compare` |
| `ks.build_index/refresh_index` (server `--preindex-knowledge`, `scripts/preindex.py`) | `swmf index build|refresh|status` |

Every subcommand accepts `--swmf-root` / `--run-dir`; `SWMF_ROOT` still resolves
automatically via `core/swmf_root.py`, so they are usually unneeded.

## Phases

### Phase 0 — Stabilize the in-flight refactor (precondition)
A large uncommitted change already removed semantic search / `fastembed` / mined
defaults, leaving keyword-only BM25. Confirm the working tree is green
(`pytest`) before building on it. The migration builds on this base, not
against it.

### Phase 1 — Add the `swmf` CLI (additive)
- New `src/swmf_mcp_server/cli.py`: an `argparse` dispatcher mapping subcommands
  to the existing tool functions; prints `json.dumps(result)` to stdout; exits
  non-zero when the result has `ok: False` / `hard_error`.
- Add console-script to `pyproject.toml`: `swmf = "swmf_mcp_server.cli:main"`
  (lands at `.venv/bin/swmf` after `uv sync`).
- Subcommands: `get-context`, `get-evidence`, `inspect`, `compare`,
  `index build|refresh|status`.

### Phase 2 — Persist the audit gate to disk
- Rework `audit/session_state.py`: disk-backed `AuditStore` writing JSON to
  `<run_dir>/.swmf_ai/audit.json` (the run dir is the natural session boundary).
- Thread a real session key (derived from `run_dir`) through the two call sites
  in `tools/inspect_artifact.py` (currently hardcoded `session_id=None`).
  `xml_audit.py` already passes it through.
- Round-trip: `swmf inspect --type xml --xml-scope commandgroup:...` records the
  read; `swmf inspect --type param --check-xml-audit` reads it back across
  separate processes. Same waiver syntax and group keys as today — only the
  storage backend changes.

### Phase 3 — Index management through the CLI
- `swmf index build/refresh/status` wraps `ks.build_index/refresh_index`,
  replacing the server-startup `--preindex-knowledge` path and folding in
  `scripts/preindex.py`. `make` calls `swmf index build`.

### (validate) — run the suite; CLI works while MCP still exists.

### Phase 5 — Rewrite skills + discipline to call the CLI
- `SWMF_CORE_DISCIPLINE.md`: retitle "V2 MCP tool surface" → "Local CLI surface";
  rewrite the tool table and per-task defaults to `swmf <subcommand>` form. Keep
  the evidence-discipline and pre-search-gate rules verbatim (interface-agnostic).
- The 9 skills with tool references: mechanically convert e.g.
  `get_context(question=..., task_type="architecture")` →
  `` `swmf get-context --question "..." --task-type architecture` ``.
  swmf-replicate's mandatory `xml_scope` calls + launch audit check map to
  `swmf inspect --xml-scope commandgroup:...` / `--check-xml-audit`.

### Phase 4 — Rewrite install (drop MCP config; make `swmf` resolvable)
- In `scripts/install.py`: **stop symlinking** the instruction file; *generate*
  it (CLAUDE.md / AGENTS.md / copilot-instructions.md) = shared discipline
  content + a generated header naming the absolute `swmf` launcher path +
  `SWMF_ROOT`. The instruction file is always in context, so the agent always
  knows the binary — no PATH setup, no per-skill templating.
- Keep symlinking the skill tree.
- Delete all `*.mcp.json` / `.codex/config.toml` generation helpers.
- Drop `SERVER_PYTHON` / MCP wiring from the `Makefile`; keep `.venv` bootstrap
  and the `.swmf_mcp_server` symlink (launcher lives under it for external targets).

### Phase 6 — Delete MCP
- Delete `server.py`, the `register()` functions in each tool, the
  `swmf-mcp-server` console script, the FastMCP fallback shim, `.mcp.json`,
  `.vscode/mcp.json`.
- Drop `mcp[cli]` from `pyproject.toml`.
- Rewrite `README.md` (mermaid diagram, "MCP Tools" section, install prompt) for
  the CLI model.

### Phase 7 — Tests & eval
- Replace `test_server_startup.py`, `test_resource_registration.py`,
  `test_tools_package_surface.py` (MCP-surface assertions) with CLI tests:
  subcommand dispatch, JSON-on-stdout, exit codes, audit round-trip across two
  separate CLI processes.
- Most existing tests call the tool functions directly → unchanged.
- Point the eval harness at `swmf`.

## Risks

1. **`swmf` resolution** is the make-or-break detail — the generated
   instruction-header approach (Phase 4) makes it robust without PATH hacks.
   Fallback: symlink the venv `swmf` into `~/.local/bin`.
2. **Audit gate semantics must stay identical** — same waiver syntax, same group
   keys; only storage changes. Guarded by a round-trip test (Phase 2/7).
3. **Sequencing for safety** — Phases 1–3 are additive (CLI works while MCP still
   exists), so the CLI is validated end-to-end before MCP is deleted in Phase 6.

## Suggested order

`0 → 1 → 2 → 3 → (validate) → 5 → 4 → 6 → 7`

Skills+discipline (5) are done before install (4) so install can be tested
against finished skills.
