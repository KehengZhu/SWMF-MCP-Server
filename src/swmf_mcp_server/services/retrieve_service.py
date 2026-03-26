from __future__ import annotations

from ..catalog.template_catalog import find_examples_using_text
from ..catalog.xml_catalog import normalize_command_name
from ..core.authority import AUTHORITY_AUTHORITATIVE, AUTHORITY_DERIVED, SOURCE_KIND_COMPONENT_PARAM_XML, SOURCE_KIND_EXAMPLE_PARAM
from ..core.models import SourceCatalog


def list_available_components(catalog: SourceCatalog) -> dict:
    payload = []
    for component, info in sorted(catalog.components.items()):
        payload.append({"component": component, "versions": info.versions})

    source_paths = sorted(
        {
            item.source_path
            for entries in catalog.commands.values()
            for item in entries
            if item.source_path and item.component is not None
        }
    )

    return {
        "ok": True,
        "authority": AUTHORITY_AUTHORITATIVE,
        "source_kind": SOURCE_KIND_COMPONENT_PARAM_XML,
        "source_paths": source_paths,
        "swmf_root_resolved": catalog.swmf_root,
        "components": payload,
        "component_count": len(payload),
    }


def get_component_versions(catalog: SourceCatalog, component: str | None = None) -> dict:
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
            "authority": AUTHORITY_AUTHORITATIVE,
            "source_kind": SOURCE_KIND_COMPONENT_PARAM_XML,
            "source_paths": [],
        }

    source_paths = sorted(
        {
            item.source_path
            for entries in catalog.commands.values()
            for item in entries
            if item.component == key and item.source_path
        }
    )

    return {
        "ok": True,
        "swmf_root_resolved": catalog.swmf_root,
        "component": key,
        "versions": match.versions,
        "authority": AUTHORITY_AUTHORITATIVE,
        "source_kind": SOURCE_KIND_COMPONENT_PARAM_XML,
        "source_paths": source_paths,
    }


def find_param_command(catalog: SourceCatalog, name: str) -> dict:
    normalized = normalize_command_name(name)
    hits = catalog.commands.get(normalized, [])
    if not hits:
        return {
            "ok": False,
            "name": name,
            "normalized": normalized,
            "message": "No command found in indexed PARAM.XML sources.",
            "authority": AUTHORITY_AUTHORITATIVE,
            "source_kind": SOURCE_KIND_COMPONENT_PARAM_XML,
            "source_paths": [],
        }

    payload = []
    source_paths: set[str] = set()
    for item in hits:
        if item.source_path:
            source_paths.add(item.source_path)
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
        "authority": AUTHORITY_AUTHORITATIVE,
        "source_kind": hits[0].source_kind,
        "source_paths": sorted(source_paths),
    }


def find_example_params(catalog: SourceCatalog, query: str, max_results: int = 30) -> dict:
    results = find_examples_using_text(catalog.templates, query=query, max_results=max_results)
    return {
        "ok": True,
        "query": query,
        "swmf_root_resolved": catalog.swmf_root,
        "source_kind": SOURCE_KIND_EXAMPLE_PARAM,
        "source_paths": results,
        "authority": AUTHORITY_DERIVED,
        "matches": results,
        "match_count": len(results),
    }


def trace_param_command(catalog: SourceCatalog, name: str, max_examples: int = 20) -> dict:
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
            "definition": AUTHORITY_AUTHORITATIVE,
            "example_usage": AUTHORITY_DERIVED,
        },
        "sources": {
            "definitions": ["PARAM.XML", "component PARAM.XML"],
            "examples": ["example PARAM.in"],
        },
        "authority": AUTHORITY_DERIVED,
        "source_kind": SOURCE_KIND_COMPONENT_PARAM_XML,
        "source_paths": source_paths + examples_payload.get("matches", []),
        "swmf_root_resolved": catalog.swmf_root,
    }
