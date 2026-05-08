"""Evaluator for `physical_constraints.yaml` against a parsed PARAM.in.

Pure if/then evaluation. No advice fields, no MCP-side judgment. The user grows the rule
set in the YAML; new predicate types are the only changes that touch this code.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - import error surface
    yaml = None  # type: ignore[assignment]


# Path is resolved relative to the repo root: src/agent_assets/skills/support/swmf-params/rules
DEFAULT_RULES_PATH = (
    Path(__file__).resolve().parents[2]
    / "agent_assets"
    / "skills"
    / "support"
    / "swmf-params"
    / "rules"
    / "physical_constraints.yaml"
)


_VALID_SEVERITIES = frozenset({"block", "warn", "info"})


def load_rules(path: Path | str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return (rules, meta). meta carries `path` and `error` keys for the caller."""
    rules_path = Path(path) if path is not None else DEFAULT_RULES_PATH
    meta: dict[str, Any] = {"path": str(rules_path), "error": None}

    if yaml is None:
        meta["error"] = "PyYAML not installed; rule evaluation disabled."
        return [], meta

    if not rules_path.is_file():
        meta["error"] = f"Rules file not found at {rules_path}."
        return [], meta

    try:
        text = rules_path.read_text(encoding="utf-8")
    except OSError as exc:
        meta["error"] = f"Could not read rules file: {exc}"
        return [], meta

    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        meta["error"] = f"YAML parse error: {exc}"
        return [], meta

    if not isinstance(loaded, list):
        meta["error"] = "Rules file must contain a top-level list of rule entries."
        return [], meta

    rules: list[dict[str, Any]] = []
    for entry in loaded:
        if isinstance(entry, dict):
            rules.append(entry)
    return rules, meta


def _normalize_command(name: str | None) -> str | None:
    if name is None:
        return None
    name = str(name).strip()
    if not name:
        return None
    if not name.startswith("#"):
        name = "#" + name
    return name.upper()


def _command_blocks_for(command: str | None, blocks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if command is None:
        return list(blocks)
    target = _normalize_command(command)
    return [b for b in blocks if str(b.get("command", "")).upper() == target]


def _row_settings(blocks: Iterable[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Return a list of (block, parsed_setting) pairs.

    Imports `_row_to_param_setting` lazily to avoid a circular import on module load.
    """
    from ..tools.inspect_artifact import _row_to_param_setting  # local to break cycle

    out: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for block in blocks:
        for row in block.get("rows", []):
            setting = _row_to_param_setting(str(row))
            if setting is not None:
                out.append((block, setting))
    return out


def _coerce_to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _evaluate_predicate(
    predicate: Any,
    blocks: list[dict[str, Any]],
    commands_present: set[str],
    *,
    session_filter: int | None = None,
) -> tuple[bool, dict[str, Any]]:
    """Return (holds, evidence). Evidence is a small dict explaining the result."""
    if predicate is None:
        return True, {"why": "empty predicate"}

    if isinstance(predicate, str):
        return _evaluate_predicate({"command_present": predicate}, blocks, commands_present, session_filter=session_filter)

    if not isinstance(predicate, dict):
        return False, {"why": f"unrecognized predicate shape: {predicate!r}"}

    # Predicate dict may carry one or more predicates; evaluate as AND.
    overall = True
    evidence: dict[str, Any] = {}
    for key, value in predicate.items():
        local_blocks = blocks
        if session_filter is not None:
            local_blocks = [b for b in blocks if b.get("session_index") == session_filter]

        if key == "command_present" or key == "command_co_occurs_with":
            target = _normalize_command(str(value))
            holds = target in commands_present
            evidence[key] = {"value": target, "holds": holds}
            overall = overall and holds
        elif key == "command_absent" or key == "command_excludes":
            target = _normalize_command(str(value))
            holds = target not in commands_present
            evidence[key] = {"value": target, "holds": holds}
            overall = overall and holds
        elif key == "command_order_before":
            if not isinstance(value, dict):
                return False, {"why": "command_order_before expects a dict {first, second}"}
            first_norm = _normalize_command(value.get("first"))
            second_norm = _normalize_command(value.get("second"))
            first_block = next(
                (b for b in local_blocks if str(b.get("command", "")).upper() == first_norm),
                None,
            )
            second_block = next(
                (b for b in local_blocks if str(b.get("command", "")).upper() == second_norm),
                None,
            )
            if first_block is None or second_block is None:
                holds = False
                evidence[key] = {
                    "first": first_norm,
                    "second": second_norm,
                    "holds": False,
                    "why": "one or both commands absent",
                }
            else:
                holds = int(first_block.get("line_number", 0)) < int(second_block.get("line_number", 0))
                evidence[key] = {
                    "first": first_norm,
                    "second": second_norm,
                    "first_line": first_block.get("line_number"),
                    "second_line": second_block.get("line_number"),
                    "holds": holds,
                }
            overall = overall and holds
        elif key in {"param_equals", "param_in_range", "param_in_set"}:
            holds, sub_evidence = _evaluate_param_predicate(key, value, local_blocks)
            evidence[key] = sub_evidence
            overall = overall and holds
        elif key == "any_of":
            if not isinstance(value, list):
                return False, {"why": "any_of expects a list of predicate dicts"}
            sub_holds = False
            sub_evidences: list[dict[str, Any]] = []
            for sub in value:
                holds, sub_evidence = _evaluate_predicate(
                    sub, blocks, commands_present, session_filter=session_filter
                )
                sub_evidences.append(sub_evidence)
                if holds:
                    sub_holds = True
            evidence[key] = {"holds": sub_holds, "candidates": sub_evidences}
            overall = overall and sub_holds
        elif key == "all_of":
            if not isinstance(value, list):
                return False, {"why": "all_of expects a list of predicate dicts"}
            sub_holds = True
            sub_evidences = []
            for sub in value:
                holds, sub_evidence = _evaluate_predicate(
                    sub, blocks, commands_present, session_filter=session_filter
                )
                sub_evidences.append(sub_evidence)
                if not holds:
                    sub_holds = False
            evidence[key] = {"holds": sub_holds, "candidates": sub_evidences}
            overall = overall and sub_holds
        elif key == "session_index":
            # Not a leaf predicate; consumed at rule scope only.
            evidence[key] = {"value": value, "holds": True}
        else:
            evidence[key] = {"holds": False, "why": f"unknown predicate key: {key}"}
            overall = False
    return overall, evidence


def _evaluate_param_predicate(
    kind: str,
    spec: Any,
    blocks: list[dict[str, Any]],
) -> tuple[bool, dict[str, Any]]:
    if not isinstance(spec, dict):
        return False, {"why": f"{kind} expects a dict spec"}
    name = spec.get("name")
    command = spec.get("command")
    if not isinstance(name, str):
        return False, {"why": f"{kind} requires 'name' string"}

    candidate_blocks = _command_blocks_for(command if isinstance(command, str) else None, blocks)
    rows = _row_settings(candidate_blocks)

    def _strip_marker(key: str) -> str:
        return key.rstrip("^?").strip()

    matched_rows = [(b, s) for (b, s) in rows if _strip_marker(str(s.get("key", ""))) == name]
    if not matched_rows:
        # param-* rules are vacuously satisfied when the named parameter is absent.
        # If the user wants to require presence, they should add a `command_present` rule.
        return True, {
            "name": name,
            "command": _normalize_command(command if isinstance(command, str) else None),
            "holds": True,
            "why": "named parameter not present; rule treated as not-applicable",
            "skipped": True,
        }

    holds_any = False
    observed_values: list[Any] = []
    evidence_lines: list[int] = []

    for block, setting in matched_rows:
        observed = setting.get("value")
        observed_values.append(observed)
        evidence_lines.append(int(block.get("line_number", 0)) + 1)
        if kind == "param_equals":
            expected = spec.get("value")
            if isinstance(expected, bool) or isinstance(observed, bool):
                if bool(observed) == bool(expected):
                    holds_any = True
            else:
                if observed == expected:
                    holds_any = True
                else:
                    obs_f = _coerce_to_float(observed)
                    exp_f = _coerce_to_float(expected)
                    if obs_f is not None and exp_f is not None and obs_f == exp_f:
                        holds_any = True
        elif kind == "param_in_range":
            obs_f = _coerce_to_float(observed)
            lo = _coerce_to_float(spec.get("min"))
            hi = _coerce_to_float(spec.get("max"))
            if obs_f is None:
                continue
            in_lo = lo is None or obs_f >= lo
            in_hi = hi is None or obs_f <= hi
            if in_lo and in_hi:
                holds_any = True
        elif kind == "param_in_set":
            allowed = spec.get("values")
            if isinstance(allowed, list):
                str_observed = str(observed)
                # Allow numeric or string comparison
                allowed_str = [str(v) for v in allowed]
                if str_observed in allowed_str or observed in allowed:
                    holds_any = True
        else:
            return False, {"why": f"unknown param predicate {kind}"}

    return holds_any, {
        "name": name,
        "command": _normalize_command(command if isinstance(command, str) else None),
        "kind": kind,
        "spec": spec,
        "observed_values": observed_values,
        "evidence_lines": evidence_lines,
        "holds": holds_any,
    }


def evaluate_rules(
    rules: list[dict[str, Any]],
    command_blocks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Evaluate every rule whose `applies_when` matches; return violations.

    A "violation" is a rule whose `require` predicate did not hold. `severity` is
    propagated from the rule. Evidence is attached for every observed value.
    """
    commands_present: set[str] = {
        str(block.get("command", "")).upper() for block in command_blocks
    }

    violations: list[dict[str, Any]] = []

    for rule in rules:
        rule_id = str(rule.get("id") or "<unnamed>")
        severity = str(rule.get("severity") or "warn")
        if severity not in _VALID_SEVERITIES:
            severity = "warn"

        applies_when = rule.get("applies_when") or {}
        # Allow session_index to scope the rule (not the predicate).
        session_filter = None
        if isinstance(applies_when, dict):
            session_value = applies_when.get("session_index")
            if isinstance(session_value, int):
                session_filter = session_value

        applies, applies_evidence = _evaluate_predicate(
            applies_when,
            command_blocks,
            commands_present,
            session_filter=session_filter,
        )
        if not applies:
            continue

        require = rule.get("require")
        if require is None:
            continue
        holds, require_evidence = _evaluate_predicate(
            require,
            command_blocks,
            commands_present,
            session_filter=session_filter,
        )
        if holds:
            continue

        # Surface the most informative observed value if a param predicate fired.
        param_kind = next(
            (k for k in ("param_equals", "param_in_range", "param_in_set") if k in (require or {})),
            None,
        ) if isinstance(require, dict) else None
        observed_value: Any | None = None
        param_name: str | None = None
        command_label: str | None = None
        evidence_line: int | None = None
        expected_text: str | None = None

        if param_kind and isinstance(require, dict):
            param_evidence = require_evidence.get(param_kind, {}) or {}
            param_name = param_evidence.get("name")
            command_label = param_evidence.get("command")
            observed_list = param_evidence.get("observed_values") or []
            if observed_list:
                observed_value = observed_list[0]
            evidence_lines = param_evidence.get("evidence_lines") or []
            if evidence_lines:
                evidence_line = evidence_lines[0]
            spec = param_evidence.get("spec") or {}
            if param_kind == "param_in_range":
                expected_text = f"{spec.get('min')} <= {param_name} <= {spec.get('max')}"
            elif param_kind == "param_equals":
                expected_text = f"{param_name} == {spec.get('value')}"
            elif param_kind == "param_in_set":
                expected_text = f"{param_name} in {spec.get('values')}"

        if command_label is None and isinstance(require, dict):
            for cmd_key in ("command_present", "command_co_occurs_with", "command_absent", "command_excludes"):
                if cmd_key in require:
                    command_label = _normalize_command(str(require[cmd_key]))
                    if expected_text is None:
                        expected_text = f"{cmd_key}: {command_label}"
                    break

        violations.append({
            "rule_id": rule_id,
            "severity": severity,
            "command": command_label,
            "param_name": param_name,
            "observed_value": str(observed_value) if observed_value is not None else None,
            "expected": expected_text,
            "reason": str(rule.get("reason") or ""),
            "evidence_line": evidence_line,
            "applies_evidence": applies_evidence,
            "require_evidence": require_evidence,
        })

    return violations
