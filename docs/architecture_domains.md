# Architecture Domains

The codebase is being reconstructed around three domains with strict ownership.

## Domain Boundaries

- `catalog` owns source indexing and keyword retrieval only.
- `reference` owns authoritative and static lookup directly from source files.
- `knowledge` owns semantic understanding and agent context assembly.

## Dependency Rules

- `catalog` may depend on parsing and shared core utilities, but it may not import embedding backends, semantic ranking code, or device-selection logic.
- `reference` may depend on parsing and shared core utilities, but it may not import `catalog` or query the catalog database.
- `knowledge` may depend on both `catalog` and `reference`, but it must not redefine authoritative truth from PARAM.XML or TestParam.pl.

## Implementation Notes

- `reference` should remain usable even when no catalog index has been built.
- `catalog` should remain usable even when semantic dependencies are not installed.
- The first reconstruction slice introduces the `reference` package and begins repointing public lookup tools to it.