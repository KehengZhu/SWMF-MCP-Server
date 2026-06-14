# PARAM.XML corrections (tier-0 source-of-truth patches)

`PARAM.XML` is the authoritative SWMF schema, but it can lag the Fortran source
when a parameter is added in code with a default value but no XML entry, or
when an XML entry's `default=`, `min=`, `max=`, or `if=` annotation is wrong.
This file is the **highest-precedence correction layer** the agent consults.

## Authority order

When the agent authors a PARAM block:

1. If `xml_corrections.md` has an entry for the command → use that.
2. Otherwise consult `PARAM.XML` via
   `swmf inspect --type xml --xml-scope 'commandgroup:<name>' --run-dir <run directory>`.
   Pass the same `--run-dir <run directory>` to this read and to the later
   `swmf inspect --type param --check-xml-audit --run-dir <run directory>` launch
   check so the XML audit gate (recorded in `<run_dir>/.swmf_ai/audit.json`)
   correlates the command-group read with the launch check.
3. Manual `.tex` sections are hint-tier only (and may also be stale —
   cross-check command names against PARAM.XML before using them).

## Entry format

Each entry is a heading at level 3 (`###`) followed by structured fields:

```
### #COMMANDNAME (component, e.g. SC)
- **Status**: missing | wrong_default | wrong_range | wrong_if | wrong_description
- **PARAM.XML says**: (whatever the XML claims, or "not present")
- **Source of truth**: file_path:line_number in SWMF source
- **Correct value/behavior**: (what to actually use)
- **Recorded**: YYYY-MM-DD by agent/human owner
- **Last reviewed**: YYYY-MM-DD
```

Entries must cite a specific Fortran source file + line. No corrections based
on "this looks wrong" — only "this disagrees with X, citation Y".

The corrections layer is intentionally small. If you find yourself adding many
entries, consider whether PARAM.XML upstream needs a patch instead.

## Active corrections

_(No entries yet — list grows as the eval surfaces stale XML.)_
