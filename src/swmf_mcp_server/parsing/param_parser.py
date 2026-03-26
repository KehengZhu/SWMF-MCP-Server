from __future__ import annotations

import re

from ..core.models import ParseResult, Session
from .component_map import COMPONENTMAP_ROW

_COMPONENT_BLOCK_BEGIN = re.compile(r"^#BEGIN_COMP\s+([A-Z0-9]{2})\s*$")
_COMPONENT_BLOCK_END = re.compile(r"^#END_COMP\s+([A-Z0-9]{2})\s*$")
_COMPONENT_SWITCH_ROW = re.compile(r"^([A-Z0-9]{2})\s+NameComp(?:\s+.*)?$")
_BOOL_ROW = re.compile(r"^(T|F|\.true\.|\.false\.)\b", re.IGNORECASE)


def _non_comment_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped.startswith("!"):
            lines.append("")
            continue
        lines.append(line)
    return lines


def parse_param_text(param_text: str) -> ParseResult:
    lines = _non_comment_lines(param_text)
    sessions: list[Session] = [Session(index=1)]
    errors: list[str] = []
    warnings: list[str] = []

    current = sessions[-1]
    in_component_map = False
    pending_component_switch: str | None = None
    open_component_block: str | None = None

    for raw in lines:
        line = raw.strip()

        if not line:
            if in_component_map:
                in_component_map = False
            continue

        begin_match = _COMPONENT_BLOCK_BEGIN.match(line)
        if begin_match:
            comp = begin_match.group(1)
            if open_component_block is not None:
                errors.append(
                    f"Nested component blocks are not supported in this prototype: opened {open_component_block}, then saw {comp}."
                )
            open_component_block = comp
            current.component_blocks.add(comp)
            current.commands.append("#BEGIN_COMP")
            continue

        end_match = _COMPONENT_BLOCK_END.match(line)
        if end_match:
            comp = end_match.group(1)
            if open_component_block != comp:
                errors.append(
                    f"Mismatched #END_COMP {comp}; currently open block is {open_component_block!r}."
                )
            open_component_block = None
            current.commands.append("#END_COMP")
            continue

        if line.startswith("#"):
            in_component_map = False
            current.commands.append(line.split()[0])

            if line.upper() == "#COMPONENTMAP":
                in_component_map = True
                continue

            if line.upper() == "#COMPONENT":
                pending_component_switch = "expect_component_name"
                continue

            if line.upper() == "#STOP":
                current.stop_present = True
                continue

            if line.upper() == "#RUN":
                if open_component_block is not None:
                    errors.append(
                        f"Session {current.index} ended with #RUN while component block {open_component_block} was still open."
                    )
                    open_component_block = None
                current = Session(index=len(sessions) + 1)
                sessions.append(current)
                continue

            if line.upper() == "#END":
                break

            continue

        if in_component_map:
            match = COMPONENTMAP_ROW.match(line)
            if match:
                row = {
                    "component": match.group("id"),
                    "proc0": int(match.group("proc0")),
                    "procend": int(match.group("procend")),
                    "stride": int(match.group("stride")),
                    "nthread": int(match.group("nthread")) if match.group("nthread") is not None else None,
                    "raw": line,
                }
                current.component_map_rows.append(row)
            else:
                warnings.append(f"Could not parse #COMPONENTMAP row: {line}")
            continue

        if pending_component_switch == "expect_component_name":
            match = _COMPONENT_SWITCH_ROW.match(line)
            if match:
                pending_component_switch = match.group(1)
            else:
                warnings.append(f"Could not parse component name after #COMPONENT: {line}")
                pending_component_switch = None
            continue

        if pending_component_switch and pending_component_switch != "expect_component_name":
            bool_match = _BOOL_ROW.match(line)
            if bool_match:
                use_comp = bool_match.group(1).lower() in {"t", ".true."}
                current.switched_components.append((pending_component_switch, use_comp))
            else:
                warnings.append(
                    f"Could not parse logical enable/disable row for component {pending_component_switch}: {line}"
                )
            pending_component_switch = None
            continue

    if open_component_block is not None:
        errors.append(f"Unclosed component block: #BEGIN_COMP {open_component_block}")

    return ParseResult(sessions=sessions, errors=errors, warnings=warnings)
