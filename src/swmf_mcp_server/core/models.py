from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .authority import Authority

# ---------------------------------------------------------------------------
# Knowledge-base models
# ---------------------------------------------------------------------------


@dataclass
class SourceSymbol:
    """A code symbol (module, subroutine, function, sub, pro) extracted from
    SWMF source files and stored in the persistent knowledge index."""

    kind: str           # "module" | "subroutine" | "function" | "sub" | "pro"
    name: str
    file_path: str
    start_line: int     # 1-based
    component: str | None
    docstring: str | None
    source_kind: str    # matches SOURCE_KIND_* constants
    authority: Authority
    uses: list[str] = field(default_factory=list)
    param_refs: list[str] = field(default_factory=list)


@dataclass
class KnowledgeRecord:
    """A single retrievable knowledge item returned from the knowledge service."""

    kind: str           # "symbol" | "param_mention" | "file_summary"
    name: str
    text: str           # human-readable summary / snippet
    source_path: str
    start_line: int | None
    component: str | None
    authority: Authority
    source_kind: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeIndexStatus:
    """Status of the persistent SQLite knowledge index for a given SWMF root."""

    ok: bool
    db_path: str
    swmf_root: str | None
    schema_version: str
    symbol_count: int
    file_count: int
    last_built_epoch_s: float | None
    is_stale: bool      # True when not yet built, or a watched file has changed
    message: str | None
    corpus_roots: list[str] = field(default_factory=list)  # all indexed corpus roots


@dataclass
class SourceRef:
    kind: str
    path: str | None
    authority: Authority


@dataclass
class CommandMetadata:
    name: str
    normalized: str
    component: str | None
    description: str | None
    aliases: list[str] = field(default_factory=list)
    defaults: dict[str, str] = field(default_factory=dict)
    allowed_values: list[str] = field(default_factory=list)
    ranges: list[str] = field(default_factory=list)
    source_kind: str = "PARAM.XML"
    source_path: str | None = None
    authority: Authority = "authoritative"
    commandgroup: str | None = None  # name of enclosing <commandgroup> in PARAM.XML
    parameters: list[dict[str, Any]] = field(default_factory=list)  # parsed <parameter> children


@dataclass
class ComponentVersion:
    component: str
    versions: list[str] = field(default_factory=list)


@dataclass
class SourceCatalog:
    swmf_root: str
    built_at_epoch_s: float
    commands: dict[str, list[CommandMetadata]]
    components: dict[str, ComponentVersion]
    templates: list[str]
    scripts: list[str]
    idl_macros: list[str]
    source_files: list[str]
    idl_procedures: dict[str, dict[str, Any]] = field(default_factory=dict)
    resolution_notes: list[str] = field(default_factory=list)
    # Reverse index: "{COMPONENT}:{commandgroup_name}" -> list of normalized command names.
    # Used by inspect_artifact(xml_scope="commandgroup:...") and the XML audit gate.
    commandgroup_to_commands: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class SwmfRootResolution:
    ok: bool
    swmf_root_resolved: str | None
    resolution_notes: list[str]
    message: str | None = None


@dataclass
class Session:
    index: int
    commands: list[str] = field(default_factory=list)
    component_blocks: set[str] = field(default_factory=set)
    switched_components: list[tuple[str, bool]] = field(default_factory=list)
    stop_present: bool = False
    component_map_rows: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ParseResult:
    sessions: list[Session]
    errors: list[str]
    warnings: list[str]
