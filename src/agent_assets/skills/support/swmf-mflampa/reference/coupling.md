# MFLAMPA coupling, libraries & grid sizing

How MFLAMPA links other code, how standalone differs from coupled, and what
`Config.pl -g` controls. Anchors drift — confirm with `swmf get-evidence --scope SP`.
The standalone path is the focus (it is the one the test suite and a term-development
loop use); the coupled path is documented for orientation.

## Two run modes

| | Standalone | Coupled (in SWMF) |
|---|---|---|
| Entry | `SP_stand_alone.f90` → `MFLAMPA.exe` | `srcInterface/SP_wrapper.f90` (SP component) |
| MHD background | read from files by `ModReadMhData` (`DoReadMhData=T`) | received from SC/IH via the coupler |
| `IsStandAlone` (ModTime) | `T` | `F` |
| Field-line grid | built locally (`init_grid`, origin points) | `CON_bline.BL_set_grid` / `BL_init` |
| Time control | local `SPTime`, `DataInputTime` | `SP_put_coupling_param` from the coupler |
| Use case | testing, term development, replaying saved MH_data | full Sun→1 AU event (SOFIE) |

### Standalone

The model reads a precomputed MHD background (B, ρ, U, waves along each line) from a
directory of `MH_data` files in time sequence:

- `#READMHDATA` with `DoReadMhData=T` and `NameInputDir <dir>` →
  `ModReadMhData.f90` (`DoReadMhData` at ~28, `NameInputDir` at ~30, reader at ~89).
- `#INCLUDE <dir>/MH_data.H` pulls in the header describing the dataset (grid size,
  variables, tags).
- The run then advances the SEP distribution along those frozen field-line snapshots.

This is exactly what `make test_mflampa` sets up (it untars an `MH_data_e20120123`
dataset into the run dir). See `workflows/test.md`.

### Coupled (orientation only)

`SP_wrapper.f90` implements the SWMF component interface and pulls field-line +
MHD data from the bline coupler:

- `use CON_coupler` (`SP_`, …), `use CON_bline` (`BL_set_grid`), `use CON_physics`
  (`get_time`).
- `SP_set_param` (46) → `BL_set_grid(TypeCoordSystem, UnitX, EnergyCoeff)` (108).
- `SP_init_session` (114) → `initialize`, `init_grid`, origin points (`ROrigin`,
  `LonMin/Max`, `LatMin/Max`).
- `SP_put_coupling_param`, `SP_adjust_lines`, `SP_run` carry the coupling cadence and
  per-step advance. The MHD side (SC/IH, AWSoM) is **out of scope** here — this skill
  owns the SP side of the interface only.

## Linked libraries

From `SP/MFLAMPA/src/Makefile` and `Makefile.def`:

| Library | Source | What MFLAMPA uses it for |
|---|---|---|
| `libSHARE.a` | `share/Library/src` | Core SWMF utilities: `ModUtilities`, `ModMpi`, `ModReadParam`, `ModCoordTransform`, `ModConst`, `ModNumConst`, time conversion. |
| `libTIMING.a` | `util/TIMING/src` | Performance timing instrumentation (`#TIMING`). |
| `libEMPIRICALCR.a` | `util/EMPIRICAL/srcCR` | Cosmic-ray / LIS spectra (`ModCosmicRay`) for GCR boundary conditions (`#UPPERENDBC` LIS, modulation potential). |

Include dirs (`SEARCH_EXTRA`): `LIBRARYDIR`, `COUPLERDIR`, `EMPIRICALCRDIR`. The
coupler interface modules (`CON_*`) come from the SWMF framework when built coupled.

## Grid sizing — `Config.pl -g`

`Config.pl -g=nX[,nP[,nMu]]` sets the compile-time dimensions in `ModSize.f90`:

| Position | `ModSize` parameter | Default | Meaning |
|---|---|---|---|
| `nX` | `nVertexMax` | 1000 | max grid points (vertices) per field line |
| `nP` | `nMomentum` | 100 | momentum (energy) grid points |
| `nMu` | `nPitchAngle` | 1 | pitch-angle grid points |

`IsPitchAngleAverage = (nPitchAngle == 1)`. So:

- `./Config.pl -g=20000` → `nVertexMax=20000`, defaults for the rest ⇒ **μ-averaged**
  (omnidirectional Parker). This is what `test_compile` uses.
- `./Config.pl -g=20000,100,5` → `nPitchAngle=5` ⇒ **pitch-angle resolved / focused
  transport**. This is what `test_compile_mu` uses.

Check the current size any time with `./Config.pl -g` (prints, does not change).

## Build entry points (standalone)

All from *inside* `SP/MFLAMPA` (not the SWMF root):

```bash
./Config.pl -g=20000        # set grid size (re-run make after a change)
make                        # build (DEFAULT_EXE = MFLAMPA.exe)
make rundir RUNDIR=run_test STANDALONE=YES SPDIR=`pwd`   # create a run directory
cd run_test && mpirun ./MFLAMPA.exe | tee runlog          # run
```

`MPIRUN` can be set empty to run serially. The full test pipeline wraps these steps
— see `workflows/test.md`.
