# swmf-params/rules — Phase 1 skeleton

User-owned rules directory. Both `inspect_artifact(artifact_type="param", check_rules=True)`
(MCP) and the `swmf-params` skill consume content here. Adding domain knowledge is a YAML
or markdown drop; only schema-vocabulary changes touch code.

## Lanes

* `physical_constraints.yaml` — **CONSTRAIN**. If/then validation rules evaluated by MCP.
* `numerical_practices.md` — narrative best practices loaded by the skill.
* `case_recipes/<archetype>.md` — **STRUCTURE**. Multi-session skeletons per case archetype.
* `templates/<archetype>.yaml` — **ANCHOR**. Template-pair manifests per archetype.
* `derivations/<topic>.yaml` — **DERIVE**. Formulas mapping spec → PARAM values.
* `defaults/<topic>.yaml` — **DEFAULT**. Operational defaults for fields the spec doesn't supply.

## Authoring ladder (for `swmf-replicate`)

For every PARAM value the agent emits, walk the ladder. The first step that supplies the
value wins; the agent records the supplying step as that value's provenance.

| Step | Lane | Provenance tag |
| ---- | ---- | -------------- |
| 1 | spec field, direct | `spec` |
| 2 | derivation match | `derivation:<id>` |
| 3 | recipe slot | `recipe:<id>` |
| 4 | template carries it | `template:<path>` |
| 5 | default applies | `default:<id>` |
| 6 | narrative practice resolves a tie | `practice:<entry>` |
| 7 | nothing supplies the value | `gap` (user prompt) |

Validation rules and `Scripts/TestParam.pl` run on the *result* at the launch gate; they
are not part of authoring. The ladder is "produce, then validate."

## Maintenance contract

Each YAML file is append-only extendable: drop a new entry, no code change.

* New validation rule → append to `physical_constraints.yaml`.
* New narrative practice → append to `numerical_practices.md`.
* New case archetype → add files under `case_recipes/`, `templates/`, and `defaults/`.
* New derivation → append to `derivations/<topic>.yaml`.
* New operational default → append to `defaults/<topic>.yaml`.
* New template-pair manifest → drop a YAML in `templates/`.

Schema changes to predicate vocabulary or expression operators are API changes and require
MCP/skill code updates.

## Predicate vocabulary (deterministic, evaluable from PARAM.in alone)

Used in `physical_constraints.yaml`:

* `command_present` / `command_absent`
* `param_equals` / `param_in_range` / `param_in_set`
* `command_co_occurs_with` / `command_excludes`
* `session_index` (rule applies only in session N)
* `command_order_before` (X must appear before Y)
* `any_of: [<predicate_dict>, ...]` — disjunction; satisfied if any sub-predicate holds.
* `all_of: [<predicate_dict>, ...]` — explicit conjunction (a dict already implies AND).

Predicates that require external evidence (magnetogram time, cluster, build flags) live in
case recipes (narrative), not here.
