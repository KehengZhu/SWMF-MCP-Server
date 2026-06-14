# crosswalks/

Maps physics phrases that appear in papers → SWMF `#COMMAND.parameter` references.

## When the agent uses these

In swmf-replicate's authoring ladder, the **crosswalk** lane fires when:

1. A physics phrase from the paper does not match any command name visible
   to the agent (i.e. the agent didn't know the command existed), **or**
2. Multiple SWMF commands could plausibly implement the same paper concept
   and the agent needs disambiguation (e.g. "source surface" → `#CURLB0`
   vs `#HARMONICSGRID.rSourceSurface`).

## Lookup

`swmf get-evidence --task-type physics_concept --query "<phrase>"` matches the
phrase against every `crosswalks/*.yaml` file by simple keyword overlap (no
embeddings; the index is keyword-only). Returns the entries whose `phrases:`
list overlaps with the query.

## Authority

Crosswalks are **hints**, not authorities. Every crosswalk entry names an
`xml_group:` that the agent must read via
`swmf inspect --type xml --xml-scope 'commandgroup:<name>'`
before authoring the matching PARAM block. The XML is still the source of
truth for parameter syntax, types, defaults, and conditional `<if>` logic.

When this read feeds the XML audit gate, pass the same `--run-dir <run directory>`
here as on the `swmf inspect --type param --check-xml-audit` launch check so the
gate can correlate the recorded command-group reads with the launch check.

## Adding entries

When `swmf-improve` classifies a gap as `crosswalk` lane, the proposed entry
must include:

- `phrases`: at least one phrase taken verbatim from the paper that the
  current agent missed.
- `commands`: the actual `#COMMAND.parameter` references that resolve the
  mapping.
- `xml_group`: the PARAM.XML commandgroup the agent should consult.
- `provenance`: the eval paper id that surfaced the gap.
- (optional) `archetypes`: narrows the crosswalk if not universal.

Contamination tripwire: no entry may include literal numeric values from
any `eval/papers/*/reference/` PARAM. Crosswalks map phrases to commands,
not to values — values come from the paper itself.
