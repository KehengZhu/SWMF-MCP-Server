---
name: swmf-mflampa
type: support
description: >-
  Support skill. MFLAMPA (SP component) expert for the SEP transport/acceleration
  model: source-module map and the per-step advance loop, linked libraries and the
  standalone-vs-coupled split, the `make test_mflampa` test workflow (compile → rundir
  → run → check) and its variants, and MFLAMPA PARAM commands with their physical
  meaning. Consulted by swmf-explain, swmf-build, swmf-run, swmf-configure, and
  swmf-debug when the component in play is SP / MFLAMPA. Reference for the physics is
  the paper set under `docs/mflampa-papers/`.
---

# swmf-mflampa (Support)

This is a **support skill**. It is not chosen directly by the agent. Entry skills
consult it when the task concerns the **SP component, MFLAMPA**, the SEP model:

- `swmf-explain` — how the SEP transport solve, coupling, or a module works.
- `swmf-build` — building/configuring MFLAMPA (`Config.pl -g`, standalone targets).
- `swmf-run` — running MFLAMPA standalone (`MFLAMPA.exe`, MH_data input).
- `swmf-configure` — MFLAMPA PARAM commands and their physical meaning.
- `swmf-debug` — failure analysis in an MFLAMPA build/run/test.

MFLAMPA = **M**ultiple **F**ield **L**ine **A**dvection **M**odel for **P**article
**A**cceleration. It solves the kinetic transport of solar energetic particles (SEPs)
along Lagrangian magnetic field lines, accelerated by diffusive shock acceleration at
CME-driven shocks. It lives at `SP/MFLAMPA` in the SWMF tree and is itself a
standalone git repository.

## Purpose

Answer MFLAMPA-specific questions that the generic (solar/heliosphere-tuned) entry
skills cannot answer correctly on their own:

- **Code**: what each `Mod*.f90` does, where the transport equation is solved, and
  what the per-timestep operator sequence is. → `reference/modules.md`
- **Coupling/build**: which external libraries MFLAMPA links, how it differs in
  standalone vs SWMF-coupled mode, and what `Config.pl -g` controls. →
  `reference/coupling.md`
- **Params**: what each MFLAMPA `#COMMAND` means physically and which test PARAM
  exercises it. → `reference/params.md`
- **Tests/runs**: the `make test_mflampa` pipeline and its variants (poisson, steady,
  spectra, pitch-angle), how to read the `.diff`, and the `BLESS` mechanism. →
  `workflows/test.md`

## Scope

In scope:

- MFLAMPA source structure, the advance loop, and where physics terms attach.
- The diffusion / turbulence / Poisson-bracket scheme distinctions.
- Standalone MFLAMPA build, run, and the `make test_mflampa` test suite.
- MFLAMPA PARAM command meaning and the standalone PARAM.in structure.

Not in scope (defer):

- Full solar/heliosphere PARAM replication and the AWSoM/SOFIE rules layer →
  `swmf-params`, `swmf-replicate`.
- CME initiation and `#CME` blocks → `swmf-cme-setup`.
- The MHD background (SC/IH, AWSoM) that *feeds* MFLAMPA when coupled → those
  components' own evidence; this skill covers only the SP side of the interface.
- Generic SWMF build/run mechanics that are not MFLAMPA-specific → keep them with
  `swmf-build` / `swmf-run`.
- Source patches: when a code change is actually requested, the implementation gate
  is `swmf-implementation`; this skill supplies the MFLAMPA-specific *where and how*,
  not the patch-readiness discipline.

## Tool Protocol

MFLAMPA is the **SP** component. Always scope source evidence to it — an unscoped
query for an MFLAMPA symbol drifts to other particle components (e.g. `PT/AMPS`
documentation).

1. **Source / symbol / mechanism** evidence:
   ```bash
   swmf get-evidence --query "<symbol or phrase>" --scope SP --goal "<why>"
   ```
   Then read only the `SP/MFLAMPA/...` files the result names.

2. **PARAM command syntax / defaults** (the authoring channel) — read the schema from
   MFLAMPA's own PARAM.XML before writing or judging a command:
   ```bash
   swmf inspect --type xml --path SP/MFLAMPA/PARAM.XML --xml-scope 'command:<NAME>'
   swmf inspect --type xml --path SP/MFLAMPA/PARAM.XML --xml-scope 'commandgroup:<GROUP>'
   ```
   Command groups: `DOMAIN`, `UNIT`, `STAND ALONE MODE`, `STOPPING CRITERIA`,
   `GRID`, `ENERGYCHANNEL`, `ENDBC`, `ADVANCE`, `ACTION`, `TURBULENCE`,
   `INPUT/OUTPUT`.

3. **A concrete PARAM.in / run directory**:
   ```bash
   swmf inspect --type param   --path <PARAM.in>
   swmf inspect --type run_dir --path <run_test or other run dir>
   ```

4. **Broad orientation** ("how does the SEP model work?"):
   ```bash
   swmf get-context --question "<question>" --scope SP
   ```

5. Load the bundled reference doc that matches the question (`reference/modules.md`,
   `reference/coupling.md`, `reference/params.md`, `workflows/test.md`). These carry
   the operational/architectural knowledge that is **not** auto-derivable from a
   single evidence hit. The physics derivations behind them are the papers under
   `docs/mflampa-papers/` (see `reference/modules.md` §Physics map).

## Authority Order

1. The live source under `SP/MFLAMPA/src` and `srcInterface` (via `get-evidence
   --scope SP`) — the ground truth for code behavior.
2. `SP/MFLAMPA/PARAM.XML` (via `inspect --type xml`) — the ground truth for command
   syntax, defaults, and allowed values.
3. `SP/MFLAMPA/Makefile` and `Config.pl` — the ground truth for build/test targets.
4. The bundled `reference/` and `workflows/` docs — the curated map that points into
   1–3 and explains the physics intent.
5. The `docs/mflampa-papers/` set — the physics derivations (cite, don't paraphrase
   numbers from memory).

When a bundled doc and the live source disagree, the **source wins** and the doc is
stale — say so. Reference docs name file:line anchors precisely so this is checkable.

## Output Contract

A useful MFLAMPA answer states:

- `component` — `SP / MFLAMPA`, standalone or coupled mode.
- `evidence` — which `swmf` command(s) and which `SP/MFLAMPA/...` files grounded the
  answer.
- For a **param** question: the command, its group, its physical meaning, and the
  test PARAM that exercises it.
- For a **code** question: the module and subroutine (`file:line`), and where it sits
  in the advance loop (`ModMain.run` → `ModAdvance.advance`).
- For a **test/run** question: the exact `make` target chain, the grid sizing
  (`Config.pl -g`), the input data, and the reference the `.diff` compares against.
- `uncertainty` — anything not confirmed against source/XML, and the next check.

## Anti-patterns

- **Do not run an unscoped `get-evidence` for an MFLAMPA symbol.** Pass `--scope SP`;
  otherwise the keyword backend returns `PT/AMPS` (a different particle code) docs.
- **Do not assume the SWMF-root build/run flow.** MFLAMPA standalone is built and
  tested from *inside* `SP/MFLAMPA` (`./Config.pl`, `make`, `make test_mflampa`,
  `mpirun ./MFLAMPA.exe`), not from the SWMF root. See `workflows/test.md`.
- **Do not invent a PARAM command or its argument order.** Read it from PARAM.XML
  via the xml-scope channel first; MFLAMPA's vocabulary is distinct from the
  AWSoM/SOFIE solar commands.
- **Do not conflate the two advance schemes.** `#ADVECTION UsePoissonBracket=T`
  selects the conservative Poisson-bracket solver (`ModAdvancePoisson`); `F` selects
  the log-advection solver (`ModAdvanceAdvection`). They take different sub-paths.
- **Do not paraphrase physics constants/equations from memory.** Anchor them to the
  papers in `docs/mflampa-papers/` or to the source comments that cite them.
