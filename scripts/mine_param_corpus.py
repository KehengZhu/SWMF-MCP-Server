#!/usr/bin/env python3
"""Mine the shipped SWMF / SWMFSOLAR PARAM corpus into archetype-keyed YAML.

Strategy C from docs/capability_enrichment_plan.md §4. The miner reads
in-corpus PARAMs, groups them by archetype (rules/archetypes.yaml), and
emits:

  rules/defaults/mined/<archetype>_required.yaml
  rules/defaults/mined/<archetype>_typical.yaml
  rules/defaults/mined/equation_set_required.yaml
  rules/defaults/mined/mining_report.md

The miner is a pure function of corpus content. Same inputs produce
byte-identical outputs. Output directory is wiped and rewritten atomically.

Corpus boundary (load-bearing):
  In:  SWMF/Param/PARAM.in.*, SWMFSOLAR/Param/PARAM.in.*,
       SWMF/{GM,SC}/BATSRUS/srcEquation/*.f90
  Out: anything under SWMFSOLAR/Run_*/ is rejected with a hard error.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Make the package importable when running from a checkout.
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "src"))

import yaml  # type: ignore[import-untyped]

from swmf_mcp_server.core.swmf_root import resolve_swmf_root
from swmf_mcp_server.parsing.param_parser import parse_param_text
from swmf_mcp_server.tools.inspect_artifact import (  # type: ignore[attr-defined]
    _parse_param_command_blocks,
    _row_to_param_setting,
)

# ---------------------------------------------------------------------------
# Corpus boundary
# ---------------------------------------------------------------------------

_RUN_DIR_RE = re.compile(r"(^|/)Run_[^/]+(/|$)")


def _reject_if_run_dir(path: Path) -> None:
    if _RUN_DIR_RE.search(str(path)):
        raise SystemExit(
            f"corpus-boundary error: {path} is under SWMFSOLAR/Run_*/ "
            f"(personal study scratch — see capability_enrichment_plan.md §4.1)"
        )


# ---------------------------------------------------------------------------
# Archetype detection
# ---------------------------------------------------------------------------

_CONFIG_FLAG_RE = re.compile(
    r"Config\.pl\s+-o=(?P<comp>[A-Z]{2}):.*?\bu=(?P<u>[A-Za-z0-9]+)"
    r"(?:.*?\be=(?P<e>[A-Za-z0-9]+))?",
)
_CONFIG_V_RE = re.compile(r"Config\.pl\s+-v=(?P<v>[A-Za-z0-9_,/\.]+)")
_CONFIG_E_ONLY_RE = re.compile(r"\be=(?P<e>[A-Za-z0-9]+)")


@dataclass
class ParamFile:
    path: Path
    rel_path: str
    name: str
    commands_by_session: list[list[str]] = field(default_factory=list)
    commands_all: set[str] = field(default_factory=set)
    blocks: list[dict[str, Any]] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    has_CME: bool = False
    has_MFLAMPA: bool = False
    has_threaded_gap: bool = False
    config_models: dict[str, str] = field(default_factory=dict)  # comp -> e=...
    archetype_id: str | None = None
    classify_notes: list[str] = field(default_factory=list)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _extract_config_flags(leading_text: str) -> tuple[dict[str, str], list[str] | None]:
    """Scan the leading comment block for `Config.pl -o=COMP:u=...,e=...` lines.

    Returns (models_per_component, components_listed_by_-v_=...).
    """
    models: dict[str, str] = {}
    components_v: list[str] | None = None
    for line in leading_text.splitlines():
        m = _CONFIG_FLAG_RE.search(line)
        if m:
            comp = m.group("comp")
            equation = m.group("e") or m.group("u") or ""
            if comp and equation:
                models.setdefault(comp, equation)
            continue
        v = _CONFIG_V_RE.search(line)
        if v:
            tokens = [tok for tok in v.group("v").split(",") if tok]
            # keep only 2-letter component IDs
            comps = []
            for tok in tokens:
                head = tok.split("/")[0].strip()
                if len(head) == 2 and head.isupper():
                    comps.append(head)
                elif "/" in tok and tok.split("/")[0].strip() == "Empty":
                    continue
            if comps:
                components_v = comps
    return models, components_v


def _parse_param_file(path: Path) -> ParamFile | None:
    try:
        text = _read_text(path)
    except OSError as exc:
        print(f"skip (read error): {path}: {exc}", file=sys.stderr)
        return None

    parsed = parse_param_text(text)
    blocks = _parse_param_command_blocks(text)

    pf = ParamFile(path=path, rel_path=str(path), name=path.name)
    pf.blocks = blocks
    pf.commands_by_session = [
        [str(c).upper() for c in session.commands] for session in parsed.sessions
    ]
    for session in parsed.sessions:
        for c in session.commands:
            pf.commands_all.add(str(c).upper())

    # Components: prefer #COMPONENTMAP rows, then #BEGIN_COMP blocks, then -v= flags.
    components: list[str] = []
    seen: set[str] = set()

    def _add(c: str) -> None:
        cu = c.strip().upper()
        if len(cu) == 2 and cu not in seen:
            seen.add(cu)
            components.append(cu)

    for session in parsed.sessions:
        for row in session.component_map_rows:
            _add(str(row.get("component", "")))
        for c in session.component_blocks:
            _add(c)

    leading = "\n".join(text.splitlines()[:40])
    models, components_v = _extract_config_flags(leading)
    if components_v:
        for c in components_v:
            _add(c)
    pf.config_models = models
    pf.components = sorted(components)

    pf.has_CME = "#CME" in pf.commands_all
    pf.has_MFLAMPA = "SP" in seen
    pf.has_threaded_gap = "#FIELDLINETHREAD" in pf.commands_all

    return pf


def _load_archetypes(rules_dir: Path) -> list[dict[str, Any]]:
    catalog_path = rules_dir / "archetypes.yaml"
    if not catalog_path.is_file():
        raise SystemExit(f"missing archetype catalog: {catalog_path}")
    with catalog_path.open("r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    if not isinstance(loaded, list):
        raise SystemExit(f"{catalog_path}: top-level must be a list of archetype entries")
    return loaded


def _archetype_matches(arch: dict[str, Any], pf: ParamFile) -> tuple[bool, list[str]]:
    notes: list[str] = []
    score = 0
    expected_components = arch.get("components")
    if isinstance(expected_components, list) and expected_components:
        if sorted(expected_components) != pf.components:
            return False, [f"components {pf.components} != {sorted(expected_components)}"]
        score += 1
    expected_cme = arch.get("has_CME")
    if isinstance(expected_cme, bool):
        if expected_cme != pf.has_CME:
            return False, [f"has_CME {pf.has_CME} != {expected_cme}"]
        score += 1
    expected_mflampa = arch.get("has_MFLAMPA")
    if isinstance(expected_mflampa, bool):
        if expected_mflampa != pf.has_MFLAMPA:
            return False, [f"has_MFLAMPA {pf.has_MFLAMPA} != {expected_mflampa}"]
        score += 1
    expected_threaded = arch.get("has_threaded_gap")
    if isinstance(expected_threaded, bool):
        if expected_threaded != pf.has_threaded_gap:
            return False, [f"has_threaded_gap {pf.has_threaded_gap} != {expected_threaded}"]
        score += 1
    expected_model = arch.get("model")
    if isinstance(expected_model, str) and pf.config_models:
        observed_models = set(pf.config_models.values())
        # SOFIE family uses AwsomSA / AwsomSAWdiff
        if expected_model == "AwsomSA":
            if not any(m.startswith("Awsom") and "SA" in m for m in observed_models):
                return False, [f"model {observed_models} != {expected_model}*"]
        elif expected_model == "AwsomAnisoPi":
            if not any("AnisoPi" in m for m in observed_models):
                return False, [f"model {observed_models} != {expected_model}*"]
        elif expected_model == "AwsomR":
            # AWSoM-R is u=AwsomR, e=Awsom
            if "AwsomR" not in observed_models and not any(
                "AwsomR" in m for m in observed_models
            ):
                # fall through if has_threaded_gap is true and model is Awsom
                if not (pf.has_threaded_gap and "Awsom" in observed_models):
                    return False, [f"model {observed_models} != {expected_model}*"]
        elif expected_model == "Awsom":
            if not any(m == "Awsom" or m.startswith("Awsom") for m in observed_models):
                return False, [f"model {observed_models} != {expected_model}*"]
        elif expected_model in {"OuterHelio", "Geospace", "Mhd", "Other"}:
            # heuristic: skip strict model check; rely on components
            pass
        else:
            if expected_model not in observed_models:
                return False, [f"model {observed_models} != {expected_model}"]
        score += 1
    return True, notes + [f"score={score}"]


def _classify(pf: ParamFile, archetypes: list[dict[str, Any]]) -> str | None:
    # Pass 1: filename hint match (most specific).
    for arch in archetypes:
        hints = arch.get("match_hints") or []
        if isinstance(hints, list):
            for hint in hints:
                if isinstance(hint, str) and hint in pf.name:
                    ok, notes = _archetype_matches(arch, pf)
                    if ok:
                        pf.classify_notes.append(
                            f"matched archetype={arch['id']} via filename hint '{hint}' ({'; '.join(notes)})"
                        )
                        return str(arch["id"])
                    pf.classify_notes.append(
                        f"filename hint '{hint}' suggested {arch['id']} but tuple mismatch: {notes}"
                    )

    # Pass 2: tuple match without filename.
    matches: list[str] = []
    for arch in archetypes:
        ok, _notes = _archetype_matches(arch, pf)
        if ok:
            matches.append(str(arch["id"]))
    if len(matches) == 1:
        pf.classify_notes.append(f"matched archetype={matches[0]} via tuple")
        return matches[0]
    if len(matches) > 1:
        # Ambiguity tiebreaker: prefer the archetype whose name shares the
        # longest prefix with the PARAM filename (e.g. `realtime.SCIH_threadbc`
        # → awsomr_steady over sofie_steady because "thread" is AwsomR's BC).
        # Falling back to the first match keeps behaviour deterministic.
        best = matches[0]
        best_score = -1
        for aid in matches:
            arch = next(a for a in archetypes if a["id"] == aid)
            hints = arch.get("match_hints") or []
            for hint in hints:
                if isinstance(hint, str) and any(
                    tok in pf.name for tok in hint.split(".") if tok
                ):
                    if len(hint) > best_score:
                        best_score = len(hint)
                        best = aid
        pf.classify_notes.append(
            f"ambiguous: matched {matches}; tiebreak chose '{best}'"
        )
        return best
    pf.classify_notes.append(
        f"unmatched: components={pf.components}, has_CME={pf.has_CME}, "
        f"has_MFLAMPA={pf.has_MFLAMPA}, has_threaded_gap={pf.has_threaded_gap}, "
        f"models={pf.config_models}"
    )
    return None


# ---------------------------------------------------------------------------
# Corpus enumeration
# ---------------------------------------------------------------------------

_PARAM_GLOB = "PARAM.in.*"


def _enumerate_param_files(swmf_root: Path, swmfsolar_root: Path | None) -> list[Path]:
    files: list[Path] = []
    for d in (swmf_root / "Param", swmfsolar_root / "Param" if swmfsolar_root else None):
        if d is None or not d.is_dir():
            continue
        for p in sorted(d.glob(_PARAM_GLOB)):
            _reject_if_run_dir(p)
            if not p.is_file():
                continue
            # skip non-PARAM artifacts colocated in the dir
            if p.name.endswith(".dat") or p.name.endswith(".in"):
                if p.name not in {"FDIPS.in", "HARMONICS.in"}:
                    # PARAM.in.* is what we want; bare PARAM.in is also acceptable
                    pass
            files.append(p)
    return files


# ---------------------------------------------------------------------------
# Set-ops
# ---------------------------------------------------------------------------

# Commands that are global control / SWMF runtime structure, not physics. The
# miner reports them but the required-set is more useful when these are
# separated.
_STRUCTURAL_COMMANDS = {
    "#BEGIN_COMP", "#END_COMP", "#RUN", "#END", "#STOP", "#INCLUDE",
    "#DESCRIPTION", "#ECHO", "#TEST",
}


def _required_commands(files: list[ParamFile], threshold: float) -> tuple[list[str], list[str]]:
    """Return (commands appearing in >= threshold fraction, commands in 100%)."""
    if not files:
        return [], []
    counts: Counter[str] = Counter()
    for pf in files:
        for cmd in pf.commands_all:
            counts[cmd] += 1
    n = len(files)
    required: list[str] = []
    intersection: list[str] = []
    for cmd, c in sorted(counts.items()):
        if cmd in _STRUCTURAL_COMMANDS:
            continue
        frac = c / n
        if frac >= 1.0:
            intersection.append(cmd)
        if frac >= threshold:
            required.append(cmd)
    return required, intersection


def _value_envelope(files: list[ParamFile]) -> dict[str, dict[str, Any]]:
    """Per-command, per-key envelope across the archetype group.

    Returns a dict keyed by command, each value a dict keyed by parameter key:
      {
        "min": <num | None>,
        "max": <num | None>,
        "mode": <value>,
        "values_seen": [...sample...],
        "files": <count of files where this key was seen>,
      }
    """
    # cmd -> key -> list[(value, file_index)]
    per_cmd: dict[str, dict[str, list[tuple[Any, int]]]] = defaultdict(lambda: defaultdict(list))
    for idx, pf in enumerate(files):
        for block in pf.blocks:
            cmd = str(block.get("command", "")).upper()
            if not cmd or cmd in _STRUCTURAL_COMMANDS:
                continue
            for row in block.get("rows", []):
                setting = _row_to_param_setting(str(row))
                if setting is None:
                    continue
                key = str(setting.get("key", "")).rstrip("^?")
                value = setting.get("value")
                per_cmd[cmd][key].append((value, idx))

    envelope: dict[str, dict[str, Any]] = {}
    for cmd, keys in per_cmd.items():
        envelope[cmd] = {}
        for key, observations in keys.items():
            values = [v for v, _ in observations]
            numeric: list[float] = []
            for v in values:
                if isinstance(v, bool):
                    continue
                if isinstance(v, (int, float)):
                    numeric.append(float(v))
            file_count = len({idx for _, idx in observations})
            mode_counter = Counter(repr(v) for v in values)
            mode_repr, _ = mode_counter.most_common(1)[0]
            mode_value = next(v for v in values if repr(v) == mode_repr)
            entry: dict[str, Any] = {
                "min": min(numeric) if numeric else None,
                "max": max(numeric) if numeric else None,
                "mode": mode_value,
                "values_seen": sorted({repr(v) for v in values})[:8],
                "files": file_count,
                "samples": len(observations),
            }
            envelope[cmd][key] = entry
    return envelope


# ---------------------------------------------------------------------------
# Equation-module mining
# ---------------------------------------------------------------------------

_NAMEVAR_RE = re.compile(
    r"NameVar_V\s*\([^)]*\)\s*=\s*\[(?P<body>.*?)\]",
    re.DOTALL,
)
_QUOTED_RE = re.compile(r"'([^']+)'")
_NAMEEQUATION_RE = re.compile(r"NameEquation\s*=\s*'([^']*)'")

_VAR_TO_COMMANDS: dict[str, list[str]] = {
    # Variables → SWMF commands that the equation set requires when present.
    # The mapping is hand-curated; extending it is the principal lever for
    # binding new equation modules into the operational PARAM checklist.
    #
    # Ehot is the carrier of suprathermal electron energy in the AWSoM family.
    # When it is present in the state vector, the equation set expects the full
    # Spitzer + collisionless heat-flux stack with semi-implicit parallel
    # conduction. The five-command block is the operational signature; missing
    # any one of them is a configuration error rather than a physics choice.
    "Ehot": [
        "#HEATCONDUCTION",
        "#HEATFLUXREGION",
        "#HEATFLUXCOLLISIONLESS",
        "#SEMIIMPLICIT",
        "#SEMIKRYLOV",
    ],
    "Ppar": ["#ANISOTROPICPRESSURE"],
    "Pe": ["#PLASMA"],  # electron pressure ratio is configured via #PLASMA
    # Wave-energy variables (I01, I02, etc.) → AWSoM coronal heating stack.
    "I01": ["#POYNTINGFLUX", "#CORONALHEATING", "#HEATPARTITIONING"],
    "I02": ["#POYNTINGFLUX", "#CORONALHEATING", "#HEATPARTITIONING"],
    "Erad": ["#RADIATIVECOOLING"],
}


def _mine_equation_modules(swmf_root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for parent in ("GM/BATSRUS/srcEquation", "SC/BATSRUS/srcEquation"):
        d = swmf_root / parent
        if not d.is_dir():
            continue
        for f in sorted(d.glob("ModEquation*.f90")):
            name = f.stem.removeprefix("ModEquation")
            if name in out:
                continue
            try:
                text = _read_text(f)
            except OSError:
                continue
            name_eq_match = _NAMEEQUATION_RE.search(text)
            description = name_eq_match.group(1) if name_eq_match else None
            vars_list: list[str] = []
            for m in _NAMEVAR_RE.finditer(text):
                body = m.group("body")
                for q in _QUOTED_RE.finditer(body):
                    token = q.group(1).strip()
                    if token and token not in vars_list:
                        # Skip wildcards like 'I?? ' produced by an implied do-loop.
                        if "?" in token:
                            continue
                        vars_list.append(token)
            required_cmds: list[str] = []
            for var in vars_list:
                for cmd in _VAR_TO_COMMANDS.get(var, []):
                    if cmd not in required_cmds:
                        required_cmds.append(cmd)
            # AWSoM heating stack is keyed by I0n wave bins; if any I## present, include.
            if any(re.match(r"^I\d+$", v) for v in vars_list):
                for cmd in ("#POYNTINGFLUX", "#CORONALHEATING", "#HEATPARTITIONING"):
                    if cmd not in required_cmds:
                        required_cmds.append(cmd)
            out[name] = {
                "description": description,
                "required_vars": vars_list,
                "required_commands": required_cmds,
                "source_module": str(f.relative_to(swmf_root)),
            }
    return out


# ---------------------------------------------------------------------------
# YAML emission
# ---------------------------------------------------------------------------

_PROVENANCE_VERSION = 1


def _yaml_dump(data: Any) -> str:
    return yaml.safe_dump(
        data,
        sort_keys=True,
        default_flow_style=False,
        allow_unicode=True,
        width=120,
    )


def _emit_required(
    archetype_id: str,
    files: list[ParamFile],
    required: list[str],
    intersection: list[str],
    threshold: float,
) -> str:
    payload = {
        "archetype": archetype_id,
        "provenance": f"mined:intersection_{archetype_id}_v{_PROVENANCE_VERSION}",
        "threshold": threshold,
        "n_corpus_files": len(files),
        "corpus_files": sorted(pf.name for pf in files),
        "required_commands": sorted(required),
        "strict_intersection": sorted(intersection),
        "note": (
            "required_commands: commands present in >= threshold fraction of corpus files. "
            "strict_intersection: commands present in 100% of corpus files. "
            "Use as a corpus-diff target when authoring a new PARAM for this archetype."
        ),
    }
    header = (
        f"# Auto-generated by scripts/mine_param_corpus.py. Do not hand-edit.\n"
        f"# Archetype: {archetype_id}\n"
        f"# Required-command intersection from {len(files)} shipped PARAMs\n"
        f"# (threshold={threshold:.2f}). Provenance: mined:intersection_{archetype_id}_v{_PROVENANCE_VERSION}.\n"
    )
    return header + _yaml_dump(payload)


def _emit_typical(
    archetype_id: str,
    files: list[ParamFile],
    envelope: dict[str, dict[str, Any]],
) -> str:
    payload = {
        "archetype": archetype_id,
        "provenance": f"mined:envelope_{archetype_id}_v{_PROVENANCE_VERSION}",
        "n_corpus_files": len(files),
        "envelope": envelope,
    }
    header = (
        f"# Auto-generated by scripts/mine_param_corpus.py. Do not hand-edit.\n"
        f"# Archetype: {archetype_id}\n"
        f"# Per-command, per-key value envelopes across {len(files)} shipped PARAMs.\n"
        f"# Provenance: mined:envelope_{archetype_id}_v{_PROVENANCE_VERSION}.\n"
    )
    return header + _yaml_dump(payload)


def _emit_equation_set(modules: dict[str, dict[str, Any]]) -> str:
    payload = {
        "provenance": f"mined:equation_set_v{_PROVENANCE_VERSION}",
        "note": (
            "Mapping from equation module (Config.pl -o=COMP:e=<Name>) to the SWMF "
            "commands the module's variable set implies. Var→command mapping is "
            "hand-coded in scripts/mine_param_corpus.py (_VAR_TO_COMMANDS); extending "
            "the map is the principal maintenance lever as new equation modules ship."
        ),
        "modules": modules,
    }
    header = (
        "# Auto-generated by scripts/mine_param_corpus.py. Do not hand-edit.\n"
        "# Equation-module → required-command mapping.\n"
    )
    return header + _yaml_dump(payload)


def _emit_report(
    archetypes: list[dict[str, Any]],
    grouped: dict[str, list[ParamFile]],
    unmatched: list[ParamFile],
    skipped: list[tuple[str, str]],
    threshold: float,
) -> str:
    lines: list[str] = []
    lines.append("# Corpus mining report\n")
    lines.append(f"Threshold (fraction of files for command to count as required): "
                 f"**{threshold:.2f}**\n")
    lines.append("## Archetype coverage\n")
    lines.append("| Archetype | Files | File names |")
    lines.append("| --- | ---: | --- |")
    for arch in archetypes:
        aid = str(arch["id"])
        members = grouped.get(aid, [])
        names = ", ".join(sorted(pf.name for pf in members)) or "*(none)*"
        lines.append(f"| `{aid}` | {len(members)} | {names} |")
    lines.append("")
    if unmatched:
        lines.append("## Unmatched PARAMs\n")
        lines.append("These were enumerated but no archetype matched. Either extend "
                     "`archetypes.yaml` or accept that they fall outside the catalog.\n")
        for pf in unmatched:
            lines.append(f"- `{pf.name}`:")
            for note in pf.classify_notes:
                lines.append(f"  - {note}")
        lines.append("")
    if skipped:
        lines.append("## Skipped files (parse error)\n")
        for path, reason in skipped:
            lines.append(f"- `{path}` — {reason}")
        lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _default_output_dir() -> Path:
    return (
        _REPO_ROOT
        / "src"
        / "agent_assets"
        / "skills"
        / "support"
        / "swmf-params"
        / "rules"
        / "defaults"
        / "mined"
    )


def _default_rules_dir() -> Path:
    return (
        _REPO_ROOT
        / "src"
        / "agent_assets"
        / "skills"
        / "support"
        / "swmf-params"
        / "rules"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--swmf-root", default=None,
                        help="Override SWMF source root (default: resolve from env/cwd).")
    parser.add_argument("--swmfsolar-root", default=None,
                        help="Override SWMFSOLAR root (default: sibling of SWMF_ROOT).")
    parser.add_argument("--output-dir", default=str(_default_output_dir()),
                        help="Where to emit mined YAML and the mining report.")
    parser.add_argument("--rules-dir", default=str(_default_rules_dir()),
                        help="Where to find archetypes.yaml.")
    parser.add_argument("--threshold", type=float, default=0.8,
                        help="Fraction of corpus files a command must appear in to count as "
                             "required (default: 0.8).")
    args = parser.parse_args(argv)

    if args.swmf_root:
        swmf_path = Path(args.swmf_root).expanduser().resolve()
    else:
        resolution = resolve_swmf_root()
        if not resolution.ok or not resolution.swmf_root_resolved:
            print("could not resolve SWMF root; pass --swmf-root", file=sys.stderr)
            return 2
        swmf_path = Path(resolution.swmf_root_resolved)

    if args.swmfsolar_root:
        swmfsolar_path: Path | None = Path(args.swmfsolar_root).expanduser().resolve()
    else:
        candidate = swmf_path.parent / "SWMFSOLAR"
        swmfsolar_path = candidate if candidate.is_dir() else None

    if swmfsolar_path is not None:
        _reject_if_run_dir(swmfsolar_path)

    rules_dir = Path(args.rules_dir).resolve()
    archetypes = _load_archetypes(rules_dir)

    files = _enumerate_param_files(swmf_path, swmfsolar_path)
    print(f"corpus: {len(files)} PARAM files "
          f"(SWMF/Param + SWMFSOLAR/Param)", file=sys.stderr)

    skipped: list[tuple[str, str]] = []
    parsed_files: list[ParamFile] = []
    for path in files:
        pf = _parse_param_file(path)
        if pf is None:
            skipped.append((str(path), "read or parse error"))
            continue
        parsed_files.append(pf)

    grouped: dict[str, list[ParamFile]] = defaultdict(list)
    unmatched: list[ParamFile] = []
    for pf in parsed_files:
        arch_id = _classify(pf, archetypes)
        pf.archetype_id = arch_id
        if arch_id is None:
            unmatched.append(pf)
        else:
            grouped[arch_id].append(pf)

    # Prepare output dir.
    out_dir = Path(args.output_dir).resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Per-archetype emission.
    for arch in archetypes:
        aid = str(arch["id"])
        members = grouped.get(aid, [])
        if not members:
            continue
        required, intersection = _required_commands(members, args.threshold)
        envelope = _value_envelope(members)

        (out_dir / f"{aid}_required.yaml").write_text(
            _emit_required(aid, members, required, intersection, args.threshold),
            encoding="utf-8",
        )
        (out_dir / f"{aid}_typical.yaml").write_text(
            _emit_typical(aid, members, envelope),
            encoding="utf-8",
        )

    # Equation modules.
    modules = _mine_equation_modules(swmf_path)
    (out_dir / "equation_set_required.yaml").write_text(
        _emit_equation_set(modules),
        encoding="utf-8",
    )

    # Report.
    report = _emit_report(archetypes, grouped, unmatched, skipped, args.threshold)
    (out_dir / "mining_report.md").write_text(report, encoding="utf-8")

    # Summary to stderr.
    print(f"emitted {len([a for a in archetypes if grouped.get(str(a['id']))])} "
          f"archetype-required YAMLs to {out_dir}", file=sys.stderr)
    print(f"{len(modules)} equation modules mapped", file=sys.stderr)
    print(f"{len(unmatched)} unmatched, {len(skipped)} skipped (see mining_report.md)",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
