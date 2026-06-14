# MFLAMPA module map & advance loop

Operational/architectural map of `SP/MFLAMPA/src`. Line numbers are anchors taken
from the source at authoring time; **they drift** — re-confirm a subroutine's home
with `swmf get-evidence --query "<name>" --scope SP` before quoting a line to a user
or editing. The source is the authority (SKILL.md §Authority Order).

## How to use this doc

- "How does the SEP solve work / where is X computed?" → §Advance loop + §Module map.
- "What physics is in MFLAMPA / which paper?" → §Physics map.
- "Where would a new physical term go?" → §Where a new term attaches (this is the
  groundwork; the full step-by-step term-implementation recipe is a deferred,
  separate workflow).

## Module map

Core data + grid:

| Module | Role |
|---|---|
| `ModSize.f90` | Compile-time grid dims: `nVertexMax` (max points/line, 1000), `nMomentum` (100), `nPitchAngle` (1 ⇒ `IsPitchAngleAverage=T`). Set by `Config.pl -g`. |
| `ModGrid.f90` | Field-line grid + state arrays. `MhData_VIB` (MHD background: Rho, T, U, B, waves) and `State_VIB` (derived: D, S, U, B, old values). `nVertex_B(iLine)` points per line; `FootPoint_VB`. |
| `ModDistribution.f90` | The VDF `Distribution_CB(nP, nMu, nVertex, nLine)`; log-momentum grid (`dLogP`, injection→max), pitch-angle grid `Mu_F`. |
| `ModUnit.f90` | Energy↔momentum, IO↔SI conversions, energy/flux units. |
| `ModTime.f90` | `SPTime`, `DataInputTime`, `iIter`, `IsSteadyState`; `IsStandAlone` flag. |
| `ModMain.f90` | Control flow: `read_param` (35), `initialize` (190), `run(TimeLimit)` (254), `finalize`. |

Physics operators (where transport terms live):

| Module | Physics |
|---|---|
| `ModAdvance.f90` | **Orchestrator.** `advance(TimeLimit)` (56–207) time-accurate; `iterate_steady_state` (209–264). Applies the per-step operator sequence (see below). |
| `ModAdvancePoisson.f90` | **Conservative Poisson-bracket scheme** (Sokolov et al. 2023). `advect_via_poisson_parker` (64) omnidirectional Parker; `advect_via_poisson_focused` (350) pitch-angle/focused transport. Steady variants `iterate_poisson_parker/focused`. |
| `ModPoissonBracket.f90` | Generic explicit Poisson-bracket solver `df/dt + {f,H}=0` (the `explicit` interface). The reusable engine the two schemes above call. |
| `ModAdvanceAdvection.f90` | **Non-conservative log-advection** scheme (the original 2004 method). `advect_via_log` (24–129): 2nd-order upwind in `ln p`, 1st-order Fermi via `dLogRho/(3 dLogP)`. |
| `ModDiffusion.f90` | Parallel diffusion. `set_diffusion_coef` (453) sets `DInnerSi/DOuterSi`; `diffuse_distribution` solves it. `TypeMhdDiffusion` switch (`'sokolov2004'`, …). |
| `ModDiffusionPerp.f90` | Perpendicular (cross-field-line) diffusion via triangulation between lines. `diffuseperp_distribution`. |
| `ModDrift.f90` | Gradient/curvature drift solve (Poisson-bracket on a 3D perpendicular grid). |
| `ModTurbulence.f90` | Turbulent-spectrum diffusion: when `UseTurbulentSpectrum`, derives `Dxx` from wave spectra (I+/I−). |
| `ModShock.f90` | Shock location (`get_shock_location`), `steepen_shock` (sharpens ρ/B jump), divU, shock skeleton. |
| `ModBc.f90` | Boundary conditions: `set_momentum_bc` (injection at the shock, Sokolov 2004 eq 3), lower/upper end BCs; GCR/LIS coupling. |
| `ModChannel.f90` | VDF → integral/differential intensity in energy channels (e.g. GOES). |
| `ModAngularSpread.f90` | Angular-spread (flux on field lines) outputs. |
| `ModSatellite.f90` | Interpolates VDF/flux to spacecraft trajectories. |
| `ModOriginPoints.f90` | Injection/origin surface: `ROrigin`, lon/lat bounds for field-line footpoints. |
| `ModReadMhData.f90` | **Standalone** MHD input: reads MH_data files in time sequence when `DoReadMhData=T`. |
| `ModRestart.f90` | `save_restart` / `read_restart` checkpointing. |
| `ModPlot.f90` | Output: distribution/shock/satellite/flux plots (the `#SAVEPLOT` machinery). |

Entry / interface:

| File | Role |
|---|---|
| `SP_stand_alone.f90` | Standalone program entry (`MFLAMPA.exe`). |
| `srcInterface/SP_wrapper.f90` | SWMF-coupled interface (`SP_set_param`, `SP_init_session`, `SP_run`, `SP_put_coupling_param`, `SP_adjust_lines`). |

## Advance loop

Top level: `ModMain.run(TimeLimit)` (ModMain.f90:254) branches on `IsSteadyState`:

- **Time-accurate** → `ModAdvance.advance(TimeLimit)` (56). For each field line, for
  each shock sub-step (`iProgress`), the per-step operator sequence is:

  1. `calc_states_poisson_focused` (120) — if Poisson + not μ-averaged.
  2. `steepen_shock` (165) — if `DoTraceShock`.
  3. `set_diffusion_coef` (171) — if `UseDiffusion`.
  4. **Advection** — one of:
     - `advect_via_poisson_parker` (177) — Poisson, μ-averaged.
     - `advect_via_poisson_focused` (184) — Poisson, pitch-angle resolved.
     - `advect_via_log` (191) — non-conservative log-advection.
     (each followed by `diffuse_distribution` internally)
  5. After all lines: `diffuseperp_distribution` (205) — if `UseDiffusion` and
     `UseDiffusionPerp`.

- **Steady-state** → `iterate_steady_state` (209): per line, `set_diffusion_coef`
  (244) then `iterate_poisson_parker` (249) / `iterate_poisson_focused` (252), then
  `diffuseperp_distribution` (262).

The advection scheme is selected by `#ADVECTION UsePoissonBracket` (T → Poisson,
F → log-advection) and `#PITCHANGLEGRID nMu` / `#FOCUSEDTRANSPORT` (μ-averaged vs
focused). See `reference/params.md`.

## Physics map

MFLAMPA solves the Parker / focused-transport equation for the SEP distribution on
Lagrangian field lines. Derivations and the equation→code mapping are in the papers
under `docs/mflampa-papers/` (and summarized there):

- **Parker eq.** `∂f/∂t + (u·∇)f − ⅓(∇·u)∂f/∂ln p = ∇·(D·∇f) + S`, reduced to 1-D
  along a frozen-in line (Sokolov 2004, eqs 1–2) → `ModAdvance` / advection modules.
- **Injection** suprathermal tail at the shock, efficiency `c_inj`, `E_inj≈10 keV`
  (Sokolov 2004 eq 3) → `ModBc.f90:141`.
- **Diffusion coeff** `D = ⅓λ‖v = ⅓(B/δB)²r_g v`; upstream per Li et al. 2003
  (Sokolov 2004 eq 4) → `ModDiffusion.f90` (`TypeMhdDiffusion='sokolov2004'`, ~502).
- **Poisson-bracket conservative scheme** `∂f/∂t + Σ{f,H_l}=0` (Sokolov et al. 2023,
  JCP) → `ModAdvancePoisson` / `ModPoissonBracket`.
- **MHD coupling, field-line tracing, turbulence-derived scattering** (Borovikov
  et al. 2018/2019) → `SP_wrapper`, `ModGrid`, `ModTurbulence`.

## Where a new term attaches

Two insertion patterns, by the math of the term:

- **Hamiltonian / advective** term (a drift, focusing, betatron, energy-change
  process): add it as **one more Poisson bracket** `{f, H_new}` in the
  `ModAdvancePoisson`/`ModPoissonBracket` path — supply the `H` contribution
  (→ phase-space velocity → face fluxes); particle conservation and CFL are handled
  by the existing finite-volume engine.
- **Diffusive / stochastic / loss** term (cross-field diffusion, a new scattering
  model, a sink): add it as a **diffusion-operator or source/sink** term, following
  `ModDiffusion.f90` (e.g. a new `TypeMhdDiffusion` branch in `set_diffusion_coef`).

Either way it is sequenced from `ModAdvance.advance` (the per-step list above) and
its control is exposed as a new `#COMMAND` read in the owning module's `read_param`,
aggregated by `ModMain.read_param` (ModMain.f90:35). A new command must also be added
to `PARAM.XML`. The full implementation/validation discipline (patch-readiness gate,
regression against the test suite) is `swmf-implementation` + `workflows/test.md`.
