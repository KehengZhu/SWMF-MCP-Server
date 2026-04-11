# Invariants Checklist

Use this checklist before patch readiness for source-level debugging.

## Required
- data_structure
- invariants_before_change
- operations_that_can_violate
- diagnostics_to_collect
- runtime_checks

## Typical invariant examples
- index bounds and offsets are valid
- array lengths are consistent across coupled buffers
- rank ownership and router assumptions remain valid
- monotonicity or conservation assumptions are preserved

## Ready criteria
Patch readiness can be true only when:
- invariant block exists
- diagnostics are actionable
- runtime checks can confirm/refute at least one candidate mechanism
