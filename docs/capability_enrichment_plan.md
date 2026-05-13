# Capability Enrichment Plan

How to grow the replication agent's capability without overfitting it to
hand-curated examples, and how to reason about the limit of what a paper alone
can tell the agent.

This doc accompanies `run_replication_plan.md` (the architecture) and
`run_replication_eval_eclipse2024.md` (the post-mortem that surfaced the
capability gap). Both are prerequisites.

## 1. Framing

There are three plausible strategies for making the agent more capable. Naming
them clearly matters because they have very different cost profiles and very
different generalization behaviors.

| Strategy | What you author | Cost | Generalization |
| --- | --- | --- | --- |
| A. Example-by-example (paper + gold PARAM pairs) | One pair per case | Linear in #papers | Poor — agent memorizes, doesn't transfer |
| B. Teach physics from textbooks | Physics rules in YAML / prose | High and ongoing | Wrong axis — LLM already knows physics |
| C. Mine the corpus once, curate deltas thereafter | Auto-extracted YAML from shipped PARAMs + a small curated overlay | Front-loaded; flat after | Good — agent diffs new cases against the corpus |

The eclipse2024 post-mortem shows the failure mode of doing none of these
systematically: the agent anchored on a thin teaching template, missed the
production-AWSoM physics block entirely, and produced a `TestParam.pl`-passing
but physically incomplete PARAM. Strategy C is the recommended fix.

## 2. Why "teach physics" is the wrong axis

The LLM already knows physics at textbook level. Alfvén-wave dissipation, the
Spitzer-Härm regime, anisotropic pressure transport, MHD Riemann solvers — all
present in training data, all reasoned about correctly when asked. What the
LLM does **not** know is *operational physics*: which combinations of `#COMMAND`
blocks in a SWMF PARAM constitute a physically meaningful run for a given
archetype. That knowledge is SWMF-specific, lives in the shipped PARAMs and
the equation-module source, and is invisible in physics literature.

Concretely:

- Paper sentence: "Spitzer heat conduction with collisionless flux beyond
  r = 5 R_sun."
- SWMF realization: `#HEATCONDUCTION T spitzer` + `#HEATFLUXREGION T 5.0 -8.0`
  + `#HEATFLUXCOLLISIONLESS T 1.05` + `#SEMIIMPLICIT T parcond` +
  `#SEMIKRYLOV GMRES 1.0e-5 10`.

The translation is not physics — it's bookkeeping in a specific simulator.
Authoring physics rules in `physical_constraints.yaml` to capture this
translation would be reinventing the SWMF command structure from scratch, when
the structure already exists in working PARAM files. Mining is cheaper than
authoring.

## 3. Why "example-by-example" overfits

A paper → gold-PARAM pair, memorized as a pair, generalizes nothing. Two
adjacent papers that vary in archetype, magnetogram, and grid will look
different enough that no learned mapping transfers. This is the textbook
overfitting story.

The cure is structural: **every example absorbed must be promoted into one of
the four lanes** (constrain / derive / structure / default) or the template
anchor — never stored as a verbatim recipe. That promotion is exactly the
maintenance contract from `run_replication_plan.md` §5.4.8. Strategy A
collapses into Strategy C if every new example produces YAML, not memory.

## 4. The corpus-mining strategy (concrete)

### 4.1 What to mine

For each archetype (AWSoM-steady, AWSoMR-CME, SOFIE-MFLAMPA, geospace-GM, …):

1. **All shipped PARAMs** matching that archetype. The corpus is **strictly
   the shipped templates** in the SWMF/SWMFSOLAR source trees:
   - `SWMF/Param/PARAM.in.*`
   - `SWMFSOLAR/Param/PARAM.in.*`
   - `SWMFSOLAR/ParamListScripts/`

   **Out of corpus** (do not mine, do not cite as precedent): any personal
   study run directory, e.g. anything under `SWMFSOLAR/Run_*/`. These dirs
   are individual researcher scratch space; they happen to live in the
   SWMFSOLAR working tree but are not part of SWMFSOLAR's authoritative
   content, may carry idiosyncratic or experimental choices, and would
   poison the mined defaults if included.
2. **Equation modules** in source. `Config.pl -o=SC:e=AwsomAnisoPi` picks a
   Fortran module which declares the variables it evolves; that declaration
   determines which `#COMMANDS` are mandatory. Mine `GM/BATSRUS/srcEquation/*`
   (or wherever the equation modules live) for variable lists and module-level
   guards.
3. **PARAM.XML** for the command-level constraints already encoded
   (allowed values, command order, required pairings).
4. **Jobscript catalog** under `SWMFSOLAR/JobScripts/` for each cluster.

### 4.2 What to emit

For each archetype, automatic extraction produces:

- `defaults/<archetype>_required.yaml` — the **command-intersection** across
  all shipped PARAMs of that archetype. If `#ANISOTROPICPRESSURE` appears in
  every shipped AWSoM-AnisoPi PARAM, it goes in the required set. This alone
  would have caught the eight-command physics gap from the eclipse2024 run.
- `defaults/<archetype>_typical.yaml` — the **value envelope** per command
  (min, max, mode) across shipped PARAMs. Seeds `physical_constraints.yaml`
  range rules with deterministic numbers, not guesses.
- `case_recipes/<archetype>.md` — a **session-structure skeleton** extracted
  from the most-cited or longest-running exemplar.
- `templates/<archetype>.yaml` — the **anchor manifest**, including a ranked
  `secondary_precedents` list.
- `defaults/equation_set_required.yaml` — a **mapping from each
  `Config.pl -o=…:e=X`** value to the `#COMMANDS` that equation module
  requires. Source: the equation-module Fortran files themselves.

### 4.3 Cost

One afternoon of work: a Python miner that classifies each PARAM by archetype
heuristics (`#COMPONENTMAP` components × `Config.pl` flags in the leading
comment block × `#CME` presence × `#FIELDLINE` presence), then performs
set-operations across each archetype's PARAMs to produce the YAMLs above.
Roughly ~50 shipped PARAMs to scan; output is reviewable in a few hours.

### 4.4 What this buys you

After one mining pass, the agent has:

- Knowledge of *which* commands every archetype needs (intersection).
- Knowledge of *what range* each command's values typically fall in (envelope).
- A ranked precedent list to diff against, instead of one teaching template.
- A static equation-set → required-command lookup, so `Config.pl -o=…:e=X`
  decisions are immediately consistent with the PARAM.

The remaining curation work is the **deltas**: per-paper idiosyncrasies that
the corpus doesn't capture (unusual AMR ladders, non-default values, novel
diagnostics). One YAML entry per surprise. The corpus is the floor; curation
is the elevation.

## 5. What the paper alone can and cannot tell the agent

A paper is supposed to be physically complete, and largely is. But "physically
complete" is not the same as "operationally complete." The asymmetry is:

| Information | In the paper? | Sufficient for PARAM? |
| --- | --- | --- |
| Physics model name ("AWSoM with anisotropic ion pressure") | yes | no — need `Config.pl -o=…:e=X` mapping from corpus |
| Initial / boundary conditions in physics units | yes | partial — translation to `#CHROMOBC`, `#PLASMA`, etc. needs corpus |
| Domain extent (radii, longitudes) | yes | yes — direct mapping |
| Free parameters (`PoyntingFluxPerBSi`, etc.) | yes | yes — direct after unit conversion |
| Numerical scheme family ("2nd-order Linde, mc3 limiter, MP5 tail") | yes | partial — exact `LimiterBeta`, `nStage`, low-order region radius rarely stated |
| AMR strategy in physics terms ("refine to 0.35° in [1.01,1.2] R_s") | yes | partial — choice of `#AMRCRITERIALEVEL` vs `#AMRCRITERIARESOLUTION` is convention, not physics |
| Session structure (background → eruption → relaxation) | implied | no — iteration counts, AMR cadence, coupling cadence are conventions |
| Diagnostic plot blocks | yes (as figure list) | no — `#SAVEPLOT` syntax is SWMF-specific |
| Cited prior runs / setups | sometimes | when present, very high signal — closest precedent |

### 5.1 Archetype detection: yes, paper-alone is enough

Archetype is a physics-level label. Every paper states it explicitly in the
abstract or §2: "AWSoM, SC only, no CME, steady state with PFSS init" maps
unambiguously to `awsom_steady_corona`. The agent does not need a hand-coded
detector; it needs a **list of archetype labels with one-line descriptions**
and the LLM matches. Adding a new archetype is one line in that list.

This works because archetype is the most abstract layer of the spec, and
papers reliably write at that abstraction.

### 5.2 Spec → PARAM derivations: paper alone is insufficient

Derivations are *translations* from physics description to SWMF command
realization. The paper writes in physics; the PARAM is in SWMF syntax. The
translation requires a dictionary, and the dictionary is the corpus.

The eclipse2024 case is instructive: the paper says (in effect) "AWSoM
anisotropic, Spitzer heat conduction, semi-implicit." Each of those phrases
is physically complete. None tells the agent the exact five-command block
that realizes "semi-implicit Spitzer + collisionless heat flux" in SWMF.
That block is not invented; it is *looked up* in every shipped AWSoM PARAM.

So derivations are authored from corpus precedent, not from paper text. The
paper supplies the *triggers* (which physics is in play); the corpus supplies
the *realization* (which commands appear and how they pair).

### 5.3 The two-source join

The realistic workflow is:

1. **Paper → physics, archetype, free parameters, validation targets, cited
   prior runs.** LLM extracts these into `paper_spec.json`.
2. **Corpus → SWMF-command realization of each physics choice.** Mined YAML
   in `defaults/` and `derivations/`.
3. **Agent joins them per the §5.4.7 authoring ladder.** "Paper says Spitzer +
   collisionless beyond 5 R_s" ∧ "corpus says that physics in AWSoM context
   is realized as this five-command block" → emit those five commands tagged
   `provenance=default:awsom_heat_conduction_block`.

The agent does not invent. The corpus is the dictionary; the paper is the
sentence; the agent translates.

### 5.4 Two interesting edge cases

- **Papers that cite prior runs.** "We use the setup of Sokolov et al. 2021
  with modifications X, Y." When the agent can resolve the citation to a
  shipped PARAM (or a public config), the derivation collapses to
  *that PARAM + delta*. This is the highest-leverage case. The spec
  normalizer should extract cited prior runs into a `precedent_hint` field,
  and the skill should treat hinted precedents as ranked above the
  archetype-default secondary precedents.

- **Papers that introduce novel numerics.** Rare in production papers, common
  in methods papers. The new scheme may have no SWMF command yet. The
  correct behavior is to surface this as a `gap` and refuse to invent. A
  methods paper proposing an unimplemented scheme cannot be replicated by
  configuration alone — only by code change. The agent must say this
  explicitly, not paper over it.

## 6. Will the agent generalize like a physicist?

Yes — within a useful definition of "like a physicist." A physicist replicating
a SWMF paper does not reinvent AWSoM from first principles. They:

1. Read the paper to identify what's being done physically.
2. Pull up the closest shipped PARAM that matches the archetype.
3. Diff: keep the parts that aren't paper-specific, edit the parts that are.
4. Surface anything the paper is silent on as a question for a colleague.

The agent built on Strategy C does exactly this, just more systematically and
with deterministic provenance tags. It is not a smarter physicist; it is a
disciplined operator with full access to the simulator's corpus.

The places where the agent will *not* generalize like a senior researcher:

- **Tuning AMR resolutions** for unprecedented archetypes. This is research,
  not configuration. The skill should refuse to invent and ask.
- **Choosing iteration counts** for a new convergence regime. Same.
- **Judging "is this run physically reasonable"** from a log file alone. The
  validation skill drives image-overlay comparisons; the judgement stays with
  the user.

These limits are appropriate and should not be papered over by overconfident
defaults.

## 7. Recommended sequence

1. **Build the corpus miner.** One afternoon. Emits `defaults/`, draft
   `case_recipes/`, draft `templates/`, and `equation_set_required.yaml`.
   This alone closes most of the eclipse2024 physics gap.
2. **Hand-author the archetype list.** A flat file with one-line descriptions.
   The LLM does archetype matching against this list directly.
3. **Hand-author the `paper_spec.json` schema with `precedent_hint` and
   `numerics_phrases` fields.** Forces the LLM to extract paper-cited prior
   runs and any explicit numerics phrases that should map to commands.
4. **Add per-paper deltas only when a replication run fails to converge to
   the production corpus.** Each delta is one YAML entry in one lane. Never a
   memorized PARAM.
5. **Re-run the corpus miner whenever SWMFSOLAR ships new exemplar PARAMs.**
   The mining is idempotent and the rules layer is additive; new exemplars
   strengthen the baseline without invalidating existing curation.

This keeps the agent on a flat capability-cost curve: the first replication
costs an afternoon of mining and a day of archetype curation; each subsequent
replication costs only as much curation as its novelty demands.

## 8. Short version

- Skip "teach physics from textbooks" — the LLM has physics.
- Skip "feed one paper+PARAM pair at a time" — overfits, wastes the corpus.
- Mine the existing SWMF/SWMFSOLAR corpus once into the four-lane rules
  framework. Cost: one afternoon. Payoff: the agent inherits the operational
  AWSoM/SOFIE/AWSoMR command vocabulary without anyone authoring physics.
- Papers are complete in physics but not in SWMF syntax. The agent translates
  paper → PARAM by joining paper-extracted physics against corpus-mined
  command realizations.
- Archetype is paper-derivable; derivations are corpus-derivable. The agent
  does the join.
- Curate deltas only. Each new paper that diverges from corpus produces one
  YAML entry per surprise — never a memorized PARAM.
- Limits stay explicit: AMR tuning, iteration counts for unprecedented
  archetypes, and physical-reasonableness judgement remain user-owned.
