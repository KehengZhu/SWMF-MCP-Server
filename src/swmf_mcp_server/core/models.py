from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .authority import Authority


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
    resolution_notes: list[str] = field(default_factory=list)


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
