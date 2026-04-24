"""Public API tool: get_evidence.

Purpose
-------
Retrieve grounded local evidence for a query. This is the main retrieval tool.
All evidence is local (source files, PARAM.XML, catalogs, knowledge index).
The caller specifies a query and optional retrieval mode; the server routes
internally across keyword, semantic, or hybrid backends. Workflow discovery is
handled as a `task_type` use case rather than a separate tool.

Internal backends (hidden from caller)
---------------------------------------
- keyword search (BM25 / catalog)
- semantic search (embedding index)
- hybrid (default: keyword + semantic, reranked)
- symbol lookup
- catalog lookup

Output contract
---------------
{
  "summary": str,
  "evidence": list[EvidenceItem],
  "provenance": {"mode_used": str, "scope": list[str]},
  "uncertainty": {"known_unknowns": list[str]}
}

EvidenceItem shape
------------------
{
  "type": "param_spec" | "code" | "doc" | "example" | "coupling" | "idl",
  "path": str,
  "snippet": str,
  "score": float,
  "metadata": {
    "kind": str,
    "relative_path": str,
    "why_relevant": str
  }
}

Example request
---------------
{
  "query": "DoCoupleGMIE",
  "mode": "hybrid",
  "scope": ["GM", "IE"],
  "top_k": 8,
  "goal": "find definition and usage"
}

Example response
----------------
{
  "summary": "4 relevant evidence items found for DoCoupleGMIE",
  "evidence": [
    {"type": "param_spec", "path": "PARAM.XML", "snippet": "...", "score": 0.91},
    {"type": "code", "path": "GM/src/ModUser.f90", "snippet": "...", "score": 0.87}
  ],
  "provenance": {"mode_used": "hybrid", "scope": ["GM", "IE"]},
  "uncertainty": {"known_unknowns": ["runtime behavior not inspected"]}
}

Field semantics
---------------
query   : Required. The search query, token, symbol name, or natural-language question.
mode    : Optional retrieval mode.
          "hybrid"   — keyword + semantic, reranked (default).
          "keyword"  — BM25 / catalog / exact match. Use when query contains precise tokens.
          "semantic" — embedding similarity only.
scope   : Optional list of SWMF component IDs to restrict retrieval (e.g. ["GM","IE"]).
top_k   : Optional max number of evidence items to return. Default 8, max 100.
goal    : Optional freeform description of what the agent is trying to accomplish.
          Used to improve reranking and snippet selection.
task_type: Optional workflow hint. Use "lookup" for ordinary evidence retrieval,
          or "configuration", "build", "run", "analysis" for workflow evidence.
module  : Optional component hint used when collecting workflow evidence.
swmf_root : Optional explicit SWMF source root path.
run_dir   : Optional run directory used for root resolution.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ._helpers import resolve_root_or_failure, with_root
from ._router import run_evidence_search
from ._workflow import discover_workflow_entrypoints
from ..reference import explain_idl_procedure_for_root, list_idl_procedures_for_root

_VALID_MODES = frozenset({"hybrid", "keyword", "semantic"})
_VALID_TASK_TYPES = frozenset({"lookup", "configuration", "build", "run", "analysis"})
_DEFAULT_TOP_K = 8
_MAX_TOP_K = 100
_IDL_TOKEN_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_]*\b")
_IDL_KNOWN_NAMES = frozenset({
    "animate_data",
    "plot_data",
    "plot_func",
    "plot_log",
    "plot_log_data",
    "read_data",
    "read_log_data",
    "show_data",
    "show_log_data",
})
_IDL_GENERIC_TOKENS = frozenset({
    "all",
    "and",
    "category",
    "data",
    "detail",
    "entry",
    "entrypoint",
    "entrypoints",
    "for",
    "function",
    "functions",
    "guidance",
    "how",
    "idl",
    "list",
    "macro",
    "macros",
    "mode",
    "plot",
    "plotting",
    "procedure",
    "procedures",
    "read",
    "signature",
    "signatures",
    "usage",
    "use",
    "visualization",
    "which",
})
_IDL_MANUAL_TOPICS: dict[str, tuple[int, int, str]] = {
    "setup": (72, 118, "IDL setup, IDL_PATH, IDL_STARTUP, idlrc, retall"),
    "startup": (72, 118, "IDL setup, IDL_PATH, IDL_STARTUP, idlrc, retall"),
    "read_data": (120, 170, "read_data snapshot header and arrays"),
    "show_data": (360, 395, "show_data quick read-and-plot workflow"),
    "plot_data": (360, 418, "plot_data function and plotmode prompts"),
    "func": (422, 455, "func strings, variables, funcdef names, expressions, vector pairs"),
    "funcdef": (958, 1005, "funcdef.pro function definition rules"),
    "plotmode": (456, 585, "plotmode strings for 1D, scalar 2D, vector, overplot, modifiers"),
    "transform": (170, 276, "regular, polar, unpolar, sphere, and custom transforms"),
    "slice": (930, 958, "slice_data and slice_data_restore for structured 3D data"),
    "slicing": (930, 958, "slice_data and slice_data_restore for structured 3D data"),
    "cut": (586, 744, "domain selection with ranges, cut, grid, triplet, quadruplet, velpos, rcut"),
    "domain": (586, 744, "domain selection with ranges, cut, grid, triplet, quadruplet, velpos, rcut"),
    "log": (1046, 1134, "read_log_data and plot_log_data log workflows"),
    "logs": (1046, 1134, "read_log_data and plot_log_data log workflows"),
    "read_log_data": (1046, 1098, "read_log_data log arrays and names"),
    "plot_log_data": (1099, 1134, "plot_log_data and show_log_data"),
    "show_log_data": (1099, 1134, "plot_log_data and show_log_data"),
    "animate_data": (788, 930, "animate_data multi-frame, comparison, movie storage"),
    "animation": (788, 930, "animate_data multi-frame, comparison, movie storage"),
    "compare": (780, 856, "multi-file plotting and comparison"),
    "comparison": (780, 856, "multi-file plotting and comparison"),
    "export": (1198, 1250, "PostScript, PDF, frame, and video export"),
    "save": (1198, 1250, "PostScript, PDF, frame, and video export"),
    "script": (1248, 1295, "IDL script and procedure reuse"),
    "scripts": (1248, 1295, "IDL script and procedure reuse"),
}
_IDL_ENTRYPOINT_PRIORITY = [
    "read_data",
    "show_data",
    "plot_data",
    "animate_data",
    "read_log_data",
    "plot_log_data",
    "show_log_data",
    "slice_data",
    "slice_data_restore",
    "plot_func",
]


def _normalize_task_type(task_type: str | None) -> str:
    if task_type in _VALID_TASK_TYPES:
        return task_type
    return "lookup"


def _normalize_module(module: str | None) -> str | None:
    value = (module or "").strip().upper()
    return value or None


def _append_unique_scope(scope: list[str], module: str | None) -> list[str]:
    resolved = [item.upper() for item in scope]
    if module and module not in resolved:
        resolved.append(module)
    return resolved


def _truncate(text: str, max_chars: int = 300) -> str:
    stripped = text.strip()
    if len(stripped) <= max_chars:
        return stripped
    return stripped[:max_chars] + "..."


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _relative_path(root: Path, candidate_path: str) -> str:
    candidate = Path(candidate_path)
    try:
        if candidate.is_absolute():
            return str(candidate.resolve().relative_to(root.resolve()))
        return str(candidate)
    except Exception:
        return str(candidate)


def _looks_like_idl_request(query: str, goal: str) -> bool:
    text = f"{query} {goal}".lower()
    if "idl" in text or ".pro" in text:
        return True
    if any(name in text for name in _IDL_KNOWN_NAMES):
        return True
    if any(topic in text for topic in ("funcdef", "plotmode", "slice_data", "savemovie")):
        return True
    return "procedure" in text and any(term in text for term in ("plot", "read", "show", "animate"))


def _idl_list_intent(query: str, goal: str) -> bool:
    text = f"{query} {goal}".lower()
    return any(term in text for term in ("list", "which", "inventory", "entrypoint", "entry point", "all"))


def _infer_idl_category(query: str, goal: str) -> str | None:
    text = f"{query} {goal}".lower()
    if any(term in text for term in ("magnetogram", "fits")):
        return "magnetogram"
    if any(term in text for term in ("animate", "animation", "movie")):
        return "animation"
    if any(term in text for term in ("read", "logfile", "log file", "snapshot")) and "plot" not in text:
        return "data_reading"
    if any(term in text for term in ("plot", "show", "visual", "contour", "stream", "vector")):
        return "plotting"
    return None


def _idl_name_candidates(query: str, goal: str) -> list[str]:
    text = f"{query} {goal}"
    candidates: list[str] = []
    for token in _IDL_TOKEN_RE.findall(text):
        lowered = token.lower()
        if lowered in _IDL_KNOWN_NAMES or ("_" in lowered and lowered not in _IDL_GENERIC_TOKENS):
            candidates.append(lowered)
    return list(dict.fromkeys(candidates))


def _manual_topic_candidates(query: str, goal: str) -> list[str]:
    text = f"{query} {goal}".lower()
    candidates: list[str] = []
    for topic in _IDL_MANUAL_TOPICS:
        if re.search(rf"(?<![a-z0-9_]){re.escape(topic)}(?![a-z0-9_])", text):
            candidates.append(topic)
    if "plot mode" in text and "plotmode" not in candidates:
        candidates.append("plotmode")
    if "function string" in text and "func" not in candidates:
        candidates.append("func")
    return list(dict.fromkeys(candidates))


def _read_doc_lines(path: Path, start_line: int, end_line: int) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    start = max(1, start_line)
    end = min(len(lines), end_line)
    return "\n".join(lines[start - 1:end])


def _manual_topic_to_evidence(root: Path, topic: str) -> dict[str, Any] | None:
    doc_path = _repo_root() / "docs" / "idl.md"
    if topic not in _IDL_MANUAL_TOPICS or not doc_path.is_file():
        return None
    start_line, end_line, why = _IDL_MANUAL_TOPICS[topic]
    snippet = _truncate(_read_doc_lines(doc_path, start_line, end_line), max_chars=900)
    if not snippet:
        return None
    return {
        "type": "idl",
        "path": str(doc_path),
        "snippet": snippet,
        "score": 1.0,
        "name": topic,
        "kind": "manual_section",
        "start_line": start_line,
        "metadata": {
            "kind": "idl_manual_section",
            "relative_path": _relative_path(root, str(doc_path)),
            "why_relevant": why,
            "topic": topic,
            "line_start": start_line,
            "line_end": end_line,
        },
    }


def _parse_funcdef_entries(funcdef_path: Path, limit: int = 40) -> list[dict[str, str]]:
    try:
        text = funcdef_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    entries: list[dict[str, str]] = []
    for match in re.finditer(r"\[\s*'([^']+)'\s*,\s*'([^']*)'\s*\]", text):
        entries.append({"name": match.group(1), "expression": match.group(2)})
        if len(entries) >= limit:
            break
    return entries


def _funcdef_inventory_evidence(root: Path) -> dict[str, Any] | None:
    funcdef_path = root / "share" / "IDL" / "General" / "funcdef.pro"
    entries = _parse_funcdef_entries(funcdef_path)
    if not entries:
        return None
    snippet = "\n".join(f"{item['name']} = {item['expression']}" for item in entries[:20])
    return {
        "type": "idl",
        "path": str(funcdef_path),
        "snippet": _truncate(snippet, max_chars=900),
        "score": 1.0,
        "name": "funcdef",
        "kind": "funcdef_inventory",
        "metadata": {
            "kind": "idl_funcdef_inventory",
            "relative_path": _relative_path(root, str(funcdef_path)),
            "why_relevant": "Parsed function names and expressions from share/IDL/General/funcdef.pro.",
            "functions": entries[:20],
            "function_count_sampled": len(entries),
        },
    }


def _collect_idl_manual_evidence(root: Path, query: str, goal: str, top_k: int) -> list[dict[str, Any]]:
    if not _looks_like_idl_request(query, goal):
        return []
    if "procedure signature" in goal.lower() and any(name in query.lower() for name in _IDL_KNOWN_NAMES):
        return []

    evidence: list[dict[str, Any]] = []
    for topic in _manual_topic_candidates(query, goal):
        item = _manual_topic_to_evidence(root, topic)
        if item is not None:
            evidence.append(item)
        if topic in {"func", "funcdef"}:
            funcdef_item = _funcdef_inventory_evidence(root)
            if funcdef_item is not None:
                evidence.append(funcdef_item)
        if len(evidence) >= top_k:
            break
    return evidence[:top_k]


def _idl_payload_to_evidence(root: Path, payload: dict[str, Any], why: str) -> dict[str, Any]:
    file_path = str(payload.get("file_path", ""))
    signature = str(payload.get("signature", ""))
    docstring = str(payload.get("docstring") or "")
    category = str(payload.get("category", ""))
    snippet = _truncate(
        "\n".join(
            part for part in [
                f"{payload.get('name', '')}: {signature}" if signature else str(payload.get("name", "")),
                f"category: {category}" if category else "",
                docstring,
            ]
            if part
        )
    )
    return {
        "type": "idl",
        "path": file_path,
        "snippet": snippet,
        "score": 1.0,
        "name": payload.get("name", ""),
        "kind": payload.get("kind", "idl_procedure"),
        "start_line": payload.get("line_number"),
        "metadata": {
            "kind": "idl_procedure_signature",
            "relative_path": _relative_path(root, file_path),
            "why_relevant": why,
            "category": category,
            "params": payload.get("params", []),
            "keywords": payload.get("keywords", []),
        },
    }


def _idl_row_to_evidence(root: Path, row: dict[str, Any], why: str) -> dict[str, Any]:
    file_path = str(row.get("file_path", ""))
    signature = str(row.get("signature", ""))
    category = str(row.get("category", ""))
    return {
        "type": "idl",
        "path": file_path,
        "snippet": _truncate(f"{row.get('name', '')}: {signature}\ncategory: {category}"),
        "score": 0.95,
        "name": row.get("name", ""),
        "kind": row.get("kind", "idl_procedure"),
        "metadata": {
            "kind": "idl_procedure_catalog_row",
            "relative_path": _relative_path(root, file_path),
            "why_relevant": why,
            "category": category,
        },
    }


def _collect_idl_catalog_evidence(
    *,
    root: Path,
    swmf_root: str,
    run_dir: str | None,
    query: str,
    goal: str,
    top_k: int,
) -> list[dict[str, Any]]:
    if not _looks_like_idl_request(query, goal):
        return []

    evidence: list[dict[str, Any]] = []
    for candidate in _idl_name_candidates(query, goal):
        payload = explain_idl_procedure_for_root(
            name=candidate,
            swmf_root=swmf_root,
            run_dir=run_dir,
        )
        if payload.get("ok"):
            evidence.append(
                _idl_payload_to_evidence(
                    root,
                    payload,
                    "Exact IDL procedure match from the deterministic IDL catalog.",
                )
            )
        if len(evidence) >= top_k:
            return evidence

    if evidence and not _idl_list_intent(query, goal):
        return evidence[:top_k]

    category = _infer_idl_category(query, goal)
    listing = list_idl_procedures_for_root(
        category=category,
        swmf_root=swmf_root,
        run_dir=run_dir,
    )
    if not listing.get("ok"):
        return evidence[:top_k]

    why = (
        f"IDL procedure catalog row in category '{category}'."
        if category
        else "IDL procedure catalog row."
    )
    seen = {(item.get("path"), item.get("name")) for item in evidence}
    rows = list(listing.get("procedures", []))
    priority = {name: index for index, name in enumerate(_IDL_ENTRYPOINT_PRIORITY)}
    rows.sort(
        key=lambda row: (
            priority.get(str(row.get("name", "")).lower(), len(priority)),
            str(row.get("category", "")),
            0 if "/general/" in str(row.get("file_path", "")).lower() else 1,
            str(row.get("name", "")).lower(),
        )
    )
    for row in rows:
        key = (row.get("file_path"), row.get("name"))
        if key in seen:
            continue
        evidence.append(_idl_row_to_evidence(root, row, why))
        seen.add(key)
        if len(evidence) >= top_k:
            break

    return evidence[:top_k]


def _workflow_metadata(
    root: Path,
    item: dict[str, Any],
    *,
    default_kind: str,
    default_why: str,
) -> dict[str, Any]:
    metadata = dict(item.get("metadata") or {})
    metadata.setdefault("kind", item.get("kind") or default_kind)
    metadata.setdefault("relative_path", _relative_path(root, item.get("path", "")))
    metadata.setdefault("why_relevant", default_why)
    return metadata


def _merge_evidence(
    primary: list[dict[str, Any]],
    secondary: list[dict[str, Any]],
    top_k: int,
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in primary + secondary:
        key = (str(item.get("path", "")), str(item.get("snippet", "")))
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
        if len(merged) >= top_k:
            break
    return merged


def _metadata_kind(item: dict[str, Any]) -> str:
    metadata = item.get("metadata") or {}
    return str(metadata.get("kind") or item.get("kind") or "")


def get_evidence(
    query: str,
    mode: str | None = None,
    scope: list[str] | None = None,
    top_k: int = _DEFAULT_TOP_K,
    goal: str | None = None,
    task_type: str | None = None,
    module: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
) -> dict[str, Any]:
    """Retrieve grounded local evidence for a query.

    Use for symbol/param/file lookup, exact questions, supporting snippets for
    a claim, or evidence gathering before answering. Hybrid mode (default) runs
    keyword + semantic search and reranks. Use keyword when the query is a
    precise token or symbol name. Use semantic for natural-language questions.
    """
    failure, root = resolve_root_or_failure(swmf_root, run_dir)
    if failure is not None or root is None:
        return failure or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}

    resolved_mode = mode if mode in _VALID_MODES else "hybrid"
    resolved_task_type = _normalize_task_type(task_type)
    resolved_module = _normalize_module(module)
    resolved_scope = _append_unique_scope(list(scope or []), resolved_module)
    resolved_top_k = max(1, min(int(top_k), _MAX_TOP_K))
    goal_text = goal or query

    assert root.swmf_root_resolved is not None
    root_path = Path(root.swmf_root_resolved)

    idl_catalog_evidence = _collect_idl_catalog_evidence(
        root=root_path,
        swmf_root=root.swmf_root_resolved,
        run_dir=run_dir,
        query=query,
        goal=goal_text,
        top_k=resolved_top_k,
    )
    idl_manual_evidence = _collect_idl_manual_evidence(
        root=root_path,
        query=query,
        goal=goal_text,
        top_k=resolved_top_k,
    )

    workflow_evidence: list[dict[str, Any]] = []
    if resolved_task_type != "lookup":
        workflow_items = discover_workflow_entrypoints(
            root.swmf_root_resolved,
            resolved_module,
            resolved_task_type,
        )
        for item in workflow_items:
            item["metadata"] = _workflow_metadata(
                root_path,
                item,
                default_kind="workflow_entrypoint",
                default_why=f"Known {resolved_task_type} entrypoint",
            )
        workflow_evidence = workflow_items

    evidence, mode_used, support_summary, degraded_reason = run_evidence_search(
        swmf_root=root.swmf_root_resolved,
        query=f"{resolved_module} {goal_text}".strip() if resolved_module else goal_text,
        mode=resolved_mode,
        scope=resolved_scope,
        top_k=resolved_top_k,
        goal=goal_text,
    )

    if resolved_task_type != "lookup":
        for item in evidence:
            item["metadata"] = _workflow_metadata(
                root_path,
                item,
                default_kind=item.get("kind") or item.get("type", "code"),
                default_why=f"Supporting {resolved_task_type} evidence from search",
            )

    if resolved_task_type == "lookup":
        combined_evidence = _merge_evidence(
            _merge_evidence(idl_manual_evidence, idl_catalog_evidence, resolved_top_k),
            evidence,
            resolved_top_k,
        )
        if idl_catalog_evidence or idl_manual_evidence:
            idl_returned = sum(1 for item in combined_evidence if _metadata_kind(item).startswith("idl_"))
            support_count = max(0, len(combined_evidence) - idl_returned)
            summary = (
                f"{idl_returned} deterministic IDL evidence item(s) and "
                f"{support_count} supporting evidence item(s) found for '{query}'"
            )
        else:
            summary = support_summary
    else:
        combined_evidence = _merge_evidence(
            _merge_evidence(
                _merge_evidence(idl_manual_evidence, idl_catalog_evidence, resolved_top_k),
                workflow_evidence,
                resolved_top_k,
            ),
            evidence,
            resolved_top_k,
        )
        workflow_returned = sum(
            1 for item in combined_evidence if _metadata_kind(item) == "workflow_entrypoint"
        )
        idl_returned = sum(1 for item in combined_evidence if _metadata_kind(item).startswith("idl_"))
        support_count = max(0, len(combined_evidence) - workflow_returned - idl_returned)
        summary = (
            f"{workflow_returned} workflow evidence item(s), "
            f"{idl_returned} IDL catalog evidence item(s), and "
            f"{support_count} supporting evidence item(s) found for '{query}'"
        )

    known_unknowns: list[str] = []
    if degraded_reason:
        known_unknowns.append(degraded_reason)
    known_unknowns.append("Runtime behavior for the current case not inspected.")

    payload: dict[str, Any] = {
        "ok": True,
        "query": query,
        "mode": resolved_mode,
        "scope": resolved_scope,
        "top_k": resolved_top_k,
        "goal": goal or "",
        "task_type": resolved_task_type,
        "module": resolved_module,
        "summary": summary,
        "evidence": combined_evidence,
        "provenance": {"mode_used": mode_used, "scope": resolved_scope},
        "uncertainty": {"known_unknowns": known_unknowns},
    }
    return with_root(payload, root)


def register(app: Any) -> None:
    app.tool(
        description=(
            "Retrieve grounded local evidence for a query (source code, PARAM.XML, docs, "
            "examples, IDL). Use mode='keyword' for precise token/symbol lookup, "
            "mode='semantic' for natural-language questions, mode='hybrid' (default) "
            "for general retrieval. Use task_type='configuration'|'build'|'run'|'analysis' "
            "when you want workflow entrypoint evidence returned through the same tool. "
            "Optionally restrict to SWMF components via scope or module."
        )
    )(get_evidence)
