# Expert-Knowledge Queue

Operator-knowledge gaps that the `swmf-improve` agent cannot resolve from
corpus, source, paper, or template. Each entry is a question for an SWMF
practitioner (Sokolov, Tóth, van der Holst, Manchester, or a SWMFSOLAR
operator). Questions are batched and resolved in 2-hour conversations;
each conversation closes 5–10 entries.

## How to add an entry

The agent appends entries automatically during Stage 3 (Classify) when a
gap routes to lane `expert-knowledge`. The agent does **not** auto-fill;
the question is queued verbatim.

## How to close entries

After an expert conversation, land each decision as a rule under
`src/agent_assets/skills/support/swmf-params/rules/defaults/` or
`rules/derivations/` with `provenance.type = expert` and
`provenance.source = expert:<name>:<YYYY-MM-DD>`. Remove the entry from
this file once the rule is merged.

## Entry template

```markdown
### <YYYY-MM-DD> — <paper-name> — `#COMMAND` <parameter-name>

- **Paper**: `eval/papers/<paper-name>/paper.pdf`
- **Attempt value**: `<what the agent produced>`
- **Reference value**: `<what the gold answer has>`
- **Agent rationale for the attempt**: `<one sentence>`
- **Why the agent couldn't decide**: `<one sentence — typically "no shipped exemplar uses this value", "paper does not state", "two templates disagree">`
- **Suggested expert prompt**: `<the question to ask, framed for an operator>`
```

## Open entries

_(empty — populated by the agent during cycles)_
