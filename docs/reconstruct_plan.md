Yes. Given your constraint that the agent must be able to fetch any evidence it needs **without user-mediated resource selection**, the clean design is:

**Use MCP tools only. Do not rely on MCP resources. Put workflow policy in SKILLs, not in tool outputs. Keep tool outputs evidence-centric and let the agent decide.** MCP supports tools, prompts, and resources as separate primitives, but implementations can support only the features they need, so a tools-only server is valid. ([Model Context Protocol][1])

Below is a complete plan.

---

# 1. Final architecture principle

Your stack should be:

```text
User task
  → SKILL
    → minimal MCP tools
      → internal retrieval/evidence backends
    → agent reasoning
    → optional grep fallback
```

The separation of concerns is:

* **SKILLs**: task policy, routing heuristics, stopping criteria
* **MCP tools**: local evidence retrieval and local affordance discovery
* **Indexes/backends**: implementation detail behind MCP tools
* **grep/rg**: external fallback for exact precision

This matches current guidance that agent systems work better with simple, composable patterns and with careful context curation instead of overloaded generic retrieval. ([Anthropic][2])

---

# 2. What to remove from the design

Remove these ideas entirely:

* MCP resources as a required part of the workflow
* “suggested next steps” in tool outputs
* MCP tools that try to prescribe agent behavior
* one tool per backend mechanism
* opaque `run_workflow` executors that hide logic from the agent

Why:

* Resources are a separate MCP feature, but you do not want a UX that depends on resource picking, so they should not be part of the critical path. MCP’s modular design allows you to support only the features you need. ([Model Context Protocol][3])
* Anthropic’s tooling guidance emphasizes clear tool boundaries and minimizing overlap; stuffing planner logic into low-level tools makes those boundaries worse, not better. ([Anthropic][4])

---

# 3. Final minimal agent-facing MCP surface

Expose only these tools:

1. `get_context`
2. `get_evidence`
3. `get_workflow_guidance`
4. `inspect_artifact`
5. `compare_artifacts`

And allow:

* `grep` / `rg` as agent fallback outside MCP

That is the smallest interface that still separates:

* broad orientation
* grounded evidence retrieval
* workflow entrypoint discovery
* deep local inspection
* comparison

---

# 4. Exact responsibilities of each tool

## A. `get_context`

Purpose:
Give the agent compact repo/task orientation, not proof and not policy.

Use for:

* vague questions
* architecture questions
* multi-component questions
* “what area of the codebase matters?”

Allowed internal backends:

* catalog
* semantic index
* Devin MCP repo Q&A
* codebase map

Should return:

* compact summary
* entities: components, files, params, symbols
* provenance
* uncertainty

Should not return:

* workflow advice
* follow-up instructions
* hidden plans

### Example schema

```json
{
  "question": "How does GM couple to IE in this setup?",
  "scope": ["GM", "IE"],
  "task_type": "architecture",
  "detail": "brief|normal|deep"
}
```

### Example result

```json
{
  "summary": "GM-IE coupling appears to involve CON-mediated timing and shared coupling parameters.",
  "entities": {
    "components": ["GM", "IE", "CON"],
    "files": ["PARAM.in", "PARAM.XML", "CON/Config.pl"],
    "params": ["DoCoupleGMIE", "DtCouple"],
    "symbols": ["..."]
  },
  "provenance": {
    "backend_used": "catalog+semantic"
  },
  "uncertainty": {
    "known_unknowns": ["current case-specific runtime state not inspected"]
  }
}
```

---

## B. `get_evidence`

Purpose:
Retrieve local evidence for a query. This is your main retrieval tool.

Arguments should include the retrieval mode, exactly as you suggested:

* `hybrid` default
* `keyword`
* `semantic`

Use for:

* symbol/param/file lookup
* exact questions
* supporting snippets for a claim
* evidence gathering before answering

Allowed internal backends:

* keyword search
* semantic search
* hybrid search
* symbol lookup
* catalog lookup
* reranker

The public API can stay simple while the server routes internally.

Should return:

* evidence list
* scores or rank
* provenance
* uncertainty

Should not return:

* “what the agent should do”
* procedural playbook logic

### Example schema

```json
{
  "query": "DoCoupleGMIE",
  "mode": "hybrid",
  "scope": ["GM", "IE"],
  "top_k": 8,
  "goal": "find definition and usage"
}
```

### Example result

```json
{
  "summary": "4 relevant evidence items found for DoCoupleGMIE",
  "evidence": [
    {
      "type": "param_spec",
      "path": "PARAM.XML",
      "snippet": "...",
      "score": 0.91
    },
    {
      "type": "code",
      "path": "GM/src/...",
      "snippet": "...",
      "score": 0.87
    }
  ],
  "provenance": {
    "mode_used": "hybrid",
    "scope": ["GM", "IE"]
  },
  "uncertainty": {
    "known_unknowns": ["runtime behavior for current case not inspected"]
  }
}
```

---

## C. `get_workflow_guidance`

Purpose:
Expose likely workflow entrypoints and usage evidence. It does **not** execute anything and does **not** synthesize the final workflow. The agent does that.

Use for:

* “how do I configure module X?”
* “what script or entrypoint is usually used?”
* “what are the relevant build/run/config scripts?”

Allowed internal backends:

* catalog
* exact lookup
* semantic context
* script inspection
* usage extraction

Should return:

* entrypoints
* usage examples/evidence
* required inputs
* constraints/caveats
* provenance
* uncertainty

Should not return:

* a fully hard-coded sequence
* “next steps”
* hidden execution

### Example schema

```json
{
  "goal": "configure GM for this case",
  "module": "GM",
  "task_type": "configuration",
  "context": {
    "case_dir": "...",
    "related_components": ["IE"]
  }
}
```

### Example result

```json
{
  "summary": "One primary configuration entrypoint found for GM.",
  "entrypoints": [
    {
      "path": "path/to/Config.pl",
      "kind": "script",
      "why_relevant": "appears to be the main GM configuration script"
    }
  ],
  "usage_evidence": [
    {
      "path": "path/to/Config.pl",
      "snippet": "...usage/help text...",
      "score": 0.89
    }
  ],
  "required_inputs": ["module settings", "case directory"],
  "constraints": ["may overwrite generated configuration files"],
  "provenance": {
    "backend_used": "catalog+keyword"
  },
  "uncertainty": {
    "known_unknowns": ["case-specific configuration flags not yet inspected"]
  }
}
```

---

## D. `inspect_artifact`

Purpose:
Inspect one specific local artifact deeply.

Use for:

* logs
* `PARAM.in`
* `PARAM.XML`
* run directories
* build outputs
* generated outputs

Should return:

* summary
* findings
* evidence excerpts
* provenance
* uncertainty

### Example schema

```json
{
  "artifact_type": "log",
  "path": "run/log.ie",
  "question": "why did initialization fail?"
}
```

---

## E. `compare_artifacts`

Purpose:
Compare two local things.

Use for:

* two PARAM files
* two run outputs
* two logs
* two generated artifacts

Should return:

* summary
* differences
* evidence
* provenance
* uncertainty

---

# 5. Internal backends hidden behind MCP

The agent should **not** see these as separate tools:

* catalog lookup
* semantic index
* keyword index
* hybrid retrieval
* symbol lookup
* reranker
* Devin MCP calls
* script help extraction
* log parser
* param validator

These should remain server-side internals of the five MCP tools.

This follows the general direction in Anthropic’s tool guidance: make tools easy to choose and avoid overlapping mechanisms exposed directly to the model. ([Anthropic][4])

---

# 6. Where SKILLs fit

SKILLs should carry all the routing and workflow policy.

A SKILL should specify:

* when to call `get_context`
* when to call `get_evidence`
* when `keyword` should override `hybrid`
* when to inspect artifacts first
* when to use grep fallback
* what counts as enough evidence
* when the agent may answer

So the rule becomes:

> **Tools provide evidence and local affordances. SKILLs provide retrieval strategy. The agent provides reasoning.**

That is the cleanest version of everything we discussed.

---

# 7. Routing policy to encode in SKILLs

## If the question is broad or cross-component

Call:

1. `get_context`
2. `get_evidence` on the most likely files/params/symbols
3. `inspect_artifact` if there is a current case/run involved

## If the question contains exact tokens

Call:

1. `get_evidence(mode="keyword")`
2. grep fallback if precision is still inadequate

## If the question is debugging a current run

Call:

1. `inspect_artifact` on logs / params / run dir first
2. `get_context` only if the failure spans multiple components
3. `get_evidence` for code/config grounding

## If the question is about how to do a workflow

Call:

1. `get_workflow_guidance`
2. optional `get_evidence` for supporting scripts/params
3. agent synthesizes the workflow text or command sequence

## If comparing two cases

Call:

1. `compare_artifacts`
2. `inspect_artifact` on whichever side is anomalous
3. `get_evidence` only if code/config interpretation is needed

---

# 8. Grep fallback policy

Keep grep outside MCP and let the agent use it directly.

Grep is allowed when:

* the query contains a precise token
* MCP evidence is broad but inconclusive
* the agent wants exact confirmation
* the agent wants a cheap local fallback

Grep is not the first choice when:

* the question is vague
* the question spans multiple components
* the task is architectural
* the task is “what script/workflow should I use?”

This gives you the behavior you want: the agent is still free to use grep, but grep stops being the only available cognitive move.

---

# 9. Devin MCP’s role in this design

Use Devin MCP only inside `get_context` and sometimes `get_workflow_guidance`, not as a public tool the agent always calls first.

That is because Devin MCP is good at repo-level documentation/search and grounded Q&A through tools like `ask_question`, `read_wiki_structure`, and `read_wiki_contents`. It is helpful for broad understanding, not necessary for every exact lookup. ([Model Context Protocol][5])

So:

* `get_context` may internally use Devin MCP
* `get_evidence` usually should not
* the agent should not have to know whether Devin was used

This keeps the public interface minimal.

---

# 10. Output contract for all tools

Use one consistent shape:

```json
{
  "summary": "...",
  "evidence": [],
  "provenance": {},
  "uncertainty": {
    "known_unknowns": []
  }
}
```

Optional extensions:

* `entities`
* `entrypoints`
* `findings`
* `differences`

But do not include:

* `suggested_next_steps`
* `recommended_agent_actions`
* planner hints

That keeps the tools honest and reusable.

---

# 11. Make hard-coded procedures minimal

Hard-code only:

* query normalization
* backend selection
* result ranking
* evidence extraction
* output shaping

Do **not** hard-code:

* large domain decision trees
* end-to-end debug logic
* workflow scripts as black-box automation
* generic “do this next” suggestions

This gives you “smart retrieval, dumb tools, smart agent.”

---

# 12. Concrete implementation phases

## Phase 1 — Define the public API

Write the schemas for:

* `get_context`
* `get_evidence`
* `get_workflow_guidance`
* `inspect_artifact`
* `compare_artifacts`

Deliverables:

* JSON schema
* example requests
* example responses
* field-level semantics

Success criterion:

* every existing public tool can be mapped into one of these five

---

## Phase 2 — Build the internal router

Create a private server-side router for each public tool.

For `get_evidence`:

* if exact token-like query → bias keyword heavily
* if natural language query → hybrid default
* if user explicitly requests semantic → semantic
* optionally rerank the final candidates

For `get_context`:

* prefer catalog + semantic + Devin MCP
* return compact entities, not long prose

For `get_workflow_guidance`:

* inspect likely scripts, help text, and config entrypoints
* return affordances, not plans

Success criterion:

* the agent never needs to know which backend answered

---

## Phase 3 — Move all routing policy into SKILLs

Create SKILLs like:

* `answer_architecture_question`
* `debug_current_case`
* `trace_parameter`
* `generate_workflow_for_module`
* `compare_two_cases`

Each SKILL specifies:

* tool call order
* evidence threshold
* grep fallback conditions
* answer rules

Success criterion:

* tool outputs become purely evidential
* agent behavior changes come from SKILL edits, not tool edits

---

## Phase 4 — Add artifact-specialized inspectors

Implement `inspect_artifact` subtypes for:

* log
* param file
* XML spec
* run directory
* build output
* generated result file

Success criterion:

* debugging tasks can start from local artifacts instead of semantic repo lookup

---

## Phase 5 — Add evaluation harness

Test on real SWMF tasks:

1. exact symbol lookup
2. cross-component architecture question
3. debug failing run
4. trace parameter through config and code
5. discover configuration workflow for one module
6. compare two runs

Measure:

* number of MCP tool calls
* grep fallback frequency
* answer correctness
* evidence grounding quality
* token usage
* time to first useful answer

Anthropic’s public guidance on agent evals and harnesses is clear that multi-turn agent systems need evaluation at the loop level, not just one-shot prompts. ([Anthropic][6])

---

# 13. Concrete SKILL examples

## SKILL: architecture question

Policy:

* if multiple components or vague NL query → `get_context`
* then `get_evidence` on the top entities returned
* answer only after at least one code/config/doc evidence item supports the explanation

## SKILL: exact lookup

Policy:

* start with `get_evidence(mode="keyword")`
* if top hits weak → grep fallback
* no `get_context` unless there is ambiguity about which component/file is relevant

## SKILL: debug run

Policy:

* start with `inspect_artifact` on logs and params
* use `get_context` only if the failure appears cross-component
* use `get_evidence` to ground hypotheses in code/config

## SKILL: workflow generation

Policy:

* call `get_workflow_guidance`
* optionally call `get_evidence` to inspect referenced scripts
* agent writes the actual workflow/commands itself

---

# 14. Final API proposal

```text
get_context(
  question,
  scope? = [],
  task_type? = "architecture|debug|lookup|workflow|compare",
  detail? = "brief|normal|deep"
)

get_evidence(
  query,
  mode? = "hybrid|keyword|semantic",
  scope? = [],
  top_k? = 8,
  goal? = ""
)

get_workflow_guidance(
  goal,
  module? = "",
  task_type? = "configuration|build|run|analysis",
  context? = {}
)

inspect_artifact(
  artifact_type,
  path,
  question? = ""
)

compare_artifacts(
  left,
  right,
  comparison_type? = "",
  question? = ""
)
```

Outside MCP:

* `grep` / `rg` fallback

That is the design I would commit to.

---

# 15. The key rules to preserve

1. **No MCP resources in the critical path.**
2. **No planner hints in MCP outputs.**
3. **No backend-specific public tools.**
4. **Hybrid retrieval is the default in `get_evidence`.**
5. **`get_workflow_guidance` returns affordances and evidence, not execution.**
6. **SKILLs contain routing behavior.**
7. **grep stays available as a precision fallback.**
8. **The agent decides. The tools prove.**

That is the complete plan.

I can turn this into a concrete deliverable next: a **single YAML design spec** for the five MCP tools plus 4–5 SWMF SKILL policies.

[1]: https://modelcontextprotocol.io/specification/2025-06-18?utm_source=chatgpt.com "Specification"
[2]: https://www.anthropic.com/research/building-effective-agents?utm_source=chatgpt.com "Building Effective AI Agents"
[3]: https://modelcontextprotocol.io/specification/2025-06-18/basic?utm_source=chatgpt.com "Overview - Model Context Protocol"
[4]: https://www.anthropic.com/engineering/writing-tools-for-agents?utm_source=chatgpt.com "Writing effective tools for AI agents—using ..."
[5]: https://modelcontextprotocol.io/specification/2025-06-18/server/prompts?utm_source=chatgpt.com "Prompts"
[6]: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents?utm_source=chatgpt.com "Demystifying evals for AI agents"
