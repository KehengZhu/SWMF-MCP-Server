from __future__ import annotations

import re
from typing import Any

COMPONENTMAP_ROW = re.compile(
    r"^(?P<id>[A-Z0-9]{2})\s+"
    r"(?P<proc0>-?\d+)\s+"
    r"(?P<procend>-?\d+)\s+"
    r"(?P<stride>-?\d+)"
    r"(?:\s+(?P<nthread>-?\d+))?"
    r"(?:\s+.*)?$"
)


def resolve_rank(value: int, nproc: int) -> int:
    return value if value >= 0 else nproc + value


def expand_component_map_rows(rows: list[dict[str, Any]], nproc: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    used_ranks: dict[int, str] = {}

    for row in rows:
        comp = row["component"]
        proc0 = resolve_rank(row["proc0"], nproc)
        procend = resolve_rank(row["procend"], nproc)
        stride = row["stride"]

        if stride == 0:
            errors.append(f"{comp}: stride cannot be 0.")
            continue

        if not (0 <= proc0 < nproc):
            errors.append(f"{comp}: resolved Proc0={proc0} is outside [0, {nproc - 1}].")
            continue

        if not (0 <= procend < nproc):
            errors.append(f"{comp}: resolved ProcEnd={procend} is outside [0, {nproc - 1}].")
            continue

        if stride < 0:
            warnings.append(
                f"{comp}: negative stride is valid in SWMF/OpenMP layouts, but this prototype only does a shallow check."
            )
            continue

        if proc0 > procend:
            errors.append(f"{comp}: Proc0={proc0} is greater than ProcEnd={procend}.")
            continue

        ranks = list(range(proc0, procend + 1, stride))
        if not ranks:
            errors.append(f"{comp}: no ranks selected by Proc0/ProcEnd/Stride.")
            continue

        for rank in ranks:
            previous = used_ranks.get(rank)
            if previous and previous != comp:
                warnings.append(
                    f"Rank {rank} is used by both {previous} and {comp}. Overlap can be intentional in SWMF, so this is only a warning."
                )
            used_ranks[rank] = comp

    return errors, warnings
