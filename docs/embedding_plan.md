I’m rebuilding the plan around the final decisions you made: `knowledge` naming, `reference` independent from `catalog`, and `sentence-transformers` with device selection across CUDA, MPS, or CPU.

Read [](file:///Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server)

Read skill [swmf-implementation](file:///Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/.github/skills/swmf-implementation/SKILL.md?vscodeLinkType%3Dskill)

Read memory [](file:///Users/zkeheng/Library/Application%20Support/Code/User/workspaceStorage/8a8a9181f7b5475ecdccdb38af5f163c/GitHub.copilot-chat/memory-tool/memories/NTMzYmU4NDYtOWJmYy00NjY4LWFjNWItMjA4YWVlYTc4Zjg2/plan.md)

I’m replacing the old reconstruction plan with the final one: `knowledge` naming, `reference` independent from `catalog`, and `sentence-transformers` with automatic CUDA/MPS/CPU device selection.

Deleted memory [](file:///Users/zkeheng/Library/Application%20Support/Code/User/workspaceStorage/8a8a9181f7b5475ecdccdb38af5f163c/GitHub.copilot-chat/memory-tool/memories/NTMzYmU4NDYtOWJmYy00NjY4LWFjNWItMjA4YWVlYTc4Zjg2/plan.md)

Created memory file [](file:///Users/zkeheng/Library/Application%20Support/Code/User/workspaceStorage/8a8a9181f7b5475ecdccdb38af5f163c/GitHub.copilot-chat/memory-tool/memories/NTMzYmU4NDYtOWJmYy00NjY4LWFjNWItMjA4YWVlYTc4Zjg2/plan.md)

## Plan: Reconstruct Catalog, Reference, and Knowledge

Rebuild the current model around three strict domains:

- `catalog`: source indexing and keyword retrieval only
- `reference`: authoritative and static lookup only, with direct file/parsing access
- `knowledge`: semantic understanding for agents, using `sentence-transformers`

`reference` should not use `catalog` as a backend. `knowledge` may consume both `catalog` and `reference`. The embedding runtime should auto-select `cuda`, then `mps`, then `cpu`.

**Core Decisions**
1. Use `knowledge`, not `domain_knowledge`.
2. `reference` is independent from `catalog`.
3. Use `sentence-transformers` plus `torch` for embeddings.
4. Device selection order:
CUDA if available, else Apple MPS if available, else CPU.
5. No backward compatibility.

**Steps**
1. Freeze the architecture note and dependency rules.
Write a short design note that states:
catalog may not import semantic logic or embedding backends, reference may not depend on catalog, and knowledge may depend on both.

2. Reconstruct the package layout.
Create or refactor these packages:
- catalog
- `src/swmf_mcp_server/reference/`
- knowledge

Move static-discovery modules from `catalog` into `reference`.

3. Narrow `catalog` to keyword-only ownership.
Simplify source_index_catalog.py so it only owns:
- source indexing
- SQLite schema/build/refresh
- keyword symbol search
- keyword chunk search
- exact symbol lookup
- keyword-style heuristic param mention extraction

Remove semantic dispatch, embedding imports, model metadata, device logic, and hybrid ownership.

4. Build the `reference` service.
Move or rewrite the current static and authoritative lookup modules under `reference`.
Update lookup.py, param.py, and relevant resources so they use `reference` directly.

5. Build the `knowledge` embedding layer with `sentence-transformers`.
Add `knowledge/embeddings.py` that:
- loads the sentence-transformers model lazily
- selects device in this order: CUDA, MPS, CPU
- reports selected device and model name in status and tool payloads

6. Build semantic retrieval in `knowledge`.
Add `knowledge/retrieval.py` and `knowledge/service.py`.
These should consume catalog-produced chunks or symbols as raw evidence, embed them with sentence-transformers, rank them, and produce agent-facing grounding outputs.

7. Add query understanding and agent context generation.
Implement:
- `knowledge/query_understanding.py`
- `knowledge/agent_context.py`

These should classify intent, extract SWMF entities, recommend corpus slices, and produce grounded context packs for agents.

8. Reconstruct the MCP tool layer.
Delete the current mixed ownership model in knowledge_service.py and rebuild tool registration in server.py around three tool families:
- catalog tools
- reference tools
- knowledge tools

9. Rewrite tests and docs.
Rewrite architecture tests, service tests, tool-surface tests, and docs around the new domain split and the sentence-transformers runtime behavior.

**Recommended New MCP Surface**
1. Catalog tools:
- `swmf_build_catalog_index`
- `swmf_refresh_catalog_index`
- `swmf_get_catalog_status`
- `swmf_search_catalog`
- `swmf_lookup_catalog_symbol`

2. Reference tools:
- `swmf_list_components`
- `swmf_get_component`
- `swmf_get_param_command`
- `swmf_get_param_trace`
- `swmf_get_param_schema`
- `swmf_find_examples`
- `swmf_get_coupling_info`
- `swmf_list_idl_procedures`
- `swmf_explain_idl_procedure`

3. Knowledge tools:
- `swmf_build_knowledge_index`
- `swmf_get_knowledge_status`
- `swmf_search_knowledge`
- `swmf_understand_source_query`
- `swmf_get_agent_context_pack`

**Relevant Files**
- source_index_catalog.py
- catalog_service.py
- component_catalog.py
- script_catalog.py
- template_catalog.py
- idl_catalog.py
- xml_catalog.py
- knowledge_service.py
- semantic_search.py
- curated.py
- lookup.py
- param.py
- knowledge.py
- server.py
- pyproject.toml

**Verification**
1. Add architecture tests proving:
catalog does not import `sentence-transformers` or `torch`, reference does not import catalog, and knowledge may depend on both.

2. Add service tests proving:
reference works without a catalog DB, and catalog keyword search works without sentence-transformers installed.

3. Add knowledge tests proving:
device selection chooses CUDA, then MPS, then CPU, and semantic retrieval fails cleanly when model loading fails.

4. Add authoritative-boundary tests proving:
PARAM.XML and TestParam.pl flows do not depend on catalog or knowledge for correctness.

5. Run a manual scenario matrix:
- keyword source lookup
- authoritative PARAM lookup
- semantic SWMF understanding on CPU
- semantic SWMF understanding on MPS if available

The new plan is saved in `plan.md`. If you want, the next step is:
1. turn this into a file move/delete/create checklist, or
2. start implementation from Phase 1 with the package split and service deletion boundary.You've used 51% of your weekly rate limit. Your weekly rate limit will reset on April 26 at 8:00 PM. [Learn More](https://aka.ms/github-copilot-rate-limit-error)