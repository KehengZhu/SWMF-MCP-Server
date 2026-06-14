# required_floors/

Lists of **must-be-present** commands for each equation set / archetype.
Every entry must cite a PARAM.XML `<if>` conditional or a Fortran source line
that proves the requirement. **No entry derived from corpus frequency.**

## What's here

- `equation_set.yaml` — required-command lists per equation set (`Awsom`,
  `AwsomAnisoPi`, `AwsomR`, `AwsomSA`, `MhdIonsPe`, etc.). Each set lists
  the commands the agent must include in PARAM.in to match the equation
  module's compiled-in expectations. Originally auto-mined; retained because
  the requirements trace to specific equation modules
  (`GM/BATSRUS/srcEquation/ModEquation*.f90`) which serve as the source of
  truth.

## Authority

These are **floors**, not ceilings. The agent must include every command in
the active floor (filtered by equation set + archetype). PARAM.XML defaults
and paper overrides apply to the *values*; the floor only enforces presence.

## Maintenance

When `swmf-improve` proposes a `recipe` lane fix that names a new required
command, the proposal must:

1. Cite the PARAM.XML `<if>` conditional or Fortran source that justifies
   the requirement.
2. Land in `required_floors/<equation_or_archetype>.yaml` — never in
   `crosswalks/` (crosswalks are phrase→command mappings, not floors).
3. Pass the regression gate: no other paper's replication may add a
   spurious new command because of the new floor entry.
