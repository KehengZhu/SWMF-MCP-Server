# MFLAMPA PARAM commands — physical meaning

A **thin overlay** over `SP/MFLAMPA/PARAM.XML`: it groups the commands by physical
role and says what each *means* and which test PARAM exercises it. It does **not**
restate argument order, defaults, or allowed values — read those from the schema:

```bash
swmf inspect --type xml --path SP/MFLAMPA/PARAM.XML --xml-scope 'command:<NAME>'
swmf inspect --type xml --path SP/MFLAMPA/PARAM.XML --xml-scope 'commandgroup:<GROUP>'
```

When the schema and this doc disagree, the schema wins. Test PARAMs live in
`SP/MFLAMPA/Param/` (`PARAM.in.test`, `.test.poisson`, `.test.spectra`,
`.test.steady.start`/`.restart`, `.test.steady_state`, `.test.mpi`). The "exercised
by" column points to the smallest test that uses the command.

## The physics knobs (read these first)

These are the commands that change the *physics* of the SEP solve — the ones that
matter for understanding a run or adding a term.

| Command | Group | Physical meaning | Exercised by |
|---|---|---|---|
| `#ADVECTION` | ADVANCE | `UsePoissonBracket` T → conservative Poisson-bracket scheme (`ModAdvancePoisson`); F → log-advection (`ModAdvanceAdvection`). | `.test.poisson`, `.test.spectra` |
| `#FOCUSEDTRANSPORT` | ADVANCE | Enables pitch-angle-resolved focused transport (betatron / inertial / scattering terms). Requires `nPitchAngle>1` (`Config.pl -g=…,nMu`). | (pitch-angle builds) |
| `#PITCHANGLEGRID` | GRID | `nMu` pitch-angle bins; `nMu=1` ⇒ μ-averaged (omnidirectional Parker). | `.test.spectra` |
| `#MOMENTUMGRID` | GRID | `nP` momentum bins, log-spaced from injection to max momentum. | `.test.spectra` |
| `#ENERGYRANGE` | GRID | `EnergyMin`/`EnergyMax` — extent of the momentum/energy grid. | `.test.spectra` |
| `#DIFFUSION` | ACTION | Parallel diffusion model (`TypeMhdDiffusion`, e.g. `'sokolov2004'`) and its parameters; sets `D` along **B** (Sokolov 2004 eq 4). | (diffusion runs) |
| `#DIFFUSIONPARA` | ACTION | Parameters of the parallel-diffusion coefficient. | — |
| `#USEFIXEDMFPUPSTREAM` | ACTION | Use a fixed upstream mean free path `MeanFreePath0InAu` (e.g. 0.3 AU — the SOFIE production simplification) instead of a turbulence-derived one. | `.test` (2nd session) |
| `#TURBULENTSPECTRUM` | TURBULENCE | Derive the scattering/diffusion coefficient from the Alfvén-wave turbulent spectrum (`ModTurbulence`, I+/I−) rather than a prescribed `D`. | — |
| `#SCALETURBULENCE` | TURBULENCE | Turbulence scaling type + amplitude at 1 AU (`ScaleTurbulence1AU`) controlling scattering strength. | `.test`, `.test.spectra` |
| `#TRACESHOCK` | ACTION | Locate, track, and `steepen_shock` the CME-driven shock so DSA (1st-order Fermi) operates. | `.test` (set F), shock runs |
| `#IDENTIFYSHOCK` | ACTION | Shock-identification method/threshold. | — |
| `#MOMENTUMBC` | ADVANCE | Momentum-space BCs: injection spectral index + efficiency at `p_min`; type at `p_max` (Sokolov 2004 eq 3). | `.test.spectra` |
| `#LOWERENDBC` | ENDBC | BC at the inner (near-Sun) line end — typically `inject`. | `.test.spectra` |
| `#UPPERENDBC` | ENDBC | BC at the outer line end — GCR/LIS spectrum (`usoskin`), modulation potential. | `.test.spectra` |
| `#FLUXINITIAL` | GRID | Initial flux level (pfu) seeding the distribution. | `.test.spectra` |
| `#ORIGIN` | DOMAIN | Injection/origin surface: radius `ROrigin` and lon/lat bounds for field-line footpoints. | (coupled / origin runs) |

## Grid, geometry & diagnostics

| Command | Group | Meaning |
|---|---|---|
| `#COORDSYSTEM` | GRID | Coordinate system (e.g. `HGR`). |
| `#GRIDNODE`, `#GRIDNODEOFFSET`, `#CHECKGRIDSIZE` | GRID | Field-line node count / offset / compile-size check. |
| `#TRIANGULATION`, `#TESTTRIANGULATE`, `#TESTPOS` | GRID | Triangulation between adjacent lines (perp diffusion, satellite/flux interpolation) and its tests. |
| `#SPREADGRID`, `#SPREADSIGMA`, `#SPREADSOLIDANGLE` | GRID | Angular-spread output grid / spreading of injection over solid angle (`ModAngularSpread`). |
| `#PARTICLEENERGYUNIT` | UNIT | Energy unit (keV/MeV/GeV) for I/O. |
| `#ECHANNEL`, `#ECHANNELSAT` | ENERGYCHANNEL | Define integral/differential energy channels (e.g. GOES ≥10 MeV), globally or per satellite. |
| `#SATELLITE` | INPUT/OUTPUT | Spacecraft trajectory files for in-situ flux output (`ModSatellite`). |
| `#SAVEPLOT`, `#NOUTPUT`, `#SAVEINITIAL` | INPUT/OUTPUT | Output: plot set (`mh1d`/`mh2d`/`mhtime`/`distr*`/`flux*`), cadence, initial-state dump (`ModPlot`). |
| `#CFL` | ADVANCE | CFL number for the explicit advance. |

## Input / framework / control (bookkeeping)

| Command | Group | Meaning |
|---|---|---|
| `#READMHDATA`, `#MHDATA`, `#NTAG` | INPUT/OUTPUT | Standalone MHD input: `DoReadMhData`, `NameInputDir`, dataset description (`ModReadMhData`). |
| `#RESTART`, `#SAVERESTART` | ACTION / STAND ALONE | Restart toggle and checkpoint cadence (`ModRestart`). |
| `#DORUN` | ACTION | Actually advance the solution (vs setup-only). |
| `#STARTTIME`, `#SETREALTIME`, `#USEDATETIME` | STAND ALONE / I/O | Simulation start time / real-time anchoring. |
| `#TIMEACCURATE`, `#TIMESIMULATION`, `#NSTEP` | STAND ALONE | Time-accurate vs steady, sim-time and step counters. |
| `#STOP`, `#CHECKSTOPFILE`, `#CPUTIMEMAX` | STOPPING | Stop criteria (`nIterMax`, `TimeMax`), stop file, CPU cap. |
| `#ECHO`, `#TIMING` | STOPPING / I/O | Echo PARAM lines; timing report. |
| `#INCLUDE`, `#RUN`, `#BEGIN_COMP`/`#END_COMP`, `#END` | STAND ALONE | Framework structure: include a file, session break, component block, end of file. |

## Reading a standalone PARAM.in (the shape)

`PARAM.in.test` is the canonical minimal standalone case and a good template to read
first: it sets the start time, turns off shock tracing, sets the turbulence scale,
`#INCLUDE`s the `MH_data` header, enables `#READMHDATA`, requests `#SAVEPLOT` output,
and `#STOP`s on `TimeMax`. A second session (after `#RUN`) switches on a fixed
upstream mean free path (`#USEFIXEDMFPUPSTREAM`). `PARAM.in.test.spectra` is the
fullest example — momentum/pitch-angle grid, momentum + end BCs, energy channels,
satellites, and the `distr*`/`flux*` plot types — read it to see the physics knobs
exercised together. Always confirm a command's exact arguments with the xml-scope
channel before authoring or editing.
