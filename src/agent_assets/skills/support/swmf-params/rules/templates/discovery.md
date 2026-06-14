# Template discovery recipe

After consulting `INDEX.md`, the agent runs this search recipe to surface
additional PARAM precedents that match the target spec but were not in the
static index. The goal is to read 3–10 templates total per archetype, never
just one.

## Where to look

```
<SWMF_ROOT>/SWMFSOLAR/Param/PARAM.in.*
<SWMF_ROOT>/SWMF/Param/                # top-level examples
<SWMF_ROOT>/SC/BATSRUS/Param/
<SWMF_ROOT>/IH/BATSRUS/Param/
<SWMF_ROOT>/GM/BATSRUS/Param/
<SWMF_ROOT>/EE/BATSRUS/Param/
<SWMF_ROOT>/OH/BATSRUS/Param/
<SWMF_ROOT>/SC/BATSRUS/Test*/PARAM.in*
<SWMF_ROOT>/IH/BATSRUS/Test*/PARAM.in*
<SWMF_ROOT>/GM/BATSRUS/Test*/PARAM.in*
<SWMF_ROOT>/IM/RCM2/Param/
<SWMF_ROOT>/IE/Ridley_serial/Param/
<SWMF_ROOT>/PC/FLEKS/Param/
<SWMF_ROOT>/SP/MFLAMPA/Param/
<SWMF_ROOT>/PT/AMPS/Param/
<SWMF_ROOT>/UA/MGITM/Param/
<SWMF_ROOT>/share/Library/test/
<SWMF_ROOT>/Scripts/
```

## Search recipe

For each archetype, the agent runs roughly the following sweep (adjust the
filter expression to the archetype's keywords):

```bash
# Step 1: enumerate every shipped PARAM* under SWMF.
find $SWMF_ROOT \( -name 'PARAM.in*' -o -name 'PARAM.expand*' -o -name 'PARAM.sofie*' \) -type f

# Step 2: filter to files containing the archetype's signature commands.
#         For awsom_steady_sc, the signature is "#POYNTINGFLUX" + "#CORONALHEATING".
grep -l -E '#POYNTINGFLUX' $(find $SWMF_ROOT -name 'PARAM.in*' -type f) | head -20
```

## Filter rules

A candidate template counts toward the survey iff:

- It contains the archetype's signature commands (e.g. AWSoM steady needs
  `#POYNTINGFLUX` AND `#CORONALHEATING.TypeCoronalHeating=turbulentcascade`).
- It is **not** under any path matching `eval/papers/*/reference/`
  (contamination tripwire — those are the gold answers for evaluation).
- It is not under a `__pycache__`, `Build`, or `tmp` directory.

## What the agent records

Each replication run produces a `template_survey.md` listing:

```
- file: <relative path>
  signatures_matched: [...]
  notable_variance: "uses Sokolov flux where INDEX primary uses Linde"
```

The survey becomes part of REPORT.md provenance — the agent cites which
templates it read and what convention variance it observed.

## When the search returns nothing

If no shipped PARAM matches the archetype's signature, the archetype is
either novel or mis-classified. The agent surfaces this as a gap with
lane=`recipe` (the archetype needs a new recipe in `case_recipes/`) or
lane=`expert_review` (the archetype is genuinely new).
