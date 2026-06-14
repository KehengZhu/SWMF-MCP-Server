# swmf-params/rules — Option-2 narrow waist

User-owned rules directory, scoped to **what PARAM.XML and the SWMF manual
cannot say**. PARAM.XML remains the authoritative SWMF schema; the manual is
hint-tier; rules cover paper-phrase crosswalks, archetype recipes, convention
tie-breakers, equation-set floors, and corrections to stale XML or manual
content.

Both `swmf inspect --type param --check-rules` (the swmf CLI) and
the `swmf-params` skill consume content here. Adding domain knowledge is a
YAML or markdown drop; only schema-vocabulary changes touch code.

## Authoring ladder (for `swmf-replicate`)

| Lane | Where | Provenance tag |
|------|-------|----------------|
| 1. spec | paper PDF | `spec` |
| 2. recipe | `case_recipes/<archetype>.md` | `recipe:<id>` |
| 3. template survey | shipped PARAMs under SWMF (via `templates/INDEX.md` + `discovery.md`) | `template_survey:<path>` |
| 4. **XML (authority)** | `swmf inspect --type xml --xml-scope 'commandgroup:...' --run-dir <run directory>` | `xml:<commandgroup>` |
| 5. manual (hint) | `SWMF/doc/Tex/*.tex` sections | `manual:<file>` |
| 6. crosswalk | `crosswalks/*.yaml` | `crosswalk:<id>` |
| 7. convention | `conventions.yaml` (machine) + `conventions.md` (prose) | `convention:<id>` |
| 8. gap | user prompt | `gap` |

The XML audit gate (`swmf inspect --type param --check-xml-audit`) enforces that
every commandgroup containing an emitted command was actually read via
`swmf inspect --type xml --xml-scope 'commandgroup:...'` during the session.
The same `--run-dir <run directory>` must be passed to both the XML reads and
the launch check: reads persist to `<run_dir>/.swmf_ai/audit.json`, and the
gate correlates them only when the run dir matches.

## Directory layout

| Path | Purpose | Tier |
|------|---------|------|
| `crosswalks/*.yaml` | paper-phrase → command/parameter mappings, with synonyms | hint |
| `case_recipes/<archetype>.md` | multi-session skeletons per archetype | authority for sessions |
| `conventions.yaml` + `conventions.md` | tie-breakers when multiple commands are valid | hint |
| `required_floors/*.yaml` | equation-set/archetype required commands, cited to PARAM.XML or Fortran | floor |
| `archetypes.yaml` | one-line-per-archetype catalog | catalog |
| `physical_constraints.yaml` | pass/warn/fail predicates evaluated by `swmf inspect --type param --check-rules` | validator |
| `templates/INDEX.md` + `discovery.md` | pointers to shipped PARAMs across SWMF (not forked copies) | catalog |
| `manual_corrections.md` | known-stale SWMF manual sections + what to do instead | correction |
| `xml_corrections.md` | known-stale PARAM.XML entries (rare) | correction tier-0 |
| `corpus_frequency/*_typical.yaml` | corpus value envelopes (warn-tier rule-checker input only) | statistical |
| `derivations/*.yaml` | formulas mapping spec → PARAM values (e.g. GL→SPHEROMAK) | derivation |

## Maintenance contract

Each YAML / markdown file is append-only extendable: drop a new entry, no
code change. `swmf-improve` writes proposals here only after the regression
gate confirms (a) the target paper improves and (b) no other paper regresses.

## Contamination tripwire

No rule entry may include literal values or text extracted from any path
matching `eval/papers/*/reference/`. The tripwire is enforced in
`swmf-improve` Stage 5; violations land in `eval/proposals/rejected/`.

## What's NOT here anymore

- `defaults/` — folded into the relevant `case_recipes/<archetype>.md`.
- `defaults/mined/*_required.yaml` — deleted. Statistical "required" lists
  were the file class that hid `#CURLB0` from the Liu et al. 2026
  replication. Required commands now come from `required_floors/`
  (PARAM.XML-attested) or PARAM.XML directly.
- `templates/*.yaml` — replaced by `templates/INDEX.md` (pointers to shipped
  PARAMs) + `templates/discovery.md` (search recipe for additional
  precedents).
- `numerical_practices.md` — folded into `conventions.md`.

## Predicate vocabulary (`physical_constraints.yaml`)

Deterministic predicates evaluable from PARAM.in alone:

- `command_present` / `command_absent`
- `param_equals` / `param_in_range` / `param_in_set`
- `command_co_occurs_with` / `command_excludes`
- `session_index` (rule applies only in session N)
- `command_order_before` (X must appear before Y)
- `any_of: [<predicate_dict>, ...]`
- `all_of: [<predicate_dict>, ...]`

Predicates requiring external evidence (magnetogram time, cluster, build
flags) live in case recipes (narrative), not here.

## Provenance on new entries (from `swmf-improve`)

```yaml
provenance:
  lane: crosswalk | convention | recipe | required_floor | manual_correction | xml_correction
  source: <absolute file path or DOI>
  cite: <line range or page+quote>
  added_by: swmf-improve
  added_on: <YYYY-MM-DD>
```

`source` must **not** resolve under any `eval/papers/*/reference/`
directory.
