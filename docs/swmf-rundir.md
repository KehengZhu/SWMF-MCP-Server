# SWMF Run Directory Structure

This note summarizes what a SWMF run/output directory usually contains. The
exact tree is component- and workflow-dependent: a prepared run, an active run,
a completed run, a post-processed output tree, and a restart tree are related
but not identical layouts.

Evidence checked:

- SWMF control docs: `/Users/zkeheng/SWMFSoftware/SWMF/PARAM.XML`
- SWMF user docs: `/Users/zkeheng/SWMFSoftware/SWMF/doc/Tex/SWMF_introduction.tex`
- Post-processing script: `/Users/zkeheng/SWMFSoftware/SWMF/share/Scripts/PostProc.pl`
- Restart script: `/Users/zkeheng/SWMFSoftware/SWMF/share/Scripts/Restart.pl`
- Local examples: `/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_SA/run01`,
  `/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP/run01`, and
  `/Users/zkeheng/SWMFSoftware/SWMFSOLAR/Run_Max_RP_CME3/run01`

## Top-Level Run Directory

A typical live run directory is the directory from which `SWMF.exe` is launched.
It must contain `PARAM.in`; the SWMF manual states that this input file must be
located in the run directory.

Common top-level entries:

```text
run01/
  PARAM.in
  SWMF.exe
  SWMFDIR -> /path/to/SWMF
  Param -> /path/to/SWMF/Param
  runlog or runlog_*
  job.* / *.slurm / *.sbatch
  PostProc.pl
  Restart.pl
  Resubmit.pl
  SWMF.SUCCESS
  SWMF.DONE
  SWMF.KILL / SWMF.STOP
  RESTART.out / RESTART.in
  STDOUT/
  <COMP>/
```

Not every entry is present in every run. For example, the sampled
`Run_Max_SA/run01` contains `PARAM.in`, `SWMF.exe`, `runlog_2604072039`,
`job.frontera`, `STDOUT/`, `SC/`, and `IH/`, but no success marker yet. The
sampled `Run_Max_RP/run01` contains `SWMF.SUCCESS` and `SWMF.DONE`, plus
post-processing and restart helpers.

Important top-level files:

- `PARAM.in`: main run control file. It can include other parameter fragments.
- `SWMF.exe`: executable or symlink to the executable.
- `SWMFDIR`: often a symlink back to the SWMF source/install root.
- `Param`: often a symlink to the SWMF `Param/` examples/templates.
- `runlog` or `runlog_*`: standard output captured from the run. Job scripts
  often launch with `tee runlog` or machine-specific timestamped names.
- `job.*`, `*.slurm`, `*.sbatch`: scheduler submission scripts.
- `PostProc.pl`: helper copied into the run directory for processing outputs.
- `Restart.pl`: helper copied into the run directory for collecting/linking
  restart state.
- `Resubmit.pl`: optional helper for queue continuation workflows.
- `core`: crash/core dump marker if the run failed badly.

Status/control markers:

- `SWMF.SUCCESS` and `SWMF.DONE`: if the last session completes successfully,
  both files are created in the run directory.
- `SWMF.SUCCESS` without `SWMF.DONE`: if the run stops through configured stop
  checking, such as CPU-time limit or `SWMF.STOP`, the success marker can be
  created without the done marker.
- `SWMF.KILL`: if the run is killed through this file, no `SWMF.SUCCESS` or
  `SWMF.DONE` files are created.
- `SWMF.STOP`: requested graceful stop when `#CHECKSTOP` is enabled.

## Component Subdirectories

Each active component normally has its own top-level component directory, named
by the two-letter SWMF component code. The actual set depends on `#COMPONENTMAP`,
`#COMPONENT`, and the component versions compiled into the executable.

Common component codes seen in SWMF scripts include:

```text
EE IE GM SC IH OH IM PC PS PT PW RB UA SP
```

Example component layout:

```text
run01/
  SC/
    Param -> /path/to/SWMF/GM/BATSRUS/Param/CORONA
    IO2/
    plots -> IO2
    restartIN -> ../RESTART_t0015.0000h/SC
    restartOUT/
    pIDL
    pTEC
    PostIDL.exe
    *.out
    *.dat
    log_n*.log
    component-specific input/helper files
  IH/
    Param -> /path/to/SWMF/GM/BATSRUS/Param/HELIOSPHERE
    IO2/
    plots -> IO2
    restartIN -> ../RESTART_t0015.0000h/IH
    restartOUT/
    pIDL
    pTEC
    PostIDL.exe
    *.out
    *.sat
    log_n*.log
```

The local `SWMFSOLAR` examples show large variation. `Run_Max_RP/run01/SC`
contains magnetogram and harmonics helpers such as `FDIPS.in`, `HARMONICS.in`,
`MAGNETOGRAMTIME.in`, `GLSETUP*.py/.pro`, `harmonics_adapt.dat`, and
`map_01.out`. `Run_Max_RP_CME3/run01/SC` and `IH` contain many direct output
snapshots like `x=0_var_1_t...out`, `y=0_var_2_t...out`,
`z=0_var_3_t...out`, `shl_var_4_t...out`, line-of-sight files, and
component logs such as `log_n080000.log`.

## Plot and Output Locations by Component

`PostProc.pl` encodes the default component output directories it knows how to
process. These are the best practical map for where outputs live before or
during post-processing:

| Component | Default output directory or directories |
| --- | --- |
| `EE` | `EE/IO2` |
| `GM` | `GM/IO2` |
| `IE` | `IE/ionosphere`, `IE/Output` |
| `IH` | `IH/IO2` |
| `OH` | `OH/IO2` |
| `IM` | `IM/plots`, `IM/output` |
| `PW` | `PW/plots` |
| `PC` | `PC/plots` |
| `PS` | `PS/Output` |
| `PT` | `PT/plots` |
| `RB` | `RB/plots` |
| `SC` | `SC/IO2` |
| `SP` | `SP/IO2` |
| `UA` | `UA/Output`, `UA/data` |
| `STDOUT` | `STDOUT` |

Some run directories also have a `plots` symlink pointing at the real output
directory, as in the sampled `SC/plots -> IO2` and `IH/plots -> IO2` layouts.

Common raw or processed output file patterns:

- `*.out`: SWMF plot/output files, often IDL-readable.
- `*.outs`: multiple-output or concatenated output form used by some workflows.
- `*.dat`: ASCII data, line-of-sight products, Tecplot-adjacent products, or
  component-specific diagnostics.
- `*.sat`: satellite/trajectory output.
- `*.log`: component log files, often with names such as `log_n*.log`.
- `*.tec`: Tecplot intermediate/output files, often processed by `pTEC`.
- Movie/tar outputs can be produced by `PostProc.pl` options.

Naming commonly encodes plot area/form, simulation time, and step number:

```text
x=0_var_1_t00010600_n00111390.out
y=0_var_2_t00012700_n00121347.out
z=0_var_3_t00005200_n00104730.out
shl_var_4_t00720000_n00010084.out
los_soho_c2_4_t00011800_n00117086.out
sat_earth_n00006560.sat
```

The exact variables, plot areas, cadence, and formats are controlled by
component-specific `#SAVEPLOT`, log, satellite, and Tecplot commands in
`PARAM.in`.

## Restart Layout

Restart handling has two related forms.

During a run, each component can write its current restart state to:

```text
<COMP>/restartOUT/
```

For the next run, each component can read restart state from:

```text
<COMP>/restartIN/
```

`Restart.pl` defines these names for `EE`, `IE`, `GM`, `SC`, `IH`, `OH`, `IM`,
`PC`, `PS`, `PT`, `PW`, `RB`, `UA`, and `SP`. It also uses framework-level
`RESTART.out` and `RESTART.in` for the SWMF control restart file.

Restart trees collect the framework restart file and component restart
directories into one portable tree:

```text
RESTART_t0015.0000h/
  RESTART.out
  SC/
    restart.H
    ...
  IH/
    restart.H
    ...
```

For post-processed result collections, the restart tree is usually placed under
the output tree:

```text
RESULTS/run1/
  RESTART/
    RESTART.out
    SC/
    IH/
```

`Restart.pl` can create names based on simulation time for time-accurate runs
or step number for steady-state runs, such as `RESTART_t0123.4567h` or
`RESTART_n012345`. It can also link `COMP/restartIN` back to an existing
restart tree.

## Post-Processed Output Tree

`PostProc.pl` can either process files in place or collect results into a
separate tree. The SWMF docs show examples such as:

```text
./PostProc.pl RESULTS/run1
./PostProc.pl -M -cat RESULTS/NewRun
```

A collected output tree is not the same as the live run directory. It is a
curated result bundle. The SWMF docs say it contains:

```text
RESULTS/NewRun/
  PARAM.in
  runlog or runlog_*
  RESTART/
  GM/
  SC/
  IH/
  ... one subdirectory per component with collected output
```

The local `SWMFSOLAR/Results/Run_Max_RP/run01` sample shows this shape in
minimal form:

```text
Results/Run_Max_RP/run01/
  RESTART/
    RESTART.out
    SC/
    IH/
```

When `PostProc.pl` collects output into a tree, it can move or copy component
outputs out of the live component directories, so directories such as
`GM/plots/` or `SC/IO2/` in the original run may be empty afterward.

## Practical Inspection Rules

When inspecting an arbitrary SWMF run/output directory:

1. Start at the directory containing `PARAM.in`; that is the live run directory.
2. Use `SWMF.SUCCESS`, `SWMF.DONE`, `SWMF.KILL`, `SWMF.STOP`, and the most recent
   `runlog*` to classify completion.
3. Read `PARAM.in` to determine active components and output intent. Do not
   assume all component directories are active just because they exist.
4. For each active component, inspect the component output directory from the
   `PostProc.pl` map above.
5. Treat `restartOUT/` as current output restart state and `restartIN/` as input
   restart links or directories.
6. Treat `RESULTS/<name>/` as a post-processed collection tree, not necessarily
   the live run tree.
7. Expect component-specific extras. SC/IH solar runs, GM/IE geospace runs,
   UA/GITM runs, PWOM runs, and particle components do not produce identical
   file names or subdirectory layouts.

