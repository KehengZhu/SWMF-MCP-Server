---
name: swmf-exact-lookup
type: support
description: "Support skill. Finds the precise location and definition of a named token: symbol, PARAM command, IDL procedure, file, or error string. Called by swmf-debug, swmf-configure, and other entry skills when exact confirmation is needed."
---

# swmf-exact-lookup (Support)

This is a **support skill** — a precision helper, not a top-level way of
thinking. Entry skills call it when they have an exact token and need its
definition or location confirmed.

## Purpose

Answer one thing: where exactly is this named token, and what does its
definition say?

## Scope

* exact symbol or procedure lookup
* PARAM command definition
* IDL procedure signature
* file or path confirmation
* error string lookup
* narrow confirmation after broader reasoning

Not in scope: architecture, build/run workflow, failure diagnosis.

## Tool Protocol

```bash
swmf get-evidence --query "<exact_token>" --mode keyword --scope <component if named> --top-k 6 --goal "find definition"
```

If score ≥ 0.7 and snippet contains the token → answer from that evidence.

Grep fallback (only if keyword returns 0 or weak results):
* Restrict to `evidence.files` paths or named component directory
* No broad SWMF tree grep

Last resort (one call only):
```bash
swmf get-evidence --query "<token>" --mode keyword --top-k 8
```
If this also fails → report not found.

## Output Contract

* type, path, start_line (if available), snippet
* Do NOT run `swmf get-context` for orientation
* Do NOT widen to multi-hop search
* After 3 failed attempts → report "not found" explicitly
