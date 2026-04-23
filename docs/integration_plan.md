Status: Approved by user on 2026-04-22. Ready for implementation handoff.


## Plan: V2 Interface Purge

Remove all stale MCP-era interface surface so the repository becomes strictly v2-only: five public tools, no legacy/admin MCP helpers, no legacy tool guidance in skills/docs, and no tests that preserve deprecated interfaces. Execute the cleanup by first protecting the current v2 dependency chain, then deleting obsolete tool modules and rewiring tests/docs to enforce the smaller contract.

**Steps**
1. Phase 1 — Freeze the target contract.
   - Declare the only supported interface as the five v2 tools defined in /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/api_v2_schema.yaml: get_context, get_evidence, get_workflow_guidance, inspect_artifact, compare_artifacts.
   - Remove all maintenance/admin MCP interfaces from the contract as part of the same cutover, since the chosen scope is v2-only with no admin exceptions.
   - Treat all `swmf_*` MCP tool functions as stale unless they are retained as private non-MCP implementation details under renamed/internalized helpers.
   - Scope boundary: parser/catalog/knowledge infrastructure may stay only when directly required by the five v2 tools; MCP-facing wrappers, compatibility aliases, and transition-era inventories are in scope for removal.
2. Phase 2 — Protect the live v2 path before deletion. *blocks Phases 3-5*
   - Extract shared helper logic currently imported from stale modules, starting with `infer_job_layout()` currently sourced from build_run.py and used by debug_protocol-backed v2 inspection paths.
   - Move any still-needed helper into a clearly private/shared location under src/swmf_mcp_server/tools or src/swmf_mcp_server/core, then repoint debug_protocol.py and any surviving consumers.
   - Recheck for any remaining imports from stale modules into the v2 tool chain and resolve them before deleting files.
3. Phase 3 — Remove stale MCP/server surfaces. *depends on 2*
   - Delete stale MCP tool registration entrypoints and legacy tool-facing functions from the obsolete tool modules.
   - Remove obsolete modules entirely where they become unused after helper extraction.
   - Simplify src/swmf_mcp_server/tools/__init__.py so it no longer exports or advertises legacy domains kept only for transition.
   - Ensure src/swmf_mcp_server/server.py registers only the five v2 tools and carries no stale/admin registration logic.
   - Decide file-by-file deletion/refactor order to keep imports green: delete pure-stale modules first, then modules previously feeding shared helpers, then any package export stubs.
4. Phase 4 — Purge stale instructions and documentation. *can start after target contract in 1, but final edits should follow 3*
   - Rewrite README.md to be strictly v2-only: replace legacy walkthroughs with a five-tool workflow, remove legacy tool inventory sections, and remove stale resource/interface descriptions.
   - Update .github/copilot-instructions.md so routing and pre-search guidance reference only the v2 interface and the current skill/support-skill structure.
   - Update entry skill files under .github/skills so example flows and helper references do not name removed legacy tools or obsolete support patterns.
   - Remove or archive superseded planning/architecture documents that preserve the old tool inventory if they no longer describe the repository truth.
   - Clean repository-scoped instruction memory that encodes the old `swmf_`-prefixed MCP convention because it conflicts with the new v2-only contract.
5. Phase 5 — Rewrite the test suite to enforce the cutover. *depends on 3 and 4*
   - Delete tests whose sole purpose is to inventory or classify legacy helper tools, especially tests that permit stale code to survive by mapping it in schema.
   - Rewrite transition-era parity tests so they enforce an exact v2 whitelist instead of “every stale helper must be mapped somewhere.”
   - Keep and strengthen tests that already defend the five-tool public server surface and the no-resource rule.
   - Remove tests dedicated to deleted legacy modules, and preserve/adapt only those that validate infrastructure still required by the v2 implementation.
   - Add replacement tests that fail on reintroduction of `swmf_*` MCP tools, stale package exports, or legacy README/skill references where appropriate.
6. Phase 6 — Final consistency pass. *depends on 3-5*
   - Align docs/api_v2_schema.yaml with the final repository state by removing stale `existing_tool_mapping` and admin-tool inventory once the cutover is complete, unless a minimal historical note is deliberately preserved outside the schema.
   - Verify no deleted interface names remain in source, tests, docs, or skills.
   - Verify import/package topology after file deletions so architecture tests reflect the new smaller tool surface instead of the old multi-module layout.

**Relevant files**
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/api_v2_schema.yaml — contract authority; remove stale mappings/admin inventory once code/docs/tests are cut over.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/server.py — final MCP registration must stay limited to the five v2 tools.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/build_run.py — current stale module that still owns infer_job_layout(); extract before deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/debug_protocol.py — surviving infrastructure for inspect_artifact/compare_artifacts; must stop importing stale modules.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/__init__.py — remove legacy exports and collapse package surface to the supported modules.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/catalog.py — stale MCP/admin surface candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/configure.py — stale MCP surface candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/knowledge.py — stale MCP/admin surface candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/param.py — stale MCP surface candidate for deletion after dependency review.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/reference.py — stale wrapper/export surface candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/retrieve.py — stale lookup tool surface candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/lookup.py — stale wrapper layer candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/diagnose.py — stale tool module candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/idl.py — stale tool module candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/postprocess.py — stale tool module candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/src/swmf_mcp_server/tools/solar_campaign.py — stale tool module candidate for deletion.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/README.md — replace transition-era walkthroughs and legacy tool inventory with v2-only guidance.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/.github/copilot-instructions.md — remove stale routing/tool references and fix current skill/support-skill guidance.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/.github/skills/swmf-debug/SKILL.md — remove legacy helper/tool references from the debug workflow.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/.github/skills/swmf-configure/SKILL.md — align support-skill references and v2-only guidance.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/.github/skills/swmf-analyze/SKILL.md — remove stale postprocessing/interface references if still present.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/docs/skills_plan.md — retire or archive if it still documents the superseded interface model.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/tests/test_legacy_capability_inventory.py — delete; currently preserves the stale helper inventory.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/tests/test_api_v2_phase1.py — rewrite parity/whitelist assertions to enforce exact v2 surface.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/tests/test_resource_registration.py — keep and strengthen as a primary gate on the public MCP surface.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/tests/test_tools_package_surface.py — update or remove depending on whether the package surface collapses fully to v2 modules.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/tests/test_reference_domain_architecture.py — delete or replace if the reference domain is removed.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/tests/test_testparam_execution_context.py — delete with param-tool removal.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/tests/test_idl_batch_shell.py — delete if the IDL tool module is removed.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/tests/test_service_layer_architecture.py — adapt to the surviving v2/core architecture after legacy domains are removed.
- /Users/zkeheng/SWMFSoftware/swmf-mcp-prototype/tests/test_source_indexed_architecture.py — adapt if it currently assumes removed param/reference surfaces.
- /memories/repo/conventions.md — stale repository instruction currently says MCP tool-facing functions should use `swmf_` prefixes; update or delete to match v2-only reality.

**Verification**
1. Run the focused test gates that define the intended contract: tests for server registration, v2 schema presence, public tool import/signature/output contract, and updated package-surface expectations.
2. Run repository-wide searches for `swmf_` MCP tool names and for removed module names across src, tests, docs, and .github; remaining hits must be either deliberate historical notes outside the active contract or zero.
3. Run a narrow import/collection pass for the surviving package to confirm no deleted module is still imported by debug_protocol.py, server.py, or the five v2 tools.
4. Re-run the architecture/test files adapted in Phase 5 to confirm the reduced topology is internally consistent.
5. Manually check README.md, .github/copilot-instructions.md, and affected SKILL.md files to ensure every example path now routes through the five v2 tools and no legacy/admin interface is presented as available.

**Decisions**
- Included: full removal of stale MCP/public/admin interfaces, stale skill/instruction language, and stale test expectations.
- Included: v2-only documentation with no legacy appendix.
- Included: deletion of admin tools rather than keeping a maintenance-only exception.
- Excluded: removal of low-level parsing, catalog, or knowledge infrastructure when directly required by the surviving five tools; these may be retained as private implementation.
- Excluded: broader non-interface refactors unrelated to the cutover.
- Key technical constraint: build_run.py cannot be deleted first because infer_job_layout() currently feeds debug_protocol.py, which underpins inspect_artifact and compare_artifacts.

**Further Considerations**
1. If docs/api_v2_schema.yaml is intended to remain a migration artifact rather than the live contract, decide whether to move historical legacy mappings into a separate archive doc instead of trimming the schema in place.
2. If tests currently assert the presence of legacy hidden modules in package layout, expect architecture-test rewrites to be broader than simple deletions because the package topology itself will change.
3. After execution, update repository memory/instructions immediately; otherwise future agents will keep trying to preserve the stale `swmf_` interface model.