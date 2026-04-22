from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.errors import resolution_failure_payload
from ..core.models import CommandMetadata, SourceCatalog, SwmfRootResolution
from ..core.swmf_root import resolve_swmf_root
from .components import discover_component_versions
from .idl import discover_idl_macros, discover_idl_procedures, get_idl_procedure, list_idl_procedures
from .scripts import discover_scripts
from .templates import discover_example_params, find_examples_using_text
from .xml import normalize_command_name, parse_param_xml_file


@dataclass
class _CacheEntry:
    catalog: SourceCatalog
    watched_paths: list[str]
    watched_mtimes: dict[str, float]


def _file_mtime_map(paths: list[str]) -> dict[str, float]:
    mtimes: dict[str, float] = {}
    for path_text in paths:
        path = Path(path_text)
        try:
            mtimes[path_text] = path.stat().st_mtime
        except OSError:
            mtimes[path_text] = -1.0
    return mtimes


class ReferenceService:
    def __init__(self) -> None:
        self._cache_by_root: dict[str, _CacheEntry] = {}

    def _watched_paths(
        self,
        swmf_root: Path,
        xml_paths: list[Path],
        scripts: list[str],
        templates: list[str],
        idl_macros: list[str],
    ) -> list[str]:
        watched: list[str] = [
            str(swmf_root.resolve()),
            str((swmf_root / "Param").resolve()),
            str((swmf_root / "PARAM").resolve()),
            str((swmf_root / "Examples").resolve()),
            str((swmf_root / "Scripts").resolve()),
            str((swmf_root / "share" / "IDL").resolve()),
        ]
        watched.extend(str(path.resolve()) for path in xml_paths)
        watched.extend(scripts)
        watched.extend(templates)
        watched.extend(idl_macros)
        return sorted(set(watched))

    def _is_cache_valid(self, cache: _CacheEntry) -> bool:
        return _file_mtime_map(cache.watched_paths) == cache.watched_mtimes

    def _build_catalog(self, swmf_root: Path, resolution_notes: list[str] | None = None) -> SourceCatalog:
        xml_paths = sorted(swmf_root.rglob("PARAM.XML"))
        commands: dict[str, list[CommandMetadata]] = {}

        for xml_path in xml_paths:
            component: str | None = None
            try:
                rel = xml_path.resolve().relative_to(swmf_root.resolve())
                if len(rel.parts) >= 3 and rel.parts[-1] == "PARAM.XML":
                    maybe_component = rel.parts[0]
                    if len(maybe_component) == 2 and maybe_component.isalnum():
                        component = maybe_component.upper()
            except ValueError:
                component = None

            for entry in parse_param_xml_file(xml_path, component=component):
                commands.setdefault(entry.normalized, []).append(entry)

        components = discover_component_versions(swmf_root, xml_paths)
        templates = discover_example_params(swmf_root)
        scripts = discover_scripts(swmf_root)
        idl_procedures = discover_idl_procedures(swmf_root)
        idl_macros = discover_idl_macros(swmf_root)

        source_files = sorted([str(path.resolve()) for path in xml_paths] + templates + scripts + idl_macros)

        return SourceCatalog(
            swmf_root=str(swmf_root.resolve()),
            built_at_epoch_s=time.time(),
            commands=commands,
            components=components,
            templates=templates,
            scripts=scripts,
            idl_macros=idl_macros,
            source_files=source_files,
            idl_procedures=idl_procedures,
            resolution_notes=resolution_notes or [],
        )

    def get_catalog(
        self,
        swmf_root: str,
        resolution_notes: list[str] | None = None,
        force_refresh: bool = False,
    ) -> SourceCatalog:
        root_path = Path(swmf_root).resolve()
        key = str(root_path)
        cache = self._cache_by_root.get(key)
        if (not force_refresh) and cache is not None and self._is_cache_valid(cache):
            return cache.catalog

        catalog = self._build_catalog(root_path, resolution_notes=resolution_notes)
        xml_paths = sorted(root_path.rglob("PARAM.XML"))
        watched = self._watched_paths(root_path, xml_paths, catalog.scripts, catalog.templates, catalog.idl_macros)
        self._cache_by_root[key] = _CacheEntry(
            catalog=catalog,
            watched_paths=watched,
            watched_mtimes=_file_mtime_map(watched),
        )
        return catalog


_REFERENCE_SERVICE = ReferenceService()


def set_reference_service(service: ReferenceService) -> None:
    global _REFERENCE_SERVICE
    _REFERENCE_SERVICE = service


def get_reference_catalog(
    root: SwmfRootResolution,
    force_refresh: bool = False,
) -> tuple[dict[str, Any] | None, SourceCatalog | None]:
    if not root.ok or root.swmf_root_resolved is None:
        return resolution_failure_payload(root.message or "Could not resolve SWMF root.", root.resolution_notes), None

    catalog = _REFERENCE_SERVICE.get_catalog(
        swmf_root=root.swmf_root_resolved,
        resolution_notes=root.resolution_notes,
        force_refresh=force_refresh,
    )
    return None, catalog


def list_available_components(catalog: SourceCatalog) -> dict[str, Any]:
    payload = []
    for component, info in sorted(catalog.components.items()):
        payload.append({"component": component, "versions": info.versions})
    return {
        "ok": True,
        "authority": "authoritative",
        "source_kind": "component PARAM.XML",
        "swmf_root_resolved": catalog.swmf_root,
        "components": payload,
        "component_count": len(payload),
    }


def get_component_versions(catalog: SourceCatalog, component: str | None = None) -> dict[str, Any]:
    if component is None:
        return list_available_components(catalog)

    key = component.strip().upper()
    match = catalog.components.get(key)
    if match is None:
        return {
            "ok": False,
            "swmf_root_resolved": catalog.swmf_root,
            "message": f"No component versions found for component '{key}'.",
            "component": key,
            "authority": "authoritative",
            "source_kind": "component PARAM.XML",
        }

    return {
        "ok": True,
        "swmf_root_resolved": catalog.swmf_root,
        "component": key,
        "versions": match.versions,
        "authority": "authoritative",
        "source_kind": "component PARAM.XML",
    }


def find_param_command(catalog: SourceCatalog, name: str) -> dict[str, Any]:
    normalized = normalize_command_name(name)
    hits = catalog.commands.get(normalized, [])
    if not hits:
        return {
            "ok": False,
            "name": name,
            "normalized": normalized,
            "message": "No command found in indexed PARAM.XML sources.",
            "authority": "authoritative",
        }

    payload = []
    for item in hits:
        payload.append(
            {
                "name": item.name,
                "normalized": item.normalized,
                "owner_component": item.component,
                "description": item.description,
                "defaults": item.defaults,
                "allowed_values": item.allowed_values,
                "ranges": item.ranges,
                "source_kind": item.source_kind,
                "source_path": item.source_path,
                "authority": item.authority,
            }
        )

    return {
        "ok": True,
        "name": name,
        "normalized": normalized,
        "matches": payload,
        "match_count": len(payload),
        "swmf_root_resolved": catalog.swmf_root,
    }


def find_example_params(catalog: SourceCatalog, query: str, max_results: int = 30) -> dict[str, Any]:
    results = find_examples_using_text(catalog.templates, query=query, max_results=max_results)
    return {
        "ok": True,
        "query": query,
        "swmf_root_resolved": catalog.swmf_root,
        "source_kind": "example PARAM.in",
        "authority": "derived",
        "matches": results,
        "match_count": len(results),
    }


def trace_param_command(catalog: SourceCatalog, name: str, max_examples: int = 20) -> dict[str, Any]:
    command_payload = find_param_command(catalog, name=name)
    normalized = command_payload.get("normalized", normalize_command_name(name))
    examples_payload = find_example_params(catalog, query=normalized, max_results=max_examples)

    owners = sorted(
        {
            item.get("owner_component")
            for item in command_payload.get("matches", [])
            if item.get("owner_component")
        }
    )
    source_paths = sorted(
        {
            item.get("source_path")
            for item in command_payload.get("matches", [])
            if item.get("source_path")
        }
    )

    return {
        "ok": True,
        "name": name,
        "normalized": normalized,
        "defined_in": source_paths,
        "owner_components": owners,
        "example_usage_files": examples_payload.get("matches", []),
        "authorities": {
            "definition": "authoritative",
            "example_usage": "derived",
        },
        "sources": {
            "definitions": ["PARAM.XML", "component PARAM.XML"],
            "examples": ["example PARAM.in"],
        },
        "swmf_root_resolved": catalog.swmf_root,
    }


def _resolve_catalog(
    swmf_root: str | None,
    run_dir: str | None,
    force_refresh: bool,
) -> tuple[dict[str, Any] | None, SourceCatalog | None]:
    root = resolve_swmf_root(swmf_root=swmf_root, run_dir=run_dir)
    return get_reference_catalog(root=root, force_refresh=force_refresh)


def swmf_list_available_components(
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _resolve_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}
    return list_available_components(catalog)


def swmf_find_param_command(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _resolve_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}
    return find_param_command(catalog, name=name)


def swmf_get_component_versions(
    component: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _resolve_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}
    return get_component_versions(catalog, component=component)


def swmf_trace_param_command(
    name: str,
    max_examples: int = 20,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _resolve_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}
    return trace_param_command(catalog, name=name, max_examples=max_examples)


def swmf_find_example_params(
    query: str,
    max_results: int = 30,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _resolve_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {"ok": False, "hard_error": True, "message": "Could not resolve SWMF root."}
    return find_example_params(catalog, query=query, max_results=max_results)


def swmf_list_idl_procedures(
    category: str | None = None,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _resolve_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {
            "ok": False,
            "hard_error": True,
            "message": "Could not load IDL reference catalog.",
        }

    rows = list_idl_procedures(catalog.idl_procedures, category=category)
    return {
        "ok": True,
        "category": category,
        "procedures": rows,
        "count": len(rows),
        "authority": "authoritative",
        "source_kind": "idl_catalog",
        "source_paths": catalog.idl_macros,
        "swmf_root_resolved": catalog.swmf_root,
    }


def swmf_explain_idl_procedure(
    name: str,
    swmf_root: str | None = None,
    run_dir: str | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    error, catalog = _resolve_catalog(swmf_root=swmf_root, run_dir=run_dir, force_refresh=force_refresh)
    if error is not None or catalog is None:
        return error or {
            "ok": False,
            "hard_error": True,
            "message": "Could not load IDL reference catalog.",
        }

    payload = get_idl_procedure(catalog.idl_procedures, name=name)
    if payload is None:
        return {
            "ok": False,
            "hard_error": False,
            "message": f"IDL procedure not found: {name}",
            "name": name,
            "source_paths": catalog.idl_macros,
            "swmf_root_resolved": catalog.swmf_root,
        }

    return {
        "ok": True,
        "name": payload["name"],
        "kind": payload["kind"],
        "signature": payload["signature"],
        "params": payload["params"],
        "keywords": payload["keywords"],
        "docstring": payload["docstring"],
        "category": payload["category"],
        "file_path": payload["file_path"],
        "line_number": payload["line_number"],
        "authority": "authoritative",
        "source_kind": "idl_catalog",
        "source_paths": catalog.idl_macros,
        "swmf_root_resolved": catalog.swmf_root,
    }