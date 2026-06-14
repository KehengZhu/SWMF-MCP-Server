# SWMF manual corrections (tier: hint-correction)

The SWMF user manual (`SWMF/doc/Tex/`) is **hint-tier** — useful for worked
examples and physical motivation, but partially stale. When the agent reads
a `.tex` section for guidance, it must cross-check every command name against
`PARAM.XML` via `swmf inspect --type xml --xml-scope 'commandgroup:...'` before using
that command in PARAM.in. Pass a consistent `--run-dir <run directory>` to this read
and to the later `swmf inspect --type param --check-xml-audit` launch check so the
XML audit gate (which records command-group reads to `<run_dir>/.swmf_ai/audit.json`)
can correlate the two.

This file lists places where the manual is known to be wrong or outdated.
Entries are tiny — only "the manual says X, the code does Y, here's the
citation."

## Entry format

```
### <topic / section>
- **Manual section**: file:section (e.g. SWMF_param.tex:§3.4)
- **Manual claim**: <what the manual says>
- **Current truth**: <what the code actually does>
- **Source of truth**: file_path:line_number
- **Recorded**: YYYY-MM-DD
```

## Active corrections

_(No entries yet — list grows as the eval surfaces stale manual sections.)_

---

When the manual and `PARAM.XML` disagree, **PARAM.XML wins** automatically;
the agent does not need an entry in this file to take XML's side.
This file exists for the rarer case where the manual is misleadingly wrong
in a way the agent might still trust (worked-example contradictions,
deprecated command recommendations).
