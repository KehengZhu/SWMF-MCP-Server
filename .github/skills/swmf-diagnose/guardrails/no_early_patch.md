# No Early Patch Guardrail

Do not propose or apply source edits until all conditions are met:

1. Failure family is classified.
2. Required context pack is complete for that family.
3. Observation report is complete and source-grounded.
4. At least two mechanism candidates are listed when ambiguity exists.
5. One cheapest discriminating check is proposed.
6. For source-change flows, invariant block is complete.

Stop conditions:
- Plot and raw-file evidence conflict.
- Version/source path mismatch is unresolved.
- First failing artifact has not been located.

If any stop condition is active, remain in evidence_collection or normalization state.
