# MFLAMPA test workflow (`make test_mflampa`)

How the standalone MFLAMPA test suite works, so the agent can run it, read its result,
and use it as the regression gate when a physical term is added. All commands run from
**inside `SP/MFLAMPA`** (the component is its own standalone repo), not the SWMF root.

## Run it

```bash
cd SP/MFLAMPA
make test_mflampa            # the nightly SEP transport test
make test                    # all three: test_mflampa + test_poisson + test_steady
make test_mflampa MPIRUN=    # force serial (empty MPIRUN) if MPI is unavailable
```

A passing test leaves a small `test_mflampa.diff` containing only the stage banners and
*no numeric differences*. See §Reading the result.

## Prerequisite: test data must be present (common gotcha)

The rundir stage untars an MHD background dataset and the check stage compares against a
gzipped reference:

- input  `SP/MFLAMPA/data/input/test_mflampa/MH_data_e20120123.tgz`
- ref    `SP/MFLAMPA/data/output/test_mflampa/MH_data.ref.gz`
  (and `MH_poisson_data.ref.gz`, `MH_steady_data.ref.gz` for the variants)

**This `data/` directory is git-ignored and may be absent in a fresh checkout.** If it
is missing, the rundir stage fails on the `tar xzf …` step. Confirm it exists before
running; if absent, it must be fetched via the SWMF test-data mechanism (the data is
hosted separately from the source). Surface this to the user rather than reporting a
spurious test failure.

```bash
ls SP/MFLAMPA/data/input/test_mflampa SP/MFLAMPA/data/output/test_mflampa
```

## The pipeline

`make test_mflampa` runs four sub-targets in order (each appends to `test_mflampa.diff`):

1. **`test_mflampa_compile`** → `test_compile`: `./Config.pl -g=20000` then `make`.
   `-g=20000` sets `nVertexMax=20000` with default `nMomentum=100`, `nPitchAngle=1`
   ⇒ **μ-averaged** build. (`test_compile_mu` uses `-g=20000,100,5` for a pitch-angle /
   focused-transport build.)
2. **`test_mflampa_rundir`**: `rm -rf run_test`; `make rundir RUNDIR=run_test
   STANDALONE=YES SPDIR=\`pwd\``; copy `SP/Param/PARAM.in.test` → `run_test/PARAM.in`;
   untar the `MH_data_e20120123` dataset into the run dir.
3. **`test_mflampa_run`** → `test_run`: `cd run_test; ${MPIRUN} ./MFLAMPA.exe | tee
   runlog`.
4. **`test_mflampa_check`**: concatenate the `MH_data*.out` outputs into `MH_data.outs`,
   then `share/Scripts/DiffNum.pl -BLESS=NO -t -r=1e-6 -a=1e-6 MH_data.outs
   data/output/test_mflampa/MH_data.ref.gz > test_mflampa.diff`; `ls -l` the diff.

Defaults (top of the Makefile testing section): `TESTDIR = run_test`, `BLESS = NO`.

## Variants

| Target | PARAM used | Reference | What it exercises |
|---|---|---|---|
| `test_mflampa` | `PARAM.in.test` | `MH_data.ref.gz` | baseline standalone SEP run |
| `test_poisson` | `PARAM.in.test.poisson` | `MH_poisson_data.ref.gz` | conservative Poisson-bracket advection (`#ADVECTION T`); `RUNDIR=run_poisson` |
| `test_steady` | `.test.steady.start` then `.test.steady.restart` | `MH_steady_data.ref.gz` | steady-state iterate + restart (runs `Restart.pl` between); `RUNDIR=run_steady` |
| `test_compile` | — | — | μ-averaged compile (`-g=20000`) |
| `test_compile_mu` | — | — | pitch-angle compile (`-g=20000,100,5`) |

There is also a separate `make test_poisson_bracket` unit test for the bracket engine
(`test_poisson_bracket.f90`), checked against `output/test_poisson*.ref*` with tighter
tolerances — independent of the SEP integration tests above.

## Reading the result

- The diff file (`test_mflampa.diff`, `test_poisson.diff`, `test_steady.diff`) holds the
  stage banners (`test_mflampa_compile...`, etc.) followed by `DiffNum.pl` output.
- **Pass** = no numeric differences reported (the diff has only banners / is otherwise
  empty). `make test` ends with `ls -l test*.diff`; a passing run shows small files.
- **Fail** = `DiffNum.pl` lists differences beyond the tolerances (`-r=1e-6`,
  `-a=1e-6`). Distinguish a *real* numerical regression from a *setup* failure
  (missing `data/`, compile error, MPI not found) — check the run log and the earlier
  stages first.
- Don't dump `runlog` wholesale; compact it via `swmf inspect --type run_dir --path
  run_test` (or `--type log`) per the core discipline, then read bounded windows.

## Updating the reference (BLESS) — use with care

`BLESS=YES` overwrites the stored reference with the current output:

```bash
make test_mflampa BLESS=YES     # re-bless: only when the new output is the intended truth
```

Only bless when a change is *expected* to alter results and the new output has been
verified correct. Blessing to make a red test green hides regressions. When a new
physical term legitimately changes the answer, bless deliberately and record why.

## Using the suite as a regression gate (for term development)

When a physical term is added (see `reference/modules.md` §Where a new term attaches):

1. Establish a green baseline first: `make test_mflampa && make test_poisson &&
   make test_steady` on the unmodified tree (requires the `data/` directory).
2. Make the change; rebuild with the appropriate `Config.pl -g` (add `nMu>1` if the
   term is pitch-angle dependent).
3. Re-run the suite. A term that is *off by default* must leave all three diffs
   unchanged (no regression). A term that is *on* will change results — add or extend a
   dedicated test PARAM + reference for it rather than blessing the existing baselines.
4. The patch-readiness / validation discipline around this is `swmf-implementation`.
